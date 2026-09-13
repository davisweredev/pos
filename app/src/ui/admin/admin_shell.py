"""Admin shell: sidebar, header, section router and all admin views."""
import flet as ft

from app.src.core.theme import (
    BG,
    BORDER,
    DANGER,
    HEADER_BG,
    PRIMARY,
    SIDEBAR_BG,
    TEXT,
    TEXT_ON_DARK,
    TEXT_ON_DARK_MUTED,
    TEXT_SECONDARY,
)
from app.src.models.user import User
from app.src.ui.components.widgets import (
    empty_state,
    form_dialog,
    loading_state,
    show_toast,
)
from app.src.ui.admin.dashboard_view import DashboardView
from app.src.ui.admin.products_view import ProductsView
from app.src.ui.admin.categories_view import CategoriesView
from app.src.ui.admin.inventory_view import InventoryView
from app.src.ui.admin.users_view import UsersView
from app.src.ui.admin.payments_view import PaymentsView
from app.src.ui.admin.reports_view import ReportsView
from app.src.ui.admin.settings_view import SettingsView
from app.src.ui.admin.sales_view import SalesView
from app.src.utils.helpers import initials


_SECTIONS = [
    ("dashboard", "Dashboard", ft.Icons.DASHBOARD),
    ("products", "Products", ft.Icons.INVENTORY_2),
    ("categories", "Categories", ft.Icons.CATEGORY),
    ("inventory", "Inventory", ft.Icons.STOREFRONT),
    ("sales", "Sales", ft.Icons.RECEIPT_LONG),
    ("reports", "Reports", ft.Icons.BAR_CHART),
    ("users", "Users", ft.Icons.PEOPLE),
    ("payments", "Payments", ft.Icons.PAYMENTS),
    ("settings", "Settings", ft.Icons.SETTINGS),
]
_SECTIONS_MAP = {k: label for k, label, _ in _SECTIONS}


def _in_page(control) -> bool:
    node = control
    while node is not None:
        if isinstance(node, ft.Page):
            return True
        node = node.parent
    return False


def _refresh(control):
    if _in_page(control):
        control.update()


