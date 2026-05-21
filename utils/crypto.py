import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VERSION_CRYPTAGE = 2
_ITERATIONS_PBKDF2 = 600_000
_LONGUEUR_SEL = 16

def generer_sel() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(_LONGUEUR_SEL)).decode()

def _deriver_cle_brute(mot_de_passe: str, sel_b64: str) -> bytes:
    sel = base64.urlsafe_b64decode(sel_b64.encode())
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sel,
        iterations=_ITERATIONS_PBKDF2,
    )
    return base64.urlsafe_b64encode(kdf.derive(mot_de_passe.encode()))

def generer_cle(mot_de_passe_maitre: str, sel: str) -> bytes:
    return _deriver_cle_brute(mot_de_passe_maitre, sel)

def hasher_mdp_maitre(mot_de_passe: str, sel: str) -> str:
    return _deriver_cle_brute(mot_de_passe, sel).decode()

def generer_cle_legacy(mot_de_passe_maitre: str) -> bytes:
    digest = hashlib.sha256(mot_de_passe_maitre.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def hasher_mdp_maitre_legacy(mot_de_passe: str) -> str:
    return hashlib.sha256(mot_de_passe.encode()).hexdigest()

def chiffrer(texte: str, cle: bytes) -> str:
    return Fernet(cle).encrypt(texte.encode()).decode()

def dechiffrer(texte_chiffre: str, cle: bytes) -> str:
    return Fernet(cle).decrypt(texte_chiffre.encode()).decode()

def dechiffrer_si_possible(texte: str, cle: bytes) -> str | None:
    try:
        return dechiffrer(texte, cle)
    except Exception:
        return None

def valider_force_mdp_maitre(mot_de_passe: str) -> tuple[bool, str]:
    if len(mot_de_passe) < 12:
        return False, "12 caractères minimum"
    if mot_de_passe.lower() == mot_de_passe or mot_de_passe.upper() == mot_de_passe:
        if not any(c.isdigit() for c in mot_de_passe):
            return False, "Ajoutez des chiffres ou des majuscules/minuscules"
    if not any(c.isalpha() for c in mot_de_passe):
        return False, "Le mot de passe doit contenir des lettres"
    return True, ""