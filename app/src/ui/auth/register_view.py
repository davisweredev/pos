import flet as ft
from app.src.services.auth_service import AuthService


def register_view(page: ft.Page, on_success=None):
    """Create registration view as a function"""
    # Assuming AuthService exists
    auth = AuthService()

    # Create controls
    name = ft.TextField(label="Full Name", width=350)
    email = ft.TextField(label="Email", width=350)
    username = ft.TextField(label="Username", width=350)
    password = ft.TextField(
        label="Password", password=True, can_reveal_password=True, width=350
    )
    status = ft.Text("", color=ft.Colors.RED)

    def handle_register(e):
        valid, msg = auth.register(
            name=name.value,
            email=email.value,
            username=username.value,
            password=password.value,
        )
        status.value = msg
        status.color = ft.Colors.GREEN if valid else ft.Colors.RED
        page.update()

        if valid and on_success:
            on_success()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Create Account", size=24, weight="bold"),
                            name,
                            email,
                            username,
                            password,
                            ft.ElevatedButton(
                                "Register",
                                on_click=handle_register,
                                bgcolor=ft.Colors.BLUE_500,
                                color=ft.Colors.WHITE,
                                height=45,
                                width=350,
                            ),
                            status,
                        ],
                        spacing=12,
                    ),
                    padding=30,
                    border_radius=12,
                    bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.BLACK),
                )
            ],
            alignment="center",
            horizontal_alignment="center",
            expand=True,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )
