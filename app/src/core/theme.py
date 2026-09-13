"""Central visual language for the POS: palette and theme builder."""

import flet as ft

# Brand palette
PRIMARY = "#2563EB"
PRIMARY_DARK = "#1D4ED8"
ACCENT = "#F59E0B"
SUCCESS = "#16A34A"
WARNING = "#D97706"
DANGER = "#DC2626"

# Surfaces
SIDEBAR_BG = "#0F172A"
SIDEBAR_HOVER = "#1E293B"
SIDEBAR_ACTIVE = "#1D4ED8"
BG = "#F1F5F9"
SURFACE = "#FFFFFF"
HEADER_BG = "#FFFFFF"

# Text
TEXT = "#0F172A"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#94A3B8"
TEXT_ON_DARK = "#E2E8F0"
TEXT_ON_DARK_MUTED = "#94A3B8"

BORDER = "#E2E8F0"

SCALE = {
    "primary": PRIMARY,
    "primary_dark": PRIMARY_DARK,
    "accent": ACCENT,
    "success": SUCCESS,
    "warning": WARNING,
    "danger": DANGER,
}

STAT_ACCENTS = [
    (PRIMARY, "#DBEAFE"),
    (ACCENT, "#FEF3C7"),
    (SUCCESS, "#DCFCE7"),
    (DANGER, "#FEE2E2"),
    ("#7C3AED", "#EDE9FE"),
    ("#0D9488", "#CCFBF1"),
]


def apply_theme(page: ft.Page) -> None:
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=PRIMARY,
        use_material3=True,
    )
    page.bgcolor = BG
    page.padding = 0
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.expand = True