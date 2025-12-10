import flet as ft
from app.src.services.auth_service import AuthService
from app.src.models.user import User
from app.src.database.db import db
from sqlmodel import select


class UserManagementView(ft.Column):
    def __init__(self):
        super().__init__()
        self.auth = AuthService()
        self.user_rows = ft.Column()

        self.status = ft.Text("", color=ft.Colors.RED)
        self.username = ft.TextField(label="Username", width=250)
        self.email = ft.TextField(label="Email", width=250)
        self.full_name = ft.TextField(label="Full Name", width=250)
        self.password = ft.TextField(
            label="Password", password=True, can_reveal_password=True, width=250
        )
        
        self.controls = [
            ft.Text("Users Management", size=24, weight="bold"),
            ft.Row([self.full_name, self.email, self.username, self.password]),
            ft.ElevatedButton(
                "Add User",
                on_click=self.add_user,
                bgcolor=ft.Colors.BLUE_400,
                color=ft.Colors.WHITE,
            ),
            self.status,
            ft.Divider(),
            ft.Text("Registered Users", size=20, weight="bold"),
            self.user_rows,
        ]
        self.spacing = 12  

    def refresh_users(self):
        with next(db.get_session()) as session:
            users = session.exec(select(User)).all()

        self.user_rows.controls.clear()
        for u in users:
            btn_toggle = ft.ElevatedButton(
                "Deactivate" if u.is_active else "Activate",
                bgcolor=ft.Colors.ORANGE_400,
                color=ft.Colors.WHITE,
                on_click=lambda e, user=u: self.toggle_user(user),
            )
            btn_delete = ft.ElevatedButton(
                "Delete",
                bgcolor=ft.Colors.RED_400,
                color=ft.Colors.WHITE,
                on_click=lambda e, user=u: self.delete_user(user),
            )
            self.user_rows.controls.append(
                ft.Row(
                    [
                        ft.Text(
                            f"{u.id}: {u.username} ({'Active' if u.is_active else 'Inactive'})"
                        ),
                        btn_toggle,
                        btn_delete,
                    ],
                    alignment="spaceBetween",
                )
            )
        self.update()

    def add_user(self, _):
        name, email, username, password = (
            self.full_name.value,
            self.email.value,
            self.username.value,
            self.password.value,
        )
        success, msg = self.auth.register(name, email, username, password)
        self.status.value, self.status.color = msg, (
            ft.Colors.GREEN if success else ft.Colors.RED
        )
        if success:
            self.username.value = self.email.value = self.full_name.value = (
                self.password.value
            ) = ""
            self.refresh_users()
        self.update()

    def toggle_user(self, user):
        with next(db.get_session()) as session:
            user.is_active = not user.is_active
            session.add(user)
            session.commit()
        self.refresh_users()

    def delete_user(self, user):
        with next(db.get_session()) as session:
            session.delete(user)
            session.commit()
        self.refresh_users()
