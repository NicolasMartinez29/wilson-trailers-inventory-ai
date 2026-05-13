"""
AI Engine - Local-first inventory intelligence (English).
Answers natural language questions about inventory, purchases, expenses,
production capacity, and SKU runout forecasts.
"""
import os
import re
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from . import models


def _today_range():
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return today, today + timedelta(days=1)


def _month_range():
    today = datetime.utcnow()
    start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start, today


def _summarize_state(db: Session) -> dict:
    total_skus = db.query(func.count(models.Product.id)).scalar() or 0
    total_units = db.query(func.coalesce(func.sum(models.Product.stock), 0)).scalar() or 0
    inventory_value = db.query(
        func.coalesce(func.sum(models.Product.stock * models.Product.unit_cost), 0.0)
    ).scalar() or 0.0
    low_stock = (
        db.query(models.Product)
        .filter(models.Product.stock <= models.Product.min_stock)
        .order_by(models.Product.stock.asc())
        .limit(10)
        .all()
    )
    m_start, _ = _month_range()
    purchases_mtd = db.query(
        func.coalesce(func.sum(models.Purchase.total), 0.0)
    ).filter(models.Purchase.date >= m_start).scalar() or 0.0
    expenses_mtd = db.query(
        func.coalesce(func.sum(models.Expense.amount), 0.0)
    ).filter(models.Expense.date >= m_start).scalar() or 0.0

    t_start, t_end = _today_range()
    purchases_today = db.query(
        func.coalesce(func.sum(models.Purchase.total), 0.0)
    ).filter(and_(models.Purchase.date >= t_start, models.Purchase.date < t_end)).scalar() or 0.0
    expenses_today = db.query(
        func.coalesce(func.sum(models.Expense.amount), 0.0)
    ).filter(and_(models.Expense.date >= t_start, models.Expense.date < t_end)).scalar() or 0.0

    top_value = (
        db.query(models.Product)
        .order_by((models.Product.stock * models.Product.unit_cost).desc())
        .limit(5)
        .all()
    )

    return {
        "total_skus": total_skus,
        "total_units": int(total_units),
        "inventory_value": float(inventory_value),
        "purchases_mtd": float(purchases_mtd),
        "expenses_mtd": float(expenses_mtd),
        "purchases_today": float(purchases_today),
        "expenses_today": float(expenses_today),
        "low_stock": [
            {"sku": p.sku, "name": p.name, "stock": p.stock, "min_stock": p.min_stock}
            for p in low_stock
        ],
        "top_value": [
            {
                "sku": p.sku, "name": p.name, "stock": p.stock,
                "unit_cost": p.unit_cost,
                "value": round(p.stock * p.unit_cost, 2),
            }
            for p in top_value
        ],
    }


def _forecast_runout(db: Session, top_n: int = 8):
    cutoff = datetime.utcnow() - timedelta(days=60)
    rows = (
        db.query(
            models.StockMovement.product_id,
            func.sum(models.StockMovement.quantity).label("total_out"),
        )
        .filter(
            models.StockMovement.movement_type == "OUT",
            models.StockMovement.date >= cutoff,
        )
        .group_by(models.StockMovement.product_id)
        .all()
    )
    forecast = []
    for pid, total_out in rows:
        p = db.query(models.Product).get(pid)
        if not p or not total_out:
            continue
        daily = float(total_out) / 60.0
        if daily <= 0:
            continue
        days_left = p.stock / daily if daily > 0 else float("inf")
        forecast.append({
            "sku": p.sku, "name": p.name, "stock": p.stock,
            "daily_rate": round(daily, 2),
            "days_left": round(days_left, 1),
            "supplier": p.supplier,
        })
    forecast.sort(key=lambda x: x["days_left"])
    return forecast[:top_n]


