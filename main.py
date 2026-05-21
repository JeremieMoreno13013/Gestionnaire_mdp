import flet as ft
from connexion import page_connexion
from utils.theme import POLICE_PRINCIPALE, POLICE_BOLD
import sys
import os

if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))

def main(page: ft.Page):
    page.fonts = {
        POLICE_PRINCIPALE: "assets/fonts/IntelOneMono-Regular.ttf",
        POLICE_BOLD: "assets/fonts/IntelOneMono-Bold.ttf"
    }

    page.theme = ft.Theme(
        font_family=POLICE_PRINCIPALE,
    )
    page_connexion(page)

ft.run(main)
