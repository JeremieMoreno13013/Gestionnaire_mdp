import tkinter as tk
from tkinter import ttk, messagebox
from utils.crypto import chiffrer, dechiffrer
from utils.stockage import ajouter_compte_data, recuperer_comptes, supprimer_donnees_compte, site_existe


def creer_champ(parent, texte, secret=False):
    """Crée un label + un champ de saisie et retourne le champ"""

    tk.Label(
        parent,
        text=texte,
        font=("Arial", 11),
        fg="#a8a8b3",
        bg="#1a1a2e",
        anchor="w"
    ).pack(fill="x", pady=(10, 3))

    frame_champ = tk.Frame(parent, bg="#1a1a2e")
    frame_champ.pack(fill="x")

    champ = tk.Entry(
        frame_champ,
        font=("Arial", 10),
        bd=8,
        fg="white",
        bg="#16213e",
        insertbackground="white",
        relief="flat",
        show="*" if secret else ""
    )
    champ.pack(side="left",fill="x", expand=True, ipady=5)

    if secret:
        champ.visible = False

        def toggle():
            if champ.visible:
                champ.config(show="*")
                btn_revealer.config(text="👁️")
                champ.visible = False
            else:
                champ.config(show="")
                btn_revealer.config(text="🙈")
                champ.visible = True
        btn_revealer = tk.Button(
            frame_champ,
            text="👁️",
            bg="#2e7d32",
            fg="white",
            bd=0,
            cursor="hand2",
            command=toggle
        )
        btn_revealer.pack(side="right", padx=(5, 0))

    return champ

