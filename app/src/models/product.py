from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    sku: Optional[str] = Field(index=True, unique=True)
    category_id: Optional[int] = Field(
        default=None, foreign_key="categories.id", index=True
    )
    price: float = Field(default=0.0, nullable=False)
    cost_price: float = Field(default=0.0)
    stock: int = Field(default=0)
    low_stock: int = Field(default=5)
    image: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)