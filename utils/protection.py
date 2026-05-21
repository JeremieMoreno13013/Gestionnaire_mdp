import shutil
import os
import sys
import hashlib
import json
from datetime import datetime
from utils.paths import repertoire_application

DOSSIER_DATA = os.path.join(repertoire_application(), "data")
_FICHIER_DESKTOP_INI = os.path.join(DOSSIER_DATA, "desktop.ini")
_ATTR_CACHE = 0x2
_ATTR_SYSTEME = 0x4
FICHIER_PRINCIPAL = os.path.join(DOSSIER_DATA, "coffre.json")
DOSSIER_BACKUP = os.path.join(DOSSIER_DATA, "backups")
FICHIER_HASH = os.path.join(DOSSIER_DATA, "hash.txt")
MAX_BACKUPS = 5

def _attribuer_masque_windows(chemin: str, cache: bool = True, systeme: bool = False) -> None:
    if sys.platform != "win32" or not os.path.exists(chemin):
        return
    import ctypes

    attributs = 0
    if cache:
        attributs |= _ATTR_CACHE
    if systeme:
        attributs |= _ATTR_SYSTEME
    if attributs:
        ctypes.windll.kernel32.SetFileAttributesW(chemin, attributs)

def _ecrire_desktop_ini() -> None:
    if sys.platform != "win32":
        return

    contenu = (
        "[.ShellClassInfo]\r\n"
        "ConfirmFileOp=1\r\n"
        "InfoTip=Données du gestionnaire de mots de passe — ne supprimez pas ce dossier.\r\n"
    )
    with open(_FICHIER_DESKTOP_INI, "w", encoding="utf-8") as f:
        f.write(contenu)
    _attribuer_masque_windows(_FICHIER_DESKTOP_INI, cache=True, systeme=True)

def restreindre_permissions_dossier() -> None:
    if sys.platform != "win32" or not os.path.isdir(DOSSIER_DATA):
        return

    utilisateur = os.environ.get("USERNAME")
    if not utilisateur:
        return

    import subprocess

    try:
        subprocess.run(
            [
                "icacls",
                DOSSIER_DATA,
                "/inheritance:r",
                "/grant:r",
                f"{utilisateur}:(OI)(CI)F",
            ],
            capture_output=True,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception:
        pass

def proteger_dossier_data() -> None:
    if not os.path.isdir(DOSSIER_DATA):
        return

    restreindre_permissions_dossier()

    if sys.platform == "win32":
        if not os.path.exists(_FICHIER_DESKTOP_INI):
            _ecrire_desktop_ini()
        _attribuer_masque_windows(DOSSIER_DATA, cache=True, systeme=True)

        for racine, dossiers, fichiers in os.walk(DOSSIER_DATA):
            for nom in dossiers + fichiers:
                chemin = os.path.join(racine, nom)
                if os.path.basename(chemin).lower() == "desktop.ini":
                    _attribuer_masque_windows(chemin, cache=True, systeme=True)
                else:
                    _attribuer_masque_windows(chemin, cache=True)

def calculer_hash_fichier(chemin):
    if not os.path.exists(chemin):
        return None
    
    with open(chemin, "rb") as f:
        contenu = f.read()
    return hashlib.sha256(contenu).hexdigest()

def sauvegarder_hash():
    hash_actuel = calculer_hash_fichier(FICHIER_PRINCIPAL)
    if hash_actuel:
        with open(FICHIER_HASH, "w", encoding="utf-8") as f:
            f.write(hash_actuel)

def verifier_integrite():
    if not os.path.exists(FICHIER_PRINCIPAL):
        return "absent"

    try:
        with open(FICHIER_PRINCIPAL, "r", encoding="utf-8") as f:
            donnees = json.load(f)

        if "mdp_maitre" not in donnees or "comptes" not in donnees:
            return "corrompu"
    except (json.JSONDecodeError, Exception):
        return "corrompu"

    if os.path.exists(FICHIER_HASH):
        with open(FICHIER_HASH, "r", encoding="utf-8") as f:
            hash_stocke = f.read().strip()

        hash_actuel = calculer_hash_fichier(FICHIER_PRINCIPAL)

        if hash_actuel != hash_stocke:
            return "modifie"

    return "intact"

def creer_backup():
    if not os.path.exists(FICHIER_PRINCIPAL):
        return False

    os.makedirs(DOSSIER_BACKUP, exist_ok=True)
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_backup = f"coffre_backup_{date}.json"
    chemin_backup = os.path.join(DOSSIER_BACKUP, nom_backup)

    try:
        shutil.copy2(FICHIER_PRINCIPAL, chemin_backup)
        nettoyer_backups()
        proteger_dossier_data()
        return True
    except Exception:
        return False

def nettoyer_backups():
    if not os.path.exists(DOSSIER_BACKUP):
        return

    backups = sorted(os.listdir(DOSSIER_BACKUP))

    while len(backups) > MAX_BACKUPS:
        ancien = backups.pop(0)
        os.remove(os.path.join(DOSSIER_BACKUP, ancien))

def restaurer_dernier_backup():
    if not os.path.exists(DOSSIER_BACKUP):
        return False

    backups = sorted(os.listdir(DOSSIER_BACKUP))

    if not backups:
        return False

    dernier = backups[-1]
    chemin_backup = os.path.join(DOSSIER_BACKUP, dernier)

    try:
        shutil.copy2(chemin_backup, FICHIER_PRINCIPAL)
        sauvegarder_hash()
        return True
    except Exception:
        return False

def lister_backups():
    if not os.path.exists(DOSSIER_BACKUP):
        return []

    backups = sorted(os.listdir(DOSSIER_BACKUP), reverse=True)
    resultats = []

    for backup in backups:
        chemin = os.path.join(DOSSIER_BACKUP, backup)
        taille = os.path.getsize(chemin)
        date = backup.replace("coffre_backup_", "").replace(".json", "")

        resultats.append({
            "nom": backup,
            "chemin": chemin,
            "taille": taille,
            "date": date
        })

    return resultats