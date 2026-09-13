"""Top-level application router: login, admin dashboard, staff placeholder."""
import flet as ft

from app.src.core.theme import apply_theme
from app.src.database.seed import seed_database
from app.src.models.user import User
from app.src.ui.admin.admin_shell import AdminShell
from app.src.ui.auth.login_view import LoginView
from app.src.ui.auth.staff_view import StaffPlaceholderView


class PosApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_user: User | None = None

    def start(self):
        page = self.page
        page.title = "SwiftPOS — Point of Sale"
        apply_theme(page)
        seed_database()
        self.show_login()

    # ------------------------------------------------------------- lifecycle
    def _render(self, control: ft.Control):
        self.page.clean()
        self.page.add(control)
        self.page.update()
        if hasattr(control, "post_attach"):
            control.post_attach()

    def show_login(self):
        self.current_user = None
        self._render(LoginView(self.page, self._on_login_success))

    def _on_login_success(self, user: User, area: str):
        self.current_user = user
        if area == "admin":
            self.show_admin(user)
        else:
            self.show_staff(user)

    def show_admin(self, user: User):
        if not user.is_admin():
            # Authorization enforced on the application layer, not just the UI.
            self.show_staff(user)
            return
        self._render(AdminShell(self.page, user, on_logout=self.show_login))

    def show_staff(self, user: User):
        self._render(StaffPlaceholderView(self.page, user, on_logout=self.show_login))

    def logout(self):
        self.show_login()