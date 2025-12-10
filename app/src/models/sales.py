from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Sale(SQLModel, table=True):
    __tablename__ = "sales"

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_number: str = Field(index=True, unique=True, nullable=False)
    user_id: int = Field(foreign_key="users.id")
    total_amount: float = Field(default=0)
    discount: float = Field(default=0)
    vat: float = Field(default=0)  # percentage or calculated total VAT
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SaleItem(SQLModel, table=True):
    __tablename__ = "sale_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    sale_id: int = Field(foreign_key="sales.id", nullable=False)
    product_id: int = Field(foreign_key="products.id", nullable=False)
    quantity: int = Field(default=1)
    unit_price: float = Field(nullable=False)
    total_price: float = Field(nullable=False)
