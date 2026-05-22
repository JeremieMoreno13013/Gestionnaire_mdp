# Gestionnaire de mots de passe

Application desktop locale de gestion de mots de passe : chiffrement bout en bout, interface Flet, packaging Windows (exe + installeur). Projet personnel démontrant le développement Python orienté sécurité et produit.

## Aperçu

L’utilisateur crée un coffre protégé par un mot de passe maître, puis gère ses comptes (site, identifiant, mot de passe) dans une interface sobre. Aucune donnée sensible n’est stockée en clair ; tout reste sur la machine de l’utilisateur.

## Compétences mises en avant

| Domaine | Réalisation |
|---------|-------------|
| **Sécurité** | PBKDF2-SHA256 (600 k itérations), Fernet, sel unique, limitation des tentatives de connexion, contrôle d’intégrité, sauvegardes rotatives |
| **Desktop Python** | UI Flet (async), fenêtrage, icônes, gestion des transitions connexion ↔ gestionnaire |
| **Architecture** | Séparation `connexion` / `gestionnaire` / `utils`, chemins adaptés dev / exe / installation |
| **Packaging Windows** | `flet pack` (PyInstaller), métadonnées exe, client Flet embarqué, Inno Setup 6 |
| **Qualité** | Typage (Pyright), venv projet, scripts de build reproductibles |

## Stack technique

- **Python 3.10+** · **Flet 0.85** · **cryptography** (Fernet) · **Pillow** · **pyperclip**
- **PyInstaller** via `flet pack` · **Inno Setup** (installeur)
- Cible principale : **Windows** (dev possible sur Linux/macOS)

## Fonctionnalités livrées

- Création et connexion au coffre (mot de passe maître fort, 12 caractères min.)
- CRUD comptes avec recherche floue (scores, normalisation accents)
- Générateur de mots de passe, copie presse-papiers à durée limitée
- Verrouillage automatique (inactivité) et manuel
- Détection d’altération du fichier coffre + restauration backup
- Réinitialisation complète avec garde-fous (`RESET TOTAL`, délai)
- Thème UI cohérent (constantes centralisées, polices embarquées)

## Architecture

```
main.py
   └── connexion.py          # Auth, intégrité, premier lancement
           └── gestionnaire.py   # UI principale, async (surveillance session)

utils/
   crypto.py          # Dérivation clé, chiffrement, migration v1 → v2
   stockage.py        # JSON atomique, coffre structuré
   paths.py           # Résolution chemins selon contexte d’exécution
   protection.py      # Backups, hash d’intégrité, attributs Windows
   fenetre.py         # Dimensions, centrage natif Windows
   win_taskbar.py     # AppUserModelID, client Flet embarqué (exe packagé)
   connexion_securite.py
   recherche.py · generateur.py · presse_papiers.py · theme.py
```

**Choix notables**

- **Données hors Program Files** : si l’app est installée sous `Program Files`, le coffre est redirigé vers `%LOCALAPPDATA%` (écriture utilisateur sans admin).
- **Exe autonome** : le client Flet est extrait du bundle PyInstaller (`.flet_runtime/`), pas le cache global `~/.flet`, pour un comportement reproductible en production.
- **UI non bloquante** : transitions de fenêtre et chargement via `page.run_task` + `async` (Flet).

## Sécurité (résumé)

- Mot de passe maître : hash PBKDF2, jamais persisté en clair
- Payload comptes : chiffré Fernet avec clé dérivée du maître
- Sauvegardes dans `data/backups/`, vérification au démarrage
- Dossier `data/` exclu de Git et masqué sous Windows

## Démarrage rapide (développeurs)

```bash
git clone <url-du-repo>
cd Gestionnaire_mdp
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt "flet[all]>=0.85.0"
py main.py
```

Rechargement à chaud : `flet run -r main.py`

## Build release (Windows)

| Script | Sortie |
|--------|--------|
| `scripts\build_windows.bat` | `dist\GestionnaireMotsDePasse.exe` (portable) |
| `scripts\build_installer.bat` | `dist\GestionnaireMotsDePasse-Setup.exe` (Inno Setup 6 requis) |

Icône : `py scripts\generer_logo_ico.py` (intégré aux scripts de build).

## Structure du dépôt

```
├── main.py · connexion.py · gestionnaire.py
├── assets/          # Polices, logo.ico / logo.png
├── installer/       # GestionnaireMotsDePasse.iss
├── scripts/         # Build & génération icône
└── utils/           # Logique métier et plateforme
```