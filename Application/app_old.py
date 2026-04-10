# Les différents imports qu'il faut
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
from scipy.interpolate import PchipInterpolator
import plotly.graph_objects as go
import streamlit.components.v1 as components
import textwrap
# ==========================================
# --- CONFIGURATION DE LA PAGE ---
# ==========================================
st.set_page_config(page_title="Simulateur PV", layout="wide")

# --- Pour le MDP ---
if "acces_config" not in st.session_state:
    st.session_state["acces_config"] = False

if "cout_pv_par_wc" not in st.session_state:
    st.session_state["cout_pv_par_wc"] = 1.50

if "cout_batterie_par_wh" not in st.session_state:
    st.session_state["cout_batterie_par_wh"] = 0.75

if "prix_electricite" not in st.session_state:
    st.session_state["prix_electricite"] = 0.25

if "prix_injection" not in st.session_state:
    st.session_state["prix_injection"] = 0.10

if "prix_communaute_achat" not in st.session_state:
    st.session_state["prix_communaute_achat"] = 0.15

if "prix_communaute_vente" not in st.session_state:
    st.session_state["prix_communaute_vente"] = 0.15


# --- Design des onglets ---
st.markdown("""
    <style>
    div[data-baseweb="tab-list"] {
        background-color: #EAF7FF;
        padding: 6px;
        border-radius: 14px;
        gap: 14px;
    }

    button[data-baseweb="tab"] {
        background-color: #D6F0FF;
        border-radius: 14px;
        border: none;
        margin-right: 20px;
    }

    button[data-baseweb="tab"] p {
        font-size: 20px !important;
        color: #23485A !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #9EDCFF !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] p {
        font-weight: bold;
        color: #123040 !important;
    }
    </style>
""", unsafe_allow_html=True)










st.markdown("""
<style>
.budget-card {
    background: #ffffff;
    border: 1px solid #e8edf3;
    border-radius: 18px;
    padding: 22px 24px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
    margin-bottom: 18px;
}

.budget-card h3 {
    margin: 0 0 18px 0;
    font-size: 24px;
    font-weight: 700;
    color: #1f2c3a;
}

.budget-card h4 {
    margin: 18px 0 8px 0;
    font-size: 18px;
    font-weight: 700;
    color: #24394d;
}

.budget-label {
    font-size: 15px;
    color: #5b6b79;
    margin-bottom: 2px;
}

.budget-value {
    font-size: 28px;
    font-weight: 800;
    color: #16283a;
    margin-bottom: 10px;
}

.budget-note {
    font-size: 15px;
    color: #3f4d5a;
    line-height: 1.6;
}

.budget-note ul {
    margin-top: 8px;
    padding-left: 20px;
}

.budget-summary {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    overflow: hidden;
    border-radius: 14px;
    border: 1px solid #d8e2eb;
    margin-top: 8px;
}

.budget-summary-item {
    padding: 14px 18px;
}

.budget-summary-item .title {
    font-size: 14px;
    color: rgba(0,0,0,0.65);
    margin-bottom: 4px;
}

.budget-summary-item .value {
    font-size: 24px;
    font-weight: 800;
    color: #102030;
}

.budget-summary-item.gray {
    background: linear-gradient(90deg, #eceff3, #d9dde3);
}

.budget-summary-item.green {
    background: linear-gradient(90deg, #8dd18a, #63b86c);
}

.budget-summary-item.blue {
    background: linear-gradient(90deg, #5faee3, #2f87c8);
}

.budget-summary-item.green .title,
.budget-summary-item.blue .title,
.budget-summary-item.green .value,
.budget-summary-item.blue .value {
    color: #ffffff;
}

.budget-table-title {
    font-size: 22px;
    font-weight: 700;
    color: #1f2c3a;
    margin: 6px 0 12px 0;
}
</style>
""", unsafe_allow_html=True)














st.markdown("""
<style>
.finance-card {
    background: #ffffff;
    border: 1px solid #e6edf5;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    margin-bottom: 18px;
}

.finance-card-blue {
    background: linear-gradient(180deg, #eef7ff, #e3f1ff);
    border: 1px solid #bcdcff;
}

.finance-card-green {
    background: linear-gradient(180deg, #effaf1, #e5f6e8);
    border: 1px solid #bfe4c8;
}

.finance-card-orange {
    background: linear-gradient(180deg, #fff6ec, #ffefdf);
    border: 1px solid #ffd4a8;
}

.finance-title {
    font-size: 22px;
    font-weight: 700;
    color: #1f2c3a;
    margin-bottom: 10px;
}

.finance-subtitle {
    font-size: 15px;
    color: #4b5a68;
    margin-bottom: 8px;
}

.finance-big {
    font-size: 26px;
    font-weight: 800;
    color: #13283a;
    margin-bottom: 8px;
}

.finance-small {
    font-size: 14px;
    color: #506070;
    line-height: 1.5;
}

.finance-section-title {
    font-size: 30px;
    font-weight: 800;
    color: #1a2d3f;
    margin-bottom: 4px;
}

.finance-section-desc {
    font-size: 15px;
    color: #5a6a78;
    margin-bottom: 18px;
}

.finance-roi-box {
    background: #ffffff;
    border: 1px solid #e6edf5;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    margin-bottom: 18px;
}
</style>
""", unsafe_allow_html=True)






















# ==========================================
# --- EN-TÊTE DE L'APPLICATION AVEC IMAGE ---
# ==========================================
col1, col2 = st.columns([3, 1]) # Crée 2 colonnes (la 1ère plus grande pour le texte)

with col1:
    st.title("Simulateur Photovoltaïque & Stockage")
    st.markdown("""
    Analysez votre production, votre consommation et l'impact d'une batterie.
    Optimisez votre taux d'autoconsommation en un clic !
    """)

with col2:
    # Affiche la photo de panneau
    try:
        st.image("panneau.jpg", use_container_width=True)
    except Exception as e:
        pass # Si l'image n'est pas trouvée, l'appli continue sans planter

st.divider() # Ajoute une belle ligne grise de séparation







# ==========================================
# --- CRÉATION DES ONGLETS ---
# ==========================================
tab_import, tab_saisons, tab_mensuel, tab_annuel, tab_budget, tab_finance, tab_config = st.tabs([
    "Import & Paramètres", 
    "Profils Journaliers", 
    "Bilan Mensuel", 
    "Résumé Annuel",
    "Budget",
    "Analyse financière",
    "Paramètres avancés"
])

donnees_conso = None
profil_choisi = None



