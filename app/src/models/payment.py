from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class PaymentMethod(SQLModel, table=True):
    __tablename__ = "payment_methods"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    code: str = Field(index=True, unique=True, nullable=False)
    is_cash: bool = Field(default=False)
    is_active: bool = Field(default=True)
    configuration: Optional[str] = None  # JSON string; never stores live secrets
    created_at: datetime = Field(default_factory=datetime.utcnow)