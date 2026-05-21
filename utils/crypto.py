import hashlib
import base64
from cryptography.fernet import Fernet

def generer_cle(mot_de_passe_maitre: str) -> bytes:
    hash = hashlib.sha256(mot_de_passe_maitre.encode()).digest()
    cle = base64.urlsafe_b64encode(hash)
    return cle

def chiffrer(texte: str, cle: bytes) -> str:
    f = Fernet(cle)
    return f.encrypt(texte.encode()).decode()

def dechiffrer(texte_chiffre: str, cle: bytes) -> str:
    f = Fernet(cle)
    return f.decrypt(texte_chiffre.encode()).decode()

def hasher_mdp_maitre(mot_de_passe: str) -> str:
    return hashlib.sha256(mot_de_passe.encode()).hexdigest()    