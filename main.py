from connexion import FenetreConnexion
import sys
import os

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

if __name__ == "__main__":
    app = FenetreConnexion()
    app.lancer_app()
