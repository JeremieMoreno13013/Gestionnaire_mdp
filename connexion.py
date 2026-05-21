import flet as ft
from utils.theme import *
from utils.crypto import valider_force_mdp_maitre
from utils.stockage import (
    initialiser_coffre,
    configurer_mdp_maitre,
    verifier_mdp_maitre,
)
from utils.paths import chemin_asset
from utils.protection import (
    verifier_integrite,
    restaurer_dernier_backup,
    lister_backups,
)
from utils.connexion_securite import (
    connexion_bloquee,
    delai_restant_connexion,
    enregistrer_echec_connexion,
    reinitialiser_echecs_connexion,
)
import os

def _construire_interface(page: ft.Page, premiere_fois: bool):
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
            color=LOGO_COULEUR,
        )

    titre = ft.Text(
        APP_NOM,
        size=TAILLE_TITRE,
        weight=ft.FontWeight.BOLD,
        color=TEXTE_PRINCIPAL,
        text_align=ft.TextAlign.CENTER,
    )

    sous_titre = ft.Text(
        "Créer votre coffre" if premiere_fois else "Accéder à votre coffre",
        size=TAILLE_SOUS_TITRE,
        color=TEXTE_SECONDAIRE,
        text_align=ft.TextAlign.CENTER,
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
        text_align=ft.TextAlign.CENTER,
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
        if connexion_bloquee():
            secondes = int(delai_restant_connexion()) + 1
            afficher_erreur(f"Trop de tentatives. Réessayez dans {secondes} s.")
            return

        mdp = champ_mdp.value.strip()

        if not mdp:
            afficher_erreur("Veuillez entrer votre mot de passe maître")
            return

        if premiere_fois:
            ok, msg = valider_force_mdp_maitre(mdp)
            if not ok:
                afficher_erreur(msg)
                return

            confirm = champ_confirm.value.strip()
            if not confirm:
                afficher_erreur("Veuillez confirmer votre mot de passe maître")
                return
            if mdp != confirm:
                champ_confirm.value = ""
                afficher_erreur("Les mots de passe ne correspondent pas")
                return

            cle = configurer_mdp_maitre(mdp)
            reinitialiser_echecs_connexion()
            ouvrir_gestionnaire(cle)
        else:
            valide, cle = verifier_mdp_maitre(mdp)
            if valide and cle is not None:
                reinitialiser_echecs_connexion()
                ouvrir_gestionnaire(cle)
            else:
                enregistrer_echec_connexion()
                champ_mdp.value = ""
                if connexion_bloquee():
                    secondes = int(delai_restant_connexion()) + 1
                    afficher_erreur(f"Mot de passe incorrect. Pause de {secondes} s.")
                else:
                    afficher_erreur("Mot de passe incorrect")

    bouton = ft.ElevatedButton(
        "Créer mon coffre" if premiere_fois else "Connexion",
        width=300,
        height=45,
        color=TEXTE_PRINCIPAL,
        bgcolor=COULEUR_PRIMAIRE,
        on_click=valider,
    )

    champ_mdp.on_submit = valider
    champ_confirm.on_submit = valider

    elements = [logo, titre, sous_titre, champ_mdp]
    if premiere_fois:
        elements.append(champ_confirm)

    elements.extend([bouton, message])

    if premiere_fois:
        elements.append(
            ft.Text(
                f"Choisissez un mot de passe maître fort ({MDP_MAITRE_MIN} caractères min.). "
                "Il est impossible de le récupérer.",
                size=TAILLE_NORMAL,
                color=TEXTE_TERTIAIRE,
                text_align=ft.TextAlign.CENTER,
                width=300,
            )
        )

    page.add(
        ft.Column(
            elements,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )

def _demarrer_apres_integrite(page: ft.Page):
    premiere_fois = initialiser_coffre()
    page.clean()
    _construire_interface(page, premiere_fois)

def _dialogue_integrite(page: ft.Page, statut: str):
    backups = lister_backups()
    peut_restaurer = bool(backups)

    if statut == "modifie":
        titre = "Fichier modifié"
        texte = (
            "Le coffre a été modifié en dehors de l'application. "
            "Restauration depuis la dernière sauvegarde recommandée."
        )
    else:
        titre = "Coffre endommagé"
        texte = (
            "Le fichier coffre.json semble corrompu. "
            "Vous pouvez tenter une restauration depuis une sauvegarde."
        )

    message = ft.Text(texte, size=TAILLE_PETIT, color=TEXTE_SECONDAIRE)

    def continuer_sans_restaurer(e):
        dlg.open = False
        page.update()
        _demarrer_apres_integrite(page)

    def restaurer(e):
        if restaurer_dernier_backup():
            dlg.open = False
            page.update()
            _demarrer_apres_integrite(page)
        else:
            message.value = "Échec de la restauration."
            message.color = COULEUR_DANGER
            page.update()

    actions = [ft.TextButton("Continuer sans restaurer", on_click=continuer_sans_restaurer)]
    if peut_restaurer:
        actions.insert(
            0,
            ft.ElevatedButton(
                "Restaurer la sauvegarde",
                bgcolor=COULEUR_PRIMAIRE,
                color=TEXTE_PRINCIPAL,
                on_click=restaurer,
            ),
        )
    else:
        message.value = texte + " Aucune sauvegarde disponible."
        actions = [
            ft.ElevatedButton(
                "Continuer",
                bgcolor=COULEUR_PRIMAIRE,
                color=TEXTE_PRINCIPAL,
                on_click=continuer_sans_restaurer,
            )
        ]

    dlg = ft.AlertDialog(
        title=ft.Text(titre, color=COULEUR_DANGER),
        content=message,
        actions=actions,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()

def page_connexion(page: ft.Page):
    page.title = APP_NOM
    page.bgcolor = FOND_PAGE
    page.window.width = FENETRE_LARGEUR_CONNEXION
    page.window.height = FENETRE_HAUTEUR_CONNEXION
    page.window.resizable = False
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    statut = verifier_integrite()
    if statut in ("modifie", "corrompu"):
        _dialogue_integrite(page, statut)
        return

    _demarrer_apres_integrite(page)
