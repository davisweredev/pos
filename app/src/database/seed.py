"""Database seeding.

Runs automatically at startup; only inserts rows when the respective tables are
empty so repeated launches are safe. The initial administrator is bootstrap-only
and can be overridden via the ADMIN_USERNAME / ADMIN_PASSWORD environment
variables (e.g. a ``.env`` file is loaded by the app).
"""
import os

from sqlmodel import select

from app.src.database.db import db
from app.src.models.category import Category
from app.src.models.payment import PaymentMethod
from app.src.models.product import Product
from app.src.models.setting import Setting
from app.src.models.user import User
from app.src.services.auth_service import AuthService

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

_DEMO_CATEGORIES = [
    ("Beverages", "Juices, sodas, water and hot drinks"),
    ("Snacks", "Crisps, biscuits and quick bites"),
    ("Groceries", "Staples, oil, rice and canned goods"),
    ("Dairy & Bakery", "Milk, yoghurt, bread and pastries"),
    ("Personal Care", "Soap, toothpaste and hygiene essentials"),
]

_DEMO_PRODUCTS = [
    # name, sku, category, price, cost, stock, low_stock
    ("Mineral Water 1L", "WTR-1001", "Beverages", 1500, 900, 120, 30),
    ("Soda 300ml", "SOD-2001", "Beverages", 2000, 1300, 200, 50),
    ("Orange Juice 500ml", "JUC-3001", "Beverages", 3500, 2300, 75, 25),
    ("Energy Drink 250ml", "ENG-4001", "Beverages", 5000, 3400, 40, 15),
    ("Potato Crisps 80g", "CRP-1002", "Snacks", 1500, 800, 150, 40),
    ("Chocolate Bar 45g", "CHC-2002", "Snacks", 3000, 1900, 60, 20),
    ("Biscuits 250g", "BSC-3002", "Snacks", 2500, 1500, 90, 25),
    ("Cooking Oil 1L", "OIL-1003", "Groceries", 9500, 7600, 55, 15),
    ("Rice 5kg", "RCE-2003", "Groceries", 42000, 35000, 20, 8),
    ("Canned Tomatoes 400g", "TMT-3003", "Groceries", 3500, 2400, 110, 30),
    ("Wheat Bread Loaf", "BRD-1004", "Dairy & Bakery", 3000, 1900, 45, 20),
    ("Fresh Milk 1L", "MLK-2004", "Dairy & Bakery", 4500, 3200, 80, 25),
    ("Yoghurt 450g", "YGH-3004", "Dairy & Bakery", 5000, 3600, 5, 15),
    ("Toothpaste 100g", "TPT-1005", "Personal Care", 5000, 3600, 70, 20),
    ("Bar Soap 150g", "SOP-2005", "Personal Care", 2500, 1500, 130, 35),
    ("Shampoo 250ml", "SHP-3005", "Personal Care", 8500, 6100, 30, 10),
]

_DEMO_PAYMENT_METHODS = [
    ("Cash", "CASH", True),
    ("Card", "CARD", False),
    ("Mobile Money", "MOMO", False),
    ("Bank Transfer", "BANK", False),
]

_DEFAULT_SETTINGS = {
    "business_name": "SwiftPOS",
    "business_tagline": "Retail & Point of Sale",
    "currency": "UGX",
    "receipt_footer": "Thank you for shopping with us.",
    "low_stock_default": "5",
    "vat_rate": "0",
}


def seed_database() -> None:
    db.create_tables()
    _seed_admin()
    _seed_categories_and_products()
    _seed_payment_methods()
    _seed_settings()


def _seed_admin() -> None:
    with next(db.get_session()) as session:
        existing = session.exec(select(User)).first()
        if existing:
            return
        username = os.getenv("ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME)
        password = os.getenv("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
        admin = User(
            full_name="Administrator",
            email=f"{username}@localhost",
            username=username,
            password_hash=AuthService.hash_password(password),
            user_type="admin",
            is_active=True,
        )
        session.add(admin)
        session.commit()


def _seed_categories_and_products() -> None:
    """Seed demo categories + products only when the products table is empty."""
    with next(db.get_session()) as session:
        products_exist = session.exec(select(Product)).first()
        if products_exist:
            return

        category_map: dict[str, Category] = {}
        for name, description in _DEMO_CATEGORIES:
            category = Category(name=name, description=description)
            session.add(category)
            category_map[name] = category
        session.add(
            Category(name="Supplies", description="Store supplies and equipment", is_active=False)
        )
        session.commit()

        for name, sku, cat, price, cost, stock, low_stock in _DEMO_PRODUCTS:
            product = Product(
                name=name,
                sku=sku,
                category_id=category_map[cat].id,
                price=float(price),
                cost_price=float(cost),
                stock=stock,
                low_stock=low_stock,
            )
            session.add(product)
        session.commit()


def _seed_payment_methods() -> None:
    with next(db.get_session()) as session:
        existing = session.exec(select(PaymentMethod)).first()
        if existing:
            return
        for name, code, is_cash in _DEMO_PAYMENT_METHODS:
            session.add(PaymentMethod(name=name, code=code, is_cash=is_cash))
        session.commit()


def _seed_settings() -> None:
    with next(db.get_session()) as session:
        existing = session.exec(select(Setting)).first()
        if existing:
            return
        for key, value in _DEFAULT_SETTINGS.items():
            session.add(Setting(key=key, value=value))
        session.commit()