import time
import asyncio
import flet as ft
from utils.crypto import chiffrer
from utils.stockage import (
    ajouter_compte_data,
    recuperer_comptes,
    supprimer_donnees_compte,
    compte_existe,
    reset_application,
    generer_cle_compte,
    lire_compte,
)
from utils.generateur import generer_mdp
from utils.presse_papiers import copier_temporaire
import os
from PIL import Image
from utils.theme import *
from utils.recherche import calculer_score
from utils.paths import chemin_asset

def page_gestionnaire(page: ft.Page, cle):
    derniere_activite = [time.time()]
    page.title = APP_NOM
    page.window.width = FENETRE_LARGEUR_GESTIONNAIRE
    page.window.height = FENETRE_HAUTEUR_GESTIONNAIRE
    page.window.resizable = False
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme = ft.Theme(
        font_family=POLICE_PRINCIPALE,
        scrollbar_theme=ft.ScrollbarTheme(
            thickness=SCROLL_EPAISSEUR,
            radius=SCROLL_ARRONDI,
            thumb_color=SCROLL_COULEUR,
        )
    )

    chemin_logo = chemin_asset("logo.png")

    if os.path.exists(chemin_logo):
        logo = ft.Image(
            src=chemin_logo,
            width=LOGO_LARGEUR,
            height=LOGO_HAUTEUR,
        )
    else:
        logo = ft.Icon(ft.Icons.LOCK, color=LOGO_COULEUR, size=LOGO_LARGEUR)

    def afficher_message(texte, couleur=COULEUR_SUCCES):
        page.overlay.clear()
        
        snackbar = ft.SnackBar(
            content=ft.Text(
                texte,
                color=TEXTE_PRINCIPAL,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=couleur,
            duration=3000,
            behavior=ft.SnackBarBehavior.FLOATING,
            shape=ft.RoundedRectangleBorder(radius=ARRONDI_CHAMP),
            margin=ft.Margin(left=20, right=20, bottom=15),
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

    def ouvrir_dialog(dlg):
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def fermer_dialog(dlg):
        dlg.open = False
        page.update()

    def toucher_activite():
        derniere_activite[0] = time.time()

    def verrouiller_session():
        page.overlay.clear()
        page.clean()
        from connexion import page_connexion

        page_connexion(page)

    async def surveillance_verrouillage():
        while True:
            await asyncio.sleep(30)
            if time.time() - derniere_activite[0] >= DELAI_VERROUILLAGE_SEC:
                verrouiller_session()
                break

    page.run_task(surveillance_verrouillage)

    barre_haut = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        logo,
                        ft.Text(
                            "Gestionnaire de mots de passe",
                            size=TAILLE_NORMAL,
                            weight=ft.FontWeight.BOLD,
                            color=TEXTE_PRINCIPAL
                        )
                    ],
                    spacing=10
                ),
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.SETTINGS,
                            icon_color=TEXTE_TERTIAIRE,
                            tooltip="Paramètres",
                            on_click=lambda e: (toucher_activite(), ouvrir_parametres()),
                        ),
                        ft.IconButton(
                            ft.Icons.LOCK,
                            icon_color=TEXTE_TERTIAIRE,
                            tooltip="Verrouiller",
                            on_click=lambda e: (toucher_activite(), verrouiller_session()),
                        ),
                        ft.IconButton(
                            ft.Icons.LOGOUT,
                            icon_color=COULEUR_DANGER,
                            tooltip="Déconnexion",
                            on_click=lambda e: (toucher_activite(), se_deconnecter()),
                        ),
                    ],
                    spacing=0
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=FOND_BARRE,
        padding=ft.Padding(20, 20, 10, 10),
        border_radius=ARRONDI_CHAMP,
    )

    def se_deconnecter():
        verrouiller_session()

    page.add(barre_haut)

    champ_recherche = ft.TextField(
        label="Rechercher un site",
        border_radius=ARRONDI_CHAMP,
        prefix_icon=ft.Icons.SEARCH,
        filled=True,
        bgcolor=FOND_CARTE,
        color=TEXTE_PRINCIPAL,
        border_color=TEXTE_TERTIAIRE,
        label_style=ft.TextStyle(color=TEXTE_SECONDAIRE),
        on_change=lambda e: (toucher_activite(), charger_comptes()),
    )

    btn_ajouter = ft.IconButton(
        ft.Icons.ADD_CIRCLE,
        icon_color=COULEUR_SUCCES,
        tooltip="Ajouter un compte",
        on_click=lambda e: (toucher_activite(), ouvrir_ajout(e)),
    )

    barre_recherche = ft.Row(
        [
            champ_recherche,
            btn_ajouter
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER
    )

    liste_comptes = ft.Column(
        spacing=8,
        expand=True,
        scroll=ft.ScrollMode.ALWAYS
    )

    def charger_comptes():
        toucher_activite()
        liste_comptes.controls.clear()

        comptes = recuperer_comptes()
        recherche = champ_recherche.value.strip().lower() if champ_recherche.value else ""

        resultats = []

        for cle_compte, donnees in comptes.items():
            site, identifiant, _ = lire_compte(donnees, cle)

            if not recherche:
                resultats.append((site, identifiant, cle_compte, 100))
                continue

            score = calculer_score(recherche, site)

            if score > 0:
                resultats.append((site, identifiant, cle_compte, score))

        resultats.sort(key=lambda x: x[3], reverse=True)

        for site, identifiant, cle_compte, score in resultats:
            liste_comptes.controls.append(creer_carte(site, identifiant, cle_compte))

        if len(liste_comptes.controls) == 0:
            liste_comptes.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.SEARCH_OFF, size=50, color=TEXTE_SECONDAIRE),
                            ft.Text(
                                "Aucun compte enregistré" if not recherche else "Aucun résultat",
                                size=TAILLE_NORMAL,
                                color=TEXTE_SECONDAIRE
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10
                    ),
                    padding=40,
                    alignment=ft.Alignment(0, 0)
                )
            )

        page.update()

    def creer_carte(site, identifiant, cle_compte):
        texte_mdp = ft.Text(
            "**********",
            size=TAILLE_CARTE_TEXTE,
            color=TEXTE_SECONDAIRE
        )

        btn_oeil = ft.IconButton(
            ft.Icons.VISIBILITY,
            icon_color=TEXTE_SECONDAIRE,
            tooltip="Afficher le mot de passe",
        )

        def toggle_mdp(e):
            toucher_activite()
            if texte_mdp.value == "**********":
                comptes = recuperer_comptes()
                _, _, mdp_clair = lire_compte(comptes[cle_compte], cle)
                texte_mdp.value = mdp_clair
                btn_oeil.icon = ft.Icons.VISIBILITY_OFF
                btn_oeil.tooltip = "Masquer le mot de passe"
            else:
                texte_mdp.value = "**********"
                btn_oeil.icon = ft.Icons.VISIBILITY
                btn_oeil.tooltip = "Afficher le mot de passe"
            page.update()

        btn_oeil.on_click = toggle_mdp

        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                site,
                                size=TAILLE_NORMAL,
                                weight=ft.FontWeight.BOLD,
                                color=TEXTE_PRINCIPAL
                            ),
                            ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.PERSON,
                                        size=TAILLE_NORMAL,
                                        color=COULEUR_PRIMAIRE
                                    ),
                                    ft.Text(
                                        identifiant,
                                        size=TAILLE_PETIT,
                                        color=TEXTE_SECONDAIRE
                                    )
                                ],
                                spacing=5
                            ),
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.KEY, size=TAILLE_NORMAL, color=TEXTE_SECONDAIRE),
                                    texte_mdp
                                ],
                                spacing=5
                            )
                        ],
                        spacing=2,
                        expand=True
                    ),
                    ft.Row(
                        [
                            btn_oeil,
                            ft.IconButton(
                                ft.Icons.COPY,
                                icon_color=TEXTE_SECONDAIRE,
                                tooltip="Copier le mot de passe",
                                on_click=lambda e, c=cle_compte: copier_mdp(c)
                            ),
                            ft.IconButton(
                                ft.Icons.MODE,
                                icon_color=COULEUR_SUCCES,
                                tooltip="Modifier le compte",
                                on_click=lambda e, c=cle_compte: modifier_compte(c)
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                icon_color=COULEUR_DANGER,
                                tooltip="Supprimer le compte",
                                on_click=lambda e, c=cle_compte: confirmer_suppression(c)
                            )
                        ],
                        spacing=0
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=FOND_BARRE,
            border_radius=ARRONDI_CARTE,
            padding=15,
        )

    def ouvrir_ajout(e):
        champ_site = ft.TextField(
            label="Site",
            prefix_icon=ft.Icons.LANGUAGE,
            border_radius=ARRONDI_CHAMP
        )

        champ_id = ft.TextField(
            label="Identifiant",
            prefix_icon=ft.Icons.PERSON,
            border_radius=ARRONDI_CHAMP
        )

        champ_mdp = ft.TextField(
            label="mot de passe",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            border_radius=ARRONDI_CHAMP
        )
        
        def sauver(e):
            site = champ_site.value.strip().lower()
            identifiant = champ_id.value.strip()
            mdp = champ_mdp.value.strip()

            if not site or not identifiant or not mdp:
                afficher_message("Remplis tous les champs !", COULEUR_DANGER)
                return
            cle_compte = generer_cle_compte(site, identifiant)
            if compte_existe(cle_compte):
                afficher_message(f"{identifiant} sur {site} existe déjà !", COULEUR_DANGER)
                return
            
            site_chiffre = chiffrer(site, cle)
            id_chiffre = chiffrer(identifiant, cle)
            mdp_chiffre = chiffrer(mdp, cle)
            ajouter_compte_data(site_chiffre, id_chiffre, mdp_chiffre, cle_compte)

            fermer_dialog(dlg)
            charger_comptes()
            afficher_message(f"{identifiant} sur {site} a été ajouté !", COULEUR_SUCCES)

        dlg = ft.AlertDialog(
            title=ft.Text("Ajouter un compte"),
            content=ft.Column(
                [
                    champ_site,
                    champ_id,
                    ft.Row(
                        [
                            champ_mdp,
                            ft.IconButton(
                                ft.Icons.CASINO,
                                tooltip="Générer un mot de passe",
                                on_click=lambda e: generer(champ_mdp)
                            )
                        ],
                        spacing=5
                    )
                ],
                spacing=10,
                tight=True
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=lambda e: fermer_dialog(dlg)
                ),
                ft.ElevatedButton(
                    "Sauvegarder",
                    color=COULEUR_SUCCES,
                    on_click=sauver
                )
            ],
        )
        ouvrir_dialog(dlg)

    def copier_mdp(cle_compte):
        toucher_activite()
        comptes = recuperer_comptes()
        _, _, mdp_clair = lire_compte(comptes[cle_compte], cle)
        copier_temporaire(mdp_clair, PRESSE_PAPIERS_DUREE_SEC)
        afficher_message(
            f"Mot de passe copié (effacé du presse-papiers dans {PRESSE_PAPIERS_DUREE_SEC} s)",
            COULEUR_SUCCES,
        )

    def generer(champ_mdp):
        champ_mdp.value = generer_mdp()
        page.update()

    def modifier_compte(cle_compte):
        toucher_activite()
        comptes = recuperer_comptes()
        site, identifiant, mdp = lire_compte(comptes[cle_compte], cle)
        
        champ_site = ft.TextField(
            label="Site",
            value=site,
            prefix_icon=ft.Icons.LANGUAGE,
            border_radius=ARRONDI_CHAMP
        )
        
        champ_id = ft.TextField(
            label="Identifiant",
            value=identifiant,
            prefix_icon=ft.Icons.PERSON,
            border_radius=ARRONDI_CHAMP
        )
        
        champ_mdp = ft.TextField(
            label="Mot de passe",
            value=mdp,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            border_radius=ARRONDI_CHAMP
        )

        def sauver_modification(e):
            nouveau_site = champ_site.value.strip().lower()
            nouveau_id = champ_id.value.strip()
            nouveau_mdp = champ_mdp.value.strip()

            if not nouveau_site or not nouveau_id or not nouveau_mdp:
                afficher_message("Remplis tous les champs !", COULEUR_DANGER)
                return

            nouvelle_cle = generer_cle_compte(nouveau_site, nouveau_id)
            
            if nouvelle_cle != cle_compte and compte_existe(nouvelle_cle):
                afficher_message("Ce compte existe déjà !", COULEUR_DANGER)
                return
            
            supprimer_donnees_compte(cle_compte)

            site_chiffre = chiffrer(nouveau_site, cle)
            id_chiffre = chiffrer(nouveau_id, cle)
            mdp_chiffre = chiffrer(nouveau_mdp, cle)
            ajouter_compte_data(site_chiffre, id_chiffre, mdp_chiffre, nouvelle_cle)

            fermer_dialog(dlg)
            charger_comptes()
            afficher_message("Compte modifié avec succès !", COULEUR_SUCCES)

        dlg = ft.AlertDialog(
            title=ft.Text("Modifier le compte"),
            content=ft.Column(
                [
                    champ_site,
                    champ_id,
                    ft.Row(
                        [
                            champ_mdp,
                            ft.IconButton(
                                ft.Icons.CASINO,
                                tooltip="Générer un mot de passe",
                                on_click=lambda e: generer(champ_mdp)
                            ),
                        ]
                    ),
                ],
                spacing=10,
                tight=True
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=lambda e: fermer_dialog(dlg)
                ),
                ft.ElevatedButton(
                    "Sauvegarder",
                    bgcolor=COULEUR_SUCCES,
                    color=TEXTE_PRINCIPAL,
                    on_click=sauver_modification
                ),
            ],
        )

        ouvrir_dialog(dlg)

    def confirmer_suppression(cle_compte):
        toucher_activite()
        comptes = recuperer_comptes()
        site, identifiant, _ = lire_compte(comptes[cle_compte], cle)
        
        dlg = ft.AlertDialog(
            title=ft.Text("Supprimer ce compte ?"),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.WARNING,
                                color=COULEUR_DANGER,
                                size=40
                            ),
                            ft.Column(
                                [
                                    ft.Text(f"Site : {site}",
                                    size=TAILLE_NORMAL,
                                    weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(
                                        f"Identifiant : {identifiant}",
                                        size=TAILLE_PETIT,
                                        color=TEXTE_SECONDAIRE
                                    ),
                                ],
                                spacing=2
                            ),
                        ],
                        spacing=15
                    ),
                    ft.Text(
                        "Cette action est irréversible.",
                        size=TAILLE_PETIT,
                        color=COULEUR_INFO
                    ),
                ],
                spacing=15,
                tight=True
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=lambda e: fermer_dialog(dlg),
                ),
                ft.ElevatedButton(
                    "Confirmer suppression",
                    bgcolor=COULEUR_DANGER,
                    color=TEXTE_PRINCIPAL,
                    on_click=lambda e: supprimer(cle_compte, dlg)
                ),
            ],
        )
        ouvrir_dialog(dlg)

    def supprimer(cle_compte, dlg):
        if supprimer_donnees_compte(cle_compte):
            fermer_dialog(dlg)
            charger_comptes()
            afficher_message("Compte supprimé !", COULEUR_SUCCES)
        else:
            afficher_message("Erreur lors de la suppression", COULEUR_DANGER)

    def ouvrir_parametres():
        compteur = [5]
        texte_bouton = ft.Text("Confirmer (5s)")
        btn_confirmer = ft.ElevatedButton(
            content=texte_bouton,
            color=TEXTE_PRINCIPAL,
            disabled=True,
        )

        decompte_lance = [False]
        thread_id = [0]

        message_reset = ft.Text(
            "",
            size=TAILLE_PETIT,
            color=COULEUR_DANGER,
            text_align=ft.TextAlign.CENTER,
        )

        def verifier_texte_reset(e):
            texte = champ_confirmation.value.strip().upper()

            def lancer_decompte(id_thread):
                import asyncio

                async def decompte():
                    for i in range(5, 0, -1):
                        if thread_id[0] != id_thread:
                            return
                        texte_bouton.value = f"Confirmer ({i}s)"
                        texte_bouton.update()
                        await asyncio.sleep(1)
                        
                    if thread_id[0] != id_thread:
                        return
                        
                    btn_confirmer.disabled = False
                    texte_bouton.value = "Confirmer"
                    texte_bouton.update()
                    btn_confirmer.bgcolor = COULEUR_DANGER
                    btn_confirmer.on_click = lambda e: executer_reset()
                    btn_confirmer.update()
                    message_reset.value = "Cliquez sur Confirmer pour tout supprimer"
                    message_reset.update()
            
                page.run_task(decompte)

            if texte == "RESET TOTAL" and not decompte_lance[0]:
                decompte_lance[0] = True
                champ_confirmation.disabled = True
                message_reset.value = "Réinitialisation dans 5 secondes..."
                btn_confirmer.visible = True
                texte_bouton.value = "Confirmer (5s)"
                texte_bouton.update()
                message_reset.update()
                champ_confirmation.update()
                btn_confirmer.update()
                
                thread_id[0] += 1
                lancer_decompte(thread_id[0])

        def executer_reset():
            if reset_application():
                fermer_dialog(dlg_reset)
                page.floating_action_button = None
                page.clean()
                afficher_message("Réinitialisation réussie", COULEUR_SUCCES)
                from connexion import page_connexion
                page_connexion(page)
            else:
                message_reset.value = "Erreur lors de la réinitialisation"
                message_reset.update()
        
        champ_confirmation = ft.TextField(
            label="Tapez 'RESET TOTAL' pour confirmer",
            border_radius=ARRONDI_CHAMP,
            text_align=ft.TextAlign.CENTER,
            on_change=verifier_texte_reset,
        )

        dlg_reset = ft.AlertDialog(
            title=ft.Text(
                "Réinitialisation totale",
                color=COULEUR_DANGER,
            ),
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.WARNING,
                        color=COULEUR_DANGER,
                        size=40
                    ),
                    ft.Text(
                        "Réinitialisation totale de l'application",
                        size=TAILLE_PETIT,
                        color=COULEUR_DANGER,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10),
                    champ_confirmation,
                    message_reset,
                ],
                spacing=10,
                tight=True,
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=lambda e: fermer_dialog(dlg_reset),
                ),
                btn_confirmer,
            ],
        )

        dlg_params = ft.AlertDialog(
            title=ft.Text("Paramètres"),
            content=ft.Column(
                [
                    ft.Text("Application", size=TAILLE_NORMAL, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DELETE_FOREVER, color=COULEUR_DANGER),
                        title=ft.Text("Réinitialiser l'application"),
                        subtitle=ft.Text(
                            "Supprime tous les comptes et le mot de passe maître",
                            size=TAILLE_PETIT,
                            color=TEXTE_TERTIAIRE
                        ),
                        on_click=lambda e: ouvrir_reset(),
                    ),
                ],
                spacing=5,
                tight=True,
            ),
            actions=[
                ft.TextButton(
                    "Fermer",
                    on_click=lambda e: fermer_dialog(dlg_params)
                ),
            ],
        )

        def ouvrir_reset():
            fermer_dialog(dlg_params)

            thread_id[0] += 1
            decompte_lance[0] = False
            texte_bouton.value = "Confirmer (5s)"
            btn_confirmer.disabled = True
            btn_confirmer.on_click = None
            champ_confirmation.value = ""
            champ_confirmation.disabled = False
            message_reset.value = ""
            message_reset.color = COULEUR_DANGER

            ouvrir_dialog(dlg_reset)

        champ_confirmation.on_submit = verifier_texte_reset

        ouvrir_dialog(dlg_params)
            

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    barre_recherche,
                    ft.Container(
                        content=liste_comptes,
                        expand=True,
                        border_radius=ARRONDI_CARTE,
                    ),
                ],
                spacing=15,
                expand=True
            ),
            padding=20,
            expand=True
        ),
    )
    charger_comptes()