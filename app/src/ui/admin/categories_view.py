"""Admin Categories management view."""
import flet as ft

from app.src.core.theme import BORDER, DANGER, PRIMARY, SURFACE, SUCCESS, TEXT_MUTED, WARNING
from app.src.services.catalog_service import CategoryService
from app.src.ui.components.widgets import badge, confirm_dialog, empty_state, form_dialog, icon_btn, primary_button, safe_update


class CategoriesView(ft.Column):
    def __init__(self, page, shell):
        super().__init__()
        self._page = page
        self.shell = shell
        self.spacing = 0
        self.expand = True

        self._container = ft.Container(content=empty_state("Loading..."), expand=True)

        toolbar = ft.Row(
            [
                ft.Text("Categories", size=20, weight=ft.FontWeight.W_700),
                ft.Container(expand=True),
                primary_button("Add Category", icon=ft.Icons.ADD, on_click=lambda _: self._add()),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.controls = [
            ft.Container(
                content=ft.Column([toolbar, ft.Container(height=8), self._container], spacing=0, expand=True),
                padding=28,
                expand=True,
            )
        ]
        self._load()

    def _load(self):
        categories = CategoryService.list_categories()
        counts = CategoryService.product_counts()
        if not categories:
            self._container.content = empty_state("No categories yet.", hint="Create your first category to organize products.")
        else:
            rows = []
            for cat in categories:
                rows.append(self._card(cat, counts.get(cat.id, 0)))
            self._container.content = ft.Column(rows, spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
        safe_update(self._container)

    def _card(self, cat, product_count: int) -> ft.Container:
        status_text = "Active" if cat.is_active else "Inactive"
        status_color = SUCCESS if cat.is_active else DANGER
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(cat.name, size=14, weight=ft.FontWeight.W_500, expand=True),
                            ft.Text(
                                f"{product_count} products · {cat.description or 'No description'}",
                                size=11,
                                color=TEXT_MUTED,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                expand=True,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    badge(status_text, status_color),
                    icon_btn(ft.Icons.EDIT_OUTLINED, "Edit", color=PRIMARY, on_click=lambda _, c=cat: self._edit(c)),
                    icon_btn(
                        ft.Icons.TOGGLE_ON if cat.is_active else ft.Icons.TOGGLE_OFF,
                        "Deactivate" if cat.is_active else "Activate",
                        color=WARNING if cat.is_active else SUCCESS,
                        on_click=lambda _, c=cat: self._toggle(c),
                    ),
                    icon_btn(ft.Icons.DELETE_OUTLINE, "Delete", color=DANGER, on_click=lambda _, c=cat: self._delete(c)),
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

    def _edit(self, cat):
        self._open_dialog(cat)

    def _open_dialog(self, cat):
        is_edit = cat is not None
        name_field = ft.TextField(
            label="Category Name *",
            value=cat.name if is_edit else "",
            prefix_icon=ft.Icons.LABEL,
            fill_color=ft.Colors.WHITE,
            filled=True,
            border_color=BORDER,
            border_radius=8,
            expand=True,
        )
        desc_field = ft.TextField(
            label="Description (optional)",
            value=cat.description if is_edit else "",
            fill_color=ft.Colors.WHITE,
            filled=True,
            border_color=BORDER,
            border_radius=8,
            expand=True,
        )
        active_field = ft.Switch(value=cat.is_active if is_edit else True, label="Active")

        def handle_save(e):
            ok, msg = CategoryService.update_category(cat.id, name_field.value, desc_field.value, active_field.value) if is_edit else CategoryService.create_category(name_field.value, desc_field.value)
            if ok:
                self.shell.toast(msg)
                self._page.pop_dialog()
                self._load()
            else:
                self.shell.toast(msg, error=True)

        form_dialog(
            self._page,
            title="Edit Category" if is_edit else "Add Category",
            fields=[name_field, desc_field, active_field],
            on_save=handle_save,
            icon=ft.Icons.CATEGORY,
        )

    def _toggle(self, cat):
        ok, msg = CategoryService.toggle_active(cat.id)
        self.shell.toast(msg, error=not ok)
        self._load()

    def _delete(self, cat):
        def on_confirm():
            ok, msg = CategoryService.delete_category(cat.id)
            self.shell.toast(msg, error=not ok)
            self._load()

        confirm_dialog(
            self._page,
            title="Delete Category",
            message=f"Are you sure you want to delete '{cat.name}'? This cannot be undone.",
            on_confirm=on_confirm,
            confirm_label="Delete",
            danger=True,
        )