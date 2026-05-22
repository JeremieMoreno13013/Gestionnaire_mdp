import os
import sys


def repertoire_executable() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _installe_dans_program_files(chemin: str) -> bool:
    normalise = os.path.normpath(chemin).lower()
    return "program files" in normalise


def repertoire_donnees() -> str:
    base = repertoire_executable()
    if getattr(sys, "frozen", False) and _installe_dans_program_files(base):
        return os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "GestionnaireMotsDePasse",
        )
    if getattr(sys, "frozen", False):
        return base
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def repertoire_application() -> str:
    return repertoire_donnees()


def chemin_coffre() -> str:
    return os.path.join(repertoire_donnees(), "data", "coffre.json")


def chemin_asset(*parties: str) -> str:
    chemin_local = os.path.join(repertoire_executable(), "assets", *parties)
    if os.path.exists(chemin_local):
        return chemin_local

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "assets", *parties)

    return chemin_local
