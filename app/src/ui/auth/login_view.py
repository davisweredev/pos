"""Login screen."""
import flet as ft

from app.src.core.theme import BORDER, DANGER, PRIMARY, TEXT_MUTED, TEXT_SECONDARY
from app.src.services.auth_service import AuthService
from app.src.services.settings_service import SettingsService


class LoginView(ft.Column):
    def __init__(self, page: ft.Page, on_success):
        super().__init__()
        self._page = page
        self.on_success = on_success
        self.auth = AuthService()
        self.busy = False

        business_name = SettingsService.get_setting("business_name", "SwiftPOS")
        tagline = SettingsService.get_setting("business_tagline", "Retail & Point of Sale")

        self.error_text = ft.Container(height=20, visible=False)

        self.username = ft.TextField(
            label="Username or Email",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            fill_color=ft.Colors.WHITE,
            filled=True,
            border_color="#CBD5E1",
            border_radius=10,
            autofocus=True,
            on_submit=self._submit,
        )
        self.password = ft.TextField(
            label="Password",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            fill_color=ft.Colors.WHITE,
            filled=True,
            border_color="#CBD5E1",
            border_radius=10,
            on_submit=self._submit,
        )

        self.sign_in_button = ft.Button(
            "Sign In",
            icon=ft.Icons.LOGIN,
            bgcolor=PRIMARY,
            color=ft.Colors.WHITE,
            elevation=0,
            height=48,
            expand=True,
            on_click=self._submit,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        brand = ft.Container(
            content=ft.Icon(ft.Icons.POINT_OF_SALE, color=ft.Colors.WHITE, size=30),
            bgcolor=PRIMARY,
            padding=14,
            border_radius=14,
            shadow=ft.BoxShadow(
                blur_radius=20, offset=ft.Offset(0, 6), color=ft.Colors.with_opacity(0.35, PRIMARY)
            ),
        )

        card = ft.Container(
            content=ft.Column(
                [
                    ft.Row([brand, ft.Container(width=12),
                            ft.Column(
                                [
                                    ft.Text(business_name, size=20, weight=ft.FontWeight.W_700, color=ft.Colors.BLACK87),
                                    ft.Text(tagline, size=12, color=TEXT_MUTED),
                                ],
                                spacing=1,
                            )],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=8),
                    ft.Text("Sign in to continue", size=13, color=TEXT_SECONDARY),
                    ft.Container(height=8),
                    self.username,
                    self.password,
                    self.error_text,
                    self.sign_in_button,
                    ft.Container(height=4),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.LOCK, size=12, color=TEXT_MUTED),
                            ft.Text(
                                "Protected area. Authorized personnel only.",
                                size=10,
                                color=TEXT_MUTED,
                            ),
                        ],
                        spacing=6,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            padding=ft.Padding(36, 34, 36, 34),
            bgcolor=ft.Colors.WHITE,
            border=ft.Border(ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER)),
            border_radius=16,
            shadow=ft.BoxShadow(
                blur_radius=40, offset=ft.Offset(0, 10), color=ft.Colors.BLACK12
            ),
            width=420,
        )

        self.controls = [
            ft.Container(
                content=ft.Row(
                    [card],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=["#EEF2FF", "#F1F5F9"],
                ),
                alignment=ft.Alignment(0, 0),
            )
        ]
        self.expand = True
        self.spacing = 0

    def _show_error(self, message: str):
        self.error_text.content = ft.Text(
            message, size=12, color=DANGER, weight=ft.FontWeight.W_500
        )
        self.error_text.visible = True
        self.error_text.update()

    def _set_busy(self, busy: bool):
        self.busy = busy
        self.username.disabled = busy
        self.password.disabled = busy
        self.sign_in_button.disabled = busy
        self.sign_in_button.content = ft.Row(
            [
                ft.ProgressRing(width=16, height=16, stroke_width=2, color=ft.Colors.WHITE),
                ft.Text("Signing in...", size=14),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
        ) if busy else "Sign In"
        self.update()

    def _submit(self, e):
        if self.busy:
            return
        username_value = (self.username.value or "").strip()
        password_value = self.password.value or ""

        if not username_value or not password_value:
            self._show_error("Enter your username/email and password.")
            return

        self.error_text.visible = False
        self._set_busy(True)
        try:
            ok, message, user = self.auth.login(username_value, password_value)
            if not ok:
                self._show_error(message)
                self._set_busy(False)
                return
            self.password.value = ""
        except Exception:
            self._show_error("Unable to sign in. Please try again.")
            self._set_busy(False)
            return

        area = "admin" if user.is_admin() else "staff"
        self.on_success(user, area)