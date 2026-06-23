import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION DE LA PAGE (Mode large et icône pro)
st.set_page_config(
    page_title="HSE Compliance Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. DESIGN & STYLE CSS PERSONNALISÉ (Pour affiner l'esthétique)
st.markdown("""
    <style>
    /* Modification de la police globale et du fond */
    html, body, [data-testid="stSidebarView"] {
        background-color: #F8F9FA;
    }
    /* Style des titres */
    h1 {
        color: #1E3A8A;
        font-weight: 700 !important;
    }
    h2, h3 {
        color: #2C3E50;
    }
    /* Personnalisation des boutons */
    .stButton>button {
        background-color: #1E3A8A !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3B82F6 !important;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# URL de votre Google Sheet (À remplacer par votre vrai lien)
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1ZK6VWg_gcCO70nt6DTyYogDeNeQUgovFmwWQufMVO-M/edit?gid=1880221270#gid=1880221270"

# --- SIMULATION DE DONNÉES PROPRES (Le temps que vous liiez votre Sheet) ---
if 'df_rapports' not in st.session_state:
    st.session_state.df_rapports = pd.DataFrame([
        {"Site": "SGB", "Année": 2025, "Catégorie": "Installations électriques", "Sous-Équipement": "TGBT Cellule A", "Date_Installation": "2022-03-15", "Nom_Rapport": "Rapport Élec Q4", "Lien_PDF": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"},
        {"Site": "MEG", "Année": 2026, "Catégorie": "Sécurité incendie", "Sous-Équipement": "Système d'extinction auto", "Date_Installation": "2024-01-10", "Nom_Rapport": "Audit Incendie Annuel", "Lien_PDF": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"},
        {"Site": "SGB", "Année": 2026, "Catégorie": "Appareil pression de gaz", "Sous-Équipement": "Compresseur d'air", "Date_Installation": "2021-06-20", "Nom_Rapport": "Épreuve sous pression", "Lien_PDF": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}
    ])

if 'df_planning' not in st.session_state:
    st.session_state.df_planning = pd.DataFrame([
        {"Équipement": "TGBT Cellule A", "Prochain_Contrôle": "2026-06-15", "Responsable": "Jean Dupont", "Statut": "Conforme"},
        {"Équipement": "Système d'extinction auto", "Prochain_Contrôle": "2026-12-20", "Responsable": "Alice Martin", "Statut": "En attente"},
        {"Équipement": "Compresseur d'air", "Prochain_Contrôle": "2026-07-01", "Responsable": "Jean Dupont", "Statut": "Non conforme"}
    ])

SOUS_EQUIPEMENTS = {
    "Installations électriques": ["TGBT Cellule A", "Armoire Secondaire", "Transformateur Haute Tension", "Groupe Électrogène"],
    "Equipement de levage": ["Pont Roulant 5T", "Grue Mobile", "Chariot Élévateur", "Palan Électrique"],
    "Sécurité incendie": ["Système d'extinction auto", "Centrale Alarme Incendie", "Réseau RIA", "Blocs Autonomes (BAES)"],
    "Installation de gaz": ["Vanne de Police Principale", "Détendeur de Gaz", "Réseau de Tuyauterie"],
    "Appareil pression de gaz": ["Compresseur d'air", "Cuve de Stockage", "Soupape de Sécurité"]
}

# --- SIDEBAR STYLE COMPACT ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1087/1087080.png", width=70) # Icône sécurité générique
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

# --- EN-TÊTE DE LA PLATFORME ---
st.title("🛡️ Portail Réglementaire & Conformité HSE")
st.caption("Plateforme d'audit synchronisée en temps réel — Accès instantané par QR Code")

# --- BANDEAU DE MÉTRIQUES (Effet Dashboard Pro) ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="Total Rapports Archivés", value=len(st.session_state.df_rapports))
with m2:
    st.metric(label="Contrôles Planifiés (2026)", value=len(st.session_state.df_planning))
with m3:
    non_conf = len(st.session_state.df_planning[st.session_state.df_planning["Statut"] == "Non conforme"])
    st.metric(label="Alertes Non-Conformité", value=non_conf, delta=-non_conf if non_conf > 0 else 0, delta_color="inverse")
with m4:
    st.metric(label="Statut Serveur", value="Opérationnel", delta="100% cloud")

st.markdown("---")

# --- ENROLEMENT DES ONGLETS ---
tab1, tab2 = st.tabs(["🔍 Registre & Rapports de Contrôle", "📅 Suivi de Performance & Planning"])

# ==========================================
# PARTIE 1 : INTERFACE DES RAPPORTS
# ==========================================
with tab1:
    st.markdown("### 🎛️ Filtres de Recherche Avancés")
    
    # Conteneur visuel pour les filtres
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

    # Filtrage des données
    df_f = st.session_state.df_rapports.copy()
    if f_site != "Tous": df_f = df_f[df_f["Site"] == f_site]
    if f_annee != "Tous": df_f = df_f[df_f["Année"].astype(str) == f_annee]
    if f_cat != "Tous": df_f = df_f[df_f["Catégorie"] == f_cat]
    if f_sous_eq != "Tous": df_f = df_f[df_f["Sous-Équipement"] == f_sous_eq]

    st.markdown("### 📋 Documents Rattachés")
    
    if not df_f.empty:
        # Affichage sous forme de tableau d'entreprise hautement interactif
        st.dataframe(
            df_f,
            column_config={
                "Lien_PDF": st.column_config.LinkColumn("Action / Téléchargement", display_text="📄 Ouvrir le PDF"),
                "Date_Installation": st.column_config.DateColumn("Date d'Installation"),
                "Année": st.column_config.NumberColumn("Exercice", format="%d")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Aucune pièce jointe ne correspond à vos filtres actuels.")

    # Section Administration Intégrée discrètement
    if role == "🔑 Responsable (Admin)" and password_correct:
        with st.expander("🛠️ Panneau d'administration : Ajouter un Rapport"):
            st.markdown("[🔗 Ouvrir la Base de Données Google Sheets en direct pour modification de masse](" + URL_GOOGLE_SHEET + ")")

# ==========================================
# PARTIE 2 : MAÎTRISE & PLANNING
# ==========================================
with tab2:
    st.markdown("### 📆 Calendrier de Maintenance Réglementaire")
    
    # Configuration avancée des couleurs de statuts pour faire "Pro"
    st.dataframe(
        st.session_state.df_planning,
        column_config={
            "Statut": st.column_config.SelectboxColumn(
                "État de Conformité",
                options=["Conforme", "En attente", "Non conforme"],
                required=True,
            ),
            "Prochain_Contrôle": st.column_config.DateColumn("Échéance Contrôle"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Légende et consignes
    st.info("💡 **Note aux équipes terrain :** Les dates affichées ci-dessus prévalent sur tout calendrier papier. En cas d'anomalie ou de non-conformité constatée, contactez immédiatement le responsable assigné.")

    if role == "🔑 Responsable (Admin)" and password_correct:
        with st.expander("🛠️ Panneau d'administration : Échéancier"):
            st.markdown("[🔗 Modifier les Responsabilités et les Contrats sur Google Sheets](" + URL_GOOGLE_SHEET + ")")
