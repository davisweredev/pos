import bcrypt


class AuthService:
    def __init__(self):
        self.users = []  # temporary storage for testing

    def register(self, name, email, username, password):
        if not all([name, email, username, password]):
            return False, "All fields are required."
        if any(u["username"] == username for u in self.users):
            return False, "Username already exists."

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.users.append(
            {"name": name, "email": email, "username": username, "password": hashed}
        )
        return True, "Registration successful!"
