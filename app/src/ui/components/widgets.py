"""Reusable UI building blocks used across the admin interface."""
import flet as ft

from app.src.core.theme import (
    BORDER,
    DANGER,
    PRIMARY,
    SUCCESS,
    SURFACE,
    TEXT_SECONDARY,
    TEXT_MUTED,
)


# ---------------------------------------------------------------- Helpers
def safe_update(control):
    """Request a control update only if it is currently attached to a page.

    Views can be constructed before they are added to the page (e.g. the shell
    builds the initial section during startup); calling update() on a detached
    control raises in flet 0.86, so guard those calls with this helper.
    """
    node = control
    while node is not None:
        if isinstance(node, ft.Page):
            control.update()
            return
        node = node.parent


# ---------------------------------------------------------------- Buttons
def primary_button(text: str, on_click=None, icon=None, width=None, expand=False, disabled=False):
    return ft.Button(
        text,
        icon=icon,
        on_click=on_click,
        bgcolor=PRIMARY,
        color=ft.Colors.WHITE,
        elevation=0,
        width=width,
        expand=expand,
        disabled=disabled,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(18, 12, 18, 12),
        ),
    )


def secondary_button(text: str, on_click=None, icon=None, width=None, expand=False):
    return ft.Button(
        text,
        icon=icon,
        on_click=on_click,
        bgcolor="#EFF6FF",
        color=PRIMARY,
        elevation=0,
        width=width,
        expand=expand,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(18, 12, 18, 12),
        ),
    )


def outline_button(text: str, on_click=None, icon=None, width=None, expand=False):
    return ft.Button(
        text,
        icon=icon,
        on_click=on_click,
        color=TEXT_SECONDARY,
        elevation=0,
        width=width,
        expand=expand,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            side=ft.BorderSide(1, BORDER),
            padding=ft.Padding(16, 10, 16, 10),
        ),
    )


def danger_button(text: str, on_click=None, icon=None, width=None, expand=False):
    return ft.Button(
        text,
        icon=icon,
        on_click=on_click,
        bgcolor=DANGER,
        color=ft.Colors.WHITE,
        elevation=0,
        width=width,
        expand=expand,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(16, 10, 16, 10),
        ),
    )


def text_button(text: str, on_click=None, icon=None):
    return ft.TextButton(text, icon=icon, on_click=on_click)


def icon_btn(icon: str, tooltip: str, on_click=None, color=TEXT_SECONDARY):
    return ft.IconButton(icon=icon, tooltip=tooltip, on_click=on_click, icon_color=color)


# ---------------------------------------------------------------- Layout
def card(
    content,
    padding=18,
    border_color=BORDER,
    radius=12,
    bgcolor=SURFACE,
    margin=0,
    shadow=False,
    expand=False,
):
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=bgcolor,
        border=ft.Border(ft.BorderSide(1, border_color), ft.BorderSide(1, border_color), ft.BorderSide(1, border_color), ft.BorderSide(1, border_color)),
        border_radius=radius,
        margin=margin,
        shadow=(
            ft.BoxShadow(
                blur_radius=14,
                offset=ft.Offset(0, 3),
                color=ft.Colors.BLACK12,
            )
            if shadow
            else None
        ),
        expand=expand,
    )


def badge(text: str, color=SUCCESS, bgcolor=None):
    return ft.Container(
        content=ft.Text(
            text.upper(),
            size=10,
            weight=ft.FontWeight.W_700,
            color=color if not bgcolor else ft.Colors.WHITE,
        ),
        bgcolor=bgcolor or ft.Colors.with_opacity(0.1, color),
        padding=ft.Padding(10, 4, 10, 4),
        border_radius=20,
    )


def section_title(text: str, subtitle: str | None = None):
    controls = [ft.Text(text, size=20, weight=ft.FontWeight.W_700, color=ft.Colors.BLACK87)]
    if subtitle:
        controls.append(
            ft.Text(subtitle, size=13, color=TEXT_MUTED)
        )
    return ft.Column(controls, spacing=2)


class StatCard(ft.Container):
    def __init__(self, label: str, value: str, icon: str, accent: str, tint: str, sub: str = ""):
        super().__init__(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, color=accent, size=22),
                        bgcolor=tint,
                        padding=12,
                        border_radius=10,
                    ),
                    ft.Column(
                        [
                            ft.Text(value, size=22, weight=ft.FontWeight.W_700, color=ft.Colors.BLACK87),
                            ft.Text(label, size=12, color=TEXT_SECONDARY),
                            ft.Text(sub, size=11, color=TEXT_MUTED) if sub else ft.Container(width=1),
                        ],
                        spacing=1,
                        expand=True,
                    ),
                ],
                spacing=14,
            ),
            padding=16,
            bgcolor=SURFACE,
            border=ft.Border(ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER)),
            border_radius=12,
            expand=True,
        )


class PanelCard(ft.Container):
    """A titled white panel used to group content on a page."""

    def __init__(self, title: str, content, subtitle: str | None = None, actions: ft.Control | None = None):
        header = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=ft.Colors.BLACK87),
                        ft.Text(subtitle, size=12, color=TEXT_MUTED) if subtitle else ft.Container(),
                    ],
                    spacing=1,
                    expand=True,
                ),
                actions or ft.Container(),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        super().__init__(
            content=ft.Column([header, ft.Container(height=12), content], spacing=0),
            padding=18,
            bgcolor=SURFACE,
            border=ft.Border(ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER)),
            border_radius=12,
            expand=True,
        )


