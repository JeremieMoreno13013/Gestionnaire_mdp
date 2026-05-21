import json
import os
from utils.paths import chemin_coffre
from utils.protection import sauvegarder_hash, creer_backup, proteger_dossier_data
from utils.crypto import (
    VERSION_CRYPTAGE,
    generer_sel,
    generer_cle,
    generer_cle_legacy,
    hasher_mdp_maitre,
    hasher_mdp_maitre_legacy,
    chiffrer,
    dechiffrer,
    dechiffrer_si_possible,
)

def _chemin_donnees() -> str:
    return chemin_coffre()

def _structure_vide() -> dict:
    return {
        "version": VERSION_CRYPTAGE,
        "sel": None,
        "mdp_maitre": None,
        "comptes": {},
    }

def _assurer_dossier_data():
    os.makedirs(os.path.dirname(_chemin_donnees()), exist_ok=True)

def initialiser_coffre():
    chemin = _chemin_donnees()
    _assurer_dossier_data()

    if not os.path.exists(chemin):
        sauvegarder(_structure_vide())
        return True

    donnees = charger()
    if donnees.get("mdp_maitre") is None:
        return True
    return False

def charger() -> dict:
    with open(_chemin_donnees(), "r", encoding="utf-8") as f:
        return json.load(f)

def sauvegarder(donnees: dict):
    _assurer_dossier_data()
    chemin = _chemin_donnees()
    tmp = chemin + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)
    os.replace(tmp, chemin)
    sauvegarder_hash()
    proteger_dossier_data()

def version_coffre() -> int:
    if not os.path.exists(_chemin_donnees()):
        return VERSION_CRYPTAGE
    return charger().get("version", 1)

def configurer_mdp_maitre(mot_de_passe: str) -> bytes:
    donnees = charger()
    sel = generer_sel()
    donnees["version"] = VERSION_CRYPTAGE
    donnees["sel"] = sel
    donnees["mdp_maitre"] = hasher_mdp_maitre(mot_de_passe, sel)
    sauvegarder(donnees)
    return generer_cle(mot_de_passe, sel)

def _lire_site_compte(compte: dict, cle: bytes) -> str:
    site = compte["site"]
    dechiffre = dechiffrer_si_possible(site, cle)
    return dechiffre if dechiffre is not None else site

def _migrer_comptes_vers_v2(comptes: dict, cle_ancienne: bytes, cle_nouvelle: bytes) -> dict:
    nouveaux = {}
    for cle_compte, compte in comptes.items():
        site = _lire_site_compte(compte, cle_ancienne)
        identifiant = dechiffrer(compte["identifiant"], cle_ancienne)
        mot_de_passe = dechiffrer(compte["mot_de_passe"], cle_ancienne)
        nouveaux[cle_compte] = {
            "site": chiffrer(site, cle_nouvelle),
            "identifiant": chiffrer(identifiant, cle_nouvelle),
            "mot_de_passe": chiffrer(mot_de_passe, cle_nouvelle),
        }
    return nouveaux

def migrer_coffre_legacy(mot_de_passe: str) -> bytes | None:
    donnees = charger()
    if donnees.get("version", 1) >= VERSION_CRYPTAGE:
        sel = donnees["sel"]
        return generer_cle(mot_de_passe, sel)

    if hasher_mdp_maitre_legacy(mot_de_passe) != donnees.get("mdp_maitre"):
        return None

    creer_backup()
    cle_ancienne = generer_cle_legacy(mot_de_passe)
    sel = generer_sel()
    cle_nouvelle = generer_cle(mot_de_passe, sel)

    donnees["version"] = VERSION_CRYPTAGE
    donnees["sel"] = sel
    donnees["mdp_maitre"] = hasher_mdp_maitre(mot_de_passe, sel)
    donnees["comptes"] = _migrer_comptes_vers_v2(donnees.get("comptes", {}), cle_ancienne, cle_nouvelle)
    sauvegarder(donnees)
    return cle_nouvelle

def verifier_mdp_maitre(mot_de_passe: str) -> tuple[bool, bytes | None]:
    donnees = charger()
    version = donnees.get("version", 1)

    if version < VERSION_CRYPTAGE:
        if hasher_mdp_maitre_legacy(mot_de_passe) != donnees.get("mdp_maitre"):
            return False, None
        cle = migrer_coffre_legacy(mot_de_passe)
        return cle is not None, cle

    sel = donnees.get("sel")
    if not sel or hasher_mdp_maitre(mot_de_passe, sel) != donnees.get("mdp_maitre"):
        return False, None
    return True, generer_cle(mot_de_passe, sel)

def lire_compte(compte: dict, cle: bytes) -> tuple[str, str, str]:
    site = _lire_site_compte(compte, cle)
    identifiant = dechiffrer(compte["identifiant"], cle)
    mot_de_passe = dechiffrer(compte["mot_de_passe"], cle)
    return site, identifiant, mot_de_passe

def ajouter_compte_data(
    site_chiffre: str,
    identifiant_chiffre: str,
    mdp_chiffre: str,
    cle_compte: str,
):
    creer_backup()
    donnees = charger()
    donnees["comptes"][cle_compte] = {
        "site": site_chiffre,
        "identifiant": identifiant_chiffre,
        "mot_de_passe": mdp_chiffre,
    }
    sauvegarder(donnees)

def supprimer_donnees_compte(cle_compte) -> bool:
    creer_backup()
    donnees = charger()
    if cle_compte in donnees["comptes"]:
        del donnees["comptes"][cle_compte]
        sauvegarder(donnees)
        return True
    return False

def compte_existe(cle_compte: str) -> bool:
    return cle_compte in charger()["comptes"]

def recuperer_comptes() -> dict:
    return charger()["comptes"]

def reset_application():
    chemin = _chemin_donnees()
    tmp = chemin + ".tmp"
    for fichier in (chemin, tmp):
        if os.path.exists(fichier):
            try:
                os.remove(fichier)
            except OSError:
                return False
    return True

def generer_cle_compte(site, identifiant):
    return f"{site}_{identifiant}".lower()
