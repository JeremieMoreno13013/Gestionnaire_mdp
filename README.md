# Gestionnaire de mots de passe

Application desktop de gestionnaire de mots de passe, développée en Python avec [Flet](https://flet.dev/). Les identifiants et mots de passe sont chiffrés localement ; seul un mot de passe maître permet d’ouvrir le coffre.

## Fonctionnalités

- **Mot de passe maître** — création du coffre à la première utilisation, puis connexion sécurisée
- **Chiffrement** — sites, identifiants et mots de passe chiffrés avec Fernet (clé PBKDF2-SHA256, 600 000 itérations + sel)
- **Gestion des comptes** — ajouter, modifier (double-clic sur une carte), supprimer
- **Recherche intelligente** — filtrage en temps réel avec score (correspondance exacte, préfixe, sous-chaîne), accents ignorés
- **Générateur de mot de passe** — création aléatoire lors de l’ajout ou de la modification
- **Copie rapide** — copie temporaire dans le presse-papiers (effacement automatique)
- **Verrouillage** — déconnexion automatique après inactivité, bouton Verrouiller
- **Intégrité** — détection de modification du coffre, restauration depuis sauvegarde
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
| [PyInstaller](https://pyinstaller.org/) | Compilation en exécutable Windows (optionnel) |

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
│   ├── crypto.py            # Chiffrement et hash du mot de passe maître
│   ├── stockage.py          # Persistance JSON
│   ├── paths.py             # Chemins (projet, .exe, bundle PyInstaller)
│   ├── generateur.py        # Génération de mots de passe
│   ├── recherche.py         # Normalisation et score de recherche
│   └── theme.py             # Couleurs, tailles, constantes UI
└── data/                    # Données locales (ignoré par Git)
    └── coffre.json
```

## Prérequis

- **Python 3.10+** recommandé (testé avec Flet 0.85)
- Windows, macOS ou Linux (exécutable `.exe` : Windows uniquement)

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

## Lancement (Python)

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

## Exécutable Windows (.exe)

Pour générer l’application en fichier unique :

```bash
pip install pyinstaller
pyinstaller PasswordManager.spec
```

L’exécutable est créé dans `dist/PasswordManager.exe`.

### Où sont stockées les données ?

| Mode | Emplacement de `coffre.json` |
|------|------------------------------|
| Python (`main.py`) | `data/coffre.json` à la racine du projet |
| `.exe` PyInstaller | `data/coffre.json` **à côté de** `PasswordManager.exe` |

Le dossier `data/` est créé automatiquement au premier lancement. Les polices et le logo sont lus depuis le bundle PyInstaller (`assets` inclus via le fichier `.spec`).

> **Important :** ne supprimez pas le dossier `data/` à côté de l’`.exe` si vous souhaitez conserver vos mots de passe.

## Sécurité et données

- Le mot de passe maître n’est **jamais** stocké en clair : dérivation PBKDF2-SHA256 (600 000 itérations) avec sel unique.
- Les comptes (site, identifiant, mot de passe) sont chiffrés dans `coffre.json` (dossier `data/` masqué sous Windows, **exclu de Git**).
- Sauvegardes automatiques dans `data/backups/`, contrôle d’intégrité au démarrage.
- Verrouillage après 10 min d’inactivité ; limitation des tentatives de connexion.
- **Sans le mot de passe maître, les données ne sont pas récupérables.** Minimum 12 caractères à la création.
- Ne partagez pas `data/` sur un dépôt public. Les coffres v1 (ancien SHA-256) sont migrés automatiquement à la première connexion.