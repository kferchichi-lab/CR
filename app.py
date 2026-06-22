import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Plateforme de Contrôle Réglementaire", layout="wide")

# --- SIMULATION DE BASE DE DONNÉES (En production, connectez à Google Sheets) ---
if 'rapports_db' not in st.session_state:
    st.session_state.rapports_db = pd.DataFrame([
        {
            "Site": "SGB", "Année": "2025", 
            "Catégorie": "Installations électriques", "Sous-Équipement": "TGBT Cellule A", 
            "Date_Installation": "2022-03-15", "Nom_Rapport": "Rapport_Elec_SGB_2025.pdf",
            "Lien_PDF": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        },
        {
            "Site": "MEG", "Année": "2026", 
            "Catégorie": "Sécurité incendie", "Sous-Équipement": "Système d'extinction auto", 
            "Date_Installation": "2024-01-10", "Nom_Rapport": "Rapport_Incendie_MEG_2026.pdf",
            "Lien_PDF": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        }
    ])

if 'planning_db' not in st.session_state:
    st.session_state.planning_db = pd.DataFrame([
        {"Équipement": "TGBT Cellule A", "Prochain_Contrôle": "2026-06-15", "Responsable": "Jean Dupont", "Contrat_Conformité": "Conforme"},
        {"Équipement": "Système d'extinction auto", "Prochain_Contrôle": "2026-12-20", "Responsable": "Alice Martin", "Contrat_Conformité": "En attente de renouvellement"}
    ])

# --- DICTIONNAIRE DES SOUS-ÉQUIPEMENTS (Pour le filtre 4) ---
SOUS_EQUIPEMENTS = {
    "Installations électriques": ["TGBT Cellule A", "Armoire Secondaire", "Transformateur Haute Tension", "Groupe Électrogène"],
    "Equipement de levage": ["Pont Roulant 5T", "Grue Mobile", "Chariot Élévateur", "Palan Électrique"],
    "Sécurité incendie": ["Système d'extinction auto", "Centrale Alarme Incendie", "Réseau RIA", "Blocs Autonomes d'Éclairage (BAES)"],
    "Installation de gaz": ["Vanne de Police Principale", "Détendeur de Gaz", "Réseau de Tuyauterie Alimentation"],
    "Appareil pression de gaz": ["Compresseur d'air", "Cuve de Stockage Sous Pression", "Soupape de Sécurité"]
}

# --- GESTION DES ACCÈS / ROLES ---
st.sidebar.title("Authentification")
role = st.sidebar.radio("Sélectionnez votre profil :", ["Visiteur (Consultation seule)", "Responsable (Admin - Modification)"])

password_correct = False
if role == "Responsable (Admin - Modification)":
    password = st.sidebar.text_input("Mot de passe Admin :", type="password")
    # Mot de passe par défaut (Modifiable)
    if password == "admin123":
        password_correct = True
        st.sidebar.success("Accès Admin Autorisé")
    elif password != "":
        st.sidebar.error("Mot de passe incorrect")
else:
    password_correct = False

st.title("🛡️ Plateforme de Contrôle Réglementaire & Conformité")
st.write("Accès rapide par Code QR pour la gestion et le suivi des équipements.")

# Création des onglets pour les deux parties demandées
tab1, tab2 = st.tabs(["📊 Partie 1 : Gestion des Rapports", "📅 Partie 2 : Maîtrise & Planification"])