class FenetreGestionnaire:
    def __init__(self, cle):
        self.cle = cle
        self.fenetre = tk.Tk()
        self.fenetre.title("Gestionnaire de mot de passe")
        self.fenetre.geometry("700x500")
        self.fenetre.configure(bg="#1a1ae2")

        self.creer_widgets()
        self.charger_comptes()

    def creer_widgets(self):
        # === BARRE DU HAUT ===
        frame_haut = tk.Frame(
            self.fenetre,
            bg="#16213e",
            pady=15
        )
        frame_haut.pack(fill="x")
        
        tk.Label(
            frame_haut,
            text="Gestionnaire de mot de passe",
            font=("Helvetica", 16, "bold"),
            bg="#16213e",
            fg="white"
        ).pack()

        # === BARRE DE RECHERCHE ===
        frame_recherche = tk.Frame(
            self.fenetre,
            bg="#1a1ae2",
            pady=10
        )
        frame_recherche.pack(fill="x", padx=20)

        self.champ_recherche = tk.Entry(
            frame_recherche,
            font=("Helvetica", 12),
            bg="#16213e",
            fg="white",
            insertbackground="white",
            bd=8,
            relief="flat"
        )
        self.champ_recherche.pack(fill="x", ipady=5)
        self.champ_recherche.bind("<KeyRelease>", self.rechercher_comptes)

        # === LISTE DES COMPTES ===
        frame_liste = tk.Frame(self.fenetre, bg="#1a1a2e")
        frame_liste.pack(fill="both", expand=True, padx=20, pady=10)

        # Définir les colonnes
        colonnes = ("site", "identifiant", "mot_de_passe", "copier")

        self.tableau = ttk.Treeview(
            frame_liste,
            columns=colonnes,
            show="headings",
            height=10
        )

        # Nommer les colonnes
        self.tableau.heading("site", text="🌐 Site")
        self.tableau.heading("identifiant", text="👤 Identifiant")
        self.tableau.heading("mot_de_passe", text="🔐 Mot de passe")
        self.tableau.heading("copier", text="")

        # Définir la largeur
        self.tableau.column("site", width=200, anchor="center")
        self.tableau.column("identifiant", width=200, anchor="center")
        self.tableau.column("mot_de_passe", width=200, anchor="center")
        self.tableau.column("copier", width=50, anchor="center")

        self.tableau.pack(fill="both", expand=True)
        self.tableau.bind("<ButtonRelease-1>", self.clic_tableau)
        self.tableau.bind("<Double-1>", self.modifier_compte)

        # === BARRE DU BAS (BOUTONS) ===
        frame_bas = tk.Frame(self.fenetre, bg="#1a1a2e", pady=10)
        frame_bas.pack(fill="x", padx=20)

        # Bouton Ajouter
        self.btn_ajouter = tk.Button(
            frame_bas,
            text="➕ Ajouter un compte",
            font=("Helvetica", 12, "bold"),
            bg="#16213e",
            fg="white",
            bd=0,
            cursor="hand2",
            command=self.ajouter_compte
        )
        self.btn_ajouter.pack(side="left", ipadx=15, ipady=5)

        # Bouton Supprimer
        self.btn_supprimer = tk.Button(
            frame_bas,
            text="❌ Supprimer",
            font=("Helvetica", 12, "bold"),
            bg="#e53935",
            fg="white",
            bd=0,
            cursor="hand2",
            command=self.supprimer_compte
        )
        self.btn_supprimer.pack(side="right", ipadx=15, ipady=5)

    def ajouter_compte(self):
        """Ouvre la fenêtre pour ajouter un compte"""
        
        # Créer la popup
        self.popup = tk.Toplevel(self.fenetre)
        self.popup.title("Ajouter un compte")
        self.popup.geometry("400x400")
        self.popup.resizable(False, False)
        self.popup.configure(bg="#1a1ae2")
        
        # Empêche de cliquer sur la fenêtre principale
        self.popup.grab_set()
        self.popup.focus_set()

        # Titre de la popup
        tk.Label(
            self.popup,
            text="Ajouter un compte",
            font=("Arial", 14, "bold"),
            bg="#1a1ae2",
            fg="white"
        ).pack(pady=(15, 0))

        # Formulaire
        frame_form = tk.Frame(self.popup, bg="#1a1a2e")
        frame_form.pack(fill="x", padx=30)

        self.champ_site = creer_champ(frame_form, "🌐 Site")
        self.champ_identifiant = creer_champ(frame_form, "👤 Identifiant")
        self.champ_mot_de_passe = creer_champ(frame_form, "🔐 Mot de passe", secret=True)

        # Bouton Sauvegarder
        btn_sauvegarder = tk.Button(
            self.popup,
            text="💾 Sauvegarder",
            font=("Arial", 12, "bold"),
            bg="#2e7d32",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.sauvegarder_compte
        )
        btn_sauvegarder.pack(pady=20, ipadx=20, ipady=8)

    def sauvegarder_compte(self):
        """Chiffre et Sauvegarde le compte"""
        
        # Récupérer les valeurs
        site = self.champ_site.get().strip().lower()
        identifiant = self.champ_identifiant.get().strip()
        mot_de_passe = self.champ_mot_de_passe.get().strip()

        #Vérifier que tout est rempli
        if not site or not identifiant or not mot_de_passe:
            messagebox.showwarning("Attention", "Remplis tous les champs !")
            return 

        # Vérifier si le site existe déjà
        if site_existe(site):
            messagebox.showwarning("Attention", "Ce site existe déjà")
            return

        # Chiffrer les infos
        identifiant_chiffre = chiffrer(identifiant, self.cle)
        mot_de_passe_chiffre = chiffrer(mot_de_passe, self.cle)

        # Sauvegarder
        ajouter_compte_data(site, identifiant_chiffre, mot_de_passe_chiffre)

        # Recharger la liste
        self.charger_comptes()

        # Fermer la popup
        self.popup.destroy()

        messagebox.showinfo("Succès", f"Compte pour '{site}' ajouté !")

    def charger_comptes(self):
        """Charge et affiche tous les comptes"""
        
        # Effacer le contenu actuel du tableau
        for item in self.tableau.get_children():
            self.tableau.delete(item)

        # Récupérer tous les comptes
        comptes = recuperer_comptes()

        # Remplir le tableau
        for site, data in comptes.items():
            identifiant = dechiffrer(data["identifiant"], self.cle)
            self.tableau.insert("", "end", values=(site, identifiant, "********", "📋"))
        

    def supprimer_compte(self):
        """Supprime le compte sélectionné dasn le tableau"""
        
        # 1. Récupérer le site sélectionné
        selection = self.tableau.selection()
        if not selection:
            messagebox.showwarning(
                "Attention",
                "Veuillez sélectionner un compte à supprimer."
            )
            return

        # 2. Obtenir le site
        site = self.tableau.item(selection[0])["values"][0]

        # 3. Confirmer
        if messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer {site} ?"
        ):
            
            # 4. Supprimer
            supprimer_donnees_compte(site)
            self.charger_comptes()
            messagebox.showinfo(
                "Succès",
                f"Compte '{site}' supprimé avec succès"
            )
        else:
            messagebox.showinfo(
                "Annulé",
                "Suppression annulée."
            )

    def rechercher_comptes(self, event=None):
        """Recherche les comptes en fonction du texte entré"""
        
        # Récupérer le texte recherché
        terme = self.champ_recherche.get().strip().lower()

        # Si le terme est vide, afficher tous les comptes
        if not terme:
            self.charger_comptes()
            return

        # Vider le tableau
        for item in self.tableau.get_children():
            self.tableau.delete(item)

        # Récupérer tous les comptes
        comptes = recuperer_comptes()

        # Remplir le tableau avec les comptes correspondants
        for site, data in comptes.items():
            identifiant = dechiffrer(data["identifiant"], self.cle)
            if terme in site.lower() or terme in identifiant.lower():
                self.tableau.insert("", "end", values=(site, identifiant, "********", "📋"))

    def copier_mdp(self):
        """Copie le mot de passe sélectionné dans le presse-papiers"""
        
        # 1. Récupérer le site sélectionné
        selection = self.tableau.selection()
        if not selection:
            return

        # 2. Obtenir le site
        site = self.tableau.item(selection[0])["values"][0]

        # 3. Récupérer les données du compte
        comptes = recuperer_comptes()
        mot_de_passe = dechiffrer(comptes[site]["mot_de_passe"], self.cle)

        # 4. Copier le mot de passe dans le presse-papiers
        self.fenetre.clipboard_clear()
        self.fenetre.clipboard_append(mot_de_passe)
        
        # 5. Changer le texte temporairement
        self.tableau.set(selection[0], "copier", "✅")
        self.fenetre.after(2000, lambda: self.tableau.set(selection[0], "copier", "📋"))

    def clic_tableau(self, event):
        """Gère les clics dans le tableau"""
        
        # Récupérer la colonne cliquée
        colonne = self.tableau.identify_column(event.x)
        
        # Si la colonne "#4" (copier mdp) est cliquée
        if colonne == "#4":
            self.copier_mdp()

    def modifier_compte(self, event=None):
        """Modifie un compte existant"""
        
        # 1. Récupérer le site sélectionné
        selection = self.tableau.selection()
        if not selection:
            return

        # 2. Obtenir le site
        site = self.tableau.item(selection[0])["values"][0]

        # 3. Récupérer les données du compte
        comptes = recuperer_comptes()
        identifiant = dechiffrer(comptes[site]["identifiant"], self.cle)
        mot_de_passe = dechiffrer(comptes[site]["mot_de_passe"], self.cle)

        # 4. Ouvrir la popup
        self.popup = tk.Toplevel(self.fenetre)
        self.popup.title("Modifier le compte")
        self.popup.geometry("400x400")
        self.popup.resizable(False, False)
        self.popup.configure(bg="#1a1ae2")
        self.popup.grab_set()
        self.popup.focus_set()

        # 5. Titre de la popup
        tk.Label(
            self.popup,
            text="Modifier le compte",
            font=("Arial", 14, "bold"),
            bg="#1a1ae2",
            fg="white"
        ).pack(pady=(15, 0))

        # 6. Formulaire
        frame_form = tk.Frame(self.popup, bg="#1a1a2e")
        frame_form.pack(fill="x", padx=30)

        self.champ_site = creer_champ(frame_form, "🌐 Site")
        self.champ_identifiant = creer_champ(frame_form, "👤 Identifiant")
        self.champ_mot_de_passe = creer_champ(frame_form, "🔐 Mot de passe", secret=True)

        # Remplir avec les données actuelles
        self.champ_site.insert(0, site)
        self.champ_identifiant.insert(0, identifiant)
        self.champ_mot_de_passe.insert(0, mot_de_passe)

        # 7. Bouton Sauvegarder
        btn_sauvegarder = tk.Button(
            self.popup,
            text="💾 Sauvegarder",
            font=("Arial", 12, "bold"),
            bg="#2e7d32",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=lambda: self.sauvegarder_modification(site)
        )
        btn_sauvegarder.pack(pady=20, ipadx=20, ipady=8)

    def sauvegarder_modification(self, site_original):
        """Sauvegarde la modification du compte"""
        
        # Récupérer les nouvelles valeurs
        site = self.champ_site.get().strip().lower()
        identifiant = self.champ_identifiant.get().strip()
        mot_de_passe = self.champ_mot_de_passe.get().strip()

        # Vérifier que tout est rempli
        if not site or not identifiant or not mot_de_passe:
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs")
            return

        # Si le site a changé, vérifier qu'il n'existe pas déjà
        if site != site_original and site_existe(site):
            messagebox.showwarning("Attention", "Ce site existe déjà")
            return

        # Supprimer l'ancien compte si le site a changé
        if site != site_original:
            supprimer_donnees_compte(site_original)

        # Chiffrer les nouvelles infos
        identifiant_chiffre = chiffrer(identifiant, self.cle)
        mot_de_passe_chiffre = chiffrer(mot_de_passe, self.cle)

        # Ajouter ou mettre à jour le compte
        ajouter_compte_data(site, identifiant_chiffre, mot_de_passe_chiffre)

        # Recharger la liste
        self.charger_comptes()

        # Fermer la popup
        self.popup.destroy()

        messagebox.showinfo("Succès", f"Compte '{site}' modifié !")

    def lancer_app(self):
        """Lance l'application"""
        self.fenetre.mainloop()
        