def _local_answer(question: str, state: dict, db: Session) -> str:
    q = question.lower().strip()
    money = lambda v: f"${v:,.2f}"

    # Runout forecast
    if any(k in q for k in ["forecast", "runout", "run out", "run-out", "days left", "deplete", "going to run", "first to", "out first", "acab"]):
        fc = _forecast_runout(db)
        if not fc:
            return "Not enough consumption history to forecast."
        lines = ["**Runout forecast (based on last 60 days of consumption):**\n"]
        for it in fc:
            days = it["days_left"]
            flag = "CRITICAL" if days < 14 else ("WARN" if days < 30 else "")
            lines.append(
                f"- `{it['sku']}` {it['name']}: **{int(days)}d** "
                f"(stock {it['stock']}, rate {it['daily_rate']}/day)"
                + (f"  [{flag}]" if flag else "")
            )
        if fc[0].get("supplier"):
            lines.append(f"\nMost critical SKU supplier: **{fc[0]['supplier']}**")
        return "\n".join(lines)

    # Production capacity
    if any(k in q for k in ["produce", "build", "buildable", "production", "make", "manufactur"]):
        boms = db.query(models.BOMLine.trailer_line).distinct().all()
        lines_list = [b[0] for b in boms]
        if not lines_list:
            return "No Bills of Materials loaded."
        lines = ["**Current production capacity:**\n"]
        for line in lines_list:
            bom = db.query(models.BOMLine).filter(models.BOMLine.trailer_line == line).all()
            buildable = float("inf")
            total_cost = 0.0
            for bl in bom:
                if bl.quantity > 0:
                    buildable = min(buildable, int(bl.product.stock // bl.quantity))
                total_cost += bl.quantity * bl.product.unit_cost
            buildable = 0 if buildable == float("inf") else int(buildable)
            lines.append(f"- **{line}**: you can build **{buildable}** units (material cost/unit: {money(total_cost)})")
        return "\n".join(lines)

    # Total stock
    if any(k in q for k in ["how much stock", "total stock", "stock total", "total inventory", "inventory total", "how many units"]):
        return (
            f"You have **{state['total_units']:,} units** across "
            f"**{state['total_skus']} SKUs**, total inventory value "
            f"**{money(state['inventory_value'])}**."
        )

    # Low stock / alerts
    if any(k in q for k in ["low", "alert", "reorder", "below min", "minimum", "short"]):
        if not state["low_stock"]:
            return "All SKUs are above minimum threshold."
        lines = [f"**{len(state['low_stock'])} SKUs below minimum:**\n"]
        for it in state["low_stock"][:8]:
            lines.append(f"- `{it['sku']}` {it['name']}: **{it['stock']}u** (min {it['min_stock']})")
        return "\n".join(lines)

    # Purchases
    if any(k in q for k in ["purchas", "po ", "vendor", "supplier", "buy", "bought"]):
        if "today" in q:
            return f"Purchases today: **{money(state['purchases_today'])}**."
        if "month" in q or "mtd" in q:
            return f"Purchases month-to-date: **{money(state['purchases_mtd'])}**."
        recent = db.query(models.Purchase).order_by(models.Purchase.date.desc()).limit(5).all()
        if not recent:
            return "No purchase orders on record."
        lines = ["**Recent 5 purchase orders:**"]
        for p in recent:
            lines.append(f"- `{p.po_number}` {p.vendor} - {money(p.total)} ({p.date.strftime('%Y-%m-%d')})")
        return "\n".join(lines)

    # Expenses
    if any(k in q for k in ["expense", "spend", "spent", "cost", "operating cost"]):
        if "today" in q:
            return f"Expenses today: **{money(state['expenses_today'])}**."
        if "month" in q or "mtd" in q or "categor" in q:
            m_start, _ = _month_range()
            rows = (
                db.query(models.Expense.category, func.sum(models.Expense.amount))
                .filter(models.Expense.date >= m_start)
                .group_by(models.Expense.category)
                .order_by(func.sum(models.Expense.amount).desc())
                .all()
            )
            lines = [f"**Expenses MTD: {money(state['expenses_mtd'])}**"]
            for cat, amt in rows:
                lines.append(f"- {cat}: {money(amt)}")
            return "\n".join(lines)
        recent = db.query(models.Expense).order_by(models.Expense.date.desc()).limit(5).all()
        lines = ["**Recent 5 expenses:**"]
        for e in recent:
            lines.append(f"- {e.date.strftime('%Y-%m-%d')} {e.category}: {e.description} - {money(e.amount)}")
        return "\n".join(lines)

    # Top value
    if any(k in q for k in ["top", "expensive", "highest", "most valuable", "by value", "ranking"]):
        lines = ["**Top 5 SKUs by inventory value:**"]
        for it in state["top_value"]:
            lines.append(f"- `{it['sku']}` {it['name']}: {it['stock']}u x {money(it['unit_cost'])} = **{money(it['value'])}**")
        return "\n".join(lines)

    # Summary
    if any(k in q for k in ["summary", "status", "overview", "snapshot", "resumen"]):
        return (
            f"**Wilson Trailers - Operations Summary**\n"
            f"- Inventory: {state['total_units']:,}u across {state['total_skus']} SKUs ({money(state['inventory_value'])})\n"
            f"- Purchases MTD: {money(state['purchases_mtd'])} | Today: {money(state['purchases_today'])}\n"
            f"- Expenses MTD: {money(state['expenses_mtd'])} | Today: {money(state['expenses_today'])}\n"
            f"- Low-stock alerts: **{len(state['low_stock'])}**"
        )

    # SKU direct lookup
    sku_match = re.search(r"\b([A-Z]{2,}-[A-Z0-9]+-?[A-Z0-9]+)\b", question.upper())
    if sku_match:
        sku = sku_match.group(1)
        p = db.query(models.Product).filter(models.Product.sku == sku).first()
        if p:
            return (
                f"**`{p.sku}` {p.name}**\n"
                f"- Stock: {p.stock}u (min {p.min_stock})\n"
                f"- Unit cost: {money(p.unit_cost)}\n"
                f"- Inventory value: {money(p.stock * p.unit_cost)}\n"
                f"- Category: {p.category} | Line: {p.trailer_line or '-'}\n"
                f"- Location: {p.location or '-'} | Supplier: {p.supplier or '-'}"
            )

    return (
        "Try asking:\n"
        "- summary\n"
        "- how many trailers can I build\n"
        "- which SKUs run out first\n"
        "- purchases this month\n"
        "- expenses by category\n"
        "- top SKUs by value\n"
        "- skus below minimum"
    )


def _claude_answer(question: str, state: dict) -> str | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        system = (
            "You are an inventory assistant for Wilson Trailer Co. "
            "Respond in English, concise, with money as $1,234.56. "
            "Use only the provided data. If a question cannot be answered "
            "with the data, say so."
        )
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=system,
            messages=[{
                "role": "user",
                "content": f"Current system data:\n{state}\n\nUser question: {question}",
            }],
        )
        return msg.content[0].text
    except Exception:
        return None


def answer(question: str, db: Session) -> dict:
    state = _summarize_state(db)
    claude = _claude_answer(question, state)
    if claude:
        return {"answer": claude, "data": state, "source": "claude"}
    return {"answer": _local_answer(question, state, db), "data": state, "source": "local"}
