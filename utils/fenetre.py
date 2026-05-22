import os
import sys
from collections.abc import Callable

import flet as ft

from utils.paths import chemin_asset
from utils.theme import (
    FOND_PAGE,
    FENETRE_HAUTEUR_CONNEXION,
    FENETRE_HAUTEUR_GESTIONNAIRE,
    FENETRE_LARGEUR_CONNEXION,
    FENETRE_LARGEUR_GESTIONNAIRE,
)


def chemin_icone_fenetre() -> str | None:
    chemin = chemin_asset("logo.ico")
    return chemin if os.path.isfile(chemin) else None


def configurer_fenetre(page: ft.Page) -> None:
    icone = chemin_icone_fenetre()
    if icone:
        page.window.icon = icone


def _appliquer_taille(page: ft.Page, largeur: int, hauteur: int) -> None:
    page.window.width = largeur
    page.window.height = hauteur
    page.window.min_width = largeur
    page.window.max_width = largeur
    page.window.min_height = hauteur
    page.window.max_height = hauteur
    page.window.resizable = False


def appliquer_taille_connexion(page: ft.Page) -> None:
    _appliquer_taille(page, FENETRE_LARGEUR_CONNEXION, FENETRE_HAUTEUR_CONNEXION)


def appliquer_taille_gestionnaire(page: ft.Page) -> None:
    _appliquer_taille(page, FENETRE_LARGEUR_GESTIONNAIRE, FENETRE_HAUTEUR_GESTIONNAIRE)


def _nudge_taille_windows(page: ft.Page) -> None:
    if sys.platform != "win32":
        return
    w, h = page.window.width, page.window.height
    if w is None or h is None:
        return
    wi, hi = int(w), int(h)
    page.window.width = wi + 1
    page.update()
    page.window.width = wi
    page.window.height = hi + 1
    page.update()
    page.window.height = hi
    page.update()


async def _centrer_fenetre(page: ft.Page) -> None:
    try:
        await page.window.center()
        page.update()
    except RuntimeError:
        _nudge_taille_windows(page)
        return
    _nudge_taille_windows(page)


async def appliquer_taille_et_centrer(
    page: ft.Page,
    appliquer_taille: Callable[[ft.Page], None],
) -> None:
    appliquer_taille(page)
    page.update()
    await _centrer_fenetre(page)


async def avant_affichage(page: ft.Page) -> None:
    page.bgcolor = FOND_PAGE
    appliquer_taille_connexion(page)
    page.window.visible = False
    page.update()
