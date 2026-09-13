"""Admin Payment Methods management view."""
import json

import flet as ft

from app.src.core.theme import BORDER, DANGER, PRIMARY, SURFACE, SUCCESS, TEXT_SECONDARY, TEXT_MUTED, WARNING
from app.src.services.settings_service import PaymentMethodService
from app.src.ui.components.widgets import badge, confirm_dialog, empty_state, form_dialog, icon_btn, primary_button, safe_update


class PaymentsView(ft.Column):
    def __init__(self, page, shell):
        super().__init__()
        self._page = page
        self.shell = shell
        self.spacing = 0
        self.expand = True

        self._container = ft.Container(content=empty_state("Loading..."), expand=True)

        toolbar = ft.Row(
            [
                ft.Text("Payment Methods", size=20, weight=ft.FontWeight.W_700),
                ft.Container(expand=True),
                primary_button("Add Payment Method", icon=ft.Icons.ADD, on_click=lambda _: self._add()),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        toolbar,
                        ft.Container(height=4),
                        self._info_banner(),
                        ft.Container(height=4),
                        self._container,
                    ],
                    spacing=0,
                    expand=True,
                ),
                padding=28,
                expand=True,
            )
        ]
        self._load()

    def _info_banner(self):
        if PaymentMethodService.external_providers_configured() == 0:
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color="#0D9488"),
                        ft.Text(
                            "Payment method configuration is a stub. No real payment provider is integrated. "
                            "Live payment processing will be implemented in Phase 2.",
                            size=11,
                            color=TEXT_SECONDARY,
                            expand=True,
                        ),
                    ],
                    spacing=8,
                ),
                padding=ft.Padding(14, 10, 14, 10),
                bgcolor="#F0FDFA",
                border=ft.Border(ft.BorderSide(1, "#CCFBF1"), ft.BorderSide(1, "#CCFBF1"), ft.BorderSide(1, "#CCFBF1"), ft.BorderSide(1, "#CCFBF1")),
                border_radius=8,
            )
        return ft.Container(height=0)

    def _load(self):
        methods = PaymentMethodService.list_methods()
        if not methods:
            self._container.content = empty_state("No payment methods configured.", hint="Add at least 'Cash' to get started.")
        else:
            rows = []
            for m in methods:
                rows.append(self._card(m))
            self._container.content = ft.Column(rows, spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
        safe_update(self._container)

    def _card(self, method):
        status_text = "Active" if method.is_active else "Inactive"
        status_color = SUCCESS if method.is_active else DANGER
        icon = ft.Icons.ATTACH_MONEY if method.is_cash else ft.Icons.CREDIT_CARD
        config_info = ""
        if method.configuration:
            try:
                config = json.loads(method.configuration)
                provider = config.get("provider")
                if provider:
                    config_info = f" · Provider: {provider}"
            except (TypeError, ValueError):
                pass

        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=18, color=PRIMARY),
                    ft.Column(
                        [
                            ft.Text(method.name, size=14, weight=ft.FontWeight.W_500, expand=True),
                            ft.Text(f"Code: {method.code}{' · Cash based' if method.is_cash else ''}{config_info}", size=11, color=TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    badge(status_text, status_color),
                    icon_btn(ft.Icons.EDIT_OUTLINED, "Edit", color=PRIMARY, on_click=lambda _, m=method: self._edit(m)),
                    icon_btn(
                        ft.Icons.TOGGLE_ON if method.is_active else ft.Icons.TOGGLE_OFF,
                        "Deactivate" if method.is_active else "Activate",
                        color=WARNING if method.is_active else SUCCESS,
                        on_click=lambda _, m=method: self._toggle(m),
                    ),
                    icon_btn(ft.Icons.DELETE_OUTLINE, "Delete", color=DANGER, on_click=lambda _, m=method: self._delete(m)),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            padding=ft.Padding(16, 14, 16, 14),
            border=ft.Border(ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER)),
            border_radius=10,
            bgcolor=SURFACE,
        )

    def _add(self):
        self._open_dialog(None)

    def _edit(self, method):
        self._open_dialog(method)

    def _open_dialog(self, method):
        is_edit = method is not None
        name_field = ft.TextField(
            label="Payment Method Name *",
            value=method.name if is_edit else "",
            prefix_icon=ft.Icons.PAYMENTS,
            fill_color=ft.Colors.WHITE,
            filled=True,
            border_color=BORDER,
            border_radius=8,
            expand=True,
        )
        code_field = ft.TextField(
            label="Code (unique identifier)",
            value=method.code if is_edit else "",
            prefix_icon=ft.Icons.LABEL,
            fill_color=ft.Colors.WHITE,
            filled=True,
            border_color=BORDER,
            border_radius=8,
            expand=True,
        )
        cash_field = ft.Switch(value=method.is_cash if is_edit else False, label="Cash-based method")

        def handle_save(e):
            if is_edit:
                ok, msg = PaymentMethodService.update_method(
                    method.id, name_field.value, method.is_active, cash_field.value
                )
            else:
                if not code_field.value.strip():
                    self.shell.toast("Code is required.", error=True)
                    return
                ok, msg = PaymentMethodService.create_method(
                    name_field.value, code_field.value, cash_field.value
                )
            if ok:
                self.shell.toast(msg)
                self._page.pop_dialog()
                self._load()
            else:
                self.shell.toast(msg, error=True)

        fields = [name_field, code_field, cash_field]
        if is_edit:
            fields[1].disabled = True

        form_dialog(
            self._page,
            title="Edit Payment Method" if is_edit else "Add Payment Method",
            fields=fields,
            on_save=handle_save,
            icon=ft.Icons.PAYMENTS,
        )

    def _toggle(self, method):
        ok, msg = PaymentMethodService.toggle_active(method.id)
        self.shell.toast(msg, error=not ok)
        self._load()

    def _delete(self, method):
        def on_confirm():
            ok, msg = PaymentMethodService.delete_method(method.id)
            self.shell.toast(msg, error=not ok)
            self._load()

        confirm_dialog(
            self._page,
            title="Delete Payment Method",
            message=f"Delete '{method.name}'? This cannot be undone.",
            on_confirm=on_confirm,
            confirm_label="Delete",
            danger=True,
        )