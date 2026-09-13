"""Analytics services.

Sales-oriented figures are currently demo data isolated behind
``USE_DEMO_SALES`` in :mod:`app.src.core.config` so that they can be swapped
for real database queries once the checkout/POS pipeline lands in Phase 2.
Catalog and inventory figures are always computed from the real database.
"""
import random
from datetime import datetime, timedelta

from app.src.core.config import config
from app.src.services.catalog_service import CategoryService, ProductService
from app.src.services.user_service import UserService

_WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class DashboardService:
    @staticmethod
    def stats() -> dict:
        """High-level figures for the dashboard."""
        summary = ProductService.stock_summary()
        staff = UserService.active_staff_count()
        categories = len(CategoryService.list_categories(include_inactive=True))

        if config.use_demo_sales:
            demos = DashboardService._demo_sales()
            today_sales = demos["today_amount"]
            month_sales = demos["month_amount"]
            total_sales = demos["total_amount"]
            orders_today = demos["orders_today"]
        else:
            today_sales = month_sales = total_sales = 0.0
            orders_today = 0

        return {
            "today_sales": today_sales,
            "month_sales": month_sales,
            "total_sales": total_sales,
            "orders_today": orders_today,
            "products_total": summary["total"],
            "low_stock": summary["low_stock"],
            "out_of_stock": summary["out_of_stock"],
            "inventory_value": summary["inventory_value"],
            "retail_value": summary["retail_value"],
            "staff_count": staff,
            "categories_count": categories,
        }

    @staticmethod
    def sales_trend(days: int = 7) -> list[dict]:
        if not config.use_demo_sales:
            return [{"label": d, "amount": 0.0, "orders": 0} for d in _WEEKDAYS[:days]]
        return DashboardService._demo_sales()["trend"][-days:]

    @staticmethod
    def recent_sales(limit: int = 10) -> list[dict]:
        if not config.use_demo_sales:
            return []
        return DashboardService._demo_sales()["recent"][:limit]

    @staticmethod
    def top_products(limit: int = 5) -> list[dict]:
        products = ProductService.list_products(include_inactive=False)
        if config.use_demo_sales:
            rng = random.Random(20240911)
            return [
                {
                    "name": p.name[:24],
                    "units": rng.randint(18, 220),
                    "revenue": round(rng.randint(1800, 90000), 2),
                }
                for p in products[:limit * 2]
            ][:limit] or [
                {"name": "Soft Drink 500ml", "units": 142, "revenue": 142000.0},
                {"name": "Cooking Oil 1L", "units": 96, "revenue": 134000.0},
                {"name": "Rice 5kg", "units": 71, "revenue": 120700.0},
                {"name": "Wheat Bread Loaf", "units": 210, "revenue": 63000.0},
                {"name": "Toothpaste 100g", "units": 83, "revenue": 41500.0},
            ][:limit]
        return []

    @staticmethod
    def inventory_alerts(limit: int = 6) -> list[dict]:
        low = ProductService.stock_low()
        alerts = []
        for product in low[:limit]:
            alerts.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "stock": product.stock,
                    "threshold": product.low_stock,
                    "status": "out" if product.stock <= 0 else "low",
                }
            )
        return alerts

    @staticmethod
    def _demo_sales() -> dict:
        """Deterministic demo figures representing a busy week of trading."""
        amounts = [1480000, 1320000, 1540000, 1210000, 1690000, 2110000, 1760000]
        orders = [84, 71, 90, 66, 97, 122, 103]
        today_idx = 6
        today_amount = amounts[today_idx]
        month_amount = sum(amounts) * 4
        total_amount = month_amount * 9
        trend = []
        for i in range(len(amounts)):
            day = datetime.now() - timedelta(days=len(amounts) - 1 - i)
            trend.append(
                {
                    "label": day.strftime("%a")[:3],
                    "amount": amounts[i],
                    "orders": orders[i],
                }
            )
        recent = [
            {
                "invoice": f"INV-{3000 + i}",
                "method": method,
                "total": amount,
                "time": (datetime.now() - timedelta(minutes=40 * (i + 1))).strftime("%I:%M %p"),
                "status": "Completed" if i % 5 else "Refunded",
            }
            for i, (method, amount) in enumerate(
                [
                    ("Cash", 12500),
                    ("Mobile Money", 48200),
                    ("Card", 22400),
                    ("Cash", 8900),
                    ("Mobile Money", 15600),
                    ("Card", 31750),
                    ("Cash", 21300),
                    ("Mobile Money", 9400),
                    ("Cash", 17600),
                    ("Bank Transfer", 66500),
                ]
            )
        ]
        return {
            "today_amount": today_amount,
            "month_amount": month_amount,
            "total_amount": total_amount,
            "orders_today": orders[today_idx],
            "trend": trend,
            "recent": recent,
        }


class ReportService:
    """Report building blocks. Sales figures are demo while catalog figures
    (inventory value, low-stock, category counts) come from the database."""

    @staticmethod
    def overview() -> dict:
        summary = ProductService.stock_summary()
        categories = CategoryService.list_categories(include_inactive=False)
        payment_total = sum(
            random.Random(5).randint(9000, 95000) for _ in range(4)
        ) if config.use_demo_sales else 0

        return {
            "summary": summary,
            "categories": len(categories),
            "payment_breakdown": [
                {"method": "Cash", "amount": 0.38 * payment_total},
                {"method": "Mobile Money", "amount": 0.34 * payment_total},
                {"method": "Card", "amount": 0.21 * payment_total},
                {"method": "Bank Transfer", "amount": 0.07 * payment_total},
            ],
            "sales_by_category": ReportService._sales_by_category(),
        }

    @staticmethod
    def kpis() -> dict:
        stats = DashboardService.stats()
        gross_margin = 22.0
        return {
            "gross_margin": gross_margin,
            "avg_order_value": round(stats["today_sales"] / max(stats["orders_today"], 1), 2),
            "profit_estimate": round(
                stats["month_sales"] * gross_margin / 100
                if config.use_demo_sales
                else 0.0,
                2,
            ),
        }

    @staticmethod
    def _sales_by_category() -> list[dict]:
        if not config.use_demo_sales:
            return []
        rng = random.Random(11)
        categories = CategoryService.list_categories(include_inactive=False)
        if not categories:
            categories = ["Beverages", "Snacks", "Groceries", "Personal Care"]
            items = []
            weights = [0.3, 0.22, 0.28, 0.2]
            for i, cat in enumerate(categories):
                items.append(
                    {
                        "category": cat,
                        "amount": round(weights[i] * 6_000_000, 2),
                    }
                )
            return items
        items = []
        for cat in categories:
            items.append(
                {
                    "category": cat.name[:18],
                    "amount": round(rng.randint(400_000, 2_400_000), 2),
                }
            )
        items.sort(key=lambda x: x["amount"], reverse=True)
        return items