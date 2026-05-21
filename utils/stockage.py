import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN_DONNEES = os.path.join(BASE_DIR, "data", "coffre.json")

def initialiser_coffre():
    """
    Crée le fichier de données s'il n'existe pas.
    Retourne True si c'est la première utilisation.
    """

    os.makedirs("data", exist_ok=True)
    if not os.path.exists(CHEMIN_DONNEES):
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
    with open(CHEMIN_DONNEES, "r", encoding="utf-8") as f:
        return json.load(f)

def sauvegarder(donnees: dict):
    """Sauvegarde les données dans le fichier"""
    with open(CHEMIN_DONNEES, "w", encoding="utf-8") as f:
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

def ajouter_compte_data(site: str, identifiant_chiffre: str, mdp_chiffre: str, cle_compte):
    """Ajoute ou met à jour un compte"""
    donnees = charger()
    donnees["comptes"][cle_compte] = {
        "site" : site,
        "identifiant" : identifiant_chiffre,
        "mot_de_passe" : mdp_chiffre
    }
    sauvegarder(donnees)

def supprimer_donnees_compte(cle_compte) -> bool:
    """
    Supprime un compte.
    Retourne True si le compte a été supprimé, False si introuvable.
    """
    donnees = charger()
    if cle_compte in donnees["comptes"]:
        del donnees["comptes"][cle_compte]
        sauvegarder(donnees)
        return True
    return False

def compte_existe(cle_compte: str) -> bool:
    """Vérifie si un site existe"""
    return cle_compte in recuperer_comptes()

def reset_application():
   if os.path.exists(CHEMIN_DONNEES):
      try:
         os.remove(CHEMIN_DONNEES)
         return True
      except Exception:
         return False
   return True

def generer_cle_compte(site, identifiant):
    """ Crée une clé unique pour chaque compte"""
    return f"{site}_{identifiant}".lower()