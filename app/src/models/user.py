from datetime import datetime
from typing import ClassVar, Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    USER_TYPES: ClassVar = ("admin", "staff")

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    full_name: Optional[str] = None
    user_type: str = Field(default="staff", index=True, nullable=False)
    is_active: bool = Field(default=True)
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def is_admin(self) -> bool:
        return self.user_type == "admin"