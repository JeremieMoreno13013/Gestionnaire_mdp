import os
import sys


def repertoire_application() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def chemin_coffre() -> str:
    return os.path.join(repertoire_application(), "data", "coffre.json")


def chemin_asset(*parties: str) -> str:
    chemin_local = os.path.join(repertoire_application(), "assets", *parties)
    if os.path.exists(chemin_local):
        return chemin_local

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "assets", *parties)

    return chemin_local
