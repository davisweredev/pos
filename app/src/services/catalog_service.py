from sqlmodel import select, func

from app.src.database.db import db
from app.src.models.category import Category
from app.src.models.inventory import StockAdjustment
from app.src.models.product import Product

STOCK_ADJUSTMENT_TYPES = ("restock", "removal", "correction")


class CategoryService:
    @staticmethod
    def list_categories(include_inactive: bool = True) -> list[Category]:
        with next(db.get_session()) as session:
            query = select(Category).order_by(Category.name)
            if not include_inactive:
                query = query.where(Category.is_active == True)  # noqa: E712
            return session.exec(query).all()

    @staticmethod
    def product_counts() -> dict[int, int]:
        with next(db.get_session()) as session:
            rows = session.exec(
                select(Product.category_id, func.count(Product.id)).group_by(
                    Product.category_id
                )
            ).all()
        return {cat_id: count for cat_id, count in rows if cat_id is not None}

    @staticmethod
    def create_category(name: str, description: str | None) -> tuple[bool, str]:
        name = name.strip()
        if not name:
            return False, "Category name is required."
        with next(db.get_session()) as session:
            duplicate = session.exec(
                select(Category).where(Category.name == name)
            ).first()
            if duplicate:
                return False, "A category with this name already exists."
            category = Category(name=name, description=(description or "").strip())
            session.add(category)
            session.commit()
        return True, "Category created."

    @staticmethod
    def update_category(
        category_id: int, name: str, description: str | None, is_active: bool
    ) -> tuple[bool, str]:
        name = name.strip()
        if not name:
            return False, "Category name is required."
        with next(db.get_session()) as session:
            category = session.get(Category, category_id)
            if not category:
                return False, "Category not found."
            duplicate = session.exec(
                select(Category).where(
                    Category.name == name, Category.id != category_id
                )
            ).first()
            if duplicate:
                return False, "A category with this name already exists."
            category.name = name
            category.description = (description or "").strip()
            category.is_active = is_active
            session.add(category)
            session.commit()
        return True, "Category updated."

    @staticmethod
    def toggle_active(category_id: int) -> tuple[bool, str]:
        with next(db.get_session()) as session:
            category = session.get(Category, category_id)
            if not category:
                return False, "Category not found."
            category.is_active = not category.is_active
            session.add(category)
            session.commit()
            return True, f"Category {'activated' if category.is_active else 'deactivated'}."

    @staticmethod
    def delete_category(category_id: int) -> tuple[bool, str]:
        with next(db.get_session()) as session:
            category = session.get(Category, category_id)
            if not category:
                return False, "Category not found."
            linked = session.exec(
                select(Product).where(Product.category_id == category_id)
            ).first()
            if linked:
                return False, "Cannot delete a category that still has products. Deactivate it instead."
            session.delete(category)
            session.commit()
        return True, "Category deleted."


