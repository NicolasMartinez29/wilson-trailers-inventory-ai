from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import Session

from . import models, schemas, ai_engine
from .database import Base, engine, get_db, SessionLocal

Base.metadata.create_all(bind=engine)


def _ensure_seeded():
    """Auto-seed if running on serverless and DB is empty."""
    db = SessionLocal()
    try:
        if db.query(models.Product).count() == 0:
            from . import seed as _seed
            _seed.run()
    finally:
        db.close()


_ensure_seeded()

app = FastAPI(title="Wilson Trailers — Inventory AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# ----------- Dashboard -----------
@app.get("/api/dashboard", response_model=schemas.DashboardKPIs)
def get_dashboard(db: Session = Depends(get_db)):
    total_skus = db.query(func.count(models.Product.id)).scalar() or 0
    total_units = db.query(func.coalesce(func.sum(models.Product.stock), 0)).scalar() or 0
    inv_value = db.query(
        func.coalesce(func.sum(models.Product.stock * models.Product.unit_cost), 0.0)
    ).scalar() or 0.0
    low_stock = db.query(func.count(models.Product.id)).filter(
        models.Product.stock <= models.Product.min_stock
    ).scalar() or 0

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today.replace(day=1)

    p_mtd = db.query(func.coalesce(func.sum(models.Purchase.total), 0.0)).filter(
        models.Purchase.date >= month_start
    ).scalar() or 0.0
    e_mtd = db.query(func.coalesce(func.sum(models.Expense.amount), 0.0)).filter(
        models.Expense.date >= month_start
    ).scalar() or 0.0
    p_today = db.query(func.coalesce(func.sum(models.Purchase.total), 0.0)).filter(
        and_(models.Purchase.date >= today, models.Purchase.date < today + timedelta(days=1))
    ).scalar() or 0.0
    e_today = db.query(func.coalesce(func.sum(models.Expense.amount), 0.0)).filter(
        and_(models.Expense.date >= today, models.Expense.date < today + timedelta(days=1))
    ).scalar() or 0.0

    cat_rows = (
        db.query(models.Product.category, func.sum(models.Product.stock * models.Product.unit_cost))
        .group_by(models.Product.category)
        .order_by(func.sum(models.Product.stock * models.Product.unit_cost).desc())
        .all()
    )
    top_categories = [{"category": c, "value": round(float(v or 0), 2)} for c, v in cat_rows]

    # Monthly trend last 6 months
    trend = []
    for i in range(5, -1, -1):
        month_ref = (today.replace(day=1) - timedelta(days=1)) if i > 0 else today
        # compute month_start_i
        anchor = today.replace(day=1)
        # back i months
        year = anchor.year
        month = anchor.month - i
        while month <= 0:
            month += 12
            year -= 1
        ms = datetime(year, month, 1)
        # next month
        nm_year, nm_month = (year + 1, 1) if month == 12 else (year, month + 1)
        me = datetime(nm_year, nm_month, 1)

        p_sum = db.query(func.coalesce(func.sum(models.Purchase.total), 0.0)).filter(
            and_(models.Purchase.date >= ms, models.Purchase.date < me)
        ).scalar() or 0.0
        e_sum = db.query(func.coalesce(func.sum(models.Expense.amount), 0.0)).filter(
            and_(models.Expense.date >= ms, models.Expense.date < me)
        ).scalar() or 0.0
        trend.append({
            "label": ms.strftime("%b"),
            "purchases": round(float(p_sum), 2),
            "expenses": round(float(e_sum), 2),
        })

    return schemas.DashboardKPIs(
        total_skus=total_skus,
        total_units=int(total_units),
        inventory_value=float(inv_value),
        low_stock_count=low_stock,
        purchases_mtd=float(p_mtd),
        expenses_mtd=float(e_mtd),
        purchases_today=float(p_today),
        expenses_today=float(e_today),
        top_categories=top_categories,
        monthly_trend=trend,
    )


# ----------- Products -----------
@app.get("/api/products", response_model=List[schemas.ProductOut])
def list_products(
    q: Optional[str] = None,
    category: Optional[str] = None,
    low_only: bool = False,
    db: Session = Depends(get_db),
):
    qs = db.query(models.Product)
    if q:
        like = f"%{q}%"
        qs = qs.filter((models.Product.name.ilike(like)) | (models.Product.sku.ilike(like)))
    if category:
        qs = qs.filter(models.Product.category == category)
    if low_only:
        qs = qs.filter(models.Product.stock <= models.Product.min_stock)
    return qs.order_by(models.Product.name).all()


@app.post("/api/products", response_model=schemas.ProductOut)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    if db.query(models.Product).filter(models.Product.sku == payload.sku).first():
        raise HTTPException(400, "SKU already exists")
    p = models.Product(**payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.put("/api/products/{pid}", response_model=schemas.ProductOut)
def update_product(pid: int, payload: schemas.ProductUpdate, db: Session = Depends(get_db)):
    p = db.query(models.Product).get(pid)
    if not p:
        raise HTTPException(404, "Not found")
    prev_stock = p.stock
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    # Movement if stock changed
    if payload.stock is not None and payload.stock != prev_stock:
        diff = payload.stock - prev_stock
        mv = models.StockMovement(
            product_id=p.id,
            movement_type="ADJUST",
            quantity=abs(diff),
            reason=f"Ajuste manual ({'+' if diff > 0 else '-'}{abs(diff)})",
        )
        db.add(mv)
        db.commit()
    return p


@app.delete("/api/products/{pid}")
def delete_product(pid: int, db: Session = Depends(get_db)):
    p = db.query(models.Product).get(pid)
    if not p:
        raise HTTPException(404, "Not found")
    db.delete(p)
    db.commit()
    return {"ok": True}


# ----------- Purchases -----------
@app.get("/api/purchases", response_model=List[schemas.PurchaseOut])
def list_purchases(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Purchase).order_by(models.Purchase.date.desc()).limit(limit).all()


@app.post("/api/purchases", response_model=schemas.PurchaseOut)
def create_purchase(payload: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    if db.query(models.Purchase).filter(models.Purchase.po_number == payload.po_number).first():
        raise HTTPException(400, "PO number already exists")

    total = 0.0
    purchase = models.Purchase(
        po_number=payload.po_number,
        vendor=payload.vendor,
        date=payload.date or datetime.utcnow(),
        status=payload.status,
        notes=payload.notes,
        total=0.0,
    )
    db.add(purchase)
    db.flush()

    for it in payload.items:
        product = db.query(models.Product).get(it.product_id)
        if not product:
            raise HTTPException(400, f"Product {it.product_id} not found")
        line = round(it.quantity * it.unit_cost, 2)
        total += line
        db.add(models.PurchaseItem(
            purchase_id=purchase.id,
            product_id=product.id,
            quantity=it.quantity,
            unit_cost=it.unit_cost,
            line_total=line,
        ))
        if payload.status == "received":
            product.stock += it.quantity
            db.add(models.StockMovement(
                product_id=product.id,
                movement_type="IN",
                quantity=it.quantity,
                reason=f"Compra {payload.po_number}",
                reference=payload.po_number,
            ))

    purchase.total = round(total, 2)
    db.commit()
    db.refresh(purchase)
    return purchase


# ----------- Expenses -----------
@app.get("/api/expenses", response_model=List[schemas.ExpenseOut])
def list_expenses(limit: int = 200, category: Optional[str] = None, db: Session = Depends(get_db)):
    qs = db.query(models.Expense)
    if category:
        qs = qs.filter(models.Expense.category == category)
    return qs.order_by(models.Expense.date.desc()).limit(limit).all()


@app.post("/api/expenses", response_model=schemas.ExpenseOut)
def create_expense(payload: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    e = models.Expense(
        date=payload.date or datetime.utcnow(),
        category=payload.category,
        description=payload.description,
        amount=payload.amount,
        paid_to=payload.paid_to,
        notes=payload.notes,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


# ----------- History -----------
@app.get("/api/history")
def get_history(limit: int = 100, db: Session = Depends(get_db)):
    moves = db.query(models.StockMovement).order_by(models.StockMovement.date.desc()).limit(limit).all()
    purchases = db.query(models.Purchase).order_by(models.Purchase.date.desc()).limit(limit).all()
    expenses = db.query(models.Expense).order_by(models.Expense.date.desc()).limit(limit).all()

    timeline = []
    for m in moves:
        prod = db.query(models.Product).get(m.product_id)
        timeline.append({
            "date": m.date.isoformat(),
            "type": "movement",
            "title": f"{m.movement_type} · {prod.sku if prod else '?'} — {m.quantity}u",
            "subtitle": m.reason or "",
            "icon": "📦",
        })
    for p in purchases:
        timeline.append({
            "date": p.date.isoformat(),
            "type": "purchase",
            "title": f"Compra {p.po_number} — {p.vendor}",
            "subtitle": f"${p.total:,.2f}",
            "icon": "🛒",
        })
    for e in expenses:
        timeline.append({
            "date": e.date.isoformat(),
            "type": "expense",
            "title": f"{e.category} — {e.description}",
            "subtitle": f"${e.amount:,.2f}",
            "icon": "💸",
        })

    timeline.sort(key=lambda x: x["date"], reverse=True)
    return timeline[:limit]


# ----------- BoM / Production -----------
@app.get("/api/bom/{trailer_line}", response_model=schemas.BOMOut)
def get_bom(trailer_line: str, db: Session = Depends(get_db)):
    rows = (
        db.query(models.BOMLine)
        .filter(models.BOMLine.trailer_line == trailer_line)
        .all()
    )
    if not rows:
        raise HTTPException(404, f"No BoM defined for {trailer_line}")

    lines = []
    total = 0.0
    max_buildable = float("inf")
    missing = []
    for bl in rows:
        p = bl.product
        line_cost = bl.quantity * p.unit_cost
        total += line_cost
        sufficient = p.stock >= bl.quantity
        if not sufficient:
            missing.append(p.sku)
        if bl.quantity > 0:
            buildable = int(p.stock // bl.quantity)
            max_buildable = min(max_buildable, buildable)
        lines.append(schemas.BOMLineOut(
            sku=p.sku, name=p.name, category=p.category,
            quantity=bl.quantity, unit_cost=p.unit_cost,
            stock=p.stock, line_cost=round(line_cost, 2),
            sufficient=sufficient,
        ))
    return schemas.BOMOut(
        trailer_line=trailer_line,
        lines=sorted(lines, key=lambda l: l.line_cost, reverse=True),
        total_cost=round(total, 2),
        max_buildable=0 if max_buildable == float("inf") else int(max_buildable),
        missing_skus=missing,
    )


@app.get("/api/bom")
def list_bom_lines(db: Session = Depends(get_db)):
    rows = db.query(models.BOMLine.trailer_line).distinct().all()
    out = []
    for (line,) in rows:
        bom = get_bom(line, db)
        out.append({
            "trailer_line": line,
            "total_cost": bom.total_cost,
            "max_buildable": bom.max_buildable,
            "missing_count": len(bom.missing_skus),
            "line_count": len(bom.lines),
        })
    return out


@app.get("/api/work-orders", response_model=List[schemas.WorkOrderOut])
def list_work_orders(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(models.WorkOrder).order_by(models.WorkOrder.date.desc()).limit(limit).all()


@app.post("/api/produce", response_model=schemas.WorkOrderOut)
def produce(payload: schemas.ProduceRequest, db: Session = Depends(get_db)):
    bom = db.query(models.BOMLine).filter(models.BOMLine.trailer_line == payload.trailer_line).all()
    if not bom:
        raise HTTPException(400, f"No BoM for {payload.trailer_line}")
    if payload.quantity < 1:
        raise HTTPException(400, "quantity must be >= 1")

    # Check sufficient stock
    insufficient = []
    for bl in bom:
        need = bl.quantity * payload.quantity
        if bl.product.stock < need:
            insufficient.append({
                "sku": bl.product.sku, "name": bl.product.name,
                "need": need, "have": bl.product.stock,
            })
    if insufficient:
        raise HTTPException(400, {
            "error": "insufficient_stock",
            "items": insufficient,
        })

    wo_num = payload.wo_number or f"WO-{int(datetime.utcnow().timestamp()) % 100000:05d}"
    if db.query(models.WorkOrder).filter(models.WorkOrder.wo_number == wo_num).first():
        raise HTTPException(400, "wo_number already exists")

    material_cost = 0.0
    now = datetime.utcnow()
    for bl in bom:
        consumed = bl.quantity * payload.quantity
        material_cost += consumed * bl.product.unit_cost
        qty_int = max(1, int(round(consumed)))
        bl.product.stock = max(0, bl.product.stock - qty_int)
        db.add(models.StockMovement(
            date=now, product_id=bl.product_id,
            movement_type="OUT", quantity=qty_int,
            reason=f"Producción {payload.trailer_line} {wo_num}",
            reference=wo_num,
        ))

    wo = models.WorkOrder(
        wo_number=wo_num, trailer_line=payload.trailer_line,
        quantity=payload.quantity, date=now,
        status="completed", material_cost=round(material_cost, 2),
        notes=payload.notes,
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    return wo


# ----------- AI Assistant -----------
@app.post("/api/ai/ask", response_model=schemas.AIResponse)
def ai_ask(query: schemas.AIQuery, db: Session = Depends(get_db)):
    result = ai_engine.answer(query.question, db)
    return schemas.AIResponse(answer=result["answer"], data=result.get("data"))


# ----------- Meta -----------
@app.get("/api/meta/categories")
def categories(db: Session = Depends(get_db)):
    rows = db.query(models.Product.category).distinct().all()
    return sorted([r[0] for r in rows if r[0]])


@app.get("/api/meta/vendors")
def vendors(db: Session = Depends(get_db)):
    rows = db.query(models.Purchase.vendor).distinct().all()
    return sorted([r[0] for r in rows if r[0]])


@app.get("/api/meta/expense_categories")
def expense_categories(db: Session = Depends(get_db)):
    rows = db.query(models.Expense.category).distinct().all()
    return sorted([r[0] for r in rows if r[0]])


# ----------- Frontend (last) -----------
@app.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
