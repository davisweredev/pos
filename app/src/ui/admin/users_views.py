import flet as ft
import bcrypt
from app.src.services.auth_service import AuthService
from app.src.models.user import User
from app.src.database.db import db
from sqlmodel import select
from typing import Optional


class UserManagementView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.auth = AuthService()
        
        self.current_edit_user: Optional[User] = None

        # Form fields
        self.status = ft.Text("", color=ft.Colors.RED)
        self.username = ft.TextField(label="Username", width=250)
        self.email = ft.TextField(label="Email", width=250)
        self.full_name = ft.TextField(label="Full Name", width=250)
        self.password = ft.TextField(
            label="Password", password=True, can_reveal_password=True, width=250
        )

        # Scrollable container for user list
        self.user_rows = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
        )

        self.build_ui()

        self.page.run_task(self.load_initial_users)

    def build_ui(self):
        """Build the user interface"""
        self.controls = [
            # Header
            ft.Text(
                "User Management", size=28, weight="bold", color=ft.Colors.BLUE_700
            ),
            # Add User Form
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Add New User", size=18, weight="bold"),
                        ft.Row(
                            [
                                self.full_name,
                                self.email,
                                self.username,
                                self.password,
                            ],
                            wrap=True,
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Add User",
                                    icon=ft.Icons.ADD,
                                    on_click=self.add_user,
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.BLUE_400,
                                        color=ft.Colors.WHITE,
                                        padding=ft.padding.symmetric(
                                            horizontal=20, vertical=10
                                        ),
                                    ),
                                ),
                                ft.ElevatedButton(
                                    "Clear",
                                    icon=ft.Icons.CLEAR,
                                    on_click=self.clear_form,
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.GREY_400,
                                        color=ft.Colors.WHITE,
                                        padding=ft.padding.symmetric(
                                            horizontal=20, vertical=10
                                        ),
                                    ),
                                ),
                            ],
                            spacing=20,
                        ),
                        self.status,
                    ],
                    spacing=15,
                ),
                padding=20,
                bgcolor=ft.Colors.BLUE_GREY_50,
                border_radius=10,
                margin=ft.margin.only(bottom=20),
            ),
            ft.Divider(height=2, color=ft.Colors.GREY_300),
    
            ft.Row(
                [
                    ft.Text(
                        "Registered Users",
                        size=22,
                        weight="bold",
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Refresh",
                        on_click=lambda e: self.refresh_users(),
                    ),
                ]
            ),

            ft.Container(
                content=self.user_rows,
                height=400, 
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                padding=10,
                expand=False,
            ),
        ]

        self.spacing = 20
        self.expand = True

    async def load_initial_users(self):
        """Load users after UI is ready"""
        self.refresh_users()

    def clear_form(self, e=None):
        """Clear all form fields"""
        self.username.value = ""
        self.email.value = ""
        self.full_name.value = ""
        self.password.value = ""
        self.status.value = ""
        self.update()

    def refresh_users(self):
        """Refresh the users list"""
        try:
            with next(db.get_session()) as session:
                users = session.exec(select(User)).all()

            self.user_rows.controls.clear()

            if not users:
                self.user_rows.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.PEOPLE_OUTLINE,
                                    size=50,
                                    color=ft.Colors.GREY_400,
                                ),
                                ft.Text(
                                    "No users found", size=16, color=ft.Colors.GREY_600
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        padding=40,
                        alignment=ft.alignment.center,
                    )
                )
            else:
                for user in users:
                    user_card = self.create_user_card(user)
                    self.user_rows.controls.append(user_card)

            self.user_rows.update()

        except Exception as e:
            print(f"Error refreshing users: {e}")
            self.show_snackbar(f"Error loading users: {str(e)}", ft.Colors.RED)

    def create_user_card(self, user: User) -> ft.Container:
        """Create a card for a user"""

        def create_edit_handler(u):
            return lambda e: self.edit_user_handler(u)

        def create_toggle_handler(u):
            return lambda e: self.toggle_user_handler(u)

        def create_delete_handler(u):
            return lambda e: self.confirm_delete_handler(u)

        return ft.Container(
            content=ft.Column(
                [
                   
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.PERSON,
                                color=(
                                    ft.Colors.GREEN
                                    if user.is_active
                                    else ft.Colors.GREY
                                ),
                                size=24,
                            ),
                            ft.Column(
                                [
                                    ft.Text(user.full_name, weight="bold", size=16),
                                    ft.Text(
                                        f"@{user.username}",
                                        color=ft.Colors.BLUE_GREY,
                                        size=12,
                                    ),
                                    ft.Text(
                                        user.email, color=ft.Colors.GREY_600, size=12
                                    ),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "ACTIVE" if user.is_active else "INACTIVE",
                                    color=ft.Colors.WHITE,
                                    size=10,
                                    weight="bold",
                                ),
                                bgcolor=(
                                    ft.Colors.GREEN if user.is_active else ft.Colors.RED
                                ),
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                border_radius=20,
                            ),
                        ],
                        alignment="start",
                        spacing=15,
                    ),
                    
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Edit",
                                icon=ft.Icons.EDIT,
                                on_click=create_edit_handler(user),
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_400,
                                    color=ft.Colors.WHITE,
                                    padding=ft.padding.symmetric(
                                        horizontal=12, vertical=6
                                    ),
                                ),
                                width=100,
                            ),
                            ft.ElevatedButton(
                                "deactivate" if user.is_active else "activate",
                                icon=(
                                    ft.Icons.TOGGLE_ON
                                    if user.is_active
                                    else ft.Icons.TOGGLE_OFF
                                ),
                                on_click=create_toggle_handler(user),
                                style=ft.ButtonStyle(
                                    bgcolor=(
                                        ft.Colors.ORANGE_400
                                        if user.is_active
                                        else ft.Colors.GREEN_400
                                    ),
                                    color=ft.Colors.WHITE,
                                    padding=ft.padding.symmetric(
                                        horizontal=12, vertical=6
                                    ),
                                ),
                                width=120,
                            ),
                            ft.ElevatedButton(
                                "Delete",
                                icon=ft.Icons.DELETE,
                                on_click=create_delete_handler(user),
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.RED_400,
                                    color=ft.Colors.WHITE,
                                    padding=ft.padding.symmetric(
                                        horizontal=12, vertical=6
                                    ),
                                ),
                                width=100,
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=15,
            ),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            margin=ft.margin.only(bottom=10),
            shadow=ft.BoxShadow(
                blur_radius=2, color=ft.Colors.BLACK12, offset=ft.Offset(0, 1)
            ),
        )

    def add_user(self, e):
        """Add a new user"""
        name = self.full_name.value.strip()
        email = self.email.value.strip()
        username = self.username.value.strip()
        password = self.password.value.strip()

      
        if not all([name, email, username, password]):
            self.status.value = "All fields are required"
            self.status.color = ft.Colors.RED
            self.update()
            return

        if len(password) < 6:
            self.status.value = "Password must be at least 6 characters"
            self.status.color = ft.Colors.RED
            self.update()
            return

        try:
            success, msg = self.auth.register(name, email, username, password)
            self.status.value = msg
            self.status.color = ft.Colors.GREEN if success else ft.Colors.RED

            if success:
                self.clear_form()
                self.refresh_users()

            self.update()

        except Exception as ex:
            self.status.value = f"Error: {str(ex)}"
            self.status.color = ft.Colors.RED
            self.update()

    def edit_user_handler(self, user):
        """Handle edit button click"""
        self.edit_user(user)

    def toggle_user_handler(self, user):
        """Handle toggle button click"""
        self.toggle_user(user)

    def confirm_delete_handler(self, user):
        """Handle delete button click"""
        self.confirm_delete(user)

    def toggle_user(self, user):
        """Toggle user active status"""
        try:
            with next(db.get_session()) as session:
                db_user = session.get(User, user.id)
                if db_user:
                    db_user.is_active = not db_user.is_active
                    session.add(db_user)
                    session.commit()
                    self.show_snackbar(
                        f"User {db_user.username} {'activated' if db_user.is_active else 'deactivated'}"
                    )
                    self.refresh_users()

        except Exception as e:
            self.show_snackbar(f"Error: {str(e)}", ft.Colors.RED)

    def confirm_delete(self, user):
        """Show confirmation dialog before deleting"""

        def delete_confirmed(e):
            self.delete_user(user)
            dlg.open = False
            self.page.update()

        def cancel_delete(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text(
                f"Are you sure you want to delete user '{user.username}'? This action cannot be undone."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.ElevatedButton(
                    "Delete",
                    on_click=delete_confirmed,
                    bgcolor=ft.Colors.RED_400,
                    color=ft.Colors.WHITE,
                ),
            ],
            actions_alignment="end",
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def delete_user(self, user):
        """Delete user from database"""
        try:
            with next(db.get_session()) as session:
                db_user = session.get(User, user.id)
                if db_user:
                    session.delete(db_user)
                    session.commit()
                    self.show_snackbar(f"User {user.username} deleted successfully")
                    self.refresh_users()

        except Exception as e:
            self.show_snackbar(f"Error: {str(e)}", ft.Colors.RED)

    def edit_user(self, user):
        """Edit user details - stores user in instance variable for proper capture"""
        self.current_edit_user = user
        name_field = ft.TextField(
            label="Full Name", value=user.full_name, width=350, autofocus=True
        )
        email_field = ft.TextField(label="Email", value=user.email, width=350)
        username_field = ft.TextField(label="Username", value=user.username, width=350)
        password_field = ft.TextField(
            label="New Password (leave empty to keep current)",
            password=True,
            can_reveal_password=True,
            width=350,
            hint_text="Minimum 6 characters",
        )

        status_txt = ft.Text("", color=ft.Colors.RED, size=12)

        def save_changes(e):

            current_user = self.current_edit_user
            if not current_user:
                status_txt.value = "User not found"
                status_txt.update()
                return

            if not all([name_field.value, email_field.value, username_field.value]):
                status_txt.value = "Name, email, and username are required"
                status_txt.update()
                return

            if password_field.value and len(password_field.value.strip()) < 6:
                status_txt.value = "Password must be at least 6 characters"
                status_txt.update()
                return

            try:
                with next(db.get_session()) as session:
                    db_user = session.get(User, current_user.id)

                    if not db_user:
                        status_txt.value = "User not found."
                        status_txt.update()
                        return

                    existing = session.exec(
                        select(User)
                        .where(
                            (User.username == username_field.value.strip())
                            | (User.email == email_field.value.strip())
                        )
                        .where(User.id != current_user.id)
                    ).first()

                    if existing:
                        status_txt.value = "Username or email already exists"
                        status_txt.update()
                        return
                    
                    db_user.full_name = name_field.value.strip()
                    db_user.email = email_field.value.strip()
                    db_user.username = username_field.value.strip()

                    if password_field.value.strip():
                        hashed = bcrypt.hashpw(
                            password_field.value.encode(), bcrypt.gensalt()
                        ).decode()
                        db_user.password_hash = hashed

                    session.add(db_user)
                    session.commit()

                self.page.dialog.open = False
                self.page.update()
                self.refresh_users()
                self.show_snackbar(f"User {db_user.username} updated successfully")

            except Exception as ex:
                status_txt.value = f"Error: {str(ex)}"
                status_txt.update()

        def cancel_edit(e):
            self.page.dialog.open = False
            self.page.update()
            self.current_edit_user = None

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.EDIT, color=ft.Colors.BLUE_400),
                    ft.Text(f"Edit User: {user.username}", size=18, weight="bold"),
                ]
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        name_field,
                        email_field,
                        username_field,
                        password_field,
                        status_txt,
                    ],
                    spacing=15,
                ),
                width=400,
                padding=10,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_edit),
                ft.ElevatedButton(
                    "Save Changes",
                    icon=ft.Icons.SAVE,
                    on_click=save_changes,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_400,
                        color=ft.Colors.WHITE,
                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                    ),
                ),
            ],
            actions_alignment="end",
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def show_snackbar(self, message: str, color=ft.Colors.GREEN_400):
        """Show a snackbar notification"""
        snackbar = ft.SnackBar(
            ft.Text(message),
            bgcolor=color,
            duration=3000,
        )
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()
