"""Admin Reports view – dashboard summaries + sales analytics."""
import flet as ft

from app.src.core.config import config
from app.src.core.theme import BORDER, DANGER, PRIMARY, SUCCESS, TEXT_MUTED, WARNING
from app.src.services.analytics_service import ReportService
from app.src.services.settings_service import SettingsService
from app.src.ui.components.widgets import PanelCard, StatCard, empty_state
from app.src.utils.helpers import format_money

try:
    import flet_charts as fch
except ImportError:
    fch = None


class ReportsView(ft.Column):
    def __init__(self, page, shell):
        super().__init__()
        self._page = page
        self.shell = shell
        self.spacing = 0
        self.expand = True

        overview = ReportService.overview()
        kpis = ReportService.kpis()
        currency = SettingsService.get_setting("currency", "UGX")

        tabs = ft.Tabs(
            length=3,
            selected_index=0,
            animation_duration=200,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Sales Analytics"),
                            ft.Tab(label="Inventory"),
                            ft.Tab(label="Payment Breakdown"),
                        ],
                        label_color=PRIMARY,
                        unselected_label_color=TEXT_MUTED,
                        indicator_color=PRIMARY,
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self._sales_tab(overview, kpis, currency),
                            self._inventory_tab(overview, currency),
                            self._payment_tab(overview, currency),
                        ],
                    ),
                ],
            ),
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Reports & Analytics", size=20, weight=ft.FontWeight.W_700),
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Text(
                                        "Demo data — live analytics arrive in Phase 2",
                                        size=11,
                                        color=TEXT_MUTED,
                                    ) if config.use_demo_sales else ft.Container(),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=4),
                        tabs,
                    ],
                    spacing=0,
                    expand=True,
                ),
                padding=28,
                expand=True,
            )
        ]

    # ---------------------------------------------------------------- tabs
    def _sales_tab(self, overview, kpis, currency):
        content = ft.Column(
            [
                ft.Row(
                    [
                        StatCard("Gross Margin", f"{kpis['gross_margin']:.1f}%", ft.Icons.SHOW_CHART, PRIMARY, "#DBEAFE"),
                        StatCard("Avg. Order Value", format_money(kpis["avg_order_value"], currency), ft.Icons.SHOPPING_CART, "#0D9488", "#CCFBF1"),
                        StatCard("Est. Monthly Profit", format_money(kpis["profit_estimate"], currency), ft.Icons.ATTACH_MONEY, SUCCESS, "#DCFCE7"),
                    ],
                    spacing=14,
                    wrap=True,
                ),
                ft.Container(height=4),
                PanelCard(
                    "Sales by Category",
                    self._category_chart(overview, currency),
                    subtitle="Demo data",
                ),
            ],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        return ft.Container(content=content, expand=True)

    def _category_chart(self, overview, currency):
        data = overview.get("sales_by_category", [])
        if not data:
            return empty_state("No category sales data.", icon=ft.Icons.CATEGORY)

        if fch is not None and data:
            total = sum(d["amount"] for d in data) or 1
            bars = []
            for i, d in enumerate(data[:8]):
                d["amount"] / total * 100
                colors = [PRIMARY, "#0D9488", SUCCESS, WARNING, "#7C3AED", DANGER, "#0891B2", "#BE185D"]
                bars.append(
                    fch.BarChartGroup(
                        x=i,
                        rods=[fch.BarChartRod(
                            to_y=d["amount"] / 1000,
                            width=36,
                            color=colors[i % len(colors)],
                            border_radius=ft.BorderRadius(6, 6, 0, 0),
                        )],
                    )
                )
            chart = fch.BarChart(
                groups=bars,
                bottom_axis=fch.ChartAxis(
                    labels=[ft.Text(d["category"][:8], size=9, color=TEXT_MUTED) for d in data[:8]],
                ),
                horizontal_grid_lines=fch.ChartGridLines(color="#E2E8F0", width=1, dash_pattern=[3, 3]),
                height=220,
                animation="none",
                interactive=False,
            )
            return chart

        # fallback table
        rows = []
        for d in data:
            rows.append(
                ft.Row(
                    [
                        ft.Text(d["category"], size=12, expand=True),
                        ft.Text(format_money(d["amount"], currency), size=12, weight=ft.FontWeight.W_500),
                    ],
                    spacing=0,
                )
            )
        return ft.Column(rows, spacing=4)

    def _inventory_tab(self, overview, currency):
        summary = overview["summary"]
        products = [
            ("Products in Stock", str(summary["total"] - summary["out_of_stock"])),
            ("Out of Stock", str(summary["out_of_stock"])),
            ("Low Stock Items", str(summary["low_stock"])),
            ("Inventory Value", format_money(summary["inventory_value"], currency)),
            ("Retail Value", format_money(summary["retail_value"], currency)),
        ]
        rows = []
        for label, value in products:
            rows.append(
                ft.Row(
                    [
                        ft.Text(label, size=13, expand=True),
                        ft.Text(value, size=13, weight=ft.FontWeight.W_500),
                    ],
                    spacing=0,
                    
                )
            )
            rows.append(ft.Divider(height=1, color=BORDER))

        content = ft.Column(
            [
                ft.Text("Inventory Summary", size=15, weight=ft.FontWeight.W_600),
                ft.Container(height=8),
                *rows,
            ],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        return ft.Container(content=content, expand=True, padding=18)

    def _payment_tab(self, overview, currency):
        breakdown = overview.get("payment_breakdown", [])
        if not breakdown:
            return empty_state("No payment data.", icon=ft.Icons.PAYMENTS)

        total = sum(d["amount"] for d in breakdown) or 1
        rows = []
        colors = [PRIMARY, "#0D9488", SUCCESS, WARNING]
        for i, d in enumerate(breakdown):
            pct = d["amount"] / total * 100
            bar_width = int(pct * 2.8)
            color = colors[i % len(colors)]
            rows.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(d["method"], size=12, weight=ft.FontWeight.W_500, expand=True),
                                ft.Text(format_money(d["amount"], currency), size=12, width=120),
                                ft.Text(f"{pct:.0f}%", size=11, color=TEXT_MUTED, width=40),
                            ],
                            spacing=0,
                        ),
                        ft.Container(
                            width=bar_width,
                            height=6,
                            bgcolor=color,
                            border_radius=3,
                            margin=ft.Margin(0, 2, 0, 0),
                        ),
                    ],
                    spacing=0,
                    margin=ft.Margin(0, 0, 0, 12),
                )
            )

        content = ft.Column(
            [
                ft.Text("Payment Method Breakdown", size=15, weight=ft.FontWeight.W_600),
                ft.Text("Share of total revenue (demo).", size=11, color=TEXT_MUTED),
                ft.Container(height=12),
                *rows,
            ],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        return ft.Container(content=content, expand=True, padding=18)