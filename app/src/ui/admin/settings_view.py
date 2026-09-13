"""Admin System Settings view – business configuration."""
import flet as ft

from app.src.core.config import config
from app.src.core.theme import BORDER, PRIMARY, TEXT_SECONDARY, TEXT_MUTED
from app.src.services.settings_service import SettingsService
from app.src.ui.components.widgets import primary_button


class SettingsView(ft.Column):
    def __init__(self, page, shell):
        super().__init__()
        self._page = page
        self.shell = shell
        self.spacing = 0
        self.expand = True

        settings = SettingsService.all_settings()

        self.fields: dict[str, ft.Control] = {}

        def _tf(key: str, label: str, icon=None, value: str | None = None, **kw):
            ctrl = ft.TextField(
                label=label,
                value=value if value is not None else settings.get(key, ""),
                prefix_icon=icon,
                fill_color=ft.Colors.WHITE,
                filled=True,
                border_color=BORDER,
                border_radius=8,
                expand=True,
                **kw,
            )
            self.fields[key] = ctrl
            return ctrl

        business_section = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.BUSINESS, size=18, color=PRIMARY),
                        ft.Text("Business Information", size=16, weight=ft.FontWeight.W_600),
                    ],
                    spacing=8,
                ),
                _tf("business_name", "Business Name *", icon=ft.Icons.SHOPPING_CART),
                _tf("business_tagline", "Tagline / Subtitle", icon=ft.Icons.INFO_OUTLINE),
                _tf("currency", "Currency Code", icon=ft.Icons.ATTACH_MONEY),
            ],
            spacing=12,
        )

        receipt_section = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.RECEIPT, size=18, color=PRIMARY),
                        ft.Text("Receipt Settings", size=16, weight=ft.FontWeight.W_600),
                    ],
                    spacing=8,
                ),
                _tf("receipt_footer", "Receipt Footer Message", icon=ft.Icons.NOTES),
            ],
            spacing=12,
        )

        tax_section = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CALCULATE, size=18, color=PRIMARY),
                        ft.Text("Tax Configuration", size=16, weight=ft.FontWeight.W_600),
                    ],
                    spacing=8,
                ),
                _tf("vat_rate", "VAT Rate (%)", icon=ft.Icons.PERCENT),
                ft.Text(
                    "Configure tax rate applied at checkout. Phase 2: tax is calculated during POS checkout.",
                    size=11,
                    color=TEXT_MUTED,
                ),
            ],
            spacing=12,
        )

        inventory_section = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INVENTORY, size=18, color=PRIMARY),
                        ft.Text("Inventory Defaults", size=16, weight=ft.FontWeight.W_600),
                    ],
                    spacing=8,
                ),
                _tf("low_stock_default", "Default Low Stock Threshold", icon=ft.Icons.WARNING_AMBER),
            ],
            spacing=12,
        )

        demo_section = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color="#0D9488"),
                    ft.Column(
                        [
                            ft.Text("Demo Mode", size=13, weight=ft.FontWeight.W_600, color="#0F766E"),
                            ft.Text(
                                f"Demo sales data is currently {'enabled' if config.use_demo_sales else 'disabled'}. "
                                "When disabled, sales/report figures will show zero until POS checkout is implemented.",
                                size=11,
                                color=TEXT_SECONDARY,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
            padding=14,
            bgcolor="#F0FDFA",
            border=ft.Border(ft.BorderSide(1, "#CCFBF1"), ft.BorderSide(1, "#CCFBF1"), ft.BorderSide(1, "#CCFBF1"), ft.BorderSide(1, "#CCFBF1")),
            border_radius=10,
            margin=ft.Margin(0, 8, 0, 0),
        )

        save_btn = primary_button(
            "Save Settings",
            icon=ft.Icons.SAVE,
            on_click=self._save,
            width=180,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Settings", size=20, weight=ft.FontWeight.W_700),
                                ft.Container(expand=True),
                                save_btn,
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [business_section, ft.Container(height=8), receipt_section],
                                        spacing=20,
                                    ),
                                    padding=20,
                                    bgcolor=ft.Colors.WHITE,
                                    border=ft.Border(ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER)),
                                    border_radius=12,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [inventory_section, ft.Container(height=4), tax_section, ft.Container(height=8), demo_section],
                                        spacing=20,
                                    ),
                                    padding=20,
                                    bgcolor=ft.Colors.WHITE,
                                    border=ft.Border(ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER)),
                                    border_radius=12,
                                    expand=True,
                                ),
                            ],
                            spacing=14,
                            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                            expand=True,
                        ),
                    ],
                    spacing=0,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=28,
                expand=True,
            )
        ]

    def _save(self, e=None):
        values = {}
        for key, ctrl in self.fields.items():
            values[key] = (ctrl.value or "").strip()
        try:
            float(values.get("vat_rate", "0"))
        except ValueError:
            self.shell.toast("VAT rate must be a number.", error=True)
            return
        try:
            float(values.get("low_stock_default", "5"))
        except ValueError:
            self.shell.toast("Low stock threshold must be a number.", error=True)
            return

        SettingsService.save_batch(values)
        self.shell.toast("Settings saved.")