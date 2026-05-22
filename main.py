import sys
import os

from utils.win_taskbar import preparer_windows_packagine

preparer_windows_packagine()

if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))

import flet as ft
from connexion import page_connexion
from utils.theme import POLICE_PRINCIPALE, POLICE_BOLD
from utils.paths import chemin_asset
from utils.fenetre import (
    appliquer_taille_et_centrer,
    appliquer_taille_connexion,
    avant_affichage,
    configurer_fenetre,
)


async def main(page: ft.Page):
    page.fonts = {
        POLICE_PRINCIPALE: chemin_asset("fonts", "IntelOneMono-Regular.ttf"),
        POLICE_BOLD: chemin_asset("fonts", "IntelOneMono-Bold.ttf"),
    }
    page.theme = ft.Theme(
        font_family=POLICE_PRINCIPALE,
    )
    configurer_fenetre(page)
    await appliquer_taille_et_centrer(page, appliquer_taille_connexion)
    page_connexion(page)
    page.window.visible = True
    page.update()


ft.run(main, before_main=avant_affichage, view=ft.AppView.FLET_APP_HIDDEN)
