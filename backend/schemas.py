from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ---------- Product ----------
class ProductBase(BaseModel):
    sku: str
    name: str
    category: str
    trailer_line: Optional[str] = None
    unit_cost: float = 0.0
    stock: int = 0
    min_stock: int = 5
    location: Optional[str] = None
    supplier: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    trailer_line: Optional[str] = None
    unit_cost: Optional[float] = None
    stock: Optional[int] = None
    min_stock: Optional[int] = None
    location: Optional[str] = None
    supplier: Optional[str] = None


class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Purchase ----------
class PurchaseItemIn(BaseModel):
    product_id: int
    quantity: int
    unit_cost: float


class PurchaseItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_cost: float
    line_total: float
    model_config = ConfigDict(from_attributes=True)


class PurchaseCreate(BaseModel):
    po_number: str
    vendor: str
    date: Optional[datetime] = None
    status: str = "received"
    notes: Optional[str] = None
    items: List[PurchaseItemIn]


class PurchaseOut(BaseModel):
    id: int
    po_number: str
    vendor: str
    date: datetime
    status: str
    total: float
    notes: Optional[str] = None
    items: List[PurchaseItemOut] = []
    model_config = ConfigDict(from_attributes=True)


# ---------- Expense ----------
class ExpenseBase(BaseModel):
    date: Optional[datetime] = None
    category: str
    description: str
    amount: float
    paid_to: Optional[str] = None
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseOut(ExpenseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Movement ----------
class StockMovementOut(BaseModel):
    id: int
    date: datetime
    product_id: int
    movement_type: str
    quantity: int
    reason: Optional[str] = None
    reference: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ---------- Dashboard ----------
class DashboardKPIs(BaseModel):
    total_skus: int
    total_units: int
    inventory_value: float
    low_stock_count: int
    purchases_mtd: float
    expenses_mtd: float
    purchases_today: float
    expenses_today: float
    top_categories: List[dict]
    monthly_trend: List[dict]


# ---------- Stock Withdraw ----------
class WithdrawRequest(BaseModel):
    product_id: int
    quantity: int
    operator: str  # who took it
    reason: str    # WO number or maintenance / sample
    notes: Optional[str] = None


class RecentMovementOut(BaseModel):
    id: int
    date: datetime
    sku: str
    item_name: str
    movement_type: str
    quantity: int
    reason: Optional[str] = None
    reference: Optional[str] = None


# ---------- BoM / Production ----------
class BOMLineOut(BaseModel):
    sku: str
    name: str
    category: str
    quantity: float
    unit_cost: float
    stock: int
    line_cost: float
    sufficient: bool
    model_config = ConfigDict(from_attributes=True)


class BOMOut(BaseModel):
    trailer_line: str
    lines: List[BOMLineOut]
    total_cost: float
    max_buildable: int
    missing_skus: List[str]


class ProduceRequest(BaseModel):
    trailer_line: str
    quantity: int = 1
    wo_number: Optional[str] = None
    notes: Optional[str] = None


class WorkOrderOut(BaseModel):
    id: int
    wo_number: str
    trailer_line: str
    quantity: int
    date: datetime
    status: str
    material_cost: float
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ---------- AI ----------
class AIQuery(BaseModel):
    question: str


class AIResponse(BaseModel):
    answer: str
    data: Optional[dict] = None
