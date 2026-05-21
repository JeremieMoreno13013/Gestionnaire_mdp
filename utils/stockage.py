import json
import os

from utils.paths import chemin_coffre


def _chemin_donnees() -> str:
    return chemin_coffre()


def _assurer_dossier_data():
    os.makedirs(os.path.dirname(_chemin_donnees()), exist_ok=True)


def initialiser_coffre():
    chemin = _chemin_donnees()
    _assurer_dossier_data()

    if not os.path.exists(chemin):
        structure_vide = {
            "mdp_maitre": None,
            "comptes": {}
        }
        sauvegarder(structure_vide)
        return True

    donnees = charger()
    if donnees["mdp_maitre"] is None:
        return True
    return False


def charger() -> dict:
    with open(_chemin_donnees(), "r", encoding="utf-8") as f:
        return json.load(f)


def sauvegarder(donnees: dict):
    _assurer_dossier_data()
    with open(_chemin_donnees(), "w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)


def sauvegarder_mdp_maitre(hash_mdp: str):
    donnees = charger()
    donnees["mdp_maitre"] = hash_mdp
    sauvegarder(donnees)


def recuperer_mdp_maitre() -> str:
    return charger()["mdp_maitre"]


def recuperer_comptes() -> dict:
    return charger()["comptes"]


def ajouter_compte_data(site: str, identifiant_chiffre: str, mdp_chiffre: str, cle_compte):
    donnees = charger()
    donnees["comptes"][cle_compte] = {
        "site": site,
        "identifiant": identifiant_chiffre,
        "mot_de_passe": mdp_chiffre,
    }
    sauvegarder(donnees)


def supprimer_donnees_compte(cle_compte) -> bool:
    donnees = charger()
    if cle_compte in donnees["comptes"]:
        del donnees["comptes"][cle_compte]
        sauvegarder(donnees)
        return True
    return False


def compte_existe(cle_compte: str) -> bool:
    return cle_compte in recuperer_comptes()


def reset_application():
    chemin = _chemin_donnees()
    if os.path.exists(chemin):
        try:
            os.remove(chemin)
            return True
        except OSError:
            return False
    return True


def generer_cle_compte(site, identifiant):
    return f"{site}_{identifiant}".lower()
