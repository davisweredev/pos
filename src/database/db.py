from pathlib import Path
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BASE_DIR / "pos.db" #this our test db, not used in production
DB_URL = f"sqlite:///{DB_FILE}"


class Database:
    """Engine + session provider for the app."""

    def __init__(self, db_url: str | None = None):
        self.db_url = db_url or DB_URL
        self.engine = create_engine(
            self.db_url,
            echo=False,
            connect_args={"check_same_thread": False},  
        )

    def create_tables(self) -> None:
        """Create all SQLModel tables (call once at startup / seed)."""
        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """Yield a session; intended for short-lived use."""
        with Session(self.engine) as session:
            yield session

db = Database()
