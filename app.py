import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION DE LA PAGE DE DIRECTION
st.set_page_config(
    page_title="Contrôle Réglementaire HSE",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ⚠️ LIEN DE SYNCHRONISATION GOOGLE SHEETS
# ==========================================
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1ZK6VWg_gcCO70nt6DTyYogDeNeQUgovFmwWQufMVO-M/edit?gid=0#gid=0"

# 2. CHARGEMENT OPTIMISÉ DES DONNÉES
@st.cache_data(ttl=5)
def charger_donnees_sheet(nom_onglet):
    try:
        base_url = URL_GOOGLE_SHEET.split("/edit")[0]
        csv_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={nom_onglet}"
        df = pd.read_csv(csv_url)
        df = df.dropna(how='all')
        return df
    except Exception as e:
        st.error(f"Erreur de connexion à l'onglet '{nom_onglet}'.")
        return pd.DataFrame()

df_rapports = charger_donnees_sheet("Rapports")
df_planning = charger_donnees_sheet("Planning")

# ==========================================
# 3. FEUILLE DE STYLE CSS PREMIUM (EXECUTIVE UI)
# ==========================================
st.markdown("""
    <style>
    /* Importation d'une typographie moderne */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebarView"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #F8FAFC !important; /* Fond gris très clair ultra-moderne */
    }
    
    /* Design des Onglets (Tabs) */
    .stTabs [data-baseweb="tab"] {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #64748B !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #1E3A8A !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1E3A8A !important;
        border-bottom-color: #1E3A8A !important;
    }

    /* Style des formulaires et des encadrés */
    [data-testid="stForm"], .stCornerRadius {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        border-radius: 12px !important;
    }
    
    /* Boutons personnalisés */
    .stButton>button {
        background-color: #1E3A8A !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 500 !important;
        padding: 10px 24px !important;
        box-shadow: 0 2px 4px rgba(30, 58, 138, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

SOUS_EQUIPEMENTS = {
    "Installations électriques": [],
    "Equipements de levage": ["Transpalette", "Table élévatrice", "Potence", "Pont roulant", "Plateforme de travail", "Nacelle", "Gerbeur", "Chariot élévateur", "Palan électrique", "Ascenseur"],
    "Sécurité incendie": [],
    "Installations de gaz": ["Industrielle", "Chaudière"],
    "Appareil pression de gaz": []
}

# ==========================================
# 4. BARRE LATÉRALE (SIDEBAR DESIGN)
# ==========================================
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1]) 
    with col2:
        # Logo de l'entreprise
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6q1BtDSDgVnJZFo0hOBfQJoDS6OYiub-qfQ&s", use_container_width=True)
    
    st.markdown(
        """
        <div style="text-align: center; margin-top: 15px; margin-bottom: 25px;">
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 4px; color: #0F172A; letter-spacing: -0.5px;">
                Tunisie Profilés d'Aluminium
            </h3>
            <p style="font-size: 0.85rem; color: #64748B; margin: 0; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">
                Direction Maintenance & TN
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()
    
    st.markdown("<p style='font-weight: 600; color: #334155; margin-bottom: 0;'>🔐 Espace sécurisé</p>", unsafe_allow_html=True)
    role = st.selectbox("Profil utilisateur :", ["Visiteur", "Responsable"], label_visibility="collapsed")
    
    password_correct = False
    if role == "Responsable":
        password = st.text_input("Code d'accès :", type="password", placeholder="•••")
        if password == "admin123*":
            password_correct = True
            st.success("Accès administrateur validé")
        elif password:
            st.error("Code d'accès incorrect")

# ==========================================
# 5. EN-TÊTE DE PAGE CENTRALISÉ
# ==========================================
st.markdown(
    """
    <div style="text-align: center; margin-top: 10px; margin-bottom: 35px;">
        <h1 style="font-size: 2.6rem; font-weight: 800; color: #0F172A; margin-bottom: 6px; letter-spacing: -1px;">
            Tableau de Bord Réglementaire
        </h1>
        <p style="font-size: 1.05rem; color: #64748B; margin: 0; font-weight: 400;">
            Suivi HSE de conformité en temps réel — Synchronisé avec Direction Maintenance
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 6. BANDEAU DE CARTES KPI DESIGN CORPO (PREMIUM)
# ==========================================
val_total_rapports = len(df_rapports) if not df_rapports.empty else 0
val_controles_planifies = len(df_planning) if not df_planning.empty else 0

if not df_planning.empty and "Statut" in df_planning.columns:
    val_alertes = len(df_planning[df_planning["Statut"].astype(str).str.strip().str.lower() == "non conforme"])
else:
    val_alertes = 0

# Génération des cartes via colonnes et blocs HTML raffinés
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    st.markdown(f"""
        <div style="background: white; padding: 22px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03); border-left: 5px solid #1E3A8A;">
            <p style="margin:0; font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Total Rapports Archivés</p>
            <p style="margin:8px 0 0 0; font-size: 34px; color: #0F172A; font-weight: 700; line-height: 1;">{val_total_rapports}</p>
        </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
        <div style="background: white; padding: 22px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03); border-left: 5px solid #0EA5E9;">
            <p style="margin:0; font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Contrôles Planifiés</p>
            <p style="margin:8px 0 0 0; font-size: 34px; color: #0F172A; font-weight: 700; line-height: 1;">{val_controles_planifies}</p>
        </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    couleur_alerte = "#EF4444" if val_alertes > 0 else "#10B981"
    st.markdown(f"""
        <div style="background: white; padding: 22px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03); border-left: 5px solid {couleur_alerte};">
            <p style="margin:0; font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Alertes Non-Conformité</p>
            <p style="margin:8px 0 0 0; font-size: 34px; color: {couleur_alerte}; font-weight: 700; line-height: 1;">{val_alertes}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Navigation principale par onglets
tab1, tab2 = st.tabs(["📋 Rapports de contrôle archivés", "📅 Suivi de performance & Planification"])

# FONCTION LIEN DIRECT DRIVE
def convertir_en_lien_direct(url):
    try:
        if "drive.google.com" in str(url) and "/file/d/" in str(url):
            id_fichier = str(url).split("/file/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?export=download&id={id_fichier}"
    except Exception:
        pass
    return url

# ==========================================
# 7. GRAPHIQUES ANALYTIQUES (RÉPARTITION)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)

# On vérifie que la base de rapports n'est pas vide pour éviter les erreurs
if not df_rapports.empty:
    
    # Identification automatique des colonnes Site et Catégorie
    col_site_chart = [c for c in df_rapports.columns if "site" in c.lower()]
    col_cat_chart = [c for c in df_rapports.columns if "cat" in c.lower()]
    
    if col_site_chart and col_cat_chart:
        # Préparation des données pour les graphiques
        df_site_count = df_rapports[col_site_chart[0]].value_counts().reset_index()
        df_site_count.columns = ['Site', 'Nombre']
        
        df_cat_count = df_rapports[col_cat_chart[0]].value_counts().reset_index()
        df_cat_count.columns = ['Domaine', 'Nombre']

        # Création de 2 colonnes pour afficher les graphiques côte à côte
        chart_col1, chart_col2 = st.columns(2)
        
        # --- GRAPH 1 : RÉPARTITION PAR SITE (Style Donut épuré) ---
        with chart_col1:
            st.markdown("""
                <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; margin-bottom: 15px;">
                    <p style="margin:0; font-size: 14px; color: #1E3A8A; font-weight: 600;">📊 Volume de rapports par Site</p>
                </div>
            """, unsafe_allow_html=True)
            
            fig_site = px.pie(
                df_site_count, 
                values='Nombre', 
                names='Site', 
                hole=0.6, # Effet anneau/donut moderne
                color_discrete_sequence=['#1E3A8A', '#0EA5E9', '#94A3B8'] # Palette corporate
            )
            fig_site.update_traces(textposition='inside', textinfo='percent+label')
            fig_site.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=220,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_site, use_container_width=True, config={'displayModeBar': False})

        # --- GRAPH 2 : RÉPARTITION PAR CATÉGORIE (Barres Horizontales) ---
        with chart_col2:
            st.markdown("""
                <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; margin-bottom: 15px;">
                    <p style="margin:0; font-size: 14px; color: #1E3A8A; font-weight: 600;">📈 Rapports par Domaine Technique</p>
                </div>
            """, unsafe_allow_html=True)
            
            fig_cat = px.bar(
                df_cat_count.sort_values(by='Nombre', ascending=True), 
                x='Nombre', 
                y='Domaine', 
                orientation='h',
                text='Nombre', # 👈 AJOUT : Indique à Plotly d'utiliser la colonne 'Nombre' comme étiquette de texte
                color_discrete_sequence=['#1E3A8A']
            )
            
            # Configuration de la position et de l'affichage du texte
            fig_cat.update_traces(
                textposition='outside', # 👈 AJOUT : Force le texte à s'afficher à l'extérieur (à droite) de la barre
                cliponaxis=False         # 👈 AJOUT : Empêche que le texte soit coupé si la barre est trop longue
            )
            
            fig_cat.update_layout(
                margin=dict(t=5, b=5, l=10, r=40), # Augmentation de la marge de droite (r=40) pour laisser de la place aux chiffres
                height=220,
                xaxis_title=None,
                yaxis_title=None,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            fig_cat.update_xaxes(showgrid=True, gridcolor='#E2E8F0')
            st.plotly_chart(fig_cat, use_container_width=True, config={'displayModeBar': False})
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# PARTIE 1 : INTERFACE DES RAPPORTS
# ==========================================
with tab1:
    # Conteneur des filtres épuré
    with st.container(border=True):
        st.markdown("<p style='font-weight: 600; color: #1E293B; margin-top:0; margin-bottom: 10px;'>🎛️ Filtres de recherche avancés</p>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            f_site = st.selectbox("Site", ["Tous", "SGB", "MEG"])
        with c2:
            f_annee = st.selectbox("Année de l'exercice", ["Tous", "2025", "2026"])
        with c3:
            f_cat = st.selectbox("Domaine technique", ["Tous"] + list(SOUS_EQUIPEMENTS.keys()))
        with c4:
            opts = ["Tous"] + SOUS_EQUIPEMENTS[f_cat] if f_cat != "Tous" else ["Tous"] + [i for sub in SOUS_EQUIPEMENTS.values() for i in sub]
            f_sous_eq = st.selectbox("Sous-équipement", opts)

    st.markdown("<br><p style='font-size: 1.2rem; font-weight: 700; color: #0F172A; margin-bottom:10px;'>📂 Documents rattachés</p>", unsafe_allow_html=True)
    
    # Filtrage intelligent
    df_f = df_rapports.copy()
    if not df_f.empty:
        # Identification dynamique des colonnes de l'utilisateur (Robustesse)
        col_site = [c for c in df_f.columns if "site" in c.lower()]
        col_ex = [c for c in df_f.columns if "exerc" in c.lower() or "ann" in c.lower()]
        col_cat = [c for c in df_f.columns if "cat" in c.lower()]
        col_seq = [c for c in df_f.columns if "sous" in c.lower()]
        col_lien = [c for c in df_f.columns if "lien" in c.lower() or "pdf" in c.lower()]
        col_date = [c for c in df_f.columns if "date" in c.lower() or "contr" in c.lower()]

        if f_site != "Tous" and col_site:
            df_f = df_f[df_f[col_site[0]].astype(str).str.strip() == f_site]
            
        if f_annee != "Tous" and col_ex:
            df_f = df_f[pd.to_numeric(df_f[col_ex[0]], errors='coerce') == int(f_annee)]
            
        if f_cat != "Tous" and col_cat:
            df_f = df_f[df_f[col_cat[0]].astype(str).str.strip() == f_cat]
            
        if f_sous_eq != "Tous" and col_seq:
            df_f = df_f[df_f[col_seq[0]].astype(str).str.strip() == f_sous_eq]

    if not df_f.empty:
        # Nettoyage des formats pour l'affichage directionnel
        if col_lien:
            df_f[col_lien[0]] = df_f[col_lien[0]].apply(convertir_en_lien_direct)

        if col_date:
            df_f[col_date[0]] = pd.to_datetime(df_f[col_date[0]], dayfirst=True, errors='coerce')

        nom_col_ex = col_ex[0] if col_ex else "Exercice"
        nom_col_date = col_date[0] if col_date else "Date de dernier contrôle"
        nom_col_lien = col_lien[0] if col_lien else "Lien PDF"

        # Affichage du tableau de données haute fidélité
        st.dataframe(
            df_f,
            column_config={
                nom_col_lien: st.column_config.LinkColumn(
                    "Action", 
                    display_text="📥 Télécharger PDF",
                    help="Télécharger directement le rapport officiel validé"
                ),
                nom_col_ex: st.column_config.NumberColumn("Exercice", format="%d"),
                nom_col_date: st.column_config.DateColumn("Date de dernier contrôle", format="DD/MM/YYYY")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Aucun rapport ne correspond aux critères sélectionnés.")

    # Panneau d'administration épuré
    if role == "Responsable" and password_correct:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🛠️ Panneau d'administration (Accès Base de Données)"):
            st.markdown(f"En tant que responsable, vous pouvez modifier directement le registre : [Ouvrir le Google Sheets externe]({URL_GOOGLE_SHEET})")

# ==========================================
# PARTIE 2 : MAÎTRISE & PLANNING
# ==========================================
with tab2:
    st.markdown("<p style='font-size: 1.2rem; font-weight: 700; color: #0F172A; margin-bottom:10px;'>📅 Planification des contrôles obligatoires</p>", unsafe_allow_html=True)
    
    if not df_planning.empty:
        col_prochain = [c for c in df_planning.columns if "prochain" in c.lower() or "échéan" in c.lower()]
        nom_col_prochain = col_prochain[0] if col_prochain else "Prochain contrôle"
        
        # Affichage du tableau du planning
        st.dataframe(
            df_planning,
            column_config={
                nom_col_prochain: st.column_config.DateColumn("Échéance contrôle", format="DD/MM/YYYY"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Le calendrier réglementaire n'affiche aucun contrôle futur planifié dans Google Sheets.")
    
    if role == "Responsable" and password_correct:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🛠️ Panneau d'administration (Gestion du Planning)"):
            st.markdown(f"Pour ajouter ou modifier des dates d'échéances de contrôle : [Modifier le calendrier Google Sheets]({URL_GOOGLE_SHEET})")
