"""Admin Inventory view – overview + adjustment history."""
import flet as ft

from app.src.core.theme import DANGER, STAT_ACCENTS, TEXT_MUTED, WARNING
from app.src.services.catalog_service import ProductService
from app.src.services.user_service import UserService
from app.src.ui.components.widgets import PanelCard, StatCard, badge, empty_state
from app.src.utils.helpers import format_datetime


class InventoryView(ft.Column):
    def __init__(self, page, shell):
        super().__init__()
        self._page = page
        self.shell = shell
        self.spacing = 0
        self.expand = True

        summary = ProductService.stock_summary()
        history = ProductService.adjustment_history()

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Inventory", size=20, weight=ft.FontWeight.W_700),
                        ft.Container(height=4),
                        ft.Row(
                            [
                                StatCard("Total Products", str(summary["total"]), ft.Icons.INVENTORY_2, *STAT_ACCENTS[2]),
                                StatCard("Low Stock", str(summary["low_stock"]), ft.Icons.WARNING_AMBER, *STAT_ACCENTS[3]),
                                StatCard("Out of Stock", str(summary["out_of_stock"]), ft.Icons.ERROR_OUTLINE, *STAT_ACCENTS[5]),
                                StatCard("Inventory Value", f"{summary['inventory_value']:,.0f}", ft.Icons.ATTACH_MONEY, *STAT_ACCENTS[1]),
                            ],
                            spacing=14,
                            wrap=True,
                        ),
                        ft.Container(height=4),
                        ft.Row(
                            [
                                PanelCard("Low Stock Products", self._low_stock_panel(), subtitle="Requires restocking"),
                                PanelCard("Recent Stock Adjustments", self._history_panel(history), subtitle="Auditable stock changes"),
                            ],
                            spacing=14,
                            expand=True,
                            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
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

    def _low_stock_panel(self):
        products = ProductService.stock_low()
        if not products:
            return empty_state("No stock issues found.", icon=ft.Icons.CHECK_CIRCLE_OUTLINE, hint="All products have sufficient stock.")
        rows = []
        for p in products:
            color = DANGER if p.stock <= 0 else WARNING
            status = "Out of Stock" if p.stock <= 0 else "Low Stock"
            rows.append(
                ft.Row(
                    [
                        ft.Text(p.name, size=12, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"{p.stock}", size=12, weight=ft.FontWeight.W_500, width=60),
                        badge(status, color),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                )
            )
        return ft.Column(rows, spacing=0, scroll=ft.ScrollMode.AUTO)

    def _history_panel(self, history):
        users_map = {}
        all_users = UserService.list_users()
        for u in all_users:
            users_map[u.id] = u.full_name or u.username

        products_map = {}
        for p in ProductService.list_products():
            products_map[p.id] = p.name

        if not history:
            return empty_state("No stock adjustments recorded yet.", icon=ft.Icons.HISTORY)

        header = ft.Row(
            [
                ft.Text("Product", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, expand=True),
                ft.Text("Change", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=80),
                ft.Text("Type", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=100),
                ft.Text("User", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=90),
                ft.Text("When", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=110),
            ],
            spacing=0,
        )
        rows = []
        for adj in history[:30]:
            change_color = "#16A34A" if adj.quantity_change > 0 else DANGER
            type_text = adj.adjustment_type.capitalize()
            rows.append(
                ft.Row(
                    [
                        ft.Text(products_map.get(adj.product_id, str(adj.product_id)), size=12, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(
                            f"+{adj.quantity_change}" if adj.quantity_change > 0 else str(adj.quantity_change),
                            size=12,
                            color=change_color,
                            weight=ft.FontWeight.W_500,
                            width=80,
                        ),
                        ft.Text(type_text, size=12, width=100),
                        ft.Text(users_map.get(adj.user_id, "System"), size=12, width=90),
                        ft.Text(format_datetime(adj.created_at), size=11, color=TEXT_MUTED, width=110),
                    ],
                    spacing=0,
                )
            )
        return ft.Column([header, ft.Container(height=4), *rows], spacing=0, scroll=ft.ScrollMode.AUTO)