# ==========================================
# PARTIE 1 : GESTION DES RAPPORTS
# ==========================================
with tab1:
    st.header("Gestion des Rapports de Contrôle Réglementaire")
    st.info("Utilisez les filtres ci-dessous pour retrouver un rapport spécifique. Vous pouvez les visualiser ou les télécharger.")
    
    # ---- SECTION FILTRES EN CASCADE ----
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filtre_site = st.selectbox("1. Sélectionner le Site :", ["Tous", "SGB", "MEG"])
    with col2:
        filtre_annee = st.selectbox("2. Sélectionner l'Année :", ["Tous", "2025", "2026"])
    with col3:
        filtre_cat = st.selectbox("3. Sélectionner la Catégorie :", ["Tous", "Installations électriques", "Equipement de levage", "Sécurité incendie", "Installation de gaz", "Appareil pression de gaz"])
    with col4:
        # Le filtre 4 dépend dynamiquement du choix du filtre 3
        if filtre_cat != "Tous":
            options_sous_eq = ["Tous"] + SOUS_EQUIPEMENTS[filtre_cat]
        else:
            options_sous_eq = ["Tous"] + [item for sublist in SOUS_EQUIPEMENTS.values() for item in sublist]
        filtre_sous_eq = st.selectbox("4. Sélectionner le Sous-Équipement :", options_sous_eq)

    # Application des filtres sur la dataframe
    df_filtree = st.session_state.rapports_db.copy()
    if filtre_site != "Tous":
        df_filtree = df_filtree[df_filtree["Site"] == filtre_site]
    if filtre_annee != "Tous":
        df_filtree = df_filtree[df_filtree["Année"] == filtre_annee]
    if filtre_cat != "Tous":
        df_filtree = df_filtree[df_filtree["Catégorie"] == filtre_cat]
    if filtre_sous_eq != "Tous":
        df_filtree = df_filtree[df_filtree["Sous-Équipement"] == filtre_sous_eq]

    # Affichage des résultats
    st.subheader("📋 Liste des rapports correspondants")
    if not df_filtree.empty:
        for idx, row in df_filtree.iterrows():
            with st.container():
                c_info, c_action = st.columns([3, 1])
                c_info.markdown(f"**[{row['Site']}] {row['Catégorie']}** - *{row['Sous-Équipement']}* (Installé le : {row['Date_Installation']}) — Année du contrôle : **{row['Année']}**")
                # Lien vers le PDF hébergé sur Google Drive
                c_action.markdown(f"[Télécharger / Imprimer le PDF 📄]({row['Lien_PDF']})", unsafe_allow_html=True)
                st.divider()
    else:
        st.warning("Aucun rapport ne correspond à ces critères de recherche.")

    # ---- ESPACE AJOUT / MODIFICATION (RÉSERVÉ ADMIN) ----
    if role == "Responsable (Admin - Modification)" and password_correct:
        st.markdown("---")
        st.subheader("➕ Ajouter un nouveau rapport (Mode Admin)")
        with st.form("ajout_rapport_form"):
            new_site = st.selectbox("Site", ["SGB", "MEG"])
            new_annee = st.selectbox("Année", ["2025", "2026"])
            new_cat = st.selectbox("Catégorie", ["Installations électriques", "Equipement de levage", "Sécurité incendie", "Installation de gaz", "Appareil pression de gaz"])
            new_sous_eq = st.selectbox("Sous-Équipement", SOUS_EQUIPEMENTS[new_cat])
            new_date_inst = st.date_input("Date d'installation", datetime.now())
            new_nom = st.text_input("Nom du rapport (ex: Rapport_Elec_2026)")
            new_lien = st.text_input("Lien URL du fichier PDF (Lien de partage Google Drive)")
            
            submit_btn = st.form_submit_button("Enregistrer le rapport")
            if submit_btn:
                if new_nom and new_lien:
                    new_row = {
                        "Site": new_site, "Année": new_annee, "Catégorie": new_cat,
                        "Sous-Équipement": new_sous_eq, "Date_Installation": str(new_date_inst),
                        "Nom_Rapport": new_nom, "Lien_PDF": new_lien
                    }
                    st.session_state.rapports_db = pd.concat([st.session_state.rapports_db, pd.DataFrame([new_row])], ignore_index=True)
                    st.success("Rapport ajouté avec succès ! Recharger la page pour voir les modifications.")
                else:
                    st.error("Veuillez remplir tous les champs obligatoires (Nom et Lien URL).")


# ==========================================
# PARTIE 2 : MAÎTRISE DES RAPPORTS
# ==========================================
with tab2:
    st.header("Maîtrise des Rapports, Planification & Conformités")
    
    st.subheader("📅 Tableau de planification des prochains contrôles")
    st.dataframe(st.session_state.planning_db, use_container_width=True)

    # ---- ESPACE MODIFICATION PLANNING (RÉSERVÉ ADMIN) ----
    if role == "Responsable (Admin - Modification)" and password_correct:
        st.markdown("---")
        st.subheader("⚙️ Mettre à jour le planning ou la répartition des responsabilités")
        with st.form("ajout_planning_form"):
            all_equipments = [item for sublist in SOUS_EQUIPEMENTS.values() for item in sublist]
            plan_eq = st.selectbox("Sélectionner l'équipement", list(set(all_equipments)))
            plan_date = st.date_input("Date du prochain contrôle réglementaire")
            plan_resp = st.text_input("Responsable de l'équipement / de la vérification")
            plan_contrat = st.selectbox("Statut du contrat de conformité", ["Conforme", "Non conforme", "En attente de renouvellement", "Sous contrat prestataire externe"])
            
            submit_plan = st.form_submit_button("Mettre à jour la planification")
            if submit_plan:
                # Si l'équipement existe déjà, on le met à jour, sinon on l'ajoute
                if plan_eq in st.session_state.planning_db["Équipement"].values:
                    st.session_state.planning_db.loc[st.session_state.planning_db["Équipement"] == plan_eq, ["Prochain_Contrôle", "Responsable", "Contrat_Conformité"]] = [str(plan_date), plan_resp, plan_contrat]
                else:
                    new_plan_row = {"Équipement": plan_eq, "Prochain_Contrôle": str(plan_date), "Responsable": plan_resp, "Contrat_Conformité": plan_contrat}
                    st.session_state.planning_db = pd.concat([st.session_state.planning_db, pd.DataFrame([new_plan_row])], ignore_index=True)
                st.success("Planning et contrat de conformité mis à jour !")
