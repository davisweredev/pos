"""Admin Sales view – recent transactions from demo/real data."""
import flet as ft

from app.src.core.config import config
from app.src.core.theme import DANGER, SUCCESS, TEXT_MUTED
from app.src.services.analytics_service import DashboardService
from app.src.ui.components.widgets import PanelCard, empty_state
from app.src.utils.helpers import format_money


class SalesView(ft.Column):
    def __init__(self, page, shell):
        super().__init__()
        self._page = page
        self.shell = shell
        self.spacing = 0
        self.expand = True

        DashboardService.stats()
        recent = DashboardService.recent_sales(limit=20)
        currency = "UGX"

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Sales", size=20, weight=ft.FontWeight.W_700),
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Text(
                                        "POS checkout coming in Phase 2",
                                        size=11,
                                        color=TEXT_MUTED,
                                    ) if config.use_demo_sales else ft.Container(),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=4),
                        PanelCard(
                            title="Recent Transactions",
                            subtitle="No real transactions yet" if not config.use_demo_sales else "Demo data",
                            content=self._recent_table(recent, currency),
                            actions=ft.Container(
                                content=ft.Text("Checkout integration is Phase 2", size=11, color=TEXT_MUTED),
                            ) if config.use_demo_sales else None,
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

    def _recent_table(self, recent, currency):
        if not recent:
            return empty_state(
                "No sales transactions recorded.",
                icon=ft.Icons.RECEIPT_LONG,
                hint="This section will populate once the POS checkout is built in Phase 2.",
            )

        header = ft.Row(
            [
                ft.Text("Invoice", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=90),
                ft.Text("Method", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=110),
                ft.Text("Total", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=110),
                ft.Text("Status", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=90),
                ft.Text("Time", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
            ],
            spacing=0,
            
        )

        rows = []
        for s in recent:
            status_color = SUCCESS if s["status"] == "Completed" else DANGER
            rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(s["invoice"], size=12, weight=ft.FontWeight.W_500, width=90),
                            ft.Text(s["method"], size=12, width=110),
                            ft.Text(format_money(s["total"], currency), size=12, weight=ft.FontWeight.W_500, width=110),
                            ft.Text(s["status"], size=11, color=status_color, weight=ft.FontWeight.W_500, width=90),
                            ft.Text(s["time"], size=12, color=TEXT_MUTED),
                        ],
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(0, 8, 0, 8),
                    border=ft.Border(None, None, ft.BorderSide(1, "#F1F5F9"), None),
                )
            )

        return ft.Column([header, *rows], spacing=0, scroll=ft.ScrollMode.AUTO)