# ---------------------------------------------------------------- Sidebar
class SidebarNavButton(ft.Container):
    def __init__(self, key: str, label: str, icon: str, active: bool, on_select):
        super().__init__(
            content=ft.Row(
                [
                    ft.Container(
                        width=3,
                        height=20,
                        bgcolor=ft.Colors.WHITE if active else ft.Colors.TRANSPARENT,
                        border_radius=2,
                    ),
                    ft.Icon(icon, size=18, color=TEXT_ON_DARK if active else TEXT_ON_DARK_MUTED),
                    ft.Text(
                        label,
                        size=13,
                        weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400,
                        color=TEXT_ON_DARK if active else TEXT_ON_DARK_MUTED,
                        expand=True,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(14, 10, 14, 10),
            border_radius=8,
            on_click=on_select,
            animate=ft.Animation(150, ft.AnimationCurve.DECELERATE),
        )
        self.key = key
        self.bgcolor = "#1E293B" if active else ft.Colors.TRANSPARENT
        self._active = active
        if not active:
            self.on_hover = self._on_hover

    def _on_hover(self, e):
        if self._active:
            return
        self.bgcolor = "#1E293B" if e.data == "true" else ft.Colors.TRANSPARENT
        self.update()

    def set_active(self, active: bool):
        self._active = active
        self.bgcolor = "#1E293B" if active else ft.Colors.TRANSPARENT
        row = self.content
        if isinstance(row, ft.Row) and len(row.controls) >= 3:
            icon = row.controls[1]
            text = row.controls[2]
            icon.color = TEXT_ON_DARK if active else TEXT_ON_DARK_MUTED
            text.weight = ft.FontWeight.W_600 if active else ft.FontWeight.W_400
            text.color = TEXT_ON_DARK if active else TEXT_ON_DARK_MUTED
        self.on_hover = None if active else self._on_hover
        _refresh(self)


class Sidebar(ft.Container):
    def __init__(self, user: User, active_key: str, on_select, on_logout):
        self._buttons: dict[str, SidebarNavButton] = {}
        nav_items: list[SidebarNavButton] = []
        for key, label, icon in _SECTIONS:
            btn = SidebarNavButton(
                key=key, label=label, icon=icon,
                active=key == active_key,
                on_select=lambda e, k=key: on_select(k),
            )
            self._buttons[key] = btn
            nav_items.append(btn)

        user_initials = initials(user.full_name or user.username)

        super().__init__(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(ft.Icons.POINT_OF_SALE, color=ft.Colors.WHITE, size=20),
                                    bgcolor=PRIMARY,
                                    padding=8,
                                    border_radius=8,
                                ),
                                ft.Column(
                                    [
                                        ft.Text("SwiftPOS", size=15, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
                                        ft.Text("Admin", size=10, color=TEXT_ON_DARK_MUTED),
                                    ],
                                    spacing=1,
                                ),
                            ],
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.Padding(16, 20, 16, 16),
                        margin=ft.Margin(0, 0, 0, 4),
                    ),
                    ft.Container(height=4),
                    ft.Column(nav_items, spacing=2, expand=True),
                    ft.Container(height=4),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Text(
                                        user_initials,
                                        size=12,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                    bgcolor="#475569",
                                    width=34,
                                    height=34,
                                    border_radius=17,
                                    alignment=ft.Alignment(0, 0),
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            user.full_name or user.username,
                                            size=12,
                                            weight=ft.FontWeight.W_600,
                                            color=ft.Colors.WHITE,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                        ft.Text(
                                            user.user_type.capitalize(),
                                            size=10,
                                            color=TEXT_ON_DARK_MUTED,
                                        ),
                                    ],
                                    spacing=1,
                                    expand=True,
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=ft.Padding(14, 8, 10, 8),
                        margin=ft.Margin(8, 0, 8, 8),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            width=226,
            bgcolor=SIDEBAR_BG,
            expand=True,
        )

    def set_active(self, key: str):
        for k, btn in self._buttons.items():
            btn.set_active(k == key)


# ---------------------------------------------------------------- Header
class Header(ft.Container):
    def __init__(self, user: User, section_key: str, on_logout, on_account, on_section):
        self.user = user
        self._section_label = ft.Text(
            _SECTIONS_MAP.get(section_key, section_key).capitalize(),
            size=20,
            weight=ft.FontWeight.W_700,
            color=TEXT,
        )

        super().__init__(
            content=ft.Row(
                [
                    self._section_label,
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(
                                    user.user_type.capitalize(),
                                    size=10,
                                    color=PRIMARY,
                                    weight=ft.FontWeight.W_600,
                                ),
                                bgcolor="#EFF6FF",
                                padding=ft.Padding(8, 4, 8, 4),
                                border_radius=20,
                            ),
                            ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(
                                        content=ft.Row(
                                            [ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=16), ft.Text("My Account", size=12)],
                                            spacing=8,
                                        ),
                                        on_click=on_account,
                                    ),
                                    ft.PopupMenuItem(),
                                    ft.PopupMenuItem(
                                        content=ft.Row(
                                            [ft.Icon(ft.Icons.SETTINGS, size=16), ft.Text("Settings", size=12)],
                                            spacing=8,
                                        ),
                                        on_click=lambda _: on_section("settings"),
                                    ),
                                    ft.PopupMenuItem(),
                                    ft.PopupMenuItem(
                                        content=ft.Row(
                                            [
                                                ft.Icon(ft.Icons.LOGOUT, size=16, color=DANGER),
                                                ft.Text("Sign Out", size=12, color=DANGER),
                                            ],
                                            spacing=8,
                                        ),
                                        on_click=lambda _: on_logout(),
                                    ),
                                ],
                                icon=ft.Icons.ACCOUNT_CIRCLE,
                                icon_color="#475569",
                                icon_size=22,
                                tooltip="Account",
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(28, 16, 28, 14),
            bgcolor=HEADER_BG,
            border=ft.Border(None, None, ft.BorderSide(1, BORDER), None),
        )

    def set_title(self, key: str):
        self._section_label.value = _SECTIONS_MAP.get(key, key).capitalize()
        _refresh(self)


