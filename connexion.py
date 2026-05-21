import flet as ft
from utils.theme import *
from utils.crypto import hasher_mdp_maitre, generer_cle
from utils.stockage import initialiser_coffre, sauvegarder_mdp_maitre, recuperer_mdp_maitre
from utils.paths import chemin_asset
import os

def page_connexion(page: ft.Page):
    page.title = APP_NOM
    page.bgcolor = FOND_PAGE
    page.window.width = FENETRE_LARGEUR_CONNEXION
    page.window.height = FENETRE_HAUTEUR_CONNEXION
    page.window.resizable = False
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    premiere_fois = initialiser_coffre()

    chemin_logo = chemin_asset("logo.png")

    if os.path.exists(chemin_logo):
        logo = ft.Image(
            src=chemin_logo,
            width=LOGO_CONNEXION_LARGEUR,
            height=LOGO_CONNEXION_HAUTEUR,
        )
    else:
        logo = ft.Icon(
            ft.Icons.LOCK,
            size=LOGO_CONNEXION_LARGEUR,
            color=LOGO_COULEUR
        )

    titre = ft.Text(
        APP_NOM,
        size=TAILLE_TITRE,
        weight=ft.FontWeight.BOLD,
        color=TEXTE_PRINCIPAL,
        text_align=ft.TextAlign.CENTER
    )

    sous_titre = ft.Text(
        "Créer votre coffre" if premiere_fois else "Accéder à votre coffre",
        size=TAILLE_SOUS_TITRE,
        color=TEXTE_SECONDAIRE,
        text_align=ft.TextAlign.CENTER
    )

    def champ_connexion(label: str) -> ft.TextField:
        return ft.TextField(
            label=label,
            password=True,
            can_reveal_password=True,
            border_radius=ARRONDI_CHAMP,
            prefix_icon=ft.Icons.KEY,
            width=300,
            filled=True,
            bgcolor=FOND_CARTE,
            color=TEXTE_PRINCIPAL,
            border_color=TEXTE_TERTIAIRE,
            label_style=ft.TextStyle(color=TEXTE_SECONDAIRE),
        )

    champ_mdp = champ_connexion("Mot de passe maître")
    champ_confirm = champ_connexion("Confirmer le mot de passe maître")
    champ_confirm.visible = premiere_fois

    message = ft.Text(
        "",
        size=TAILLE_PETIT,
        color=COULEUR_DANGER,
        text_align=ft.TextAlign.CENTER
    )

    def afficher_erreur(texte: str):
        message.value = texte
        message.color = COULEUR_DANGER
        page.update()

    def ouvrir_gestionnaire(cle):
        page.clean()
        from gestionnaire import page_gestionnaire
        page_gestionnaire(page, cle)

    def valider(e):
        mdp = champ_mdp.value.strip()

        if not mdp:
            afficher_erreur("Veuillez entrer votre mot de passe maître")
            return

        if len(mdp) < 6:
            afficher_erreur("6 caractères minimum")
            return
        
        if premiere_fois:
            confirm = champ_confirm.value.strip()

            if not confirm:
                afficher_erreur("Veuillez confirmer votre mot de passe maître")
                return
            
            if mdp != confirm:
                champ_confirm.value=""
                afficher_erreur("Les mots de passe ne correspondent pas")
                return

            sauvegarder_mdp_maitre(hasher_mdp_maitre(mdp))
            cle = generer_cle(mdp)
            ouvrir_gestionnaire(cle)
        else:
            if hasher_mdp_maitre(mdp) == recuperer_mdp_maitre():
                cle = generer_cle(mdp)
                ouvrir_gestionnaire(cle)
            else:
                champ_mdp.value = ""
                afficher_erreur("Mot de passe incorrect")

    bouton = ft.ElevatedButton(
        "Créer mon coffre" if premiere_fois else "Connexion",
        width=300,
        height=45,
        color=TEXTE_PRINCIPAL,
        bgcolor=COULEUR_PRIMAIRE,
        on_click=valider
    )

    champ_mdp.on_submit = valider
    champ_confirm.on_submit = valider

    elements = [
        logo,
        titre,
        sous_titre,
        champ_mdp,
    ]

    if premiere_fois:
        elements.append(champ_confirm)
    
    elements.extend([
        bouton,
        message,
    ])
    
    if premiere_fois:
        elements.append(
            ft.Text(
                "Choisissez bien votre mot de passe maître, il est impossible de le récupérer !",
                size=TAILLE_NORMAL,
                color=TEXTE_TERTIAIRE,
                text_align=ft.TextAlign.CENTER,
                width=300
            )
        )

    page.add(
        ft.Column(
            elements,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    )
            
        