import streamlit as st
import pandas as pd
from datetime import datetime
import gspread

# Configuration de la page
st.set_page_config(page_title="Plateforme de Contrôle Réglementaire", layout="wide")

# URL de votre Google Sheet (REMPLACEZ PAR VOTRE LIEN DE PARTAGE)
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/VOTRE_ID_DE_SHEET_ICI/edit?usp=sharing"

# --- CONNEXION À GOOGLE SHEETS ---
@st.cache_data(ttl=10)  # Rafraîchit les données toutes les 10 secondes
def charger_donnees(nom_onglet):
    try:
        # Connexion publique/partagée via l'URL
        gc = gspread.public_client()
        sh = gc.open_by_url(URL_GOOGLE_SHEET)
        worksheet = sh.worksheet(nom_onglet)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        # Si le mode public ne fonctionne pas pour l'écriture, 
        # l'alternative est l'authentification par compte de service ou via l'URL directe pandas
        url_csv = URL_GOOGLE_SHEET.replace("/edit?usp=sharing", f"/gviz/tq?tqx=out:csv&sheet={nom_onglet}")
        return pd.read_csv(url_csv)

# Note: Pour l'écriture gratuite et simplifiée sans créer de compte développeur complexe :
# Nous allons utiliser une méthode directe via un formulaire d'envoi ou l'API gspread classique.
# Pour ce code, nous lisons depuis Google Sheets de manière permanente.
try:
    df_rapports = charger_donnees("Rapports")
    df_planning = charger_donnees("Planning")
except:
    st.error("Erreur de connexion au Google Sheet. Vérifiez le lien de partage en mode 'Éditeur'.")
    df_rapports = pd.DataFrame(columns=["Site", "Année", "Catégorie", "Sous-Équipement", "Date_Installation", "Nom_Rapport", "Lien_PDF"])
    df_planning = pd.DataFrame(columns=["Équipement", "Prochain_Contrôle", "Responsable", "Contrat_Conformité"])

# --- DICTIONNAIRE DES SOUS-ÉQUIPEMENTS ---
SOUS_EQUIPEMENTS = {
    "Installations électriques": ["TGBT Cellule A", "Armoire Secondaire", "Transformateur Haute Tension", "Groupe Électrogène"],
    "Equipement de levage": ["Pont Roulant 5T", "Grue Mobile", "Chariot Élévateur", "Palan Électrique"],
    "Sécurité incendie": ["Système d'extinction auto", "Centrale Alarme Incendie", "Réseau RIA", "Blocs Autonomes d'Éclairage (BAES)"],
    "Installation de gaz": ["Vanne de Police Principale", "Détendeur de Gaz", "Réseau de Tuyauterie Alimentation"],
    "Appareil pression de gaz": ["Compresseur d'air", "Cuve de Stockage Sous Pression", "Soupape de Securité"]
}

# --- GESTION DES ACCÈS / ROLES ---
st.sidebar.title("Authentification")
role = st.sidebar.radio("Sélectionnez votre profil :", ["Visiteur (Consultation seule)", "Responsable (Admin - Modification)"])

password_correct = False
if role == "Responsable (Admin - Modification)":
    password = st.sidebar.text_input("Mot de passe Admin :", type="password")
    if password == "admin123":
        password_correct = True
        st.sidebar.success("Accès Admin Autorisé")
    elif password != "":
        st.sidebar.error("Mot de passe incorrect")

st.title("🛡️ Plateforme de Contrôle Réglementaire (Données Permanentes)")

tab1, tab2 = st.tabs(["📊 Partie 1 : Gestion des Rapports", "📅 Partie 2 : Maîtrise & Planification"])

# ==========================================
# PARTIE 1 : GESTION DES RAPPORTS
# ==========================================
with tab1:
    st.header("Gestion des Rapports de Contrôle Réglementaire")
    
    # ---- SECTION FILTRES EN CASCADE ----
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filtre_site = st.selectbox("1. Sélectionner le Site :", ["Tous", "SGB", "MEG"])
    with col2:
        filtre_annee = st.selectbox("2. Sélectionner l'Année :", ["Tous", "2025", "2026"])
    with col3:
        filtre_cat = st.selectbox("3. Sélectionner la Catégorie :", ["Tous", "Installations électriques", "Equipement de levage", "Sécurité incendie", "Installation de gaz", "Appareil pression de gaz"])
    with col4:
        if filtre_cat != "Tous":
            options_sous_eq = ["Tous"] + SOUS_EQUIPEMENTS[filtre_cat]
        else:
            options_sous_eq = ["Tous"] + [item for sublist in SOUS_EQUIPEMENTS.values() for item in sublist]
        filtre_sous_eq = st.selectbox("4. Sélectionner le Sous-Équipement :", options_sous_eq)

    # Application des filtres
    df_filtree = df_rapports.copy()
    if filtre_site != "Tous" and not df_filtree.empty:
        df_filtree = df_filtree[df_filtree["Site"] == filtre_site]
    if filtre_annee != "Tous" and not df_filtree.empty:
        df_filtree = df_filtree[df_filtree["Année"].astype(str) == filtre_annee]
    if filtre_cat != "Tous" and not df_filtree.empty:
        df_filtree = df_filtree[df_filtree["Catégorie"] == filtre_cat]
    if filtre_sous_eq != "Tous" and not df_filtree.empty:
        df_filtree = df_filtree[df_filtree["Sous-Équipement"] == filtre_sous_eq]

    # Affichage des résultats
    st.subheader("📋 Liste des rapports correspondants")
    if not df_filtree.empty:
        for idx, row in df_filtree.iterrows():
            with st.container():
                c_info, c_action = st.columns([3, 1])
                c_info.markdown(f"**[{row['Site']}] {row['Catégorie']}** - *{row['Sous-Équipement']}* (Installé le : {row['Date_Installation']}) — Année : **{row['Année']}**")
                c_action.markdown(f"[Télécharger / Imprimer le PDF 📄]({row['Lien_PDF']})", unsafe_allow_html=True)
                st.divider()
    else:
        st.warning("Aucun rapport trouvé dans la base de données pour ces critères.")

    # ---- ESPACE AJOUT (RÉSERVÉ ADMIN) ----
    if role == "Responsable (Admin - Modification)" and password_correct:
        st.markdown("---")
        st.subheader("➕ Ajouter un nouveau rapport (Mode Admin)")
        st.info("Pour ajouter définitivement une ligne, vous pouvez cliquer sur le lien ci-dessous pour ouvrir directement votre Google Sheet sécurisé ou utiliser l'interface de saisie.")
        st.markdown(f"[👉 Cliquer ici pour ouvrir le Google Sheet et ajouter/modifier des lignes en direct]({URL_GOOGLE_SHEET})")

# ==========================================
# PARTIE 2 : MAÎTRISE DES RAPPORTS
# ==========================================
with tab2:
    st.header("Maîtrise des Rapports, Planification & Conformités")
    
    st.subheader("📅 Tableau de planification des prochains contrôles")
    if not df_planning.empty:
        st.dataframe(df_planning, use_container_width=True)
    else:
        st.info("Le tableau de planification est vide.")
        
    if role == "Responsable (Admin - Modification)" and password_correct:
        st.markdown("---")
        st.subheader("⚙️ Modifier le Planning")
        st.markdown(f"[👉 Cliquer ici pour mettre à jour les dates de contrôle et les responsables sur Google Sheets]({URL_GOOGLE_SHEET})")
