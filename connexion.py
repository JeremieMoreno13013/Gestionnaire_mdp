import tkinter as tk
from utils.crypto import hasher_mdp_maitre, generer_cle
from utils.stockage import initialiser_coffre, recuperer_mdp_maitre, sauvegarder_mdp_maitre

class FenetreConnexion:
    def __init__(self):
        # Initialiser le coffre (crée le fichier si besoin)
        self.premiere_connexion = initialiser_coffre()
        
        # Créer la fenêtre principale
        self.fenetre = tk.Tk()
        self.fenetre.title("Gestionnaire de mots de passe - Connexion")
        self.fenetre.geometry("400x500")
        self.fenetre.resizable(False, False)
        self.fenetre.configure(bg="#f0f0f0")
        
        # Centre la fenêtre
        self.centrer_fenetre(400, 500)

        # Construis l'interface
        self.creer_widgets()

        #La clé de chiffrement (sera définie après connexion)
        self.cle = None

    def centrer_fenetre(self, largeur, hauteur):
        """Centre la fenêtre sur l'écran"""
        ecran_largeur = self.fenetre.winfo_screenwidth()
        ecran_hauteur = self.fenetre.winfo_screenheight()
        pos_x = (ecran_largeur - largeur) // 2
        pos_y = (ecran_hauteur - hauteur) // 2
        self.fenetre.geometry(f"{largeur}x{hauteur}+{pos_x}+{pos_y}")

    def creer_widgets(self):
        """Crée les éléments visuels de la fenêtre"""
        # LOGO + TITRE
        cadre_titre = tk.Frame(self.fenetre, bg="#f0f0f0")
        cadre_titre.pack(pady=40)

        tk.Label(
            cadre_titre,
            text="🔐",
            font=("Arial", 50),
            bg="#1a1a2e"
        ).pack()

        tk.Label(
            cadre_titre,
            text="Gestionnaire de mot de passe",
            font=("Arial", 18, "bold"),
            bg="#1a1a2e",
            fg="#ffffff"
        ).pack()

        tk.Label(
            cadre_titre,
            text="Créer votre coffre" if self.premiere_connexion else "Se connecter",
            font=("Arial", 10),
            bg="#1a1a2e",
            fg="#ffffff"
        ).pack(pady=5)

        # === FORMULAIRE ===
        cadre_formulaire = tk.Frame(self.fenetre, bg="#f0f0f0")
        cadre_formulaire.pack(pady=10, padx=40, fill="x")

        # Label pour le mot de passe maître
        tk.Label(
            cadre_formulaire,
            text="Mot de passe maître :",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#1a1a2e",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        # Champ pour le mot de passe maître
        self.champ_mdp = tk.Entry(
            cadre_formulaire,
            font=("Arial", 12),
            show="*",
            bg="#ffffff",
            fg="#1a1a2e",
            bd=2,
            relief="solid",
            insertbackground="#1a1a2e"
        )
        self.champ_mdp.pack(fill="x", ipady=5)
        self.champ_mdp.focus() #focus automatique sur le champ
        self.champ_mdp.bind("<Return>", lambda e: self.valider_connexion())

        # Case afficher/cacher mdp
        self.afficher_mdp = tk.BooleanVar()
        tk.Checkbutton(
            cadre_formulaire,
            text="Afficher le mot de passe",
            font=("Arial",10),
            bg="#f0f0f0",
            fg="#1a1a2e",
            selectcolor="#f0f0f0",
            variable=self.afficher_mdp,
            command=self.toggle_mdp,
            activebackground="#f0f0f0",
            activeforeground="#1a1a2e"
        ).pack(anchor="w", pady=(5,0))

        #Bouton Valider
        self.bouton_valider = tk.Button(
            cadre_formulaire,
            text="Créer mon coffre" if self.premiere_connexion else "Se connecter",
            font=("Arial", 12, "bold"),
            bg="#e94560",
            fg="white",
            activebackground="#1a1a2e",
            activeforeground="#ffffff",
            cursor="hand2",
            bd=0,
            relief="flat",
            padx=20,
            pady=10,
            command=self.valider_connexion
        )
        self.bouton_valider.pack(fill="x", pady=(20, 10), ipady=10)

        # Effet survol
        self.bouton_valider.bind("<Enter>", lambda e: self.bouton_valider.config(bg="#1a1a2e"))
        self.bouton_valider.bind("<Leave>", lambda e: self.bouton_valider.config(bg="#e94560"))

        # Message d'erreur/info
        self.label_message = tk.Label(
            cadre_formulaire,
            text="⚠️ Choisissez bien votre mot de passe,\nil est impossible à récupérer !" if self.premiere_connexion else "",
            font=("Arial",10),
            fg="#a8a8b3",
            bg="#1a1a2e",
            justify="center",
        )
        self.label_message.pack(pady=(15, 0))           
        
    def toggle_mdp(self):
        """Affiche ou cache le mot de passe"""
        self.champ_mdp.config(show="" if self.afficher_mdp.get() else "*")

    def valider_connexion(self):
        """Valide le mot de passe maitre et ouvre le coffre ou affiche une erreur"""
        mdp = self.champ_mdp.get()
        if not mdp:
            self.afficher_erreur("⚠️ Entre ton mot de passe maître !")
            return
        if len(mdp) < 6:
            self.afficher_erreur("⚠️ Le mot de passe doit contenir au moins 6 caractères.")
            return
        
        # === PREMIERE FOIS : création ===
        if self.premiere_connexion:
            # Génération des clés de chiffrement
            sauvegarder_mdp_maitre(hasher_mdp_maitre(mdp))
            self.cle = generer_cle(mdp)
            self.ouvrir_gestionnaire()

        # === CONNEXION NORMALE : vérification ===
        else:
            hash_stocke = recuperer_mdp_maitre()
            hash_saisi = hasher_mdp_maitre(mdp)

            if hash_saisi == hash_stocke:
                self.cle = generer_cle(mdp)
                self.ouvrir_gestionnaire()
            else:
                self.afficher_erreur("⚠️ Mot de passe incorrect. Réessayez.")
                self.champ_mdp.delete(0, tk.END)
                self.champ_mdp.focus()

    def afficher_erreur(self, message: str):
        """Affiche un message d'erreur"""
        self.label_message.config(text=message, fg="#e94560")

    def ouvrir_gestionnaire(self):
        """Ferme la fenêtre de connexion et ouvre le gestionnaire"""
        self.fenetre.destroy()

        from gestionnaire import FenetreGestionnaire
        gestionnaire = FenetreGestionnaire(self.cle)
        gestionnaire.lancer_app()

    def lancer_app(self):
        """Lance l'application"""
        self.fenetre.mainloop()
    

        
            
        