# ---------------------------------------------------------------- States
def empty_state(message: str, icon=ft.Icons.INVENTORY_2, hint: str | None = None):
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(icon, size=42, color=TEXT_MUTED),
                ft.Text(message, size=14, color=TEXT_SECONDARY),
                ft.Text(hint, size=12, color=TEXT_MUTED) if hint else ft.Container(),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        padding=40,
        alignment=ft.Alignment(0, 0),
        expand=True,
    )


def loading_state(message: str = "Loading..."):
    return ft.Container(
        content=ft.Column(
            [
                ft.ProgressRing(width=28, height=28),
                ft.Text(message, size=13, color=TEXT_MUTED),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=40,
        alignment=ft.Alignment(0, 0),
        expand=True,
    )


def error_state(message: str, on_retry=None):
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=42, color=DANGER),
                ft.Text(message, size=14, color=TEXT_SECONDARY),
                ft.TextButton("Retry", icon=ft.Icons.REFRESH, on_click=on_retry) if on_retry else ft.Container(),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        padding=40,
        alignment=ft.Alignment(0, 0),
        expand=True,
    )


# ---------------------------------------------------------------- Product thumb
_PLACEHOLDER_GRADIENTS = [
    (("#2563EB", "#1E40AF"), ft.Icons.LOCAL_CAFE),
    (("#0D9488", "#0F766E"), ft.Icons.CAKE),
    (("#F59E0B", "#B45309"), ft.Icons.RICE_BOWL),
    (("#7C3AED", "#5B21B6"), ft.Icons.SPA),
    (("#DC2626", "#991B1B"), ft.Icons.SHOPPING_BASKET),
    (("#0891B2", "#155E75"), ft.Icons.WATER_DROP),
    (("#16A34A", "#15803D"), ft.Icons.ECO),
]


def product_thumb(product, size: int = 44, radius: int = 10):
    """Local product placeholder. If the product has an image reference it is
    shown; otherwise a category-colored gradient placeholder is rendered."""
    if getattr(product, "image", None):
        return ft.Container(
            width=size,
            height=size,
            content=ft.Image(
                src=product.image,
                fit=ft.BoxFit.COVER,
                width=size,
                height=size,
            ),
            border_radius=radius,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

    gradient_index = (getattr(product, "id", 0) or 0) % len(_PLACEHOLDER_GRADIENTS)
    colors, icon = _PLACEHOLDER_GRADIENTS[gradient_index]
    return ft.Container(
        width=size,
        height=size,
        content=ft.Icon(icon, color=ft.Colors.WHITE, size=int(size * 0.45)),
        bgcolor=ft.Colors.WHITE,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=colors,
        ),
        alignment=ft.Alignment(0, 0),
        border_radius=radius,
    )


# ---------------------------------------------------------------- Dialogs & toasts
def show_toast(page: ft.Page, message: str, error: bool = False):
    snack = ft.SnackBar(
        content=ft.Text(message, size=12),
        bgcolor=DANGER if error else SUCCESS,
        duration=3000,
        behavior=ft.SnackBarBehavior.FLOATING,
    )
    page.show_dialog(snack)


def open_dialog(page: ft.Page, dialog: ft.DialogControl):
    page.show_dialog(dialog)


def close_dialog(page: ft.Page, dialog: ft.DialogControl):
    dialog.open = False
    dialog.update()


def confirm_dialog(
    page: ft.Page,
    title: str,
    message: str,
    on_confirm,
    confirm_label: str = "Confirm",
    danger: bool = False,
):
    def handle_confirm(e):
        close_dialog(page, dlg)
        on_confirm()

    def handle_cancel(e):
        close_dialog(page, dlg)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(
                    ft.Icons.WARNING_AMBER if danger else ft.Icons.HELP_OUTLINE,
                    color=DANGER if danger else PRIMARY,
                    size=22,
                ),
                ft.Text(title, size=16, weight=ft.FontWeight.W_600),
            ],
            spacing=10,
        ),
        content=ft.Container(
            content=ft.Text(message, size=13, color=TEXT_SECONDARY),
            width=380,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=handle_cancel),
            (
                danger_button(confirm_label, on_click=handle_confirm)
                if danger
                else primary_button(confirm_label, on_click=handle_confirm)
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    open_dialog(page, dlg)


def form_dialog(page: ft.Page, title: str, fields: list, actions_title: str = "Save", on_save=None, icon=ft.Icons.EDIT_NOTE):
    """Generic dialog host. ``fields`` is a list of controls; ``on_save(e)`` reads them."""
    def handle_save(e):
        on_save(e)

    def handle_cancel(e):
        close_dialog(page, dlg)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(icon, color=PRIMARY, size=22),
                ft.Text(title, size=16, weight=ft.FontWeight.W_600),
            ],
            spacing=10,
        ),
        content=ft.Container(
            content=ft.Column(fields, spacing=14),
            width=440,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=handle_cancel),
            primary_button(actions_title, icon=ft.Icons.SAVE, on_click=handle_save),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    open_dialog(page, dlg)
    return dlg