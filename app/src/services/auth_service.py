import bcrypt
from sqlmodel import select
from app.src.database.db import db
from app.src.models.user import User


class AuthService:
    """Handles user registration and authentication."""

    def register(self, name, email, username, password):
        if not all([name, email, username, password]):
            return False, "All fields are required."

        # check if username/email exists
        with next(db.get_session()) as session:
            existing = session.exec(
                select(User).where((User.username == username) | (User.email == email))
            ).first()
            if existing:
                return False, "Username or email already exists."

            # hash password
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            # create user
            user = User(
                full_name=name,
                email=email,
                username=username,
                password_hash=hashed,
            )
            session.add(user)
            session.commit()

        return True, "Registration successful!"
