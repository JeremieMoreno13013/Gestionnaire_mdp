import hashlib
import base64
from cryptography.fernet import Fernet

def generer_cle(mot_de_passe_maitre: str) -> bytes:
    """
    Génère une clé de chiffrement à partir du mot de passe maitre.
    Le même mot de passe donnera toujours la même clé.
    """
    hash = hashlib.sha256(mot_de_passe_maitre.encode()).digest()
    cle = base64.urlsafe_b64encode(hash)
    return cle

def chiffrer(texte: str, cle: bytes) -> str:
    """Chiffre un texte et retourne une chaine chiffrée"""
    f = Fernet(cle)
    return f.encrypt(texte.encode()).decode()

def dechiffrer(texte_chiffre: str, cle: bytes) -> str:
    """Déchiffre un texte et retourne le texte original"""
    f = Fernet(cle)
    return f.decrypt(texte_chiffre.encode()).decode()

def hasher_mdp_maitre(mot_de_passe: str) -> str:
    """
    Hash le mot de passe maitre pour le stocker sans le connaitre.
    On ne stocke JAMAIS un mot de passe en clair !
    """
    return hashlib.sha256(mot_de_passe.encode()).hexdigest()    