class ProductService:
    @staticmethod
    def list_products(
        category_id: int | None = None,
        search: str = "",
        sort: str = "name",
        include_inactive: bool = True,
    ) -> list[Product]:
        """Return products with optional filters (no pagination)."""
        with next(db.get_session()) as session:
            query = select(Product)
            if not include_inactive:
                query = query.where(Product.is_active == True)  # noqa: E712
            if category_id:
                query = query.where(Product.category_id == category_id)
            if search:
                term = f"%{search.strip().lower()}%"
                query = query.where(
                    Product.name.ilike(term) | Product.sku.ilike(term)
                )
            if sort == "price_low":
                query = query.order_by(Product.price.asc())
            elif sort == "price_high":
                query = query.order_by(Product.price.desc())
            elif sort == "stock":
                query = query.order_by(Product.stock.asc())
            else:
                query = query.order_by(Product.name)
            return session.exec(query).all()

    @staticmethod
    def get_product(product_id: int) -> Product | None:
        with next(db.get_session()) as session:
            return session.get(Product, product_id)

    @staticmethod
    def create_product(data: dict) -> tuple[bool, str]:
        error = ProductService._validate(data)
        if error:
            return False, error
        with next(db.get_session()) as session:
            if data.get("sku"):
                duplicate = session.exec(
                    select(Product).where(Product.sku == data["sku"].strip().upper())
                ).first()
                if duplicate:
                    return False, "A product with this SKU already exists."
            product = Product(
                name=data["name"].strip(),
                sku=(data.get("sku") or "").strip().upper() or None,
                price=round(data["price"], 2),
                cost_price=round(data.get("cost_price") or 0.0, 2),
                stock=int(data.get("stock") or 0),
                low_stock=int(data.get("low_stock") or 5),
                image=data.get("image") or None,
            )
            session.add(product)
            session.commit()
        return True, "Product created."

    @staticmethod
    def update_product(product_id: int, data: dict) -> tuple[bool, str]:
        error = ProductService._validate(data)
        if error:
            return False, error
        with next(db.get_session()) as session:
            product = session.get(Product, product_id)
            if not product:
                return False, "Product not found."
            if data.get("sku"):
                existing = session.exec(
                    select(Product).where(
                        Product.sku == data["sku"].strip().upper(),
                        Product.id != product_id,
                    )
                ).first()
                if existing:
                    return False, "A product with this SKU already exists."
            product.name = data["name"].strip()
            product.sku = (data.get("sku") or "").strip().upper() or None
            product.category_id = data.get("category_id") or None
            product.price = round(data["price"], 2)
            product.cost_price = round(data.get("cost_price") or 0.0, 2)
            product.stock = int(data.get("stock") or 0)
            product.low_stock = int(data.get("low_stock") or 5)
            product.image = data.get("image") or None
            session.add(product)
            session.commit()
        return True, "Product updated."

    @staticmethod
    def toggle_active(product_id: int) -> tuple[bool, str]:
        with next(db.get_session()) as session:
            product = session.get(Product, product_id)
            if not product:
                return False, "Product not found."
            product.is_active = not product.is_active
            session.add(product)
            session.commit()
            return True, f"Product {'activated' if product.is_active else 'deactivated'}."

    @staticmethod
    def stock_summary() -> dict:
        """Summary used across dashboard + inventory views."""
        with next(db.get_session()) as session:
            products = session.exec(select(Product)).all()
        total = len(products)
        out_of_stock = sum(1 for p in products if p.stock <= 0)
        low_stock = sum(1 for p in products if 0 < p.stock <= p.low_stock)
        inventory_value = round(sum(p.stock * p.cost_price for p in products), 2)
        retail_value = round(sum(p.stock * p.price for p in products), 2)
        return {
            "total": total,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "inventory_value": inventory_value,
            "retail_value": retail_value,
        }

    @staticmethod
    def adjust_stock(
        product_id: int,
        result_stock: int,
        previous_stock: int,
        adjustment_type: str,
        reason: str,
        user_id: int | None,
    ) -> tuple[bool, str]:
        """Set a product stock to a new value and record an auditable adjustment.

        The quantity change is derived from the supplied previous value so the
        history stays accurate even if the form computed it differently.
        """
        if adjustment_type not in STOCK_ADJUSTMENT_TYPES:
            return False, "Invalid adjustment type."
        delta = int(result_stock) - int(previous_stock)
        if delta == 0:
            return False, "New stock quantity is the same as the current value."
        if int(result_stock) < 0:
            return False, "Stock cannot be negative."

        with db.engine.begin() as connection:
            from sqlmodel import Session

            session = Session(connection)
            product = session.get(Product, product_id)
            if not product:
                return False, "Product not found."
            product.stock = int(result_stock)
            session.add(product)
            session.add(
                StockAdjustment(
                    product_id=product_id,
                    quantity_change=delta,
                    adjustment_type=adjustment_type,
                    reason=(reason or "").strip() or None,
                    user_id=user_id,
                )
            )
            session.commit()
        return True, "Stock adjusted."

    @staticmethod
    def adjustment_history(limit: int = 50) -> list[StockAdjustment]:
        with next(db.get_session()) as session:
            return session.exec(
                select(StockAdjustment).order_by(
                    StockAdjustment.created_at.desc()
                )
            ).all()[:limit]

    @staticmethod
    def stock_low() -> list[Product]:
        with next(db.get_session()) as session:
            return session.exec(
                select(Product).where(
                    Product.is_active == True,  # noqa: E712
                    Product.stock <= Product.low_stock,
                )
            ).all()

    @staticmethod
    def _validate(data: dict) -> str | None:
        if not data.get("name") or not data["name"].strip():
            return "Product name is required."
        try:
            price = float(data.get("price") or 0)
        except (TypeError, ValueError):
            return "Selling price must be a number."
        if price < 0:
            return "Selling price cannot be negative."
        try:
            cost = float(data.get("cost_price") or 0)
            if cost < 0:
                return "Cost price cannot be negative."
        except (TypeError, ValueError):
            return "Cost price must be a number."
        try:
            if int(data.get("stock") or 0) < 0:
                return "Stock cannot be negative."
            if int(data.get("low_stock") or 5) < 0:
                return "Low stock threshold cannot be negative."
        except (TypeError, ValueError):
            return "Stock values must be whole numbers."
        return None


def categories_by_id() -> dict[int, Category]:
    return {c.id: c for c in CategoryService.list_categories()}