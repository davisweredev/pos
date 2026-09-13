import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BASE_DIR / "pos.db"  # this our test db, not used in production
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

    @staticmethod
    def _db_file(db_url: str) -> Path:
        prefix = "sqlite:///"
        if db_url.startswith(prefix):
            return Path(db_url[len(prefix):])
        raise ValueError(f"Unsupported database URL: {db_url}")

    @staticmethod
    def _model_columns() -> dict[str, set[str]]:
        return {
            table.name: {column.name for column in table.columns}
            for table in SQLModel.metadata.sorted_tables
        }

    def schema_is_current(self) -> bool:
        """True when every model table exists with all of its columns.

        SQLModel's ``create_all`` never alters existing tables, so a database
        created by an older revision is missing new columns and raises
        ``no such column`` on every read. This is a dev/test database, so an
        outdated schema is safely rebuilt instead of crashing the app.
        """
        path = self._db_file(self.db_url)
        if not path.exists():
            return True
        try:
            connection = sqlite3.connect(path)
        except sqlite3.Error:
            return False
        existing: dict[str, set[str]] = {}
        try:
            names = [
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            ]
            for name in names:
                existing[name] = {
                    row[1] for row in connection.execute(f"PRAGMA table_info({name})")
                }
        except sqlite3.Error:
            return False
        finally:
            connection.close()

        for table, columns in self._model_columns().items():
            if table not in existing or not columns.issubset(existing[table]):
                return False
        return True

    def rebuild_if_outdated(self) -> bool:
        """Back up and recreate the dev database when its schema is stale.

        The original file is preserved as ``pos.db.bak-<timestamp>``. Returns
        True when the database was rebuilt.
        """
        if self.schema_is_current():
            return False
        path = self._db_file(self.db_url)
        if path.exists():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = path.with_name(f"pos.db.bak-{stamp}")
            path.replace(backup)
            print(f"Debug database schema out of date; backed up to {backup}")
        return True

    def create_tables(self) -> None:
        """Create all SQLModel tables (call once at startup / seed).

        A stale database is rebuilt first so the new models can be read.
        """
        self.rebuild_if_outdated()
        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """Yield a session; intended for short-lived use."""
        with Session(self.engine, expire_on_commit=False) as session:
            yield session

db = Database()
