import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="HSE Compliance Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ⚠️ REMPLACEZ CE LIEN PAR LE VOTRE ⚠️
# ==========================================
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1ZK6VWg_gcCO70nt6DTyYogDeNeQUgovFmwWQufMVO-M/edit?gid=0#gid=0"

# 2. FONCTION DE CONNEXION DIRECTE ET GRATUITE A GOOGLE SHEETS
@st.cache_data(ttl=5) # Rafraîchit les données toutes les 5 secondes
def charger_donnees_sheet(nom_onglet):
    try:
        # Transformation du lien pour télécharger directement le format CSV de l'onglet demandé
        base_url = URL_GOOGLE_SHEET.split("/edit")[0]
        csv_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={nom_onglet}"
        df = pd.read_csv(csv_url)
        # Nettoyage des colonnes vides si présentes
        df = df.dropna(how='all')
        return df
    except Exception as e:
        st.error(f"Erreur de connexion à l'onglet '{nom_onglet}'. Vérifiez le lien de votre Google Sheet.")
        return pd.DataFrame()

# Chargement des vraies données en direct
df_rapports = charger_donnees_sheet("Rapports")
df_planning = charger_donnees_sheet("Planning")

# 3. DESIGN & STYLE CSS PERSONNALISÉ
st.markdown("""
    <style>
    html, body, [data-testid="stSidebarView"] { background-color: #F8F9FA; }
    h1 { color: #1E3A8A; font-weight: 700 !important; }
    h2, h3 { color: #2C3E50; }
    .stButton>button {
        background-color: #1E3A8A !important; color: white !important;
        border-radius: 6px !important; border: none !important;
        font-weight: 600; transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #3B82F6 !important; transform: translateY(-1px); }
    </style>
""", unsafe_allow_html=True)

SOUS_EQUIPEMENTS = {
    "Installations électriques": ["TGBT Cellule A", "Armoire Secondaire", "Transformateur Haute Tension", "Groupe Électrogène"],
    "Equipement de levage": ["Pont Roulant 5T", "Grue Mobile", "Chariot Élévateur", "Palan Électrique"],
    "Sécurité incendie": ["Système d'extinction auto", "Centrale Alarme Incendie", "Réseau RIA", "Blocs Autonomes (BAES)"],
    "Installation de gaz": ["Vanne de Police Principale", "Détendeur de Gaz", "Réseau de Tuyauterie"],
    "Appareil pression de gaz": ["Compresseur d'air", "Cuve de Stockage", "Soupape de Sécurité"]
}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### **Espace Sécurisé**")
    role = st.selectbox("Profil Utilisateur :", ["👤 Visiteur (Lecture seule)", "🔑 Responsable (Admin)"])
    
    password_correct = False
    if role == "🔑 Responsable (Admin)":
        password = st.text_input("Code d'accès :", type="password")
        if password == "admin123":
            password_correct = True
            st.success("Accès Admin Activé")
        elif password:
            st.error("Code incorrect")

# --- EN-TÊTE ---
st.title("🛡️ Portail Réglementaire & Conformité HSE")
st.caption("Plateforme synchronisée en temps réel avec Google Sheets — Accès par QR Code")

# --- BANDEAU DE MÉTRIQUES ---
m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="Total Rapports Archivés", value=len(df_rapports) if not df_rapports.empty else 0)
with m2:
    st.metric(label="Contrôles Planifiés", value=len(df_planning) if not df_planning.empty else 0)
with m3:
    if not df_planning.empty and "Statut" in df_planning.columns:
        non_conf = len(df_planning[df_planning["Statut"] == "Non conforme"])
    else:
        non_conf = 0
    st.metric(label="Alertes Non-Conformité", value=non_conf, delta=-non_conf if non_conf > 0 else 0, delta_color="inverse")

st.markdown("---")
tab1, tab2 = st.tabs(["🔍 Registre & Rapports de Contrôle", "📅 Suivi de Performance & Planning"])

# ==========================================
# PARTIE 1 : INTERFACE DES RAPPORTS
# ==========================================
# ==========================================
# PARTIE 1 : INTERFACE DES RAPPORTS
# ==========================================
with tab1:
    st.markdown("### 🎛️ Filtres de Recherche Avancés")
    
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            f_site = st.selectbox("Site Établissement", ["Tous", "SGB", "MEG"])
        with c2:
            f_annee = st.selectbox("Année de l'exercice", ["Tous", "2025", "2026"])
        with c3:
            f_cat = st.selectbox("Domaine Technique", ["Tous"] + list(SOUS_EQUIPEMENTS.keys()))
        with c4:
            opts = ["Tous"] + SOUS_EQUIPEMENTS[f_cat] if f_cat != "Tous" else ["Tous"] + [i for sub in SOUS_EQUIPEMENTS.values() for i in sub]
            f_sous_eq = st.selectbox("Sous-Équipement cible", opts)

    # Filtrage des données (Adapté à vos colonnes exactes)
    df_f = df_rapports.copy()
    if not df_f.empty:
        if f_site != "Tous" and "Site" in df_f.columns: 
            df_f = df_f[df_f["Site"].astype(str) == f_site]
        if f_annee != "Tous" and "Exercice" in df_f.columns: 
            df_f = df_f[df_f["Exercice"].astype(str) == f_annee]
        if f_cat != "Tous" and "Catégorie" in df_f.columns: 
            df_f = df_f[df_f["Catégorie"].astype(str) == f_cat]
        if f_sous_eq != "Tous" and "Sous-équipement" in df_f.columns: 
            df_f = df_f[df_f["Sous-équipement"].astype(str) == f_sous_eq]

    st.markdown("### 📋 Documents Rattachés")
    
    if not df_f.empty:
        # Affichage avec configuration de l'icône de téléchargement
        st.dataframe(
            df_f,
            column_config={
                "Lien PDF": st.column_config.LinkColumn(
                    "Action", 
                    display_text="📥 Télécharger",
                    help="Cliquez pour ouvrir ou imprimer le rapport PDF"
                ),
                "Exercice": st.column_config.NumberColumn("Exercice", format="%d"),
                "Date de dernier contrôle": st.column_config.DateColumn("Date de dernier contrôle")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Aucun rapport ne correspond à vos filtres actuels ou la base de données est vide.")

    if role == "🔑 Responsable (Admin)" and password_correct:
        with st.expander("🛠️ Panneau d'administration"):
            st.markdown(f"[🔗 Ouvrir le Google Sheets pour ajouter/modifier des rapports]({URL_GOOGLE_SHEET})")

# ==========================================
# PARTIE 2 : MAÎTRISE & PLANNING
# ==========================================
with tab2:
    st.markdown("### 📆 Calendrier de Maintenance Réglementaire")
    
    if not df_planning.empty:
        st.dataframe(
            df_planning,
            column_config={
                "Prochain_Contrôle": st.column_config.DateColumn("Échéance Contrôle"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Le tableau de planification est vide sur Google Sheets.")
    
    if role == "🔑 Responsable (Admin)" and password_correct:
        with st.expander("🛠️ Panneau d'administration"):
            st.markdown(f"[🔗 Ouvrir le Google Sheets pour modifier le planning]({URL_GOOGLE_SHEET})")
