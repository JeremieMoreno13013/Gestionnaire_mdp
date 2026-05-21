import unicodedata

def normaliser(texte):
    texte = texte.lower().strip()

    texte = unicodedata.normalize("NFD", texte)
    texte="".join(c for c in texte if unicodedata.category(c) != "Mn")

    return texte

def calculer_score(recherche, site):
    recherche = normaliser(recherche)
    site=normaliser(site)

    if recherche == site:
        return 100

    if site.startswith(recherche):
        return 80

    if recherche in site:
        return 50

    return 0