"""Admin Products management view."""
import flet as ft

from app.src.core.theme import BORDER, DANGER, PRIMARY, SURFACE, TEXT_SECONDARY, TEXT_MUTED, SUCCESS, WARNING
from app.src.services.catalog_service import (
    ProductService,
    categories_by_id,
)
from app.src.services.settings_service import SettingsService
from app.src.ui.components.widgets import (
    badge,
    empty_state,
    form_dialog,
    icon_btn,
    loading_state,
    primary_button,
    product_thumb,
    safe_update,
)
from app.src.utils.helpers import format_money


class ProductsView(ft.Column):
    def __init__(self, page, shell):
        super().__init__()
        self._page = page
        self.shell = shell
        self.spacing = 0
        self.expand = True

        self._category_id: int | None = None
        self._search = ""
        self._sort = "name"
        self.currency = SettingsService.get_setting("currency", "UGX")
        self.categories = categories_by_id()

        self._search_field = ft.TextField(
            label="Search products",
            prefix_icon=ft.Icons.SEARCH,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_color=BORDER,
            border_radius=8,
            expand=True,
            on_change=self._on_search,
            on_submit=self._on_search,
        )

        self._category_filter = ft.Dropdown(
            value="All Categories",
            options=[
                ft.dropdown.Option("All Categories"),
                *[ft.dropdown.Option(str(c.name)) for c in sorted(self.categories.values(), key=lambda c: c.name)],
            ],
            fill_color=ft.Colors.WHITE,
            filled=True,
            border_color=BORDER,
            border_radius=8,
            width=180,
            on_select=self._on_category,
        )

        self._sort_dropdown = ft.Dropdown(
            value="name",
            options=[
                ft.dropdown.Option("name", "Name A-Z"),
                ft.dropdown.Option("price_low", "Price: Low → High"),
                ft.dropdown.Option("price_high", "Price: High → Low"),
                ft.dropdown.Option("stock", "Stock: Low → High"),
            ],
            fill_color=ft.Colors.WHITE,
            filled=True,
            border_color=BORDER,
            border_radius=8,
            width=170,
            on_select=self._on_sort,
        )

        self._products_container = ft.Container(content=loading_state(), expand=True)

        toolbar = ft.Row(
            [
                ft.Text("Products", size=20, weight=ft.FontWeight.W_700),
                ft.Container(expand=True),
                self._search_field,
                self._category_filter,
                self._sort_dropdown,
                primary_button("Add Product", icon=ft.Icons.ADD, on_click=lambda _: self._add_product()),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            wrap=True,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [toolbar, ft.Container(height=4), self._products_container],
                    spacing=0,
                    expand=True,
                ),
                padding=28,
                expand=True,
            )
        ]
        self._load_products()

    def _load_products(self):
        products = ProductService.list_products(
            category_id=self._category_id,
            search=self._search,
            sort=self._sort,
        )
        self.categories = categories_by_id()
        if not products:
            self._products_container.content = empty_state(
                "No products found.",
                icon=ft.Icons.INVENTORY_2,
                hint="Add your first product to get started.",
            )
        else:
            rows = []
            for p in products:
                rows.append(self._product_row(p))
            self._products_container.content = ft.Column(rows, spacing=4, scroll=ft.ScrollMode.AUTO, expand=True)
        safe_update(self._products_container)

    def _product_row(self, product) -> ft.Container:
        cat = self.categories.get(product.category_id)
        cat_name = cat.name if cat else "—"
        status_color = SUCCESS if product.is_active else DANGER
        status_text = "Active" if product.is_active else "Inactive"
        stock_color = (
            SUCCESS if product.stock > product.low_stock
            else WARNING if product.stock > 0
            else DANGER
        )
        stock_label = (
            "In Stock" if product.stock > product.low_stock
            else "Low Stock" if product.stock > 0
            else "Out of Stock"
        )

        return ft.Container(
            content=ft.Row(
                [
                    product_thumb(product, size=42),
                    ft.Column(
                        [
                            ft.Text(product.name, size=13, weight=ft.FontWeight.W_500, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                            ft.Text(f"{product.sku or '—'} · {cat_name}", size=11, color=TEXT_MUTED),
                        ],
                        spacing=1,
                        expand=True,
                    ),
                    ft.Column(
                        [
                            ft.Text(format_money(product.price, self.currency), size=13, weight=ft.FontWeight.W_600),
                            ft.Text(f"Cost: {format_money(product.cost_price, self.currency)}", size=10, color=TEXT_MUTED),
                        ],
                        spacing=1,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                    ft.Column(
                        [
                            ft.Text(str(product.stock), size=13, weight=ft.FontWeight.W_500),
                            ft.Text(f"Min: {product.low_stock}", size=10, color=TEXT_MUTED),
                        ],
                        spacing=1,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        width=70,
                    ),
                    badge(stock_label, stock_color),
                    badge(status_text, status_color),
                    ft.Row(
                        [
                            icon_btn(ft.Icons.EDIT_OUTLINED, "Edit", color=PRIMARY, on_click=lambda _, p=product: self._edit_product(p)),
                            icon_btn(ft.Icons.SHOPPING_BAG, "Stock", color="#0D9488", on_click=lambda _, p=product: self._adjust_stock(p)),
                            icon_btn(ft.Icons.TOGGLE_ON if product.is_active else ft.Icons.TOGGLE_OFF,
                                     "Deactivate" if product.is_active else "Activate",
                                     color=WARNING if product.is_active else SUCCESS,
                                     on_click=lambda _, p=product: self._toggle(p)),
                        ],
                        spacing=2,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
            ),
            padding=ft.Padding(16, 12, 16, 12),
            border=ft.Border(ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER), ft.BorderSide(1, BORDER)),
            border_radius=10,
            bgcolor=SURFACE,
        )

    # --------------------------------------------------------- search / filter
    def _on_search(self, e):
        self._search = self._search_field.value or ""
        self._load_products()

    def _on_category(self, e):
        selected = self._category_filter.value
        if selected == "All Categories":
            self._category_id = None
        else:
            for cat in self.categories.values():
                if cat.name == selected:
                    self._category_id = cat.id
                    break
        self._load_products()

    def _on_sort(self, e):
        self._sort = self._sort_dropdown.value or "name"
        self._load_products()

    # --------------------------------------------------------- add / edit
    def _add_product(self):
        self._open_dialog(None)

    def _edit_product(self, product):
        self._open_dialog(product)

    def _open_dialog(self, product):
        is_edit = product is not None
        categories = sorted(self.categories.values(), key=lambda c: c.name)

        def _ctrl(label, value=None, icon=None, prefix=None, suffix=None, **kwargs):
            return ft.TextField(
                label=label,
                value=str(value) if value is not None else "",
                prefix_icon=prefix,
                suffix_icon=suffix,
                fill_color=ft.Colors.WHITE,
                filled=True,
                border_color=BORDER,
                border_radius=8,
                expand=True,
                **kwargs,
            )

        cat_options = [ft.dropdown.Option("None")]
        for c in categories:
            cat_options.append(ft.dropdown.Option(str(c.name)))

        cat_value = "None"
        if product and product.category_id in self.categories:
            cat_value = self.categories[product.category_id].name

        fields = [
            _ctrl("Product Name *", product.name if is_edit else "", prefix=ft.Icons.INVENTORY_2),
            ft.Row(
                [_ctrl("SKU", product.sku if is_edit else "", prefix=ft.Icons.QR_CODE)],
                spacing=12,
            ),
            ft.Dropdown(
                label="Category",
                value=cat_value,
                options=cat_options,
                fill_color=ft.Colors.WHITE,
                filled=True,
                border_color=BORDER,
                border_radius=8,
                expand=True,
            ),
            ft.Row(
                [
                    _ctrl("Selling Price *", product.price if is_edit else "0", prefix=ft.Icons.ATTACH_MONEY),
                    _ctrl("Cost Price", product.cost_price if is_edit else "0", prefix=ft.Icons.SHOW_CHART),
                ],
                spacing=12,
            ),
            ft.Row(
                [
                    _ctrl("Stock Quantity", product.stock if is_edit else "0", prefix=ft.Icons.STORE),
                    _ctrl("Low Stock Threshold", product.low_stock if is_edit else "5", prefix=ft.Icons.WARNING_AMBER),
                ],
                spacing=12,
            ),
            _ctrl("Image URL (optional)", product.image if is_edit else "", prefix=ft.Icons.IMAGE),
        ]

        def handle_save(e):
            name_val = fields[0].value.strip()
            if not name_val:
                self.shell.toast("Product name is required.", error=True)
                return

            cat_val = fields[2].value
            cat_id = None
            if cat_val and cat_val != "None":
                for c in categories:
                    if c.name == cat_val:
                        cat_id = c.id
                        break

            data = {
                "name": name_val,
                "sku": fields[1].controls[0].value.strip(),
                "category_id": cat_id,
                "price": fields[3].controls[0].value,
                "cost_price": fields[3].controls[1].value,
                "stock": fields[4].controls[0].value,
                "low_stock": fields[4].controls[1].value,
                "image": fields[5].value.strip() or None,
            }

            if is_edit:
                ok, msg = ProductService.update_product(product.id, data)
            else:
                ok, msg = ProductService.create_product(data)

            if ok:
                self.shell.toast(msg)
                self._page.pop_dialog()
                self._load_products()
            else:
                self.shell.toast(msg, error=True)

        form_dialog(
            self._page,
            title="Edit Product" if is_edit else "Add Product",
            fields=fields,
            on_save=handle_save,
            icon=ft.Icons.EDIT_NOTE if is_edit else ft.Icons.ADD_CIRCLE_OUTLINE,
        )

    # --------------------------------------------------------- stock & toggle
    def _adjust_stock(self, product):
        self._current_stock_product = product
        fields = [
            ft.Text(f"Adjusting stock for: {product.name}", size=14, weight=ft.FontWeight.W_500),
            ft.Text(f"Current stock: {product.stock}", size=12, color=TEXT_SECONDARY),
            ft.TextField(
                label="New Stock Quantity",
                value=str(product.stock),
                prefix_icon=ft.Icons.INVENTORY,
                fill_color=ft.Colors.WHITE,
                filled=True,
                border_color=BORDER,
                border_radius=8,
                expand=True,
            ),
            ft.Dropdown(
                label="Reason",
                value="restock",
                options=[
                    ft.dropdown.Option("restock", "Restock"),
                    ft.dropdown.Option("correction", "Stock Count Correction"),
                ],
                fill_color=ft.Colors.WHITE,
                filled=True,
                border_color=BORDER,
                border_radius=8,
            ),
            ft.TextField(
                label="Notes (optional)",
                fill_color=ft.Colors.WHITE,
                filled=True,
                border_color=BORDER,
                border_radius=8,
                expand=True,
            ),
        ]

        def handle_save(e):
            try:
                new_stock = int(fields[2].value)
            except ValueError:
                self.shell.toast("Stock must be a whole number.", error=True)
                return
            ok, msg = ProductService.adjust_stock(
                product_id=product.id,
                result_stock=new_stock,
                previous_stock=product.stock,
                adjustment_type=fields[3].value,
                reason=fields[4].value,
                user_id=self.shell.user.id,
            )
            if ok:
                self.shell.toast(msg)
                self._page.pop_dialog()
                self._load_products()
            else:
                self.shell.toast(msg, error=True)

        form_dialog(
            self._page,
            title="Adjust Stock",
            fields=fields,
            on_save=handle_save,
            icon=ft.Icons.STOREFRONT,
        )

    def _toggle(self, product):
        ok, msg = ProductService.toggle_active(product.id)
        self.shell.toast(msg, error=not ok)
        self._load_products()