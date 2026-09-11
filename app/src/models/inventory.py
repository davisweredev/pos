from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class StockAdjustment(SQLModel, table=True):
    __tablename__ = "stock_adjustments"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", index=True, nullable=False)
    quantity_change: int = Field(nullable=False)
    adjustment_type: str = Field(
        default="restock", index=True, nullable=False
    )  # restock | removal | correction | sale
    reason: Optional[str] = None
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)