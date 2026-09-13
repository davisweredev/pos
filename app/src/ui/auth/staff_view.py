"""Temporary view for staff users. Phase 2 will add the actual POS terminal."""
import flet as ft

from app.src.core.theme import BG, PRIMARY, TEXT_SECONDARY
from app.src.models.user import User
from app.src.ui.components import primary_button
from app.src.utils.helpers import initials


class StaffPlaceholderView(ft.Column):
    def __init__(self, page: ft.Page, user: User, on_logout):
        super().__init__()
        self._page = page
        self.on_logout = on_logout

        initials_label = initials(user.full_name or user.username)

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(initials_label, color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_600),
                            bgcolor=PRIMARY,
                            width=64,
                            height=64,
                            border_radius=32,
                            alignment=ft.Alignment(0, 0),
                            margin=ft.Margin(0, 0, 0, 12),
                        ),
                        ft.Text(
                            f"Welcome, {user.full_name or user.username}",
                            size=20,
                            weight=ft.FontWeight.W_700,
                            color=ft.Colors.BLACK87,
                        ),
                        ft.Container(height=4),
                        ft.Text(
                            "POS Terminal",
                            size=15,
                            weight=ft.FontWeight.W_600,
                            color=PRIMARY,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            "The staff POS interface will be available in Phase 2.\nThis account is confirmed active and authenticated.",
                            size=13,
                            color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=20),
                        primary_button("Logout", icon=ft.Icons.LOGOUT, on_click=lambda _: on_logout()),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                bgcolor=ft.Colors.WHITE,
                border=ft.Border(ft.BorderSide(1, ft.Colors.GREY_200), ft.BorderSide(1, ft.Colors.GREY_200), ft.BorderSide(1, ft.Colors.GREY_200), ft.BorderSide(1, ft.Colors.GREY_200)),
                border_radius=16,
                padding=ft.Padding(40, 40, 40, 40),
                alignment=ft.Alignment(0, 0),
            )
        ]
        self.expand = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 0
        self.bgcolor = BG