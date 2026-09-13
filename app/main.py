import flet as ft

from app.src.ui.app import PosApp


def main(page: ft.Page):
    app = PosApp(page)
    app.start()


ft.run(main=main, assets_dir="app/assets")
