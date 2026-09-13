from sqlmodel import select

from app.src.database.db import db
from app.src.models.user import User
from app.src.services.auth_service import AuthService

VALID_USER_TYPES = User.USER_TYPES


class UserService:
    """CRUD operations for users. Role/record checks are performed here."""

    @staticmethod
    def list_users() -> list[User]:
        with next(db.get_session()) as session:
            return session.exec(select(User).order_by(User.created_at.desc())).all()

    @staticmethod
    def active_staff_count() -> int:
        with next(db.get_session()) as session:
            return len(
                session.exec(
                    select(User).where(User.is_active == True, User.user_type != "admin")  # noqa: E712
                ).all()
            )

    @staticmethod
    def create_user(full_name, email, username, password, user_type) -> tuple[bool, str]:
        return AuthService().register(full_name, email, username, password, user_type)

    @staticmethod
    def update_user(
        user_id: int,
        full_name: str,
        email: str,
        username: str,
        user_type: str,
        is_active: bool,
        new_password: str | None = None,
    ) -> tuple[bool, str]:
        if user_type not in VALID_USER_TYPES:
            return False, "Invalid user type."
        if new_password and len(new_password.strip()) < 6:
            return False, "Password must be at least 6 characters."

        with next(db.get_session()) as session:
            user = session.get(User, user_id)
            if not user:
                return False, "User not found."

            existing = session.exec(
                select(User).where(
                    ((User.username == username.strip()) | (User.email == email.strip().lower())),
                    User.id != user_id,
                )
            ).first()
            if existing:
                return False, "Username or email is already in use."

            user.full_name = full_name.strip()
            user.email = email.strip().lower()
            user.username = username.strip()
            user.user_type = user_type
            user.is_active = is_active
            if new_password and new_password.strip():
                user.password_hash = AuthService.hash_password(new_password.strip())
            session.add(user)
            session.commit()

        return True, "User updated successfully."

    @staticmethod
    def toggle_active(user_id: int) -> tuple[bool, str, bool | None]:
        with next(db.get_session()) as session:
            user = session.get(User, user_id)
            if not user:
                return False, "User not found.", None
            user.is_active = not user.is_active
            session.add(user)
            session.commit()
            return True, f"User {'activated' if user.is_active else 'deactivated'}.", user.is_active

    @staticmethod
    def delete_user(user_id: int) -> tuple[bool, str]:
        with next(db.get_session()) as session:
            user = session.get(User, user_id)
            if not user:
                return False, "User not found."
            session.delete(user)
            session.commit()
        return True, "User deleted."

    @staticmethod
    def get_user(user_id: int) -> User | None:
        with next(db.get_session()) as session:
            return session.get(User, user_id)