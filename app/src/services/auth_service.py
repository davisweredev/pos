import re
from datetime import datetime

import bcrypt
from sqlmodel import select

from app.src.database.db import db
from app.src.models.user import User


class AuthService:
    """Handles user registration, authentication, credentials and profile updates."""

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except ValueError:
            return False

    def register(self, name, email, username, password, user_type="staff"):
        if not all([name, email, username, password]):
            return False, "All fields are required."
        if user_type not in User.USER_TYPES:
            return False, "Invalid user type."
        if not self._valid_email(email):
            return False, "Enter a valid email address."
        if len(password.strip()) < 6:
            return False, "Password must be at least 6 characters."

        with next(db.get_session()) as session:
            existing = session.exec(
                select(User).where((User.username == username) | (User.email == email))
            ).first()
            if existing:
                return False, "Username or email already exists."

            user = User(
                full_name=name.strip(),
                email=email.strip().lower(),
                username=username.strip(),
                password_hash=self.hash_password(password),
                user_type=user_type,
            )
            session.add(user)
            session.commit()

        return True, "User created successfully."

    def login(self, username_or_email: str, password: str):
        """Authenticate a user. Returns (ok: bool, message: str, user: User | None)."""
        identifier = (username_or_email or "").strip()
        if not identifier or not password:
            return False, "Enter your username/email and password.", None

        with next(db.get_session()) as session:
            user = session.exec(
                select(User).where(
                    (User.username == identifier) | (User.email == identifier.lower())
                )
            ).first()

            if not user or not self.verify_password(password, user.password_hash):
                return False, "Invalid username/email or password.", None

            if not user.is_active:
                return False, "This account is inactive. Contact your administrator.", None

            user.last_login = datetime.utcnow()
            session.add(user)
            session.commit()

        return True, "Login successful.", user

    def change_password(self, user_id: int, current_password: str, new_password: str):
        if not new_password or len(new_password.strip()) < 6:
            return False, "New password must be at least 6 characters."

        with next(db.get_session()) as session:
            user = session.get(User, user_id)
            if not user:
                return False, "User not found."
            if not self.verify_password(current_password, user.password_hash):
                return False, "Current password is incorrect."

            user.password_hash = self.hash_password(new_password.strip())
            session.add(user)
            session.commit()

        return True, "Password changed successfully."

    def update_profile(self, user_id: int, full_name: str, email: str):
        if not full_name or not full_name.strip():
            return False, "Full name is required."
        if not self._valid_email(email):
            return False, "Enter a valid email address."

        with next(db.get_session()) as session:
            user = session.get(User, user_id)
            if not user:
                return False, "User not found."

            existing = session.exec(
                select(User).where(User.email == email.strip().lower(), User.id != user_id)
            ).first()
            if existing:
                return False, "Email is already in use by another account."

            user.full_name = full_name.strip()
            user.email = email.strip().lower()
            session.add(user)
            session.commit()

        return True, "Profile updated successfully."

    @staticmethod
    def _valid_email(email: str) -> bool:
        return bool(re.match(r"^[\w\.\+\-]+@[\w\-]+\.[\w\.\-]+$", email.strip()))