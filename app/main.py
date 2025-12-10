import flet as ft
from app.src.ui.auth.register_view import register_view
from app.src.database.db import db
from app.src.models.user import User
from app.src.models.product import Product
from app.src.models.sales import Sale, SaleItem

# Create all tables
db.create_tables()


def main(page: ft.Page):
    page.title = "Register"
    page.theme_mode = ft.ThemeMode.SYSTEM

    def on_success():
        page.snack_bar = ft.SnackBar(ft.Text("Registration successful!"))
        page.snack_bar.open = True
        page.update()

    # Get the view
    view = register_view(page, on_success=on_success)
    page.add(view)


ft.app(target=main)
