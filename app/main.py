import flet as ft
from app.src.ui.auth.register_view import RegisterView


def main(page: ft.Page):
    page.title = "Register"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.add(RegisterView())


ft.app(target=main)
