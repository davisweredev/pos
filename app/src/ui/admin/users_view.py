"""Admin Users / Staff management view."""
import flet as ft

from app.src.core.theme import BORDER, DANGER, PRIMARY, SURFACE, SUCCESS, TEXT_MUTED, WARNING
from app.src.models.user import User
from app.src.services.user_service import UserService, VALID_USER_TYPES
from app.src.ui.components.widgets import (
    badge,
    confirm_dialog,
    empty_state,
    form_dialog,
    icon_btn,
    primary_button,
    safe_update,
)
from app.src.utils.helpers import format_datetime, initials


class UsersView(ft.Column):
    def __init__(self, page, shell):
        super().__init__()
        self._page = page
        self.shell = shell
        self.spacing = 0
        self.expand = True

        self._container = ft.Container(content=empty_state("Loading..."), expand=True)

        toolbar = ft.Row(
            [
                ft.Text("Users", size=20, weight=ft.FontWeight.W_700),
                ft.Container(expand=True),
                primary_button("Add Staff", icon=ft.Icons.PERSON_ADD, on_click=lambda _: self._add_user()),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.controls = [
            ft.Container(
                content=ft.Column([toolbar, ft.Container(height=8), self._container], spacing=0, expand=True),
                padding=28,
                expand=True,
            )
        ]
        self._load()

    def _load(self):
        users = UserService.list_users()
        if not users:
            self._container.content = empty_state("No users found.", hint="Add your first staff member.")
        else:
            rows = [self._user_row(u) for u in users]
            self._container.content = ft.Column(
                [self._table_header(), ft.Container(height=2), *rows],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        safe_update(self._container)

    def _table_header(self):
        return ft.Row(
            [
                ft.Text("User", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, expand=True),
                ft.Text("Email", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, expand=True),
                ft.Text("Role", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=80),
                ft.Text("Status", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=80),
                ft.Text("Last Login", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=120),
                ft.Text("", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=130),
            ],
            spacing=0,
        )

    def _user_row(self, user: User):
        role_color = PRIMARY if user.user_type == "admin" else "#0D9488"
        status_color = SUCCESS if user.is_active else DANGER
        initials_val = initials(user.full_name or user.username)

        return ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(initials_val, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                                bgcolor="#475569",
                                width=34,
                                height=34,
                                border_radius=17,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column(
                                [
                                    ft.Text(user.full_name or "—", size=13, weight=ft.FontWeight.W_500, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                    ft.Text(f"@{user.username}", size=11, color=TEXT_MUTED),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                    ft.Text(user.email or "—", size=12, color=TEXT_MUTED, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                    badge(user.user_type.capitalize(), role_color),
                    badge("Active" if user.is_active else "Inactive", status_color),
                    ft.Text(format_datetime(user.last_login, "Never"), size=11, color=TEXT_MUTED, width=120),
                    ft.Row(
                        [
                            icon_btn(ft.Icons.EDIT_OUTLINED, "Edit", color=PRIMARY, on_click=lambda _, u=user: self._edit_user(u)),
                            icon_btn(
                                ft.Icons.TOGGLE_ON if user.is_active else ft.Icons.TOGGLE_OFF,
                                "Deactivate" if user.is_active else "Activate",
                                color=WARNING if user.is_active else SUCCESS,
                                on_click=lambda _, u=user: self._toggle(u),
                            ),
                            icon_btn(ft.Icons.DELETE_OUTLINE, "Delete", color=DANGER, on_click=lambda _, u=user: self._confirm_delete(u)),
                        ],
                        spacing=2,
                        width=130,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            padding=ft.Padding(14, 12, 14, 12),
            border=ft.Border(ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER)),
            border_radius=10,
            bgcolor=SURFACE,
            margin=ft.Margin(0, 0, 0, 4),
        )

    def _add_user(self):
        self._open_dialog(None)

    def _edit_user(self, user):
        self._open_dialog(user)

    def _open_dialog(self, user):
        is_edit = user is not None

        def _tf(label, value, icon=None, **kw):
            return ft.TextField(
                label=label,
                value=value or "",
                prefix_icon=icon,
                fill_color=ft.Colors.WHITE,
                filled=True,
                border_color=BORDER,
                border_radius=8,
                expand=True,
                **kw,
            )

        name_field = _tf("Full Name *", user.full_name if is_edit else "", icon=ft.Icons.PERSON)
        email_field = _tf("Email *", user.email if is_edit else "", icon=ft.Icons.EMAIL)
        username_field = _tf("Username *", user.username if is_edit else "", icon=ft.Icons.LOCK_OPEN)
        password_field = _tf("New Password", "", icon=ft.Icons.LOCK, password=True, can_reveal_password=True)

        user_type_options = [ft.dropdown.Option(ut) for ut in VALID_USER_TYPES]
        user_type_field = ft.Dropdown(
            label="Role *",
            value=user.user_type if is_edit else "staff",
            options=user_type_options,
            fill_color=ft.Colors.WHITE,
            filled=True,
            border_color=BORDER,
            border_radius=8,
        )
        active_field = ft.Switch(value=user.is_active if is_edit else True, label="Active")

        def handle_save(e):
            password_val = password_field.value.strip() if password_field.value else ""
            if is_edit:
                ok, msg = UserService.update_user(
                    user.id, name_field.value, email_field.value, username_field.value,
                    user_type_field.value, active_field.value,
                    new_password=password_val or None,
                )
            else:
                if not password_val:
                    self.shell.toast("Password is required for new users.", error=True)
                    return
                ok, msg = UserService.create_user(
                    name_field.value, email_field.value, username_field.value,
                    password_val, user_type_field.value,
                )

            if ok:
                self.shell.toast(msg)
                self._page.pop_dialog()
                self._load()
            else:
                self.shell.toast(msg, error=True)

        form_dialog(
            self._page,
            title="Edit User" if is_edit else "Add Staff Member",
            fields=[name_field, email_field, username_field, user_type_field, password_field, active_field],
            on_save=handle_save,
            icon=ft.Icons.PERSON if is_edit else ft.Icons.PERSON_ADD,
        )

    def _toggle(self, user):
        ok, msg, _ = UserService.toggle_active(user.id)
        self.shell.toast(msg, error=not ok)
        self._load()

    def _confirm_delete(self, user):
        def on_confirm():
            ok, msg = UserService.delete_user(user.id)
            self.shell.toast(msg, error=not ok)
            self._load()

        confirm_dialog(
            self._page,
            title="Delete User",
            message=f"Delete user '{user.username}'? This cannot be undone. Consider deactivating the account instead.",
            on_confirm=on_confirm,
            confirm_label="Delete User",
            danger=True,
        )