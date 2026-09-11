import flet as ft
from app.src.ui.admin.users_views import UserManagementView
from app.src.database.db import db
from app.src.models.user import User


def main(page: ft.Page):
    page.title = "Admin Dashboard"
    page.scroll = 'auto'
    db.create_tables()
    users_panel = UserManagementView(page)
    page.add(users_panel)
    users_panel.refresh_users()


ft.app(target=main)
