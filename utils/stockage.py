import json
import os

# Chemin du fichier de stockage
FICHIER = "data/coffre.json"

def initialiser_coffre():
    """
    Crée le fichier de données s'il n'existe pas.
    Retourne True si c'est la première utilisation.
    """

    os.makedirs("data", exist_ok=True)
    if not os.path.exists(FICHIER):
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
    """Charge les données du fichier json"""
    with open(FICHIER, "r", encoding="utf-8") as f:
        return json.load(f)

def sauvegarder(donnees: dict):
    """Sauvegarde les données dans le fichier"""
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)

def sauvegarder_mdp_maitre(hash_mdp: str):
    """Sauvegarde le hash du mot de passe maitre"""
    donnees = charger()
    donnees["mdp_maitre"] = hash_mdp
    sauvegarder(donnees)

def recuperer_mdp_maitre() -> str:
    """Récupère le hash du mot de passe maitre"""
    return charger()["mdp_maitre"]

def recuperer_comptes() -> dict:
    """Retourne tous les comptes enregistrés"""
    return charger()["comptes"]

def ajouter_compte_data(site: str, identifiant_chiffre: str, mdp_chiffre: str):
    """Ajoute ou met à jour un compte"""
    donnees = charger()
    donnees["comptes"][site] = {
        "identifiant" : identifiant_chiffre,
        "mot_de_passe" : mdp_chiffre
    }
    sauvegarder(donnees)

def supprimer_donnees_compte(site: str) -> bool:
    """
    Supprime un compte.
    Retourne True si le compte a été supprimé, False si introuvable.
    """
    donnees = charger()
    if site not in donnees["comptes"]:
        return False
    del donnees["comptes"][site]
    sauvegarder(donnees)
    return True

def site_existe(site: str) -> bool:
    """Vérifie si un site existe"""
    return site in recuperer_comptes()

