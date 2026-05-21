import time

_echecs = 0
_prochaine_tentative = 0.0

def enregistrer_echec_connexion() -> None:
    global _echecs, _prochaine_tentative
    _echecs += 1
    if _echecs < 3:
        return
    delai = min(30.0, 5.0 * (2 ** (_echecs - 3)))
    _prochaine_tentative = time.time() + delai

def reinitialiser_echecs_connexion() -> None:
    global _echecs, _prochaine_tentative
    _echecs = 0
    _prochaine_tentative = 0.0

def delai_restant_connexion() -> float:
    return max(0.0, _prochaine_tentative - time.time())

def connexion_bloquee() -> bool:
    return delai_restant_connexion() > 0