# ---------------------------------------------------------------- Shell
class AdminShell(ft.Column):
    def __init__(self, page: ft.Page, user: User, on_logout):
        super().__init__()
        self._page = page
        self.user = user
        self._on_logout = on_logout
        self.current_section = "dashboard"

        self.header = Header(
            user=user,
            section_key=self.current_section,
            on_logout=self._on_logout,
            on_account=self._show_account,
            on_section=self.navigate,
        )

        self._content_area = ft.Container(content=loading_state("Loading"), expand=True)

        self.sidebar = Sidebar(
            user=user,
            active_key=self.current_section,
            on_select=self.navigate,
            on_logout=self._on_logout,
        )

        self.controls = [
            ft.Row(
                [
                    self.sidebar,
                    ft.Column(
                        [
                            self.header,
                            self._content_area,
                        ],
                        expand=True,
                        spacing=0,
                    ),
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        ]
        self.expand = True
        self.spacing = 0
        self.bgcolor = BG

    def post_attach(self):
        """Called by PosApp after the shell is added to the page."""
        self.navigate(self.current_section)

    # --------------------------------------------------------- navigation
    def navigate(self, key: str):
        self.current_section = key
        self.sidebar.set_active(key)
        self.header.set_title(key)
        self._content_area.content = self._build_view(key)
        if _in_page(self):
            self._page.update()

    def _build_view(self, key: str):
        match key:
            case "dashboard":
                return DashboardView(self._page, self)
            case "products":
                return ProductsView(self._page, self)
            case "categories":
                return CategoriesView(self._page, self)
            case "inventory":
                return InventoryView(self._page, self)
            case "sales":
                return SalesView(self._page, self)
            case "reports":
                return ReportsView(self._page, self)
            case "users":
                return UsersView(self._page, self)
            case "payments":
                return PaymentsView(self._page, self)
            case "settings":
                return SettingsView(self._page, self)
            case _:
                return empty_state("Section not found.")

    def toast(self, msg: str, error: bool = False):
        show_toast(self._page, msg, error)

    # --------------------------------------------------------- account modal
    def _show_account(self, e=None):
        user = self.user
        fields = [
            ft.Text("Account Information", size=15, weight=ft.FontWeight.W_600),
            ft.TextField(
                label="Full Name",
                value=user.full_name or "",
                fill_color=ft.Colors.WHITE,
                filled=True,
                border_color=BORDER,
                border_radius=8,
                expand=True,
            ),
            ft.TextField(
                label="Email",
                value=user.email or "",
                fill_color=ft.Colors.WHITE,
                filled=True,
                border_color=BORDER,
                border_radius=8,
                expand=True,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Divider(height=1, color=BORDER),
                        ft.Text("Change Password", size=14, weight=ft.FontWeight.W_600, color=TEXT_SECONDARY),
                        ft.TextField(
                            label="Current Password",
                            password=True,
                            can_reveal_password=True,
                            fill_color=ft.Colors.WHITE,
                            filled=True,
                            border_color=BORDER,
                            border_radius=8,
                        ),
                        ft.TextField(
                            label="New Password",
                            password=True,
                            can_reveal_password=True,
                            fill_color=ft.Colors.WHITE,
                            filled=True,
                            border_color=BORDER,
                            border_radius=8,
                        ),
                    ],
                    spacing=10,
                ),
                padding=ft.Padding(0, 8, 0, 0),
            ),
        ]

        def handle_save(e):
            from app.src.services.auth_service import AuthService

            name_ctrl = fields[1]
            email_ctrl = fields[2]
            password_section = fields[3].content
            current_pw_ctrl = password_section.controls[2]
            new_pw_ctrl = password_section.controls[3]

            if name_ctrl.value.strip() != (user.full_name or "") or email_ctrl.value.strip() != (user.email or ""):
                auth = AuthService()
                ok, msg = auth.update_profile(user.id, name_ctrl.value, email_ctrl.value)
                if not ok:
                    self.toast(msg, error=True)
                    return
                user.full_name = name_ctrl.value.strip()
                user.email = email_ctrl.value.strip().lower()

            if new_pw_ctrl.value and new_pw_ctrl.value.strip():
                auth = AuthService()
                ok, msg = auth.change_password(user.id, current_pw_ctrl.value or "", new_pw_ctrl.value.strip())
                if not ok:
                    self.toast(msg, error=True)
                    return
                self.toast(msg)

            self.toast("Account updated.")
            # get the dialog from scope via page overlay detection is tricky;
            # just pop the dialog and update.
            self._page.pop_dialog()

        form_dialog(
            self._page,
            title="My Account",
            fields=fields,
            on_save=handle_save,
            icon=ft.Icons.ACCOUNT_CIRCLE,
        )