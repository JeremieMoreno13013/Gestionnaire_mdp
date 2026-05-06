import random
import string

def generer_mdp(longueur=16, avec_symboles=True):
    """Génère un mot de passe aléatoire"""
    caracteres = string.ascii_letters + string.digits

    if avec_symboles:
        caracteres += string.punctuation
    mdp = "".join(random.choice(caracteres) for _ in range(longueur))
    return mdp
    