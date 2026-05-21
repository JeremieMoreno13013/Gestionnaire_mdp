# Gestionnaire de mots de passe

Application desktop de gestionnaire de mots de passe, développée en Python avec [Flet](https://flet.dev/). Les identifiants et mots de passe sont chiffrés localement ; seul un mot de passe maître permet d’ouvrir le coffre.

## Fonctionnalités

- **Mot de passe maître** — création du coffre à la première utilisation, puis connexion sécurisée
- **Chiffrement** — identifiants et mots de passe chiffrés avec Fernet (clé dérivée du mot de passe maître via SHA-256)
- **Gestion des comptes** — ajouter, modifier (double-clic sur une carte), supprimer
- **Recherche intelligente** — filtrage en temps réel avec score (correspondance exacte, préfixe, sous-chaîne), accents ignorés
- **Générateur de mot de passe** — création aléatoire lors de l’ajout ou de la modification
- **Copie rapide** — copie du mot de passe dans le presse-papiers
- **Affichage masqué** — révéler ou masquer le mot de passe sur chaque carte
- **Paramètres** — réinitialisation totale du coffre (confirmation `RESET TOTAL` + délai de sécurité)
- **Interface** — thème sombre, police Intel One Mono, messages via SnackBar

## Technologies

| Composant | Usage |
|-----------|--------|
| [Flet](https://flet.dev/) | Interface graphique |
| [cryptography](https://pypi.org/project/cryptography/) | Chiffrement Fernet |
| [pyperclip](https://pypi.org/project/pyperclip/) | Copie dans le presse-papiers |
| [Pillow](https://pypi.org/project/Pillow/) | Traitement d’images (logo) |

## Structure du projet

```
Gestionnaire_mdp/
├── main.py              # Point d’entrée, thème et polices
├── connexion.py         # Écran de connexion / création du coffre
├── gestionnaire.py      # Interface principale (liste, CRUD, paramètres)
├── requirements.txt     # Dépendances Python
├── assets/
│   ├── fonts/           # Intel One Mono
│   └── logo.png         # Optionnel (icône cadenas par défaut si absent)
├── utils/
│   ├── crypto.py        # Chiffrement et hash du mot de passe maître
│   ├── stockage.py      # Persistance JSON (data/coffre.json)
│   ├── generateur.py    # Génération de mots de passe
│   ├── recherche.py     # Normalisation et score de recherche
│   └── theme.py         # Couleurs, tailles, constantes UI
└── data/                # Données locales (ignoré par Git)
    └── coffre.json
```

## Prérequis

- **Python 3.10+** recommandé (testé avec Flet 0.85)
- Windows, macOS ou Linux

## Installation

```bash
git clone https://github.com/VOTRE_UTILISATEUR/Gestionnaire_mdp.git
cd Gestionnaire_mdp
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Sous Windows, si `python` n’est pas reconnu, utilisez `py` à la place :

```bash
py -m venv .venv
py -m pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

Ou avec `py` :

```bash
py main.py
```

### Mode développement (rechargement automatique)

```bash
flet run -r main.py
```

Les modifications dans `connexion.py`, `gestionnaire.py` et `utils/` sont prises en compte à chaque sauvegarde.

## Sécurité et données

- Le mot de passe maître n’est **jamais** stocké en clair : seul son hash SHA-256 est enregistré.
- Les comptes sont chiffrés dans `data/coffre.json` (dossier **exclu du dépôt Git** via `.gitignore`).
- **Sans le mot de passe maître, les données ne sont pas récupérables.** Choisissez-le avec soin.
- Ne partagez pas `data/coffre.json` sur un dépôt public.