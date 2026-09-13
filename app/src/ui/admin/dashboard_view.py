"""Admin Dashboard view – real DB stats + demo sales figures."""
import flet as ft

from app.src.core.theme import PRIMARY, STAT_ACCENTS, TEXT_SECONDARY, TEXT_MUTED, SUCCESS, WARNING, DANGER
from app.src.services.analytics_service import DashboardService
from app.src.services.settings_service import SettingsService
from app.src.utils.helpers import format_money, today_label
from app.src.ui.components.widgets import PanelCard, StatCard, empty_state

try:
    import flet_charts as fch
except ImportError:
    fch = None


class DashboardView(ft.Column):
    def __init__(self, page, shell):
        super().__init__()
        self._page = page
        self.shell = shell
        self.spacing = 0
        self.expand = True

        stats = DashboardService.stats()
        SettingsService.get_setting("business_name", "SwiftPOS")
        currency = SettingsService.get_setting("currency", "UGX")

        # stat cards row
        stat_cards = ft.Row(
            [
                StatCard("Today's Revenue", format_money(stats["today_sales"], currency), ft.Icons.TRENDING_UP, *STAT_ACCENTS[0]),
                StatCard("Total Revenue", format_money(stats["total_sales"], currency), ft.Icons.RECEIPT_LONG, *STAT_ACCENTS[1]),
                StatCard("Products in Stock", str(stats["products_total"]), ft.Icons.INVENTORY_2, *STAT_ACCENTS[2]),
                StatCard("Low Stock Alerts", str(stats["low_stock"]), ft.Icons.WARNING_AMBER, *STAT_ACCENTS[3]),
            ],
            spacing=14,
            wrap=True,
        )

        chart_row = ft.Row(
            [
                self._sales_chart(currency),
                self._alerts_card(),
            ],
            spacing=14,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        bottom_row = ft.Row(
            [
                self._recent_sales_panel(),
                self._top_products_panel(),
            ],
            spacing=14,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("Dashboard", size=22, weight=ft.FontWeight.W_700),
                                        ft.Text(today_label(), size=13, color=TEXT_MUTED),
                                    ],
                                    spacing=2,
                                ),
                                ft.Container(),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        stat_cards,
                        ft.Container(height=2),
                        chart_row,
                        ft.Container(height=2),
                        bottom_row,
                    ],
                    spacing=14,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=28,
                expand=True,
            )
        ]

    # ---------------------------------------------------------------- panels
    def _sales_chart(self, currency: str):
        trend = DashboardService.sales_trend()
        if fch is None or not trend:
            return PanelCard("Sales Trend (7 Days)", ft.Container(
                content=ft.Text("Install flet-charts for charting.", size=12, color=TEXT_MUTED),
                padding=20,
            ))

        data_points = [
            fch.LineChartDataPoint(i, d["amount"] / 1000)
            for i, d in enumerate(trend)
        ]
        labels = [ft.Text(d["label"], size=10, color=TEXT_MUTED) for d in trend]
        chart = fch.LineChart(
            data_series=[
                fch.LineChartData(
                    points=data_points,
                    color=PRIMARY,
                    curved=True,
                    stroke_width=3,
                )
            ],
            left_axis=fch.ChartAxis(
                title=ft.Text("K " + currency, size=10, color=TEXT_MUTED),
                labels=[ft.Text("0", size=9)],
            ),
            bottom_axis=fch.ChartAxis(
                labels=labels,
            ),
            horizontal_grid_lines=fch.ChartGridLines(color="#E2E8F0", width=1, dash_pattern=[3, 3]),
            height=200,
            animation="none",
            interactive=False,
        )

        content = ft.Column(
            [
                chart,
                ft.Container(height=4),
                ft.Text(
                    "Revenue in thousands (demo). Connect POS checkout for live data.",
                    size=10,
                    color=TEXT_MUTED,
                ),
            ],
            spacing=0,
        )
        return PanelCard("Sales Trend (Last 7 Days)", content)

    def _alerts_card(self):
        alerts = DashboardService.inventory_alerts()
        if not alerts:
            content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=SUCCESS, size=32),
                        ft.Text("All stock levels look good.", size=13, color=TEXT_SECONDARY),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=30,
                alignment=ft.Alignment(0, 0),
            )
        else:
            rows = []
            for item in alerts:
                color = DANGER if item["status"] == "out" else WARNING
                badge_text = "Out" if item["status"] == "out" else f"{item['stock']}/{item['threshold']}"
                rows.append(
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(item["name"], size=13, weight=ft.FontWeight.W_500, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                    ft.Text(f"{item['stock']} units remaining", size=11, color=TEXT_MUTED),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(badge_text, size=10, weight=ft.FontWeight.W_600, color=color),
                                bgcolor=ft.Colors.with_opacity(0.12, color),
                                padding=ft.Padding(8, 4, 8, 4),
                                border_radius=12,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    )
                )
            content = ft.Column(rows, spacing=0, scroll=ft.ScrollMode.AUTO)
        return PanelCard("Inventory Alerts", content, subtitle="Low / out of stock")

    def _recent_sales_panel(self):
        recent = DashboardService.recent_sales()
        if not recent:
            content = empty_state(
                "No sales yet — POS checkout launches in Phase 2.",
                icon=ft.Icons.RECEIPT_LONG,
            )
        else:
            header = ft.Row(
                [ft.Text("Invoice", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                 ft.Text("Method", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                 ft.Text("Total", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                 ft.Text("Status", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                 ft.Text("Time", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED)],
                spacing=0,
            )
            rows = []
            for s in recent:
                status_color = SUCCESS if s["status"] == "Completed" else DANGER
                rows.append(
                    ft.Row(
                        [
                            ft.Text(s["invoice"], size=12, weight=ft.FontWeight.W_500, width=90),
                            ft.Text(s["method"], size=12, width=100),
                            ft.Text(format_money(s["total"]), size=12, weight=ft.FontWeight.W_500, width=110),
                            ft.Text(s["status"], size=11, color=status_color, weight=ft.FontWeight.W_500, width=80),
                            ft.Text(s["time"], size=12, color=TEXT_MUTED),
                        ],
                        spacing=0,
                    )
                )
            content = ft.Column([header, ft.Container(height=4), *rows], spacing=0, scroll=ft.ScrollMode.AUTO)
        return PanelCard("Recent Sales", content, subtitle="Demo data — POS checkout pending")

    def _top_products_panel(self):
        top = DashboardService.top_products()
        if not top:
            content = empty_state("No products registered yet.", icon=ft.Icons.SHOPPING_BAG)
        else:
            header = ft.Row(
                [ft.Text("Product", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, expand=True),
                 ft.Text("Units", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=60),
                 ft.Text("Revenue", size=11, weight=ft.FontWeight.W_600, color=TEXT_MUTED, width=100)],
                spacing=0,
            )
            rows = []
            for p in top:
                rows.append(
                    ft.Row(
                        [
                            ft.Text(p["name"], size=12, expand=True),
                            ft.Text(str(p["units"]), size=12, width=60),
                            ft.Text(format_money(p["revenue"]), size=12, width=100),
                        ],
                        spacing=0,
                        
                    )
                )
            content = ft.Column([header, *rows], spacing=0)
        return PanelCard("Top Selling Products", content, subtitle="Demo data")