# ==========================================
# ONGLET 1 : IMPORT ET PARAMÈTRES
# ==========================================
with tab_import:
    st.sidebar.image("logo.jpg", use_container_width=True)
    st.header("Paramètres du projet")
    puissance_crete = st.number_input("Puissance Crête à installer (kWc)", min_value=0.0, value=10.0, step=0.1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Production Solaire")

        mode_prod = st.radio(
            "Type de fichier de production :",
            ["CSV SolarEdge", "Fichier simple Excel"]
        )

        if mode_prod == "CSV SolarEdge":
            fichier_prod = st.file_uploader(
                "Importez le CSV SolarEdge",
                type=['csv'],
                key="prod_solaredge"
            )
        else:
            fichier_prod = st.file_uploader(
                "Importez le fichier Excel de production",
                type=['xlsx', 'xls'],
                key="prod_simple_excel"
            )
        
    with col2:
        st.subheader("Source de Consommation")
        mode_conso = st.radio("Choix de la méthode :", 
                             ["Profils types (Fichier CSV)", "Calculateur personnalisé (Tableau)"])

    # --- INITIALISATION DES VARIABLES ---
    profil_24h_custom = np.zeros(24)

    # --- CHARGEMENT ET CALCUL DE LA CONSO ---
    try:
        if mode_conso == "Profils types (Fichier CSV)":
            donnees_conso = pd.read_csv('consommation.csv', sep=";", decimal=",")
            choix_profils = [col for col in donnees_conso.columns if col.lower() != "date" and "unnamed" not in col.lower()]
            
            st.success("Fichier de profils détecté !")
            profil_choisi = st.selectbox("Choisissez le profil à simuler :", choix_profils)
            
            conso_col = pd.to_numeric(donnees_conso[profil_choisi], errors='coerce').fillna(0)
            dates_apercu = pd.date_range(start='2024-01-01', periods=len(donnees_conso), freq='h')
            
            y_jour = conso_col.groupby(dates_apercu.hour).mean()
            y_mois = conso_col.groupby(dates_apercu.month).sum() / 1000
            total_kwh = conso_col.sum() / 1000

        else:
            # --- MODE PERSONNALISÉ ---
            st.info("💡 Ajoutez vos appareils. Horaires : '8-10' ou '12-13;19-21'")
            default_devices = [
                {"Appareil": "Talon (Veilles, Box, Frigo)", "Puissance (W)": 150, "Horaires": "0-24", "Actif": True},
                {"Appareil": "Éclairage & Prises", "Puissance (W)": 300, "Horaires": "7-9;18-23", "Actif": True},
                {"Appareil": "Lave-Linge", "Puissance (W)": 2000, "Horaires": "14-16", "Actif": True},
                {"Appareil": "Plaques Cuisson", "Puissance (W)": 1500, "Horaires": "12-13;19-20", "Actif": True},
            ]
            df_custom = st.data_editor(pd.DataFrame(default_devices), num_rows="dynamic", use_container_width=True)
            
            def parse_h(h_str):
                p = np.zeros(24)
                try:
                    for b in str(h_str).split(';'):
                        d, f = map(int, b.split('-'))
                        p[d:f] = 1
                except: pass
                return p

            for _, row in df_custom.iterrows():
                if row["Actif"]:
                    profil_24h_custom += parse_h(row["Horaires"]) * row["Puissance (W)"]
            
            y_jour = pd.Series(profil_24h_custom)
            jours_mois = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            y_mois = pd.Series([(y_jour.sum() * j / 1000) for j in jours_mois], index=range(1, 13))
            total_kwh = y_mois.sum()
            profil_choisi = "Sur Mesure"

        # --- AFFICHAGE COMMUN DES GRAPHES ---
        st.markdown("---")
        st.subheader(f"Aperçu : {profil_choisi} (Total : {total_kwh:,.0f} kWh)".replace(',', ' '))
        
        # On ajoute les metrics pour le mode personnalisé
        if mode_conso == "Calculateur personnalisé (Tableau)":
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Annuel", f"{total_kwh:,.0f} kWh".replace(",", " "))
            c2.metric("Puissance Max", f"{profil_24h_custom.max():,.0f} W")
            c3.metric("Conso / Jour", f"{(profil_24h_custom.sum()/1000):.1f} kWh")

        fig_apercu, (ax_jour, ax_mois) = plt.subplots(1, 2, figsize=(14, 4))
        ax_jour.plot(y_jour.index, y_jour.values, color='#1565C0', linewidth=2.5)
        ax_jour.fill_between(y_jour.index, y_jour.values, color='#1565C0', alpha=0.2)
        ax_jour.set_title("Modèle sur un jour type")
        ax_jour.set_xticks(range(0, 24, 2))
        ax_jour.grid(True, linestyle='--', alpha=0.6)
        
        mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        ax_mois.bar(mois_noms, y_mois.values, color='#FF9800', edgecolor='black', alpha=0.8)
        ax_mois.set_title("Consommation Mensuelle Totale")
        ax_mois.grid(axis='y', linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        st.pyplot(fig_apercu)

    except Exception as e:
        st.error(f"Erreur : {e}")

# --- BARRIÈRE DE SÉCURITÉ ---
if fichier_prod is None:
    st.info("Veuillez importer le fichier de production SolarEdge pour voir le reste de la simulation.")
    st.stop()


# =========================================================
# 1. IMPORT DE LA PRODUCTION ET CRÉATION DU TABLEAU PRINCIPAL
# =========================================================

# On remet le curseur du fichier au début avant lecture
fichier_prod.seek(0)

# ---------------------------------------------------------
# 1.1 Lecture du fichier de production selon le format choisi
# ---------------------------------------------------------
if mode_prod == "CSV SolarEdge":
    # Lecture du CSV SolarEdge
    donnees_prod = pd.read_csv(fichier_prod, sep=",", skiprows=[1], index_col=False)
    # Nettoyage des lignes utiles et reconstruction de la date
    donnees_prod = donnees_prod[donnees_prod['Date&Time'].astype(str).str.contains('-', na=False)]
    donnees_prod['Date&Time'] = donnees_prod['Date&Time'].astype(str) + " 2024"
    donnees_prod['Date&Time'] = pd.to_datetime(
        donnees_prod['Date&Time'],
        format='%d-%b %H:%M:%S %Y',
        errors='coerce'
    )
    # Construction du tableau principal avec les colonnes utiles
    mon_tableau = donnees_prod[['Date&Time', 'Inverter Output']].copy()
    mon_tableau['Inverter Output'] = pd.to_numeric(
        mon_tableau['Inverter Output'],
        errors='coerce'
    ).fillna(0)

else:
    # Lecture du fichier Excel simple (2 colonnes : date + production)
    donnees_prod = pd.read_excel(fichier_prod, header=None)
    # Renommage des colonnes et conversion des types
    donnees_prod = donnees_prod.iloc[:, :2].copy()
    donnees_prod.columns = ['Date&Time', 'Inverter Output']
    donnees_prod['Date&Time'] = pd.to_datetime(donnees_prod['Date&Time'], errors='coerce')
    donnees_prod['Inverter Output'] = pd.to_numeric(
        donnees_prod['Inverter Output'],
        errors='coerce'
    ).fillna(0)
    # Suppression des lignes invalides
    donnees_prod = donnees_prod.dropna(subset=['Date&Time']).copy()
    # Tableau principal
    mon_tableau = donnees_prod.copy()

# =========================================================
# 2. AJUSTEMENT ÉVENTUEL DE LA PRODUCTION PV
# =========================================================

# Paramètre utilisateur pour appliquer une hausse ou une baisse
augmentation_prod_pct = st.sidebar.number_input(
    "Augmentation de la production (%)",
    min_value=-10.0,
    value=0.0,
    step=1.0
)

# Application du facteur multiplicatif sur la production
facteur_augmentation_prod = 1 + augmentation_prod_pct / 100
mon_tableau['Inverter Output'] = mon_tableau['Inverter Output'] * facteur_augmentation_prod

# =========================================================
# 3. AJOUT DU PROFIL DE CONSOMMATION
# =========================================================

# Deux cas possibles :
# - consommation calculée depuis le tableau personnalisé
# - consommation issue d'un profil type chargé depuis fichier
if mode_conso == "Calculateur personnalisé (Tableau)":
    conso_base = np.tile(profil_24h_custom, len(mon_tableau) // 24 + 1)[:len(mon_tableau)]
    mon_tableau['Consumption'] = conso_base
else:
    if donnees_conso is not None and profil_choisi is not None:
        valeurs_conso = pd.to_numeric(
            donnees_conso[profil_choisi],
            errors='coerce'
        ).fillna(0).values
        mon_tableau['Consumption'] = valeurs_conso[:len(mon_tableau)]
    else:
        mon_tableau['Consumption'] = 0.0

# =========================================================
# 4. CALCULS ÉNERGÉTIQUES DE BASE (SANS BATTERIE)
# =========================================================

# Calcul des flux élémentaires :
mon_tableau['Autoconsommation'] = np.minimum(mon_tableau['Inverter Output'],mon_tableau['Consumption'])
mon_tableau['Import_Reseau'] = np.maximum(0,mon_tableau['Consumption'] - mon_tableau['Inverter Output'])
mon_tableau['Export_Reseau'] = np.maximum(0,mon_tableau['Inverter Output'] - mon_tableau['Consumption'])

# =========================================================
# 5. PARAMÉTRAGE DE LA BATTERIE DANS LA SIDEBAR
# =========================================================

st.sidebar.markdown("---")
st.sidebar.subheader("Stockage (Batterie)")

st.sidebar.markdown("---")
st.sidebar.subheader("Évolution de la production PV")

# ---------------------------------------------------------
# 5.1 Chargement de la base de données batteries
# ---------------------------------------------------------
try:
    df_batteries = pd.read_excel('batteries.xlsx')
    # Suppression des lignes incomplètes
    df_batteries = df_batteries.dropna(subset=['Energie util', 'P charge / décharge'])
except Exception as e:
    st.sidebar.error("Fichier batteries.xlsx introuvable. Placez-le dans le dossier.")
    df_batteries = pd.DataFrame()
# Activation ou non de la batterie
activer_batterie = st.sidebar.checkbox("Activer la simulation de batterie", value=False)
# Valeurs par défaut
capa_wh = 0.0
puiss_w = 0.0

# ---------------------------------------------------------
# 5.2 Sélection du modèle de batterie
# ---------------------------------------------------------
if activer_batterie and not df_batteries.empty:
    liste_batteries = df_batteries['Référence'].tolist()
    choix_batterie = st.sidebar.selectbox("Choisissez un modèle :", liste_batteries)
    infos_batterie = df_batteries[df_batteries['Référence'] == choix_batterie].iloc[0]
    # Lecture des caractéristiques
    capa_kwh = float(str(infos_batterie['Energie util']).replace(',', '.'))
    puiss_kw = float(str(infos_batterie['P charge / décharge']).replace(',', '.'))
    # Affichage dans la sidebar
    st.sidebar.info(f"Capacité : {capa_kwh:.2f} kWh\n Puissance Max : {puiss_kw:.2f} kW")
    # Conversion en Wh / W pour l'algorithme
    capa_wh = capa_kwh * 1000
    puiss_w = puiss_kw * 1000

# =========================================================
# 6. FONCTION DE SIMULATION DE LA BATTERIE
# =========================================================

def simuler_batterie(production_wh, consommation_wh, capacite_max_wh, puissance_max_w):
    niveau_actuel = 0.0
    niveaux, charges, decharges, exports, achats = [], [], [], [], []
    for prod, conso in zip(production_wh, consommation_wh):
        # Part consommée directement depuis le PV
        autoconso_directe = min(prod, conso)
        # Calcul du surplus ou du manque
        surplus = prod - autoconso_directe
        manque = conso - autoconso_directe
        charge, decharge, export, achat = 0.0, 0.0, 0.0, 0.0
        # Cas 1 : surplus PV -> on charge la batterie puis on exporte le reste
        if surplus > 0:
            charge = min(surplus, puissance_max_w, capacite_max_wh - niveau_actuel)
            niveau_actuel += charge
            export = surplus - charge
        # Cas 2 : production insuffisante -> on décharge la batterie puis on importe le reste
        elif manque > 0:
            decharge = min(manque, puissance_max_w, niveau_actuel)
            niveau_actuel -= decharge
            achat = manque - decharge
        # Sauvegarde des résultats à chaque pas de temps
        niveaux.append(niveau_actuel)
        charges.append(charge)
        decharges.append(decharge)
        exports.append(export)
        achats.append(achat)
    return niveaux, charges, decharges, exports, achats

# =========================================================
# 7. APPLICATION DE LA LOGIQUE BATTERIE AU TABLEAU PRINCIPAL
# =========================================================

# Autoconsommation directe avant prise en compte éventuelle de la batterie
mon_tableau['Autoconso_Directe'] = np.minimum(mon_tableau['Inverter Output'],mon_tableau['Consumption'])
if activer_batterie and capa_wh > 0:
    # -----------------------------------------------------
    # 7.1 Cas avec batterie
    # -----------------------------------------------------
    niveaux, charges, decharges, exports, achats = simuler_batterie(
        mon_tableau['Inverter Output'].values,
        mon_tableau['Consumption'].values,
        capacite_max_wh=capa_wh,
        puissance_max_w=puiss_w
    )
    mon_tableau['Niveau_Batterie'] = niveaux
    mon_tableau['Charge_Batterie'] = charges
    mon_tableau['Decharge_Batterie'] = decharges
    mon_tableau['Export_Reseau'] = exports
    mon_tableau['Import_Reseau'] = achats
    # L'autoconsommation totale = PV direct + énergie fournie par la batterie
    mon_tableau['Autoconsommation'] = (mon_tableau['Autoconso_Directe'] + mon_tableau['Decharge_Batterie'])
else:
    # -----------------------------------------------------
    # 7.2 Cas sans batterie
    # -----------------------------------------------------
    mon_tableau['Decharge_Batterie'] = 0.0
    mon_tableau['Autoconsommation'] = mon_tableau['Autoconso_Directe']
    mon_tableau['Import_Reseau'] = np.maximum(0,mon_tableau['Consumption'] - mon_tableau['Inverter Output'])
    mon_tableau['Export_Reseau'] = np.maximum(0,mon_tableau['Inverter Output'] - mon_tableau['Consumption'])



# ===================================================================================================
# ONGLET 2 : LES 4 SAISONS (PROFILS JOURNALIERS)
# ===================================================================================================
with tab_saisons:
    st.header("Analyse des 4 Saisons")
    
    st.markdown("**Sélectionnez les courbes à afficher :**")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    afficher_prod = col1.checkbox("Production", value=True)
    afficher_conso = col2.checkbox("Consommation", value=True)
    afficher_auto = col3.checkbox("Autoconsommation", value=False)
    afficher_import = col4.checkbox("Importé (Réseau)", value=False)
    afficher_export = col5.checkbox("Exporté (Réseau)", value=False)

    fig1, axes = plt.subplots(2, 2, figsize=(14, 8))
    
    dates_a_tracer = [
        (12, 20, "20 Décembre (Hiver)", axes[0,0]), 
        (3, 21, "21 Mars (Printemps)", axes[0,1]), 
        (6, 6, "6 Juin (Été)", axes[1,0]), 
        (9, 15, "15 Septembre (Automne)", axes[1,1])
    ]

    handles_globaux = []
    labels_globaux = []

    for mois, jour, titre, ax in dates_a_tracer:
        journee = mon_tableau[(mon_tableau['Date&Time'].dt.month == mois) & (mon_tableau['Date&Time'].dt.day == jour)]
        
        # --- LA MOULINETTE DE LISSAGE ---
        # 1. On traduit les heures en chiffres pour les maths
        x_dates = journee['Date&Time']
        x_num = mdates.date2num(x_dates)
        
        # 2. On crée 300 points pour rendre la courbe très fluide
        x_dense_num = np.linspace(x_num.min(), x_num.max(), 300)
        x_dense_dates = mdates.num2date(x_dense_num)

        # 3. La petite fonction magique qui arrondit SANS faire de vagues
        def lisser_courbe(y_vals):
            # On utilise Pchip au lieu de spline pour éviter les faux rebonds
            lisseur = PchipInterpolator(x_num, y_vals)
            return np.clip(lisseur(x_dense_num), 0, None)
        # --- TRACÉ DES COURBES LISSÉES ---
        if afficher_prod:
            ax.plot(x_dense_dates, lisser_courbe(journee['Inverter Output']), label='Production', color='#FFD700', linewidth=2.5)
        if afficher_conso:
            ax.plot(x_dense_dates, lisser_courbe(journee['Consumption']), label='Consommation', color='#2196F3', linewidth=2.5)

        if afficher_auto:
            y_auto_directe = lisser_courbe(journee['Autoconso_Directe'])

            ax.fill_between(
                x_dense_dates,
                y_auto_directe,
                label='Autoconso directe',
                color="#67AD17",
                alpha=0.6
            )

            if activer_batterie and 'Decharge_Batterie' in journee.columns:
                y_batterie = lisser_courbe(journee['Decharge_Batterie'])

                ax.fill_between(
                    x_dense_dates,
                    y_auto_directe,
                    y_auto_directe + y_batterie,
                    label='Via batterie',
                    color="#91FF00",
                    alpha=0.6
                )


        if afficher_import:
            ax.plot(x_dense_dates, lisser_courbe(journee['Import_Reseau']), label='Importé (Réseau)', color='#F44336', linewidth=2, linestyle='--')
        if afficher_export:
            ax.plot(x_dense_dates, lisser_courbe(journee['Export_Reseau']), label='Exporté (Réseau)', color='#FF9800', linewidth=2, linestyle='--')
            
        ax.set_title(titre)
        ax.set_ylabel('Énergie (Wh)')
        ax.grid(True, linestyle='--', alpha=0.6)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        ax.tick_params(axis='x', rotation=45)
        
        if mois == 12 and jour == 21:
            handles_globaux, labels_globaux = ax.get_legend_handles_labels()

    plt.tight_layout()
    
    if handles_globaux:
        fig1.legend(handles_globaux, labels_globaux, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=5, fontsize=11)
        fig1.subplots_adjust(top=0.88)

    st.pyplot(fig1, use_container_width=False)



# ====================================================================================================
# ONGLET 3 : Bilan mensuel
# ====================================================================================================
with tab_mensuel:
    st.header("Bilan Énergétique Mensuel")

    bilan_mensuel = mon_tableau.groupby(mon_tableau['Date&Time'].dt.month)[
        ['Consumption', 'Inverter Output', 'Autoconsommation', 'Import_Reseau', 'Export_Reseau']
    ].sum() / 1000

    mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    x = np.arange(len(mois_noms))

    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

    # Graphique consommation
    ax1.bar(x, bilan_mensuel['Autoconsommation'], width=0.6, label='Autoconsommation', color="#88FF00")
    ax1.bar(
        x,
        bilan_mensuel['Import_Reseau'],
        width=0.6,
        bottom=bilan_mensuel['Autoconsommation'],
        label='Import réseau',
        color="#FF00C8"
    )

    ax1.set_title("Répartition de la consommation",fontsize=16)
    ax1.set_ylabel("Énergie (kWh)",fontsize=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels(mois_noms)
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    totaux_conso = bilan_mensuel['Autoconsommation'] + bilan_mensuel['Import_Reseau']
    for i, total in enumerate(totaux_conso):
        ax1.text(i, total + 5, f"{total:.0f}", ha='center', va='bottom', fontsize=9)

    # Graphique production
    ax2.bar(x, bilan_mensuel['Autoconsommation'], width=0.6, label='Autoconsommation', color="#88FF00")
    ax2.bar(
        x,
        bilan_mensuel['Export_Reseau'],
        width=0.6,
        bottom=bilan_mensuel['Autoconsommation'],
        label='Export réseau',
        color="#00E1FF"
    )

    ax2.set_title("Répartition de la production",fontsize=16)
    ax2.set_ylabel("Énergie (kWh)",fontsize=14)
    ax2.set_xticks(x)
    ax2.set_xticklabels(mois_noms)
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    totaux_prod = bilan_mensuel['Autoconsommation'] + bilan_mensuel['Export_Reseau']
    for i, total in enumerate(totaux_prod):
        ax2.text(i, total + 5, f"{total:.0f}", ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.4)
    st.pyplot(fig2, use_container_width=False)



# ====================================================================================================
# ONGLET 4 : LE BILAN ANNUEL
# ====================================================================================================

with tab_annuel:
    st.header("Flux d'Énergie Annuel")

    # =========================
    # 1. CALCULS
    # =========================
    total_prod = mon_tableau['Inverter Output'].sum() / 1000
    total_conso = mon_tableau['Consumption'].sum() / 1000
    total_auto = mon_tableau['Autoconsommation'].sum() / 1000
    total_import = mon_tableau['Import_Reseau'].sum() / 1000
    total_export = mon_tableau['Export_Reseau'].sum() / 1000
    total_ess = mon_tableau['Decharge_Batterie'].sum() / 1000
    total_solaire_direct = max(0, total_auto - total_ess)

    taux_autoconso = (total_auto / total_prod * 100) if total_prod > 0 else 0
    taux_autonomie = (total_auto / total_conso * 100) if total_conso > 0 else 0
    taux_batterie = (total_ess / total_conso * 100) if total_conso > 0 else 0
    taux_reseau = (total_import / total_conso * 100) if total_conso > 0 else 0

    if 'capa_wh' in locals() and capa_wh > 0:
        nombre_cycles = total_ess / (capa_wh / 1000)
        soc_moyen = (mon_tableau['Niveau_Batterie'].mean() / capa_wh * 100)
        soc_moyen = max(0, min(100, soc_moyen))
    else:
        nombre_cycles = 0
        soc_moyen = 0

    batterie_active = total_ess > 0.1

    # =========================
    # 2. FONCTIONS SVG
    # =========================
    def polar_to_cartesian(cx, cy, r, angle_deg):
        import math
        angle_rad = math.radians(angle_deg - 90)
        return cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)

    def donut_arc(cx, cy, r, pct, color, bg="#E6E6E6", stroke=16):
        pct = max(0, min(100, pct))
        start_x, start_y = polar_to_cartesian(cx, cy, r, 0)
        end_x, end_y = polar_to_cartesian(cx, cy, r, pct * 3.6)
        large_arc = 1 if pct > 50 else 0

        bg_circle = (
            f'<circle cx="{cx}" cy="{cy}" r="{r}" '
            f'stroke="{bg}" stroke-width="{stroke}" fill="none" />'
        )

        if pct <= 0:
            fg_arc = ""
        elif pct >= 99.999:
            fg_arc = (
                f'<circle cx="{cx}" cy="{cy}" r="{r}" '
                f'stroke="{color}" stroke-width="{stroke}" fill="none" '
                f'stroke-linecap="butt" />'
            )
        else:
            fg_arc = (
                f'<path d="M {start_x:.2f} {start_y:.2f} '
                f'A {r} {r} 0 {large_arc} 1 {end_x:.2f} {end_y:.2f}" '
                f'stroke="{color}" stroke-width="{stroke}" fill="none" '
                f'stroke-linecap="butt" />'
            )
        return bg_circle + fg_arc

    def add_segment(cx, cy, r, start_pct, seg_pct, color, stroke=16):
        if seg_pct <= 0:
            return ""

        start_angle = start_pct * 3.6
        end_angle = (start_pct + seg_pct) * 3.6

        x1, y1 = polar_to_cartesian(cx, cy, r, start_angle)
        x2, y2 = polar_to_cartesian(cx, cy, r, end_angle)
        large_arc = 1 if seg_pct > 50 else 0

        if seg_pct >= 99.999:
            return (
                f'<circle cx="{cx}" cy="{cy}" r="{r}" '
                f'stroke="{color}" stroke-width="{stroke}" fill="none" />'
            )

        return (
            f'<path d="M {x1:.2f} {y1:.2f} '
            f'A {r} {r} 0 {large_arc} 1 {x2:.2f} {y2:.2f}" '
            f'stroke="{color}" stroke-width="{stroke}" fill="none" />'
        )

    # =========================
    # 3. COULEURS
    # =========================
    c_pv = "#FFAE00"
    c_batt = "#2B9930"
    c_grid = "#957CC5"
    c_direct = "#F5A623"
    c_text = "#303030"
    c_bg = "#FFFFFF"
    c_ring_bg = "#FFF27B"

    # =========================
    # 4. POURCENTAGES
    # =========================
    pv_pct = (total_auto / total_prod * 100) if total_prod > 0 else 0
    grid_pct = (total_import / (total_import + total_export) * 100) if (total_import + total_export) > 0 else 0
    batt_pct = soc_moyen if batterie_active else 0

    direct_pct_charge = (total_solaire_direct / total_conso * 100) if total_conso > 0 else 0
    batt_pct_charge = (total_ess / total_conso * 100) if total_conso > 0 else 0
    grid_pct_charge = (total_import / total_conso * 100) if total_conso > 0 else 0


    pv_injection_pct = (total_export / total_prod * 100) if total_prod > 0 else 0
    pv_auto_pct = (total_auto / total_prod * 100) if total_prod > 0 else 0

    batt_soc_pct = batt_pct
    grid_import_pct_total = grid_pct

    # =========================
    # 5. GÉOMÉTRIE
    # =========================
    W = 1000
    H = 560
    x=40

    pv_x, pv_y = 500, 105+x
    batt_x, batt_y = 205-50, 315-70+x
    load_x, load_y = 500, 355+50+x
    grid_x, grid_y = 795+50, 315-70+x

    r_main = 68
    r_side = 58

    svg_parts = []

    # fond
    svg_parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{c_bg}" rx="18"/>')

    # =========================
    # 6. CONNEXIONS
    # =========================
    svg_parts.append(f'''
        <path d="M {pv_x} {pv_y + 85} L {pv_x} {load_y - 85}"
            stroke="{c_direct}" stroke-width="4" fill="none" stroke-linecap="round"
            marker-end="url(#arrow-direct)"/>
    ''')

    if batterie_active:
        svg_parts.append(f'''
            <path d="M {pv_x - 72} {pv_y + 42}
                    L {batt_x + 78} {batt_y - 30}"
                stroke="{c_batt}" stroke-width="4" fill="none"
                stroke-linecap="round" stroke-linejoin="round"
                marker-end="url(#arrow-batt)"/>
        ''')

        svg_parts.append(f'''
            <path d="M {batt_x + 78} {batt_y + 30}
                    L {load_x - 72} {load_y - 42}"
                stroke="{c_batt}" stroke-width="4" fill="none"
                stroke-linecap="round" stroke-linejoin="round"
                marker-end="url(#arrow-batt)"/>
        ''')

    svg_parts.append(f'''
        <path d="M {pv_x + 72} {pv_y + 42}
                L {grid_x - 78} {grid_y - 30}"
            stroke="{c_grid}" stroke-width="4" fill="none"
            stroke-linecap="round" stroke-linejoin="round"
            marker-end="url(#arrow-grid)"/>
    ''')

    svg_parts.append(f'''
        <path d="M {grid_x - 78} {grid_y + 30}
                L {load_x + 72} {load_y - 42}"
            stroke="{c_grid}" stroke-width="4" fill="none"
            stroke-linecap="round" stroke-linejoin="round"
            marker-end="url(#arrow-grid)"/>
    ''')


    # =========================
    # 7. DONUT PV
    # =========================
    svg_parts.append(donut_arc(pv_x, pv_y, r_main, pv_pct, c_pv, bg=c_ring_bg, stroke=16))
    svg_parts.append(f'''
        <text x="{pv_x}" y="{pv_y - 92}" text-anchor="middle" font-size="22" font-weight="700" fill="{c_text}">PV</text>
        <text x="{pv_x}" y="{pv_y - 4}" text-anchor="middle" font-size="30">☀️</text>
        <text x="{pv_x}" y="{pv_y + 22}" text-anchor="middle" font-size="18" fill="{c_text}">{total_prod:,.0f} kWh</text>
    '''.replace(",", " "))
    svg_parts.append(f'''
    <text x="{pv_x + 92}" y="{pv_y - 8-50}" text-anchor="start" font-size="15" font-weight="600" fill="{c_grid}">
        Injection : {pv_injection_pct:.1f}%
    </text>
    <text x="{pv_x + 92}" y="{pv_y + 16-50}" text-anchor="start" font-size="15" font-weight="600" fill="{c_direct}">
        Direct : {pv_auto_pct:.1f}%
    </text>
    '''.replace(",", " "))

    # =========================
    # 8. DONUT BATTERIE
    # =========================
    if batterie_active:
        svg_parts.append(donut_arc(batt_x, batt_y, r_side, batt_pct, c_batt, bg="#E5EFE5", stroke=13))
        svg_parts.append(f'''
            <text x="{batt_x}" y="{batt_y + 4}" text-anchor="middle" font-size="28">🔋</text>
            <text x="{batt_x}" y="{batt_y + 28}" text-anchor="middle" font-size="17" fill="{c_text}">{total_ess:,.0f} kWh</text>
            <text x="{batt_x}" y="{batt_y + 94}" text-anchor="middle" font-size="18" font-weight="700" fill="{c_text}">Batterie</text>
        '''.replace(",", " "))



    # =========================
    # 9. DONUT RÉSEAU
    # =========================
    svg_parts.append(donut_arc(grid_x, grid_y, r_side, grid_pct, c_grid, bg="#EEE6F5", stroke=13))
    svg_parts.append(f'''
        <text x="{grid_x}" y="{grid_y + 4}" text-anchor="middle" font-size="28">⚡</text>
        <text x="{grid_x}" y="{grid_y + 28}" text-anchor="middle" font-size="17" fill="{c_text}">{total_import:,.0f} kWh</text>
        <text x="{grid_x}" y="{grid_y + 94}" text-anchor="middle" font-size="18" font-weight="700" fill="{c_text}">Réseau</text>
    '''.replace(",", " "))

    # =========================
    # 10. DONUT CHARGE - consommation
    # =========================
    svg_parts.append(
        f'<circle cx="{load_x}" cy="{load_y}" r="{r_main}" '
        f'stroke="{c_ring_bg}" stroke-width="16" fill="none" />'
    )

    start = 0
    svg_parts.append(add_segment(load_x, load_y, r_main, start, direct_pct_charge, c_direct, stroke=16))
    start += direct_pct_charge

    if batterie_active:
        svg_parts.append(add_segment(load_x, load_y, r_main, start, batt_pct_charge, c_batt, stroke=16))
        start += batt_pct_charge

    svg_parts.append(add_segment(load_x, load_y, r_main, start, grid_pct_charge, c_grid, stroke=16))

    svg_parts.append(f'''
        <text x="{load_x}" y="{load_y - 2}" text-anchor="middle" font-size="30">🏠</text>
        <text x="{load_x}" y="{load_y + 24}" text-anchor="middle" font-size="18" fill="{c_text}">{total_conso:,.0f} kWh</text>
        <text x="{load_x}" y="{load_y + 96}" text-anchor="middle" font-size="18" font-weight="700" fill="{c_text}">Consommation</text>
    '''.replace(",", " "))


    svg_parts.append(f'''
    <text x="{load_x + 95}" y="{load_y - 22+50}" text-anchor="start" font-size="15" font-weight="600" fill="{c_batt}">
        Batterie : {batt_pct_charge:.1f}%
    </text>
    <text x="{load_x + 95}" y="{load_y + 2+50}" text-anchor="start" font-size="15" font-weight="600" fill="{c_direct}">
        PV : {direct_pct_charge:.1f}%
    </text>
    <text x="{load_x + 95}" y="{load_y + 26+50}" text-anchor="start" font-size="15" font-weight="600" fill="{c_grid}">
        Réseau : {grid_pct_charge:.1f}%
    </text>
    '''.replace(",", " "))

# =========================
# 11. TEXTES DE FLUX
# =========================
    svg_parts.append(f'''
        <text x="{pv_x + 10}" y="292" font-size="15" fill="{c_direct}">{total_solaire_direct:,.0f} kWh</text>
        <text x="650" y="200" font-size="15" fill="{c_grid}">{total_export:,.0f} kWh</text>
    '''.replace(",", " "))

    if batterie_active:
        svg_parts.append(f'''
            <text x="285" y="390" font-size="15" fill="{c_batt}">{total_ess:,.0f} kWh</text>
        '''.replace(",", " "))
    svg_parts.append(f'''
        <text x="652" y="390" font-size="15" fill="{c_grid}">{total_import:,.0f} kWh</text>
    '''.replace(",", " "))

    # =========================
    # 12. AFFICHAGE HTML / SVG
    # =========================
    svg_html = f"""
    <div style="width:100%; display:flex; justify-content:center; padding:8px 0 0 0;">
        <svg viewBox="0 0 {W} {H}" style="width:100%; max-width:1000px; height:auto;">
            <defs>
                <marker id="arrow-direct" markerWidth="10" markerHeight="10" refX="6.5" refY="3"
                        orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L8,3 z" fill="{c_direct}" />
                </marker>

                <marker id="arrow-batt" markerWidth="10" markerHeight="10" refX="6.5" refY="3"
                        orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L8,3 z" fill="{c_batt}" />
                </marker>

                <marker id="arrow-grid" markerWidth="10" markerHeight="10" refX="6.5" refY="3"
                        orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L8,3 z" fill="{c_grid}" />
                </marker>
            </defs>

            {''.join(svg_parts)}
        </svg>
    </div>
    """

    components.html(svg_html, height=600)

    # =========================
    # 13. KPI DU BAS
    # =========================
    st.divider()
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Taux autoconso", f"{taux_autoconso:.1f}%")
    c2.metric("Taux autonomie", f"{taux_autonomie:.1f}%")
    c3.metric("Solaire direct", f"{total_solaire_direct:,.0f} kWh".replace(",", " "))
    c4.metric("Via batterie", f"{total_ess:,.0f} kWh".replace(",", " "))
    c5.metric("Importé", f"{total_import:,.0f} kWh".replace(",", " "))
    c6.metric("Cycles / an", f"{nombre_cycles:.0f}")


# CREATION FICHIER CSV DANS ONGLET 4

with tab_annuel:
    # ==========================================
    # TABLEAU DE VÉRIFICATION HORAIRE
    # ==========================================
    tableau_verification = pd.DataFrame()

    tableau_verification['Date&Time'] = mon_tableau['Date&Time']
    tableau_verification['Consommation_Wh'] = mon_tableau['Consumption']
    tableau_verification['Production_Wh'] = mon_tableau['Inverter Output']
    tableau_verification['Autoconsommation_Wh'] = mon_tableau['Autoconsommation']
    tableau_verification['Import_Reseau_Wh'] = mon_tableau['Import_Reseau']
    tableau_verification['Export_Reseau_Wh'] = mon_tableau['Export_Reseau']

    # Colonnes batterie si elles existent
    if 'Charge_Batterie' in mon_tableau.columns:
        tableau_verification['Charge_Batterie_Wh'] = mon_tableau['Charge_Batterie']
    else:
        tableau_verification['Charge_Batterie_Wh'] = 0.0

    if 'Decharge_Batterie' in mon_tableau.columns:
        tableau_verification['Decharge_Batterie_Wh'] = mon_tableau['Decharge_Batterie']
    else:
        tableau_verification['Decharge_Batterie_Wh'] = 0.0

    if 'Niveau_Batterie' in mon_tableau.columns:
        tableau_verification['Niveau_Batterie_Wh'] = mon_tableau['Niveau_Batterie']
    else:
        tableau_verification['Niveau_Batterie_Wh'] = 0.0

    # Capacité batterie identique sur toutes les lignes pour rappel
    tableau_verification['Capacite_Batterie_Wh'] = capa_wh if 'capa_wh' in locals() else 0.0

    # Optionnel : niveau batterie en %
    if 'capa_wh' in locals() and capa_wh > 0:
        tableau_verification['Niveau_Batterie_%'] = (tableau_verification['Niveau_Batterie_Wh'] / capa_wh) * 100
    else:
        tableau_verification['Niveau_Batterie_%'] = 0.0

    # Arrondir pour lecture plus propre
    colonnes_a_arrondir = [
        'Consommation_Wh',
        'Production_Wh',
        'Autoconsommation_Wh',
        'Import_Reseau_Wh',
        'Export_Reseau_Wh',
        'Charge_Batterie_Wh',
        'Decharge_Batterie_Wh',
        'Niveau_Batterie_Wh',
        'Capacite_Batterie_Wh',
        'Niveau_Batterie_%'
    ]

    for col in colonnes_a_arrondir:
        tableau_verification[col] = tableau_verification[col].round(2)

    st.divider()
    st.subheader("Tableau horaire de vérification")

    st.markdown("Ce tableau permet de contrôler heure par heure les flux énergétiques calculés.")

    # Affichage du tableau
    st.dataframe(tableau_verification, use_container_width=True, height=400)

    # Export CSV
    csv_verification = tableau_verification.to_csv(index=False, sep=';').encode('utf-8-sig')

    st.download_button(
        label="Télécharger le tableau de vérification (CSV)",
        data=csv_verification,
        file_name="tableau_verification_horaire.csv",
        mime="text/csv",
        key="download_verification_csv"
    )









# ====================================================================================================
# ONGLET 5 : LE BUDGET
# ====================================================================================================
with tab_budget:
    st.header("Investissement initial 📊")

    # =====================================================
    # 1. CALCUL DES AIDES
    # =====================================================
    puissance_crete_arrondie = round(puissance_crete, 2)

    if puissance_crete_arrondie < 15:
        aide_pv = puissance_crete_arrondie * (
            1155 - (1155 / 35) * puissance_crete_arrondie
        )
        aide_pv = round(aide_pv, 2)
        texte_aide_pv = "Installation < 15 kWc : aide calculée selon la formule."
    else:
        aide_pv = 10000.00
        texte_aide_pv = "Installation ≥ 15 kWc : aide fixée à 10 000 €."

    if activer_batterie and 'capa_kwh' in locals():
        capacite_batterie_arrondie = round(capa_kwh, 2)

        if capacite_batterie_arrondie < 9:
            aide_batterie = capacite_batterie_arrondie * (
                500 - (500 / 18) * capacite_batterie_arrondie
            )
            aide_batterie = round(aide_batterie, 2)
            texte_aide_batterie = "Batterie < 9 kWh : aide calculée selon la formule."
        else:
            aide_batterie = 2250.00
            texte_aide_batterie = "Batterie ≥ 9 kWh : aide fixée à 2 250 €."
    else:
        capacite_batterie_arrondie = 0.0
        aide_batterie = 0.0
        texte_aide_batterie = "Aucune batterie activée."

    aide_totale = round(aide_pv + aide_batterie, 2)

    # =====================================================
    # 2. CALCUL DES COÛTS
    # =====================================================
    cout_pv = puissance_crete * 1000 * st.session_state["cout_pv_par_wc"]

    if activer_batterie and 'capa_wh' in locals():
        cout_batterie = capa_wh * st.session_state["cout_batterie_par_wh"]
    else:
        cout_batterie = 0.0

    cout_pv = round(cout_pv, 2)
    cout_batterie = round(cout_batterie, 2)

    cout_total_brut = round(cout_pv + cout_batterie, 2)
    cout_total_net = round(cout_total_brut - aide_totale, 2)

    # =====================================================
    # 3. CARTES PRINCIPALES
    # =====================================================
    col_gauche, col_droite = st.columns(2)

    with col_gauche:
        components.html(f"""
        <div style="
            background: linear-gradient(180deg, #f4fbf6, #edf8f0);
            border: 1px solid #bfe3c8;
            border-radius: 18px;
            padding: 22px 24px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
            margin-bottom: 18px;
            font-family: Arial, sans-serif;
        ">
            <h3 style="margin:0 0 18px 0; font-size:24px; font-weight:700; color:#1f2c3a;">
                Aides financières
            </h3>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 18px;">
                <div>
                    <div style="font-size:20px; color:#5b6b79; margin-bottom:2px;">Aide PV ☀️</div>
                    <div style="font-size:28px; font-weight:800; color:#16283a;">{f"{aide_pv:,.2f} €".replace(",", " ")}</div>
                </div>
                <div>
                    <div style="font-size:20px; color:#5b6b79; margin-bottom:2px;">Aide batterie 🔋</div>
                    <div style="font-size:28px; font-weight:800; color:#16283a;">{f"{aide_batterie:,.2f} €".replace(",", " ")}</div>
                </div>
            </div>

            <div style="font-size:15px; color:#3f4d5a; line-height:1.6;">
                <h4 style="margin:18px 0 8px 0; font-size:18px; font-weight:700; color:#24394d;">Photovoltaïque</h4>
                <ul style="margin-top:8px; padding-left:20px;">
                    <li>Puissance prise en compte : <strong>{puissance_crete_arrondie:.2f} kWc</strong></li>
                    <li>{texte_aide_pv}</li>
                </ul>

                <h4 style="margin:18px 0 8px 0; font-size:18px; font-weight:700; color:#24394d;">Batterie</h4>
                <ul style="margin-top:8px; padding-left:20px;">
                    <li>Capacité prise en compte : <strong>{capacite_batterie_arrondie:.2f} kWh</strong></li>
                    <li>{texte_aide_batterie}</li>
                </ul>
            </div>
        </div>
        """, height=400)

    with col_droite:
        components.html(f"""
        <div style="
            background: linear-gradient(180deg, #f3f9fe, #ebf4fb);
            border: 1px solid #bfdaf0;
            border-radius: 18px;
            padding: 22px 24px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
            margin-bottom: 18px;
            font-family: Arial, sans-serif;
        ">
            <h3 style="margin:0 0 18px 0; font-size:24px; font-weight:700; color:#1f2c3a;">
                Coûts estimés
            </h3>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 18px;">
                <div>
                    <div style="font-size:20px; color:#5b6b79; margin-bottom:2px;">Coût installation PV ☀️</div>
                    <div style="font-size:28px; font-weight:800; color:#16283a;">{f"{cout_pv:,.2f} €".replace(",", " ")}</div>
                </div>
                <div>
                    <div style="font-size:20px; color:#5b6b79; margin-bottom:2px;">Coût batterie 🔋</div>
                    <div style="font-size:28px; font-weight:800; color:#16283a;">{f"{cout_batterie:,.2f} €".replace(",", " ")}</div>
                </div>
            </div>

            <div style="font-size:15px; color:#3f4d5a; line-height:1.6;">
                <h4 style="margin:18px 0 8px 0; font-size:18px; font-weight:700; color:#24394d;">Hypothèses économiques</h4>
                <ul style="margin-top:8px; padding-left:20px;">
                    <li>Coût PV : <strong>{st.session_state["cout_pv_par_wc"]:.2f} €/Wc</strong></li>
                    <li>Coût batterie : <strong>{st.session_state["cout_batterie_par_wh"]:.2f} €/Wh</strong></li>
                </ul>
            </div>
        </div>
        """, height=400)

    # =====================================================
    # 4. SYNTHÈSE FINANCIÈRE
    # =====================================================
    components.html(f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e8edf3;
        border-radius: 18px;
        padding: 22px 24px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
        margin-bottom: 18px;
        font-family: Arial, sans-serif;
    ">
        <h3 style="margin:0 0 18px 0; font-size:24px; font-weight:700; color:#1f2c3a;">
            Synthèse financière
        </h3>

        <div style="
            display:grid;
            grid-template-columns: 1fr 1fr 1fr;
            overflow:hidden;
            border-radius:14px;
            border:1px solid #d8e2eb;
        ">
            <div style="padding:14px 18px; background:linear-gradient(90deg, #eef2f7, #d9e2ec);">
                <div style="font-size:20px; color:rgba(0,0,0,0.65); margin-bottom:4px;">Coût total brut</div>
                <div style="font-size:24px; font-weight:800; color:#102030;">{f"{cout_total_brut:,.2f} €".replace(",", " ")}</div>
            </div>

            <div style="padding:14px 18px; background:linear-gradient(90deg, #7fd6a3, #43b581);">
                <div style="font-size:20px; color:white; margin-bottom:4px;">Aide totale</div>
                <div style="font-size:24px; font-weight:800; color:white;">{f"{aide_totale:,.2f} €".replace(",", " ")}</div>
            </div>

            <div style="padding:14px 18px; background:linear-gradient(90deg, #5faee3, #2f87c8);">
                <div style="font-size:20px; color:white; margin-bottom:4px;">Coût net après aides</div>
                <div style="font-size:24px; font-weight:800; color:white;">{f"{cout_total_net:,.2f} €".replace(",", " ")}</div>
            </div>
        </div>
    </div>
    """, height=250)
























# ====================================================================================================
# ONGLET 6 : ANALYSE FINANCIÈRE
# ====================================================================================================
with tab_finance:
    st.markdown('<div class="finance-section-title">Analyse financière</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="finance-section-desc">Comparaison des scénarios de valorisation de l’énergie et projection des gains cumulés sur 10 ans.</div>',
        unsafe_allow_html=True
    )

    # =====================================================
    # 1. HYPOTHÈSES DE CALCUL
    # =====================================================
    prix_electricite = st.session_state["prix_electricite"]
    prix_injection = st.session_state["prix_injection"]
    prix_communaute_achat = st.session_state["prix_communaute_achat"]
    prix_communaute_vente = st.session_state["prix_communaute_vente"]

    with st.expander("⚙️ Hypothèses de calcul", expanded=False):
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("Prix achat réseau", f"{prix_electricite:.2f} €/kWh")
        h2.metric("Prix vente réseau", f"{prix_injection:.2f} €/kWh")
        h3.metric("Prix achat communauté", f"{prix_communaute_achat:.2f} €/kWh")
        h4.metric("Prix vente communauté", f"{prix_communaute_vente:.2f} €/kWh")

    # =====================================================
    # 2. BILAN ÉNERGÉTIQUE ANNUEL
    # =====================================================
    total_conso_kwh = mon_tableau['Consumption'].sum() / 1000
    total_import_kwh = mon_tableau['Import_Reseau'].sum() / 1000
    total_export_kwh = mon_tableau['Export_Reseau'].sum() / 1000
    total_auto_directe_kwh = mon_tableau['Autoconso_Directe'].sum() / 1000
    total_batterie_kwh = mon_tableau['Decharge_Batterie'].sum() / 1000

    cout_sans_installation = round(total_conso_kwh * prix_electricite, 2)
    economie_auto_directe = round(total_auto_directe_kwh * prix_electricite, 2)
    economie_batterie = round(total_batterie_kwh * prix_electricite, 2)

    # =====================================================
    # 3. MODE NORMAL
    # =====================================================
    cout_import_normal = round(total_import_kwh * prix_electricite, 2)
    revenu_export_normal = round(total_export_kwh * prix_injection, 2)
    solde_normal = round(cout_import_normal - revenu_export_normal, 2)
    gain_normal = round(cout_sans_installation - solde_normal, 2)

    # =====================================================
    # 4. MODE COMMUNAUTÉ 100 %
    # =====================================================
    cout_import_communaute = round(total_import_kwh * prix_communaute_achat, 2)
    revenu_export_communaute = round(total_export_kwh * prix_communaute_vente, 2)
    solde_communaute = round(cout_import_communaute - revenu_export_communaute, 2)
    gain_communaute = round(cout_sans_installation - solde_communaute, 2)

    # =====================================================
    # 5. MODE COMMUNAUTÉ 50 %
    # =====================================================
    cout_import_mix = round(
        0.5 * total_import_kwh * prix_communaute_achat
        + 0.5 * total_import_kwh * prix_electricite,
        2
    )

    revenu_export_mix = round(
        0.5 * total_export_kwh * prix_communaute_vente
        + 0.5 * total_export_kwh * prix_injection,
        2
    )

    solde_mix = round(cout_import_mix - revenu_export_mix, 2)
    gain_mix = round(cout_sans_installation - solde_mix, 2)




    if gain_normal != 0:
        pct_gain_communaute = ((gain_communaute - gain_normal) / gain_normal) * 100
        pct_gain_mix = ((gain_mix - gain_normal) / gain_normal) * 100
    else:
        pct_gain_communaute = 0.0
        pct_gain_mix = 0.0

    pct_gain_communaute = round(pct_gain_communaute, 1)
    pct_gain_mix = round(pct_gain_mix, 1)



    # =====================================================
    # 6. KPI PRINCIPAUX
    # =====================================================
    if gain_normal > 0:
        tr_normal = cout_total_net / gain_normal
    else:
        tr_normal = None

    if gain_mix > 0:
        tr_mix = cout_total_net / gain_mix
    else:
        tr_mix = None

    if gain_communaute > 0:
        tr_communaute = cout_total_net / gain_communaute
    else:
        tr_communaute = None

    gain_10_ans_normal = round(gain_normal * 10, 2)
    gain_10_ans_mix = round(gain_mix * 10, 2)
    gain_10_ans_communaute = round(gain_communaute * 10, 2)

    st.subheader("Indicateurs clés")

    k1, k2, k3 = st.columns(3)

    with k1:
        st.markdown(f"""
        <div class="finance-card finance-card-blue">
            <div class="finance-title">📘 Mode normal</div>
            <div class="finance-subtitle">Gain annuel estimé</div>
            <div class="finance-big">{f"{gain_normal:,.2f} €".replace(",", " ")}</div>
            <div class="finance-small">Temps de retour : <strong>{f"{tr_normal:.1f} ans" if tr_normal is not None else "Non calculable"}</strong></div>
            <div class="finance-small">Gain cumulé à 10 ans : <strong>{f"{gain_10_ans_normal:,.2f} €".replace(",", " ")}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        components.html(f"""
        <div style="
            background: linear-gradient(180deg, #effaf1, #e5f6e8);
            border: 1px solid #bfe4c8;
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            margin-bottom: 18px;
            font-family: Arial, sans-serif;
        ">
            <div style="font-size:22px; font-weight:700; color:#1f2c3a; margin-bottom:10px;">📗 Communauté 50 %</div>

            <div style="font-size:15px; color:#4b5a68; margin-bottom:8px;">
                Gain annuel estimé
                <span style="font-size:13px; color:#4f6a5a;">
                    ({pct_gain_mix:+.1f} % par rapport au mode normal)
                </span>
            </div>

            <div style="font-size:26px; font-weight:800; color:#13283a; margin-bottom:8px;">
                {f"{gain_mix:,.2f} €".replace(",", " ")}
            </div>

            <div style="font-size:14px; color:#506070; line-height:1.5;">
                Temps de retour : <strong>{f"{tr_mix:.1f} ans" if tr_mix is not None else "Non calculable"}</strong>
            </div>
            <div style="font-size:14px; color:#506070; line-height:1.5;">
                Gain cumulé à 10 ans : <strong>{f"{gain_10_ans_mix:,.2f} €".replace(",", " ")}</strong>
            </div>
        </div>
        """, height=220)

    with k3:
        components.html(f"""
        <div style="
            background: linear-gradient(180deg, #fff6ec, #ffefdf);
            border: 1px solid #ffd4a8;
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            margin-bottom: 18px;
            font-family: Arial, sans-serif;
        ">
            <div style="font-size:22px; font-weight:700; color:#1f2c3a; margin-bottom:10px;">📙 Communauté</div>

            <div style="font-size:15px; color:#4b5a68; margin-bottom:8px;">
                Gain annuel estimé
                <span style="font-size:13px; color:#7a5a3b;">
                    ({pct_gain_communaute:+.1f} % par rapport au mode normal)
                </span>
            </div>

            <div style="font-size:26px; font-weight:800; color:#13283a; margin-bottom:8px;">
                {f"{gain_communaute:,.2f} €".replace(",", " ")}
            </div>

            <div style="font-size:14px; color:#506070; line-height:1.5;">
                Temps de retour : <strong>{f"{tr_communaute:.1f} ans" if tr_communaute is not None else "Non calculable"}</strong>
            </div>
            <div style="font-size:14px; color:#506070; line-height:1.5;">
                Gain cumulé à 10 ans : <strong>{f"{gain_10_ans_communaute:,.2f} €".replace(",", " ")}</strong>
            </div>
        </div>
        """, height=220)

    


    st.markdown(f"""
    <div class="finance-roi-box">
        <div class="finance-title">⏱ Temps de retour estimé (mode normal)</div>
        <div class="finance-big">{f"{tr_normal:.1f} ans" if tr_normal is not None else "Non calculable"}</div>
        <div class="finance-small">
            Économies annuelles via autoconsommation directe : <strong>{f"{economie_auto_directe:,.2f} €".replace(",", " ")}</strong><br>
            Économies annuelles via batterie : <strong>{f"{economie_batterie:,.2f} €".replace(",", " ")}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
 









    st.markdown("---")
    st.subheader("📈 Projection des gains cumulés sur 15 ans")

    nb_annees = 15
    annees = np.arange(1, nb_annees + 1)

    gains_cumules_normal = gain_normal * annees
    gains_cumules_mix = gain_mix * annees
    gains_cumules_communaute = gain_communaute * annees

    fig_compare, ax = plt.subplots(figsize=(8, 4))

    ax.plot(
        annees,
        gains_cumules_normal,
        linewidth=2.5,
        marker='o',
        label="Mode normal"
    )

    ax.plot(
        annees,
        gains_cumules_mix,
        linewidth=2.5,
        marker='o',
        label="Communauté 50 %"
    )

    ax.plot(
        annees,
        gains_cumules_communaute,
        linewidth=2.5,
        marker='o',
        label="Communauté"
    )

    ax.axhline(
        y=cout_total_net,
        linewidth=2,
        linestyle='--',
        label="Coût net après aides"
    )

    ax.set_title("Gains cumulés sur 15 ans", fontsize=14)
    ax.set_xlabel("Année", fontsize=11)
    ax.set_ylabel("Montant (€)", fontsize=11)
    ax.set_xticks(annees)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(fontsize=6)

    st.pyplot(fig_compare, use_container_width=False)







    st.markdown("---")

    with st.expander("📘 Détail – Mode normal", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Facture sans installation", f"{cout_sans_installation:,.2f} €".replace(",", " "))
        c2.metric("Coût imports", f"{cout_import_normal:,.2f} €".replace(",", " "))
        c3.metric("Revenu export", f"{revenu_export_normal:,.2f} €".replace(",", " "))
        c4.metric("Gain annuel estimé", f"{gain_normal:,.2f} €".replace(",", " "))

        c5, c6, c7 = st.columns(3)
        c5.metric("Économie autoconsommation directe", f"{economie_auto_directe:,.2f} €".replace(",", " "))
        c6.metric("Économie via batterie", f"{economie_batterie:,.2f} €".replace(",", " "))
        c7.metric("Solde annuel", f"{solde_normal:,.2f} €".replace(",", " "))

    with st.expander("📗 Détail – Communauté 50 %", expanded=False):
        e1, e2, e3, e4 = st.columns(4)
        e1.metric("Facture sans installation", f"{cout_sans_installation:,.2f} €".replace(",", " "))
        e2.metric("Coût imports mixte", f"{cout_import_mix:,.2f} €".replace(",", " "))
        e3.metric("Revenu ventes mixte", f"{revenu_export_mix:,.2f} €".replace(",", " "))
        e4.metric("Gain annuel estimé", f"{gain_mix:,.2f} €".replace(",", " "))

        e5, e6 = st.columns(2)
        e5.metric("Solde annuel mixte", f"{solde_mix:,.2f} €".replace(",", " "))
        e6.metric("Gain cumulé 10 ans", f"{gain_10_ans_mix:,.2f} €".replace(",", " "))

    with st.expander("📙 Détail – Communauté", expanded=False):
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Facture sans installation", f"{cout_sans_installation:,.2f} €".replace(",", " "))
        d2.metric("Coût imports communauté", f"{cout_import_communaute:,.2f} €".replace(",", " "))
        d3.metric("Revenu vente communauté", f"{revenu_export_communaute:,.2f} €".replace(",", " "))
        d4.metric("Gain annuel estimé", f"{gain_communaute:,.2f} €".replace(",", " "))

        d5, d6 = st.columns(2)
        d5.metric("Solde annuel communauté", f"{solde_communaute:,.2f} €".replace(",", " "))
        d6.metric("Gain cumulé 10 ans", f"{gain_10_ans_communaute:,.2f} €".replace(",", " "))

















# ====================================================================================================
# ONGLET 6 : PARAMETRES PRIVES
# ====================================================================================================

MOT_DE_PASSE_CONFIG = "1234"

with tab_config:
    st.header("Paramètres avancés")

    # -----------------------------------------------------
    # Accès protégé par mot de passe
    # -----------------------------------------------------
    if not st.session_state["acces_config"]:
        mot_de_passe = st.text_input("Entrez le mot de passe", type="password")

        if st.button("Valider le mot de passe"):
            if mot_de_passe == MOT_DE_PASSE_CONFIG:
                st.session_state["acces_config"] = True
                st.success("Accès autorisé")
                st.rerun()
            else:
                st.error("Mot de passe incorrect")

    else:
        st.success("Accès autorisé aux paramètres avancés")

        # -------------------------------------------------
        # Hypothèses économiques
        # -------------------------------------------------
        st.subheader("Hypothèses économiques")

        st.session_state["cout_pv_par_wc"] = st.number_input(
            "Coût installation PV (€/Wc)",
            min_value=0.0,
            value=st.session_state["cout_pv_par_wc"],
            step=0.05
        )

        st.session_state["cout_batterie_par_wh"] = st.number_input(
            "Coût batterie (€/Wh utile)",
            min_value=0.0,
            value=st.session_state["cout_batterie_par_wh"],
            step=0.05
        )


        # -------------------------------------------------
        # Paramètres énergie
        # -------------------------------------------------
        st.subheader("Paramètres énergie")

        st.session_state["prix_electricite"] = st.number_input(
            "Prix achat électricité (€/kWh)",
            min_value=0.0,
            value=st.session_state["prix_electricite"],
            step=0.01
        )

        st.session_state["prix_injection"] = st.number_input(
            "Prix injection (€/kWh)",
            min_value=0.0,
            value=st.session_state["prix_injection"],
            step=0.01
        )



        st.session_state["prix_communaute_achat"] = st.number_input(
            "Prix d'achat communauté (€/kWh)",
            min_value=0.0,
            value=st.session_state["prix_communaute_achat"],
            step=0.01
        )

        st.session_state["prix_communaute_vente"] = st.number_input(
            "Prix de vente communauté (€/kWh)",
            min_value=0.0,
            value=st.session_state["prix_communaute_vente"],
            step=0.01
        )




        # -------------------------------------------------
        # Fermeture de l'accès
        # -------------------------------------------------
        if st.button("Fermer l'accès"):
            st.session_state["acces_config"] = False
            st.rerun()





