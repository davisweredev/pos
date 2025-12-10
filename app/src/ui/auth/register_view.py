import flet as ft
from app.src.services.auth_service import AuthService


class RegisterView(ft.Control): 
    def __init__(self, on_success=None):
        super().__init__()
        self.on_success = on_success
        self.auth = AuthService()

        self.name = ft.TextField(label="Full Name", width=350)
        self.email = ft.TextField(label="Email", width=350)
        self.username = ft.TextField(label="Username", width=350)
        self.password = ft.TextField(
            label="Password", password=True, can_reveal_password=True, width=350
        )
        self.status = ft.Text("", color=ft.Colors.RED)

    def build(self):
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Create Account", size=24, weight="bold"),
                            self.name,
                            self.email,
                            self.username,
                            self.password,
                            ft.ElevatedButton(
                                "Register",
                                on_click=self.handle_register,
                                bgcolor=ft.Colors.BLUE_500,
                                color=ft.Colors.WHITE,
                                height=45,
                                width=350,
                            ),
                            self.status,
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
        )

    def handle_register(self, e):
        valid, msg = self.auth.register(
            name=self.name.value,
            email=self.email.value,
            username=self.username.value,
            password=self.password.value,
        )
        self.status.value = msg
        self.status.color = ft.Colors.GREEN if valid else ft.Colors.RED
        self.update()

        if valid and self.on_success:
            self.on_success()
