# ==========================================
# IMPORTS
# ==========================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
from scipy.interpolate import PchipInterpolator
import plotly.graph_objects as go
import streamlit.components.v1 as components
import textwrap
from pathlib import Path

import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO

from reportlab.lib.utils import ImageReader

# ==========================================
# CHEMINS / CONSTANTES
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
logo_path = BASE_DIR / "logo.jpg"
conso_path = BASE_DIR / "consommation.csv"
batteries_path = BASE_DIR / "batteries.xlsx"
panneau_path = BASE_DIR / "panneau.jpg"
prod_excel_path = BASE_DIR / "production.xlsx"

MOT_DE_PASSE_CONFIG = "1234"

# ==========================================
# INITIALISATION
# ==========================================
def initialiser_page():
    st.set_page_config(page_title="Simulateur PV", layout="wide")

def initialiser_session_state():
    valeurs_defaut = {
        "acces_config": False,
        "cout_pv_par_wc": 1.50,
        "cout_batterie_par_wh": 0.75,
        "prix_electricite": 0.25,
        "prix_injection": 0.05,
        "prix_communaute_achat": 0.25,
        "prix_communaute_vente": 0.15,
        "aide_pv_active": True,
        "aide_batterie_active": True,
    }

    for cle, valeur in valeurs_defaut.items():
        if cle not in st.session_state:
            st.session_state[cle] = valeur

# ==========================================
# CSS
# ==========================================
def injecter_css():
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
# FONCTIONS UTILITAIRES
# ==========================================
def parse_horaires_borne(h_str):
    plages = []
    try:
        for bloc in str(h_str).split(";"):
            debut, fin = map(int, bloc.split("-"))
            if 0 <= debut <= 23 and 0 <= fin <= 24 and debut < fin:
                plages.append((debut, fin))
    except Exception:
        pass
    return plages

def duree_totale_horaires(h_str):
    duree = 0
    try:
        for bloc in str(h_str).split(";"):
            debut, fin = map(int, bloc.split("-"))
            if 0 <= debut <= 23 and 0 <= fin <= 24 and debut < fin:
                duree += (fin - debut)
    except Exception:
        pass
    return duree

def generer_profil_borne(date_series, puissance_borne_kw, horaires_borne, jours_selectionnes):
    puissance_borne_wh = puissance_borne_kw * 1000
    plages = parse_horaires_borne(horaires_borne)

    mapping_jours = {
        "Lundi": 0,
        "Mardi": 1,
        "Mercredi": 2,
        "Jeudi": 3,
        "Vendredi": 4,
        "Samedi": 5,
        "Dimanche": 6
    }

    jours_actifs = {mapping_jours[j] for j in jours_selectionnes}

    profil = []

    for dt in pd.to_datetime(date_series):
        heure = dt.hour
        jour_semaine = dt.weekday()

        actif_jour = jour_semaine in jours_actifs

        actif_heure = False
        if actif_jour:
            for debut, fin in plages:
                if debut <= heure < fin:
                    actif_heure = True
                    break

        if actif_heure:
            profil.append(puissance_borne_wh)
        else:
            profil.append(0.0)

    return np.array(profil)

def profil_solaire_journalier(mois, heure):
    lever_coucher = {
        1: (8, 16),
        2: (7, 17),
        3: (7, 18),
        4: (6, 20),
        5: (6, 21),
        6: (5, 22),
        7: (5, 22),
        8: (6, 21),
        9: (7, 20),
        10: (7, 18),
        11: (8, 17),
        12: (8, 16),
    }

    lever, coucher = lever_coucher.get(mois, (8, 16))

    if heure < lever or heure > coucher:
        return 0.0

    duree = coucher - lever
    if duree <= 0:
        return 0.0

    x = (heure - lever) / duree
    val = np.sin(np.pi * x)**3

    return max(val, 0.0)

def generer_production_theorique_horaire(puissance_crete, prod_specifique, prod_mensuelle_kwh):
    date_index = pd.date_range(
        start="2025-01-01 00:00:00",
        periods=365 * 24,
        freq="h"
    )

    df = pd.DataFrame({"Date&Time": date_index})
    df["Mois"] = df["Date&Time"].dt.month
    df["Heure"] = df["Date&Time"].dt.hour

    prod_mensuelle_kwh = np.array(prod_mensuelle_kwh, dtype=float)

    # sécurité si la liste est vide ou incorrecte
    if len(prod_mensuelle_kwh) != 12 or prod_mensuelle_kwh.sum() <= 0:
        production_annuelle_kwh = puissance_crete * prod_specifique
        coeffs_defaut = np.array([0.03, 0.05, 0.08, 0.10, 0.12, 0.13,
                                  0.13, 0.12, 0.09, 0.07, 0.05, 0.03])
        prod_mensuelle_kwh = coeffs_defaut * production_annuelle_kwh

    prod_mensuelle_wh = {
        mois: prod_mensuelle_kwh[mois - 1] * 1000
        for mois in range(1, 13)
    }

    production_horaire = []

    for mois in range(1, 13):
        masque_mois = df["Mois"] == mois
        df_mois = df.loc[masque_mois].copy()

        profil_brut = df_mois["Heure"].apply(lambda h: profil_solaire_journalier(mois, h)).values
        somme_profil = profil_brut.sum()

        if somme_profil <= 0:
            profil_mois = np.zeros(len(df_mois))
        else:
            profil_mois = profil_brut / somme_profil * prod_mensuelle_wh[mois]

        production_horaire.extend(profil_mois)

    df["Inverter Output"] = np.array(production_horaire)

    return df[["Date&Time", "Inverter Output"]]

def simuler_batterie(production_wh, consommation_wh, capacite_max_wh, puissance_max_w):
    niveau_actuel = 0.0
    niveaux, charges, decharges, exports, achats = [], [], [], [], []

    for prod, conso in zip(production_wh, consommation_wh):
        autoconso_directe = min(prod, conso)
        surplus = prod - autoconso_directe
        manque = conso - autoconso_directe

        charge, decharge, export, achat = 0.0, 0.0, 0.0, 0.0

        if surplus > 0:
            charge = min(surplus, puissance_max_w, capacite_max_wh - niveau_actuel)
            niveau_actuel += charge
            export = surplus - charge

        elif manque > 0:
            decharge = min(manque, puissance_max_w, niveau_actuel)
            niveau_actuel -= decharge
            achat = manque - decharge

        niveaux.append(niveau_actuel)
        charges.append(charge)
        decharges.append(decharge)
        exports.append(export)
        achats.append(achat)

    return niveaux, charges, decharges, exports, achats

def parse_h(h_str):
    p = np.zeros(24)
    try:
        for b in str(h_str).split(';'):
            d, f = map(int, b.split('-'))
            if 0 <= d <= 23 and 0 <= f <= 24 and d < f:
                p[d:f] = 1
    except Exception:
        pass
    return p

def afficher_apercu_production(mon_tableau_prod, titre="Aperçu production"):
    st.markdown("---")
    st.subheader(titre)

    if mon_tableau_prod is None or mon_tableau_prod.empty:
        st.warning("Aucune donnée de production disponible pour l’aperçu.")
        return

    df = mon_tableau_prod.copy()
    df["Date&Time"] = pd.to_datetime(df["Date&Time"], errors="coerce")
    df = df.dropna(subset=["Date&Time"]).copy()

    if "Inverter Output" not in df.columns:
        st.warning("La colonne 'Inverter Output' est introuvable.")
        return

    df["Inverter Output"] = pd.to_numeric(df["Inverter Output"], errors="coerce").fillna(0)

    total_kwh = df["Inverter Output"].sum() / 1000
    puissance_max_w = df["Inverter Output"].max()
    production_jour_moyenne_kwh = total_kwh / 365 if len(df) >= 24 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Production annuelle", f"{total_kwh:,.0f} kWh".replace(",", " "))
    c2.metric("Puissance max", f"{puissance_max_w:,.0f} W".replace(",", " "))
    c3.metric("Production / jour moyen", f"{production_jour_moyenne_kwh:.1f} kWh")

    # --- Courbes jour type été / hiver
    jour_ete = df[
        (df["Date&Time"].dt.month == 6) &
        (df["Date&Time"].dt.day == 21)
    ].copy()

    jour_hiver = df[
        (df["Date&Time"].dt.month == 12) &
        (df["Date&Time"].dt.day == 21)
    ].copy()

    # --- Répartition mensuelle
    prod_mensuelle = df.groupby(df["Date&Time"].dt.month)["Inverter Output"].sum() / 1000
    prod_mensuelle = prod_mensuelle.reindex(range(1, 13), fill_value=0)

    fig_prod, (ax_jour, ax_mois) = plt.subplots(1, 2, figsize=(14, 4))

    if not jour_ete.empty:
        ax_jour.plot(
            jour_ete["Date&Time"].dt.hour,
            jour_ete["Inverter Output"],
            linewidth=2.5,
            label="Type été "
        )

    if not jour_hiver.empty:
        ax_jour.plot(
            jour_hiver["Date&Time"].dt.hour,
            jour_hiver["Inverter Output"],
            linewidth=2.5,
            linestyle="--",
            label="Type hiver "
        )

    ax_jour.set_title("Production sur un jour type")
    ax_jour.set_xlabel("Heure")
    ax_jour.set_ylabel("Puissance (W)")
    ax_jour.set_xticks(range(0, 24, 2))
    ax_jour.grid(True, linestyle="--", alpha=0.6)
    ax_jour.legend()

    mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

    ax_mois.bar(mois_noms, prod_mensuelle.values, color="#FFD54F", edgecolor="black", alpha=0.85)
    ax_mois.set_title("Production Mensuelle Totale")
    ax_mois.set_xlabel("Mois")
    ax_mois.set_ylabel("Énergie (kWh)")
    ax_mois.grid(axis="y", linestyle="--", alpha=0.6)

    plt.tight_layout()
    st.pyplot(fig_prod)

def trouver_meilleure_puissance_reference(mon_tableau):
    puissances_reference = [3, 7, 12, 17, 27, 43, 70, 100, 150, 200]

    meilleurs_resultats = []
    for p_ref in puissances_reference:
        res = calcul_frais_reseau(mon_tableau, p_ref)
        meilleurs_resultats.append({
            "puissance_reference_kw": p_ref,
            "redevance_fixe_annuelle": res["redevance_fixe_annuelle"],
            "redevance_volumetrique": res["redevance_volumetrique"],
            "depassement_total_kwh": res["depassement_total_kwh"],
            "cout_depassement_total": res["cout_depassement_total"],
            "cout_total_reseau": res["cout_total_reseau"]
        })

    df_res = pd.DataFrame(meilleurs_resultats)
    idx_min = df_res["cout_total_reseau"].idxmin()

    return df_res, df_res.loc[idx_min].to_dict()

# ==========================================
# FONCTION SAUVEGARDE PDF
# ==========================================

def construire_donnees_projet():
    projet = {
        "puissance_crete": st.session_state.get("puissance_crete", 10.0),
        "augmentation_prod_pct": st.session_state.get("augmentation_prod_pct", 0.0),
        "borne_active": st.session_state.get("borne_active", False),
        "puissance_borne_kw": st.session_state.get("puissance_borne_kw", 11.0),
        "horaires_borne": st.session_state.get("horaires_borne", "18-20"),
        "jours_selectionnes": st.session_state.get("jours_selectionnes", ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]),
        "chauffe_eau_actif": st.session_state.get("chauffe_eau_actif", False),
        "puissance_chauffe_eau_kw": st.session_state.get("puissance_chauffe_eau_kw", 2.0),
        "horaires_chauffe_eau": st.session_state.get("horaires_chauffe_eau", "6-8;18-20"),
        "jours_chauffe_eau": st.session_state.get("jours_chauffe_eau", ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]),
        "pac_active": st.session_state.get("pac_active", False),
        "puissance_pac_kw": st.session_state.get("puissance_pac_kw", 2.5),
        "horaires_pac": st.session_state.get("horaires_pac", "6-9;17-22"),
        "jours_pac": st.session_state.get("jours_pac", ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]),
        "chauffage_active": st.session_state.get("chauffage_active", False),
        "puissance_chauffage_kw": st.session_state.get("puissance_chauffage_kw", 1.5),
        "horaires_chauffage": st.session_state.get("horaires_chauffage", "6-8;19-22"),
        "jours_chauffage": st.session_state.get("jours_chauffage", ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]),
        "aide_pv_active": st.session_state.get("aide_pv_active", True),
        "aide_batterie_active": st.session_state.get("aide_batterie_active", True),
        "mode_prod": st.session_state.get("mode_prod", "CSV SolarEdge"),
        "mode_conso": st.session_state.get("mode_conso", "Profils types (Fichier CSV)"),
        "prod_specifique": st.session_state.get("prod_specifique", 900.0),
        "activer_batterie": st.session_state.get("activer_batterie", False),
        "choix_batterie": st.session_state.get("choix_batterie", None),
        "profil_choisi": st.session_state.get("profil_choisi", None),
        "appareils_personnalises": st.session_state.get("appareils_personnalises", []),
        "coeffs_mensuels_conso": st.session_state.get("coeffs_mensuels_conso", [1.0] * 12),
    }

    return projet

def generer_pdf_resume(
    data_import,
    sidebar_data,
    indicateurs,
    budget,
    finance_pv,
    finance_pv_batt,
    scenario_batterie_disponible,
    mon_tableau,
    budget_pv,
    budget_pv_batt,
    numero_projet="P-2026-001",
    nom_client="",
    prenom_client="",
    adresse_projet=""
):
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    marge_gauche = 40
    y = height - 40

    bleu = colors.HexColor("#2F87C8")
    vert = colors.HexColor("#43B581")
    gris = colors.HexColor("#4F5B66")
    noir = colors.black
    gris_clair = colors.HexColor("#EAF2F8")

    def dessiner_titre(texte, y_pos):
        pdf.setFillColor(bleu)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(marge_gauche, y_pos, texte)
        pdf.setStrokeColor(bleu)
        pdf.line(marge_gauche, y_pos - 4, width - 40, y_pos - 4)

    def ligne_info(label, valeur, y_pos, label_width=170):
        pdf.setFillColor(noir)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(marge_gauche, y_pos, label)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(marge_gauche + label_width, y_pos, str(valeur))

    def check_page(y_pos, min_y=80):
        if y_pos < min_y:
            pdf.showPage()
            return height - 40
        return y_pos

    # Bandeau haut
    pdf.setFillColor(bleu)
    pdf.rect(0, height - 70, width, 70, fill=1, stroke=0)

    if logo_path.exists():
        try:
            pdf.drawImage(str(logo_path), 5, height - 40, width=140, height=50, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(150, height - 40, "Rapport de simulation photovoltaïque")

    y = height - 95

    # Bloc infos générales
    pdf.setFillColor(gris_clair)
    pdf.roundRect(35, y - 90, width - 70, 85, 10, fill=1, stroke=0)

    pdf.setFillColor(noir)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(45, y - 20, "Informations du projet")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(45, y - 40, f"Numéro de projet : {numero_projet}")
    pdf.drawString(45, y - 58, f"Client : {prenom_client} {nom_client}".strip())
    pdf.drawString(45, y - 76, f"Adresse : {adresse_projet}")

    y -= 120

    # Résumé projet
    dessiner_titre("1. Paramètres du projet", y)
    y -= 25
    ligne_info("Puissance crête", f"{data_import['puissance_crete']:.2f} kWc", y)
    y -= 18
    ligne_info("Mode de production", data_import["mode_prod"], y)
    y -= 18
    ligne_info("Mode de consommation", data_import["mode_conso"], y)
    y -= 18
    ligne_info("Augmentation de production", f"{sidebar_data['augmentation_prod_pct']:.1f} %", y)
    y -= 30

    y = check_page(y)

    # Résultats énergétiques
    dessiner_titre("2. Résultats énergétiques", y)
    y -= 25
    ligne_info("Production annuelle", f"{indicateurs['total_prod']:.0f} kWh", y)
    y -= 18
    ligne_info("Consommation annuelle", f"{indicateurs['total_conso']:.0f} kWh", y)
    y -= 18
    ligne_info("Autoconsommation", f"{indicateurs['total_auto']:.0f} kWh", y)
    y -= 18
    ligne_info("Import réseau", f"{indicateurs['total_import']:.0f} kWh", y)
    y -= 18
    ligne_info("Export réseau", f"{indicateurs['total_export']:.0f} kWh", y)
    y -= 18
    ligne_info("Taux d'autoconsommation", f"{indicateurs['taux_autoconso']:.1f} %", y)
    y -= 18
    ligne_info("Taux d'autonomie", f"{indicateurs['taux_autonomie']:.1f} %", y)
    y -= 30

    y = check_page(y)

    # Détail consommation
    dessiner_titre("3. Détail de la consommation", y)
    y -= 25
    ligne_info("Consommation de base", f"{indicateurs.get('total_conso_base', 0):.0f} kWh", y)
    y -= 18
    ligne_info("Borne de recharge", f"{indicateurs.get('total_borne', 0):.0f} kWh", y)
    y -= 18
    ligne_info("Chauffe-eau", f"{indicateurs.get('total_chauffe_eau', 0):.0f} kWh", y)
    y -= 18
    ligne_info("Pompe à chaleur", f"{indicateurs.get('total_pac', 0):.0f} kWh", y)
    y -= 18
    ligne_info("Chauffage électrique", f"{indicateurs.get('total_chauffage', 0):.0f} kWh", y)
    y -= 30

    y = check_page(y)

    # Budget
    dessiner_titre("4. Budget", y)
    y -= 25
    ligne_info("Coût total brut", f"{budget['cout_total_brut']:.2f} EUR", y)
    y -= 18
    ligne_info("Aide totale", f"{budget['aide_totale']:.2f} EUR", y)
    y -= 18
    ligne_info("Coût net après aides", f"{budget['cout_total_net']:.2f} EUR", y)
    y -= 30

    y = check_page(y)

    # Analyse financière
    dessiner_titre("5. Analyse financière", y)
    y -= 25
    ligne_info("Gain annuel PV", f"{finance_pv['gain_normal']:.2f} EUR", y)
    y -= 18
    ligne_info(
        "ROI PV",
        f"{finance_pv['tr_normal']:.1f} ans" if finance_pv["tr_normal"] is not None else "Non calculable",
        y
    )
    y -= 18

    if scenario_batterie_disponible and finance_pv_batt is not None:
        ligne_info("Gain annuel PV + batterie", f"{finance_pv_batt['gain_normal']:.2f} EUR", y)
        y -= 18
        ligne_info(
            "ROI PV + batterie",
            f"{finance_pv_batt['tr_normal']:.1f} ans" if finance_pv_batt["tr_normal"] is not None else "Non calculable",
            y
        )
        y -= 18




    y = check_page(y, min_y=300)

    dessiner_titre("6. Graphiques", y)
    y -= 25

    # Graphique mensuel
    img_bilan = ImageReader(generer_graphique_bilan_mensuel(mon_tableau))
    pdf.drawImage(img_bilan, 40, y - 220, width=520, height=220, preserveAspectRatio=True, mask='auto')
    y -= 240

    y = check_page(y, min_y=300)

    img_roi = ImageReader(
        generer_graphique_roi(
            finance_pv=finance_pv,
            budget_pv=budget_pv,
            finance_pv_batt=finance_pv_batt if scenario_batterie_disponible else None,
            budget_pv_batt=budget_pv_batt if scenario_batterie_disponible else None
        )
    )
    pdf.drawImage(img_roi, 40, y - 220, width=520, height=220, preserveAspectRatio=True, mask='auto')
    y -= 240



    # Pied de page
    pdf.setFillColor(gris)
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(40, 25, "Rapport généré automatiquement par le simulateur photovoltaïque")

    pdf.save()
    buffer.seek(0)
    return buffer



def generer_graphique_bilan_mensuel(mon_tableau):
    bilan_mensuel = mon_tableau.groupby(mon_tableau['Date&Time'].dt.month)[
        ['Consumption', 'Inverter Output', 'Autoconsommation', 'Import_Reseau', 'Export_Reseau']
    ].sum() / 1000

    bilan_mensuel = bilan_mensuel.reindex(range(1, 13), fill_value=0)

    mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

    fig, ax = plt.subplots(figsize=(9, 4.5))

    ax.bar(mois_noms, bilan_mensuel['Autoconsommation'], label='Autoconsommation')
    ax.bar(
        mois_noms,
        bilan_mensuel['Import_Reseau'],
        bottom=bilan_mensuel['Autoconsommation'],
        label='Import réseau'
    )

    ax.set_title("Répartition mensuelle de la consommation")
    ax.set_ylabel("Énergie (kWh)")
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.legend()

    plt.tight_layout()

    image_buffer = BytesIO()
    fig.savefig(image_buffer, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig)
    image_buffer.seek(0)

    return image_buffer

def generer_graphique_roi(finance_pv, budget_pv, finance_pv_batt=None, budget_pv_batt=None):
    nb_annees = 15
    annees = np.arange(1, nb_annees + 1)

    fig, ax = plt.subplots(figsize=(9, 4.5))

    gains_cumules_pv = finance_pv["gain_normal"] * annees
    ax.plot(annees, gains_cumules_pv, marker='o', linewidth=2, label="Avec PV")
    ax.axhline(y=budget_pv["cout_total_net"], linestyle='--', linewidth=2, label="Coût net PV")

    if finance_pv_batt is not None and budget_pv_batt is not None:
        gains_cumules_pv_batt = finance_pv_batt["gain_normal"] * annees
        ax.plot(annees, gains_cumules_pv_batt, marker='o', linewidth=2, label="Avec PV + batterie")
        ax.axhline(y=budget_pv_batt["cout_total_net"], linestyle=':', linewidth=2, label="Coût net PV + batterie")

    ax.set_title("Projection des gains cumulés")
    ax.set_xlabel("Année")
    ax.set_ylabel("Montant (€)")
    ax.set_xticks(annees)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()

    plt.tight_layout()

    image_buffer = BytesIO()
    fig.savefig(image_buffer, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig)
    image_buffer.seek(0)

    return image_buffer



def charger_projet_json(fichier_json):
    try:
        projet = json.load(fichier_json)

        st.session_state["projet_a_charger"] = projet
        st.success("Projet chargé. Application des paramètres...")
        st.rerun()

    except Exception as e:
        st.error(f"Erreur lors de l'import du projet : {e}")

# ==========================================
# CHARGEMENT DES DONNÉES
# ==========================================

def charger_batteries():
    try:
        df_batteries = pd.read_excel(batteries_path)
        df_batteries = df_batteries.dropna(subset=['Energie util', 'P charge / décharge'])
        return df_batteries
    except Exception:
        return pd.DataFrame()

def charger_production(mode_prod, fichier_prod, puissance_crete, prod_specifique=None, df_repartition=None, colonne_prod=None):
    if mode_prod == "CSV SolarEdge":
        donnees_prod = pd.read_csv(fichier_prod, sep=",", skiprows=[1], index_col=False)
        donnees_prod = donnees_prod[donnees_prod['Date&Time'].astype(str).str.contains('-', na=False)]
        donnees_prod['Date&Time'] = donnees_prod['Date&Time'].astype(str) + " 2024"
        donnees_prod['Date&Time'] = pd.to_datetime(
            donnees_prod['Date&Time'],
            format='%d-%b %H:%M:%S %Y',
            errors='coerce'
        )

        mon_tableau = donnees_prod[['Date&Time', 'Inverter Output']].copy()
        mon_tableau['Inverter Output'] = pd.to_numeric(
            mon_tableau['Inverter Output'],
            errors='coerce'
        ).fillna(0)

        return mon_tableau

    elif mode_prod == "Fichier simple Excel":
        donnees_prod = pd.read_excel(fichier_prod)

        donnees_prod['Date&Time'] = pd.to_datetime(donnees_prod.iloc[:, 0], errors='coerce')

        if colonne_prod is not None:
            donnees_prod['Inverter Output'] = pd.to_numeric(
                donnees_prod[colonne_prod],
                errors='coerce'
            ).fillna(0)
        else:
            donnees_prod['Inverter Output'] = pd.to_numeric(
                donnees_prod.iloc[:, 1],
                errors='coerce'
            ).fillna(0)

        donnees_prod = donnees_prod.dropna(subset=['Date&Time']).copy()

        return donnees_prod[['Date&Time', 'Inverter Output']].copy()

    else:
        prod_mensuelle_kwh = pd.to_numeric(
            df_repartition["Production (kWh)"], errors="coerce"
        ).fillna(0).tolist()

        return generer_production_theorique_horaire(
            puissance_crete=puissance_crete,
            prod_specifique=prod_specifique,
            prod_mensuelle_kwh=prod_mensuelle_kwh
        )

def construire_tableau_principal(
    mode_prod,
    fichier_prod,
    puissance_crete,
    prod_specifique,
    df_repartition,
    augmentation_prod_pct,
    mode_conso,
    donnees_conso,
    profil_choisi,
    profil_24h_custom,
    profil_24h_semaine,
    profil_24h_weekend,
    coeffs_mensuels_conso,
    borne_active,
    puissance_borne_kw,
    horaires_borne,
    jours_selectionnes,
    chauffe_eau_actif,
    puissance_chauffe_eau_kw,
    horaires_chauffe_eau,
    jours_chauffe_eau,
    pac_active,
    puissance_pac_kw,
    horaires_pac,
    jours_pac,
    chauffage_active,
    puissance_chauffage_kw,
    horaires_chauffage,
    jours_chauffage,
    activer_batterie,
    capa_wh,
    puiss_w,
    colonne_prod
):

    mon_tableau = charger_production(
        mode_prod=mode_prod,
        fichier_prod=fichier_prod,
        puissance_crete=puissance_crete,
        prod_specifique=prod_specifique,
        df_repartition=df_repartition,
        colonne_prod=colonne_prod
    )

    facteur_augmentation_prod = 1 + augmentation_prod_pct / 100
    mon_tableau['Inverter Output'] = mon_tableau['Inverter Output'] * facteur_augmentation_prod

    if mode_conso == "Calculateur personnalisé (Tableau)":
        conso_base = []

        for dt in pd.to_datetime(mon_tableau["Date&Time"]):
            coeff_mois = coeffs_mensuels_conso[dt.month - 1]

            if dt.weekday() < 5:
                valeur = profil_24h_semaine[dt.hour]
            else:
                valeur = profil_24h_weekend[dt.hour]

            conso_base.append(valeur * coeff_mois)

        mon_tableau["Consumption_base"] = np.array(conso_base)
    else:

        if donnees_conso is not None and profil_choisi is not None:
            valeurs_conso = pd.to_numeric(
                donnees_conso[profil_choisi],
                errors='coerce'
            ).fillna(0).values

            if len(valeurs_conso) < len(mon_tableau):
                valeurs_conso = np.pad(
                    valeurs_conso,
                    (0, len(mon_tableau) - len(valeurs_conso)),
                    mode='constant',
                    constant_values=0
                )
            else:
                valeurs_conso = valeurs_conso[:len(mon_tableau)]

            mon_tableau["Consumption_base"] = valeurs_conso
        else:
            mon_tableau["Consumption_base"] = 0.0

    if borne_active:
        mon_tableau["Conso_Borne"] = generer_profil_borne(
            mon_tableau["Date&Time"],
            puissance_borne_kw=puissance_borne_kw,
            horaires_borne=horaires_borne,
            jours_selectionnes=jours_selectionnes
        )
    else:
        mon_tableau["Conso_Borne"] = 0.0


    if chauffe_eau_actif:
        mon_tableau["Conso_ChauffeEau"] = generer_profil_borne(
            mon_tableau["Date&Time"],
            puissance_borne_kw=puissance_chauffe_eau_kw,
            horaires_borne=horaires_chauffe_eau,
            jours_selectionnes=jours_chauffe_eau
        )
    else:
        mon_tableau["Conso_ChauffeEau"] = 0.0


    if pac_active:
        mon_tableau["Conso_PAC"] = generer_profil_borne(
            mon_tableau["Date&Time"],
            puissance_borne_kw=puissance_pac_kw,
            horaires_borne=horaires_pac,
            jours_selectionnes=jours_pac
        )
    else:
        mon_tableau["Conso_PAC"] = 0.0

    if chauffage_active:
        mon_tableau["Conso_Chauffage"] = generer_profil_borne(
            mon_tableau["Date&Time"],
            puissance_borne_kw=puissance_chauffage_kw,
            horaires_borne=horaires_chauffage,
            jours_selectionnes=jours_chauffage
        )
    else:
        mon_tableau["Conso_Chauffage"] = 0.0




    mon_tableau["Consumption"] = (
        mon_tableau["Consumption_base"]
        + mon_tableau["Conso_Borne"]
        + mon_tableau["Conso_ChauffeEau"]
        + mon_tableau["Conso_PAC"]
        + mon_tableau["Conso_Chauffage"]
    )

    mon_tableau['Autoconsommation'] = np.minimum(mon_tableau['Inverter Output'], mon_tableau['Consumption'])
    mon_tableau['Import_Reseau'] = np.maximum(0, mon_tableau['Consumption'] - mon_tableau['Inverter Output'])
    mon_tableau['Export_Reseau'] = np.maximum(0, mon_tableau['Inverter Output'] - mon_tableau['Consumption'])
    mon_tableau['Autoconso_Directe'] = np.minimum(mon_tableau['Inverter Output'], mon_tableau['Consumption'])

    if activer_batterie and capa_wh > 0:
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
        mon_tableau['Autoconsommation'] = mon_tableau['Autoconso_Directe'] + mon_tableau['Decharge_Batterie']
    else:
        mon_tableau['Niveau_Batterie'] = 0.0
        mon_tableau['Charge_Batterie'] = 0.0
        mon_tableau['Decharge_Batterie'] = 0.0
        mon_tableau['Autoconsommation'] = mon_tableau['Autoconso_Directe']

    return mon_tableau

def creer_tableau_verification(mon_tableau, capa_wh):
    tableau_verification = pd.DataFrame()

    tableau_verification['Date&Time'] = mon_tableau['Date&Time']
    tableau_verification['Consommation_base_Wh'] = mon_tableau.get('Consumption_base', 0.0)
    tableau_verification['Conso_Borne_Wh'] = mon_tableau.get('Conso_Borne', 0.0)
    tableau_verification['Conso_ChauffeEau_Wh'] = mon_tableau.get('Conso_ChauffeEau', 0.0)
    tableau_verification['Conso_PAC_Wh'] = mon_tableau.get('Conso_PAC', 0.0)
    tableau_verification['Conso_Chauffage_Wh'] = mon_tableau.get('Conso_Chauffage', 0.0)

    tableau_verification['Consommation_Wh'] = mon_tableau['Consumption']
    tableau_verification['Production_Wh'] = mon_tableau['Inverter Output']
    tableau_verification['Autoconsommation_Wh'] = mon_tableau['Autoconsommation']
    tableau_verification['Import_Reseau_Wh'] = mon_tableau['Import_Reseau']
    tableau_verification['Export_Reseau_Wh'] = mon_tableau['Export_Reseau']
    tableau_verification['Charge_Batterie_Wh'] = mon_tableau.get('Charge_Batterie', 0.0)
    tableau_verification['Decharge_Batterie_Wh'] = mon_tableau.get('Decharge_Batterie', 0.0)
    tableau_verification['Niveau_Batterie_Wh'] = mon_tableau.get('Niveau_Batterie', 0.0)
    tableau_verification['Capacite_Batterie_Wh'] = capa_wh if capa_wh > 0 else 0.0

    if capa_wh > 0:
        tableau_verification['Niveau_Batterie_%'] = (tableau_verification['Niveau_Batterie_Wh'] / capa_wh) * 100
    else:
        tableau_verification['Niveau_Batterie_%'] = 0.0

    colonnes_a_arrondir = [
        'Consommation_base_Wh',
        'Conso_Borne_Wh',
        'Conso_ChauffeEau_Wh',
        'Conso_PAC_Wh',
        'Conso_Chauffage_Wh',
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
        tableau_verification[col] = pd.to_numeric(tableau_verification[col], errors='coerce').fillna(0).round(2)

    return tableau_verification

# ==========================================
# CALCULS SYNTHÉTIQUES
# ==========================================

def calculer_indicateurs_annuels(mon_tableau, capa_wh):
    total_prod = mon_tableau['Inverter Output'].sum() / 1000
    total_conso = mon_tableau['Consumption'].sum() / 1000
    total_auto = mon_tableau['Autoconsommation'].sum() / 1000
    total_import = mon_tableau['Import_Reseau'].sum() / 1000
    total_export = mon_tableau['Export_Reseau'].sum() / 1000
    total_ess = mon_tableau['Decharge_Batterie'].sum() / 1000
    total_solaire_direct = max(0, total_auto - total_ess)


    total_conso_base = mon_tableau.get('Consumption_base', pd.Series(0, index=mon_tableau.index)).sum() / 1000
    total_borne = mon_tableau.get('Conso_Borne', pd.Series(0, index=mon_tableau.index)).sum() / 1000
    total_chauffe_eau = mon_tableau.get('Conso_ChauffeEau', pd.Series(0, index=mon_tableau.index)).sum() / 1000
    total_pac = mon_tableau.get('Conso_PAC', pd.Series(0, index=mon_tableau.index)).sum() / 1000
    total_chauffage = mon_tableau.get('Conso_Chauffage', pd.Series(0, index=mon_tableau.index)).sum() / 1000

    taux_autoconso = (total_auto / total_prod * 100) if total_prod > 0 else 0
    taux_autonomie = (total_auto / total_conso * 100) if total_conso > 0 else 0
    taux_batterie = (total_ess / total_conso * 100) if total_conso > 0 else 0
    taux_reseau = (total_import / total_conso * 100) if total_conso > 0 else 0

    if capa_wh > 0:
        nombre_cycles = total_ess / (capa_wh / 1000)
        soc_moyen = (mon_tableau['Niveau_Batterie'].mean() / capa_wh * 100)
        soc_moyen = max(0, min(100, soc_moyen))
    else:
        nombre_cycles = 0
        soc_moyen = 0

    return {
        "total_prod": total_prod,
        "total_conso": total_conso,
        "total_auto": total_auto,
        "total_import": total_import,
        "total_export": total_export,
        "total_ess": total_ess,
        "total_solaire_direct": total_solaire_direct,
        "taux_autoconso": taux_autoconso,
        "taux_autonomie": taux_autonomie,
        "taux_batterie": taux_batterie,
        "taux_reseau": taux_reseau,
        "nombre_cycles": nombre_cycles,
        "soc_moyen": soc_moyen,
        "total_conso_base": total_conso_base,
        "total_borne": total_borne,
        "total_chauffe_eau": total_chauffe_eau,
        "total_pac": total_pac,
        "total_chauffage": total_chauffage
    }

def calculer_budget(puissance_crete, activer_batterie, capa_kwh, capa_wh, aide_pv_active=True, aide_batterie_active=True):
    puissance_crete_arrondie = round(puissance_crete, 2)

    if aide_pv_active:
        if puissance_crete_arrondie < 15:
            aide_pv = puissance_crete_arrondie * (1155 - (1155 / 35) * puissance_crete_arrondie)
            aide_pv = round(aide_pv, 2)
            texte_aide_pv = "Installation < 15 kWc : aide calculée selon la formule."
        else:
            aide_pv = 10000.00
            texte_aide_pv = "Installation ≥ 15 kWc : aide fixée à 10 000 €."
    else:
        aide_pv = 0.0
        texte_aide_pv = "Aide PV désactivée."

    if activer_batterie and capa_kwh > 0:
        capacite_batterie_arrondie = round(capa_kwh, 2)

        if aide_batterie_active:
            if capacite_batterie_arrondie < 9:
                aide_batterie = capacite_batterie_arrondie * (500 - (500 / 18) * capacite_batterie_arrondie)
                aide_batterie = round(aide_batterie, 2)
                texte_aide_batterie = "Batterie < 9 kWh : aide calculée selon la formule."
            else:
                aide_batterie = 2250.00
                texte_aide_batterie = "Batterie ≥ 9 kWh : aide fixée à 2 250 €."
        else:
            aide_batterie = 0.0
            texte_aide_batterie = "Aide batterie désactivée."
    else:
        capacite_batterie_arrondie = 0.0
        aide_batterie = 0.0
        texte_aide_batterie = "Aucune batterie activée."

    aide_totale = round(aide_pv + aide_batterie, 2)

    cout_pv = round(puissance_crete * 1000 * st.session_state["cout_pv_par_wc"], 2)
    cout_batterie = round(capa_wh * st.session_state["cout_batterie_par_wh"], 2) if activer_batterie and capa_wh > 0 else 0.0

    cout_total_brut = round(cout_pv + cout_batterie, 2)
    cout_total_net = round(cout_total_brut - aide_totale, 2)

    return {
        "aide_pv": aide_pv,
        "aide_batterie": aide_batterie,
        "aide_totale": aide_totale,
        "texte_aide_pv": texte_aide_pv,
        "texte_aide_batterie": texte_aide_batterie,
        "capacite_batterie_arrondie": capacite_batterie_arrondie,
        "puissance_crete_arrondie": puissance_crete_arrondie,
        "cout_pv": cout_pv,
        "cout_batterie": cout_batterie,
        "cout_total_brut": cout_total_brut,
        "cout_total_net": cout_total_net,
    }

def calculer_analyse_financiere(mon_tableau, cout_total_net):
    prix_electricite = st.session_state["prix_electricite"]
    prix_injection = st.session_state["prix_injection"]
    prix_communaute_achat = st.session_state["prix_communaute_achat"]
    prix_communaute_vente = st.session_state["prix_communaute_vente"]

    total_conso_kwh = mon_tableau['Consumption'].sum() / 1000
    total_import_kwh = mon_tableau['Import_Reseau'].sum() / 1000
    total_export_kwh = mon_tableau['Export_Reseau'].sum() / 1000
    total_auto_directe_kwh = mon_tableau['Autoconso_Directe'].sum() / 1000
    total_batterie_kwh = mon_tableau['Decharge_Batterie'].sum() / 1000

    cout_sans_installation = round(total_conso_kwh * prix_electricite, 2)
    economie_auto_directe = round(total_auto_directe_kwh * prix_electricite, 2)
    economie_batterie = round(total_batterie_kwh * prix_electricite, 2)

    cout_import_normal = round(total_import_kwh * prix_electricite, 2)
    revenu_export_normal = round(total_export_kwh * prix_injection, 2)
    solde_normal = round(cout_import_normal - revenu_export_normal, 2)
    gain_normal = round(cout_sans_installation - solde_normal, 2)

    cout_import_communaute = round(total_import_kwh * prix_communaute_achat, 2)
    revenu_export_communaute = round(total_export_kwh * prix_communaute_vente, 2)
    solde_communaute = round(cout_import_communaute - revenu_export_communaute, 2)
    gain_communaute = round(cout_sans_installation - solde_communaute, 2)

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
        pct_gain_communaute = round(((gain_communaute - gain_normal) / gain_normal) * 100, 1)
        pct_gain_mix = round(((gain_mix - gain_normal) / gain_normal) * 100, 1)
    else:
        pct_gain_communaute = 0.0
        pct_gain_mix = 0.0

    tr_normal = (cout_total_net / gain_normal) if gain_normal > 0 else None
    tr_mix = (cout_total_net / gain_mix) if gain_mix > 0 else None
    tr_communaute = (cout_total_net / gain_communaute) if gain_communaute > 0 else None

    return {
        "prix_electricite": prix_electricite,
        "prix_injection": prix_injection,
        "prix_communaute_achat": prix_communaute_achat,
        "prix_communaute_vente": prix_communaute_vente,
        "total_conso_kwh": total_conso_kwh,
        "total_import_kwh": total_import_kwh,
        "total_export_kwh": total_export_kwh,
        "total_auto_directe_kwh": total_auto_directe_kwh,
        "total_batterie_kwh": total_batterie_kwh,
        "cout_sans_installation": cout_sans_installation,
        "economie_auto_directe": economie_auto_directe,
        "economie_batterie": economie_batterie,
        "cout_import_normal": cout_import_normal,
        "revenu_export_normal": revenu_export_normal,
        "solde_normal": solde_normal,
        "gain_normal": gain_normal,
        "cout_import_communaute": cout_import_communaute,
        "revenu_export_communaute": revenu_export_communaute,
        "solde_communaute": solde_communaute,
        "gain_communaute": gain_communaute,
        "cout_import_mix": cout_import_mix,
        "revenu_export_mix": revenu_export_mix,
        "solde_mix": solde_mix,
        "gain_mix": gain_mix,
        "pct_gain_communaute": pct_gain_communaute,
        "pct_gain_mix": pct_gain_mix,
        "tr_normal": tr_normal,
        "tr_mix": tr_mix,
        "tr_communaute": tr_communaute,
        "gain_10_ans_normal": round(gain_normal * 10, 2),
        "gain_10_ans_mix": round(gain_mix * 10, 2),
        "gain_10_ans_communaute": round(gain_communaute * 10, 2),
    }

def calcul_frais_reseau(mon_tableau, puissance_reference_kw):
    tarifs_reseau = {
        3:   {"fixe": 7.42},
        7:   {"fixe": 12.84},
        12:  {"fixe": 19.61},
        17:  {"fixe": 26.39},
        27:  {"fixe": 39.94},
        43:  {"fixe": 61.62},
        70:  {"fixe": 98.20},
        100: {"fixe": 138.85},
        150: {"fixe": 206.60},
        200: {"fixe": 274.35},
    }

    TARIF_VOLUMETRIQUE = 0.051
    TARIF_DEP_JOUR = 0.0765
    TARIF_DEP_NUIT = 0.0076

    df = mon_tableau.copy()
    df["Import_kWh"] = df["Import_Reseau"] / 1000
    df["Heure"] = pd.to_datetime(df["Date&Time"]).dt.hour
    df["Depassement_kWh"] = (df["Import_kWh"] - puissance_reference_kw).clip(lower=0)

    df["Tarif_depassement"] = np.where(
        (df["Heure"] >= 6) & (df["Heure"] < 22),
        TARIF_DEP_JOUR,
        TARIF_DEP_NUIT
    )

    df["Cout_depassement"] = df["Depassement_kWh"] * df["Tarif_depassement"]

    import_total_kwh = df["Import_kWh"].sum()
    depassement_total_kwh = df["Depassement_kWh"].sum()

    redevance_fixe_annuelle = tarifs_reseau[puissance_reference_kw]["fixe"] * 12
    redevance_volumetrique = import_total_kwh * TARIF_VOLUMETRIQUE
    cout_depassement_total = df["Cout_depassement"].sum()

    cout_total_reseau = (
        redevance_fixe_annuelle
        + redevance_volumetrique
        + cout_depassement_total
    )

    return {
        "redevance_fixe_annuelle": redevance_fixe_annuelle,
        "redevance_volumetrique": redevance_volumetrique,
        "depassement_total_kwh": depassement_total_kwh,
        "cout_depassement_total": cout_depassement_total,
        "cout_total_reseau": cout_total_reseau,
        "df_detail": df
    }

# ==========================================
# AFFICHAGE EN-TÊTE
# ==========================================

def afficher_entete():
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title("Simulateur Photovoltaïque & Stockage")
        st.markdown("""
        Analysez votre production, votre consommation et l'impact d'une batterie.  
        Optimisez votre taux d'autoconsommation en un clic !
        """)

    with col2:
        if panneau_path.exists():
            st.image(str(panneau_path), use_container_width=True)

    st.divider()

# ==========================================
# ONGLET IMPORT
# ==========================================

def afficher_onglet_import(tab_import):
    with tab_import:
        if logo_path.exists():
            st.sidebar.image(str(logo_path), use_container_width=True)
        else:
            st.sidebar.warning("Logo introuvable")

        st.subheader("Étape 1 : Paramètres du projet ⚙️")

        if "puissance_crete" not in st.session_state:
            st.session_state["puissance_crete"] = 10.0

        puissance_crete = st.number_input(
            "Puissance Crête à installer (kWc)",
            min_value=0.0,
            step=0.1,
            key="puissance_crete"
        )

        donnees_conso = None
        profil_choisi = None
        prod_specifique = 900.0
        profil_24h_custom = np.zeros(24)
        profil_24h_semaine = np.zeros(24)
        profil_24h_weekend = np.zeros(24)
        coeffs_mensuels_conso = [1.0] * 12
        fichier_prod = None
        df_repartition = None
        colonne_prod = None


        st.markdown("---")
        # =====================================================
        # 1. PRODUCTION SOLAIRE
        # =====================================================
        st.subheader("Étape 2 : Production Solaire ☀️")

        if "mode_prod" not in st.session_state:
            st.session_state["mode_prod"] = "CSV SolarEdge"

        mode_prod = st.radio(
            "Type de fichier de production :",
            ["CSV SolarEdge", "Fichier simple Excel", "Production théorique personnalisée"],
            key="mode_prod"
        )

        if mode_prod == "CSV SolarEdge":
            fichier_prod = st.file_uploader(
                "Importez le CSV SolarEdge",
                type=['csv'],
                key="prod_solaredge"
            )

        elif mode_prod == "Fichier simple Excel":
            colonne_prod = None
            fichier_prod = prod_excel_path

            if prod_excel_path.exists():
                df_preview = pd.read_excel(prod_excel_path)

                colonnes_dispo = df_preview.columns.tolist()

                if len(colonnes_dispo) > 1:
                    st.success("Fichier Excel de production détecté.")
                    colonne_prod = st.selectbox(
                        "Choisissez la production à utiliser :",
                        colonnes_dispo[1:],
                        key="choix_colonne_prod_excel"
                    )
                else:
                    st.error("Le fichier Excel doit contenir au moins une colonne Date et une colonne de production.")
            else:
                st.error("Le fichier production.xlsx est introuvable dans le dossier de l'application.")

        else:
            st.markdown("### Paramètres de production théorique")

            if "prod_specifique" not in st.session_state:
                st.session_state["prod_specifique"] = 900.0

            prod_specifique = st.number_input(
                "Production spécifique (kWh/kWc/an)",
                min_value=700.0,
                max_value=1200.0,
                step=10.0,
                key="prod_specifique"
            )

            production_annuelle_theorique = puissance_crete * prod_specifique

            st.metric(
                "Production annuelle estimée",
                f"{production_annuelle_theorique:,.0f} kWh".replace(",", " ")
            )


            st.markdown("#### Répartition mensuelle personnalisable")

            mois_noms = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
                        "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]

            valeurs_defaut = [
                0.03, 0.05, 0.07, 0.10, 0.12, 0.13,
                0.13, 0.12, 0.10, 0.07, 0.05, 0.03
            ]

            valeurs_defaut_kwh = [v * production_annuelle_theorique for v in valeurs_defaut]

            productions_mensuelles = []
            cols_mois = st.columns(4)

            for i, mois in enumerate(mois_noms):
                with cols_mois[i % 4]:
                    val = st.number_input(
                        f"{mois}",
                        min_value=0.0,
                        value=float(valeurs_defaut_kwh[i]),
                        step=50.0,
                        key=f"prod_mois_{mois}"
                    )
                    productions_mensuelles.append(val)

            df_repartition = pd.DataFrame({
                "Mois": mois_noms,
                "Production (kWh)": productions_mensuelles
            })



            prod_mensuelle_kwh = pd.to_numeric(
                df_repartition["Production (kWh)"],
                errors="coerce"
            ).fillna(0)

            somme_prod = prod_mensuelle_kwh.sum()

            st.caption(
                f"Somme actuelle des productions mensuelles : {somme_prod:,.0f} kWh".replace(",", " ")
            )

            if somme_prod <= 0:
                st.warning("La somme des productions mensuelles est nulle.")
            elif abs(somme_prod - production_annuelle_theorique) > 1:
                st.warning(
                    f"La somme des mois ({somme_prod:,.0f} kWh) ne correspond pas à la production annuelle estimée "
                    f"({production_annuelle_theorique:,.0f} kWh).".replace(",", " ")
                )
            else:
                st.success("La somme mensuelle correspond bien à la production annuelle estimée.")

        # ------------------------------------------------------
        # AFFICHAGE DE LA PRODUCTION
        # ------------------------------------------------------

        mon_tableau_prod_apercu = None

        try:
            if mode_prod == "CSV SolarEdge" and fichier_prod is not None:
                fichier_prod.seek(0)

            if mode_prod in ["CSV SolarEdge", "Fichier simple Excel"] and fichier_prod is not None:
                mon_tableau_prod_apercu = charger_production(
                    mode_prod=mode_prod,
                    fichier_prod=fichier_prod,
                    colonne_prod=colonne_prod,
                    puissance_crete=puissance_crete,
                    prod_specifique=prod_specifique,
                    df_repartition=df_repartition
                )

            elif mode_prod == "Production théorique personnalisée":
                mon_tableau_prod_apercu = charger_production(
                    mode_prod=mode_prod,
                    fichier_prod=None,
                    puissance_crete=puissance_crete,
                    prod_specifique=prod_specifique,
                    df_repartition=df_repartition
                )

            if mon_tableau_prod_apercu is not None:
                afficher_apercu_production(mon_tableau_prod_apercu, titre="Aperçu de la production")

        except Exception as e:
            st.warning(f"Aperçu production indisponible : {e}")




        st.markdown("---")

        # =====================================================
        # 2. CONSOMMATION
        # =====================================================
        st.subheader("Étape 3 : Source de Consommation 🏠")

        if "mode_conso" not in st.session_state:
            st.session_state["mode_conso"] = "Profils types (Fichier CSV)"

        mode_conso = st.radio(
            "Choix de la méthode :",
            ["Profils types (Fichier CSV)", "Calculateur personnalisé (Tableau)"],
            key="mode_conso"
        )


        try:
            if mode_conso == "Profils types (Fichier CSV)":
                donnees_conso = pd.read_csv(conso_path, sep=";", decimal=",")

                choix_profils = [
                    col for col in donnees_conso.columns
                    if col.lower() != "date" and "unnamed" not in col.lower()
                ]

                st.success("Fichier de profils détecté !")

                if "profil_choisi" not in st.session_state and len(choix_profils) > 0:
                    st.session_state["profil_choisi"] = choix_profils[0]

                if len(choix_profils) > 0 and st.session_state.get("profil_choisi") not in choix_profils:
                    st.session_state["profil_choisi"] = choix_profils[0]

                profil_choisi = st.selectbox(
                    "Choisissez le profil à simuler :",
                    choix_profils,
                    key="profil_choisi"
                )

                conso_col = pd.to_numeric(
                    donnees_conso[profil_choisi],
                    errors='coerce'
                ).fillna(0)

                dates_apercu = pd.date_range(
                    start='2025-01-01',
                    periods=len(donnees_conso),
                    freq='h'
                )

                y_jour = conso_col.groupby(dates_apercu.hour).mean()
                y_mois = conso_col.groupby(dates_apercu.month).sum() / 1000
                total_kwh = conso_col.sum() / 1000

            else:
                st.info("Ajoutez vos appareils. Horaires : '8-10' ou '12-13;19-21'")

                default_devices = [
                    {"Appareil": "Talon (Veilles, Box, Frigo)", "Puissance (W)": 200, "Horaires": "0-24", "Type de jour": "Tous", "Actif": True},
                    {"Appareil": "Éclairage & Prises", "Puissance (W)": 350, "Horaires": "7-9;18-23", "Type de jour": "Semaine", "Actif": True},
                    {"Appareil": "Lave-Linge", "Puissance (W)": 2000, "Horaires": "17-20", "Type de jour": "Semaine", "Actif": True},
                    {"Appareil": "Plaques Cuisson", "Puissance (W)": 1800, "Horaires": "19-21", "Type de jour": "Semaine", "Actif": True},
                    {"Appareil": "Éclairage & Prises", "Puissance (W)": 350, "Horaires": "10-12;16-23", "Type de jour": "Week-end", "Actif": True},
                    {"Appareil": "Lave-Linge", "Puissance (W)": 2000, "Horaires": "11-13;18-21", "Type de jour": "Week-end", "Actif": True},
                    {"Appareil": "Plaques Cuisson", "Puissance (W)": 1800, "Horaires": "12-14;19-21", "Type de jour": "Week-end", "Actif": True},
                ]

                st.markdown("### Appareils et horaires")

                if "appareils_personnalises" not in st.session_state:
                    st.session_state["appareils_personnalises"] = default_devices

                df_custom = st.data_editor(
                    pd.DataFrame(st.session_state["appareils_personnalises"]),

                    num_rows="dynamic",
                    use_container_width=True,
                    key="tableau_custom_conso_unique",
                    column_config={
                        "Type de jour": st.column_config.SelectboxColumn(
                            "Type de jour",
                            options=["Tous", "Semaine", "Week-end"],
                            required=True
                        ),
                        "Actif": st.column_config.CheckboxColumn("Actif")
                    }
                )

                st.session_state["appareils_personnalises"] = df_custom.to_dict(orient="records")

                st.markdown("### Saisonnalité mensuelle")

                mois_noms = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
                            "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]

                valeurs_defaut = [1.00, 1.00, 1.00, 1.00, 1.00, 1.00,
                                1.00, 1.00, 1.00, 1.00, 1.00, 1.00]

                

                if "coeffs_mensuels_conso" not in st.session_state:
                    st.session_state["coeffs_mensuels_conso"] = [1.0] * 12

                coeffs_mensuels_conso = []

                cols_mois = st.columns(4)
                for i, mois in enumerate(mois_noms):
                    with cols_mois[i % 4]:
                        cle_coeff = f"coeff_conso_{i}"

                        if cle_coeff not in st.session_state:
                            st.session_state[cle_coeff] = st.session_state["coeffs_mensuels_conso"][i]

                        coeff = st.number_input(
                            mois,
                            min_value=0.50,
                            max_value=2.00,
                            step=0.05,
                            key=cle_coeff
                        )
                        coeffs_mensuels_conso.append(coeff)
                st.session_state["coeffs_mensuels_conso"] = coeffs_mensuels_conso
                profil_24h_semaine = np.zeros(24)
                profil_24h_weekend = np.zeros(24)

                for _, row in df_custom.iterrows():
                    if row["Actif"]:
                        profil_h = parse_h(row["Horaires"]) * row["Puissance (W)"]
                        type_jour = row["Type de jour"]

                        if type_jour == "Tous":
                            profil_24h_semaine += profil_h
                            profil_24h_weekend += profil_h
                        elif type_jour == "Semaine":
                            profil_24h_semaine += profil_h
                        elif type_jour == "Week-end":
                            profil_24h_weekend += profil_h

                # aperçu jour type
                y_jour = pd.DataFrame({
                    "Heure": range(24),
                    "Semaine": profil_24h_semaine,
                    "Week-end": profil_24h_weekend
                }).set_index("Heure")

                # estimation annuelle
                dates_annee = pd.date_range(start="2025-01-01 00:00:00", periods=365 * 24, freq="h")
                conso_horaire = []

                for dt in dates_annee:
                    coeff_mois = coeffs_mensuels_conso[dt.month - 1]

                    if dt.weekday() < 5:
                        valeur = profil_24h_semaine[dt.hour]
                    else:
                        valeur = profil_24h_weekend[dt.hour]

                    conso_horaire.append(valeur * coeff_mois)

                conso_horaire = np.array(conso_horaire)

                df_temp = pd.DataFrame({
                    "Date&Time": dates_annee,
                    "Consumption": conso_horaire
                })

                y_mois = df_temp.groupby(df_temp["Date&Time"].dt.month)["Consumption"].sum() / 1000
                total_kwh = df_temp["Consumption"].sum() / 1000

                profil_choisi = "Sur Mesure (Semaine / Week-end)"

            st.markdown("---")
            st.subheader(f"Aperçu : {profil_choisi}")

            if mode_conso == "Calculateur personnalisé (Tableau)":
                conso_jour_semaine = profil_24h_semaine.sum() / 1000
                conso_jour_weekend = profil_24h_weekend.sum() / 1000
                puissance_max = max(profil_24h_semaine.max(), profil_24h_weekend.max())

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Annuel", f"{total_kwh:,.0f} kWh".replace(",", " "))
                c2.metric("Puissance Max", f"{puissance_max:,.0f} W")
                c3.metric("Conso / jour semaine", f"{conso_jour_semaine:.1f} kWh")
                c4.metric("Conso / jour week-end", f"{conso_jour_weekend:.1f} kWh")

            else:
                puissance_max = y_jour.max()

                c1, c2, c3 = st.columns(3)
                c1.metric("Total Annuel", f"{total_kwh:,.0f} kWh".replace(",", " "))
                c2.metric("Puissance Max", f"{puissance_max:,.0f} W")
                c3.metric("Conso / jour moyen", f"{(y_jour.sum()/1000):.1f} kWh")

            fig_apercu, (ax_jour, ax_mois) = plt.subplots(1, 2, figsize=(14, 4))

            if mode_conso == "Calculateur personnalisé (Tableau)":
                ax_jour.plot(y_jour.index, y_jour["Semaine"], linewidth=2.5, label="Semaine")
                ax_jour.plot(y_jour.index, y_jour["Week-end"], linewidth=2.5, linestyle="--", label="Week-end")
                ax_jour.set_title("Modèle sur un jour type")
                ax_jour.set_xticks(range(0, 24, 2))
                ax_jour.set_xlabel("Heure")
                ax_jour.set_ylabel("Puissance (W)")
                ax_jour.grid(True, linestyle='--', alpha=0.6)
                ax_jour.legend()
            else:
                ax_jour.plot(y_jour.index, y_jour.values, color='#1565C0', linewidth=2.5)
                ax_jour.fill_between(y_jour.index, y_jour.values, color='#1565C0', alpha=0.2)
                ax_jour.set_title("Modèle sur un jour type")
                ax_jour.set_xticks(range(0, 24, 2))
                ax_jour.set_xlabel("Heure")
                ax_jour.set_ylabel("Puissance (W)")
                ax_jour.grid(True, linestyle='--', alpha=0.6)

            mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            ax_mois.bar(mois_noms, y_mois.values, color='#FF9800', edgecolor='black', alpha=0.8)
            ax_mois.set_title("Consommation Mensuelle Totale")
            ax_mois.set_xlabel("Mois")
            ax_mois.set_ylabel("Énergie (kWh)")
            ax_mois.grid(axis='y', linestyle='--', alpha=0.6)

            plt.tight_layout()
            st.pyplot(fig_apercu)

        except Exception as e:
            st.error(f"Erreur : {e}")

    return {
        "puissance_crete": puissance_crete,
        "mode_prod": mode_prod,
        "fichier_prod": fichier_prod,
        "prod_specifique": prod_specifique,
        "df_repartition": df_repartition if mode_prod == "Production théorique personnalisée" else None,
        "mode_conso": mode_conso,
        "donnees_conso": donnees_conso,
        "profil_choisi": profil_choisi,
        "profil_24h_custom": profil_24h_custom,
        "profil_24h_semaine": profil_24h_semaine,
        "profil_24h_weekend": profil_24h_weekend,
        "coeffs_mensuels_conso": coeffs_mensuels_conso,
        "colonne_prod": colonne_prod
    }

# ==========================================
# SIDEBAR
# ==========================================

def afficher_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Évolution de la production PV 📈")

    if "augmentation_prod_pct" not in st.session_state:
        st.session_state["augmentation_prod_pct"] = 0.0

    augmentation_prod_pct = st.sidebar.number_input(
        "Augmentation de la production (%)",
        min_value=-10.0,
        step=1.0,
        key="augmentation_prod_pct"
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Stockage (Batterie) 🔋")

    df_batteries = charger_batteries()
    if df_batteries.empty:
        st.sidebar.error("Fichier batteries.xlsx introuvable ou vide.")

    if "activer_batterie" not in st.session_state:
        st.session_state["activer_batterie"] = False

    activer_batterie = st.sidebar.checkbox(
        "Activer la simulation de batterie",
        key="activer_batterie"
    )


    capa_wh = 0.0
    puiss_w = 0.0
    capa_kwh = 0.0

    if activer_batterie and not df_batteries.empty:
        liste_batteries = df_batteries['Référence'].tolist()

        if "choix_batterie" not in st.session_state and len(liste_batteries) > 0:
            st.session_state["choix_batterie"] = liste_batteries[0]

        if len(liste_batteries) > 0 and st.session_state.get("choix_batterie") not in liste_batteries:
            st.session_state["choix_batterie"] = liste_batteries[0]

        choix_batterie = st.sidebar.selectbox(
            "Choisissez un modèle :",
            liste_batteries,
            key="choix_batterie"
        )

        infos_batterie = df_batteries[df_batteries['Référence'] == choix_batterie].iloc[0]

        capa_kwh = float(str(infos_batterie['Energie util']).replace(',', '.'))
        puiss_kw = float(str(infos_batterie['P charge / décharge']).replace(',', '.'))

        st.sidebar.info(f"Capacité : {capa_kwh:.2f} kWh\nPuissance Max : {puiss_kw:.2f} kW")

        capa_wh = capa_kwh * 1000
        puiss_w = puiss_kw * 1000




    st.sidebar.markdown("---")
    st.sidebar.subheader("Borne de recharge")

    if "borne_active" not in st.session_state:
        st.session_state["borne_active"] = False

    borne_active = st.sidebar.checkbox(
        "Ajouter une borne de recharge",
        key="borne_active"
    )

    puissance_borne_kw = 0.0
    horaires_borne = "18-20"
    jours_selectionnes = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

    if borne_active:
        if "puissance_borne_kw" not in st.session_state:
            st.session_state["puissance_borne_kw"] = 11.0

        puissance_borne_kw = st.sidebar.selectbox(
            "Puissance de la borne (kW)",
            [3, 7, 11.0, 22.0],
            key="puissance_borne_kw"
        )

        if "horaires_borne" not in st.session_state:
            st.session_state["horaires_borne"] = "18-20"

        horaires_borne = st.sidebar.text_input(
            "Plage horaire de charge",
            key="horaires_borne"
        )

        if "jours_selectionnes" not in st.session_state:
            st.session_state["jours_selectionnes"] = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

        jours_selectionnes = st.sidebar.multiselect(
            "Jours de charge",
            ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
            key="jours_selectionnes"
        )

        heures_par_jour = duree_totale_horaires(horaires_borne)
        energie_jour_kwh = puissance_borne_kw * heures_par_jour
        energie_semaine_kwh = energie_jour_kwh * len(jours_selectionnes)
        energie_an_kwh = energie_semaine_kwh * 52

        st.sidebar.caption(f"Charge par jour actif : {energie_jour_kwh:.1f} kWh")
        st.sidebar.caption(f"Charge par semaine : {energie_semaine_kwh:.1f} kWh")

        km_equivalent = (energie_an_kwh / 15) * 100

        st.sidebar.success(
            f"Consommation annuelle estimée : {energie_an_kwh:,.0f} kWh\n\n"
            f"Équivalent : {km_equivalent:,.0f} km/an\n"
            f"(base : 15 kWh / 100 km)".replace(",", " ")
        )








    st.sidebar.markdown("---")
    st.sidebar.subheader("Chauffe-eau électrique")

    if "chauffe_eau_actif" not in st.session_state:
        st.session_state["chauffe_eau_actif"] = False

    chauffe_eau_actif = st.sidebar.checkbox(
        "Ajouter un chauffe-eau",
        key="chauffe_eau_actif"
    )

    puissance_chauffe_eau_kw = 0.0
    horaires_chauffe_eau = "6-8;18-20"
    jours_chauffe_eau = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    if chauffe_eau_actif:
        if "puissance_chauffe_eau_kw" not in st.session_state:
            st.session_state["puissance_chauffe_eau_kw"] = 2.0

        puissance_chauffe_eau_kw = st.sidebar.number_input(
            "Puissance chauffe-eau (kW)",
            min_value=0.5,
            step=0.1,
            key="puissance_chauffe_eau_kw"
        )

        if "horaires_chauffe_eau" not in st.session_state:
            st.session_state["horaires_chauffe_eau"] = "6-8;18-20"

        horaires_chauffe_eau = st.sidebar.text_input(
            "Plage horaire chauffe-eau",
            key="horaires_chauffe_eau"
        )

        if "jours_chauffe_eau" not in st.session_state:
            st.session_state["jours_chauffe_eau"] = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

        jours_chauffe_eau = st.sidebar.multiselect(
            "Jours chauffe-eau",
            ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
            key="jours_chauffe_eau"
        )





    st.sidebar.markdown("---")
    st.sidebar.subheader("Pompe à chaleur")

    if "pac_active" not in st.session_state:
        st.session_state["pac_active"] = False

    pac_active = st.sidebar.checkbox(
        "Ajouter une pompe à chaleur",
        key="pac_active"
    )

    puissance_pac_kw = 0.0
    horaires_pac = "6-9;17-22"
    jours_pac = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    if pac_active:
        if "puissance_pac_kw" not in st.session_state:
            st.session_state["puissance_pac_kw"] = 2.5

        puissance_pac_kw = st.sidebar.number_input(
            "Puissance pompe à chaleur (kW)",
            min_value=0.5,
            step=0.1,
            key="puissance_pac_kw"
        )
        if "horaires_pac" not in st.session_state:
            st.session_state["horaires_pac"] = "6-9;17-22"

        horaires_pac = st.sidebar.text_input(
            "Plage horaire PAC",
            key="horaires_pac"
        )

        if "jours_pac" not in st.session_state:
            st.session_state["jours_pac"] = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

        jours_pac = st.sidebar.multiselect(
            "Jours PAC",
            ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
            key="jours_pac"
        )




    st.sidebar.markdown("---")
    st.sidebar.subheader("Chauffage électrique")
    if "chauffage_active" not in st.session_state:
        st.session_state["chauffage_active"] = False

    chauffage_active = st.sidebar.checkbox(
        "Ajouter un chauffage électrique",
        key="chauffage_active"
    )
    puissance_chauffage_kw = 0.0
    horaires_chauffage = "6-8;19-22"
    jours_chauffage = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    if chauffage_active:
        if "puissance_chauffage_kw" not in st.session_state:
            st.session_state["puissance_chauffage_kw"] = 1.5

        puissance_chauffage_kw = st.sidebar.number_input(
            "Puissance chauffage électrique (kW)",
            min_value=0.5,
            step=0.1,
            key="puissance_chauffage_kw"
        )

        if "horaires_chauffage" not in st.session_state:
            st.session_state["horaires_chauffage"] = "6-8;19-22"

        horaires_chauffage = st.sidebar.text_input(
            "Plage horaire chauffage",
            key="horaires_chauffage"
        )

        if "jours_chauffage" not in st.session_state:
            st.session_state["jours_chauffage"] = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

        jours_chauffage = st.sidebar.multiselect(
            "Jours chauffage",
            ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
            key="jours_chauffage"
        )




    return {
        "augmentation_prod_pct": augmentation_prod_pct,
        "activer_batterie": activer_batterie,
        "capa_wh": capa_wh,
        "puiss_w": puiss_w,
        "capa_kwh": capa_kwh,
        "borne_active": borne_active,
        "puissance_borne_kw": puissance_borne_kw,
        "horaires_borne": horaires_borne,
        "jours_selectionnes": jours_selectionnes,
        "chauffe_eau_actif": chauffe_eau_actif,
        "puissance_chauffe_eau_kw": puissance_chauffe_eau_kw,
        "horaires_chauffe_eau": horaires_chauffe_eau,
        "jours_chauffe_eau": jours_chauffe_eau,
        "pac_active": pac_active,
        "puissance_pac_kw": puissance_pac_kw,
        "horaires_pac": horaires_pac,
        "jours_pac": jours_pac,
        "chauffage_active": chauffage_active,
        "puissance_chauffage_kw": puissance_chauffage_kw,
        "horaires_chauffage": horaires_chauffage,
        "jours_chauffage": jours_chauffage
    }

# ==========================================
# ONGLET SAISONS
# ==========================================

def afficher_onglet_saisons(tab_saisons, mon_tableau, activer_batterie):
    with tab_saisons:
        st.header("Analyse des 4 Saisons")

        st.markdown("**Sélectionnez les courbes à afficher :**")
        col1, col2, col3, col4, col5 = st.columns(5)

        afficher_prod = col1.checkbox("Production", value=True)
        afficher_conso = col2.checkbox("Consommation", value=True)
        afficher_auto = col3.checkbox("Autoconsommation", value=True)
        afficher_import = col4.checkbox("Importé (Réseau)", value=False)
        afficher_export = col5.checkbox("Exporté (Réseau)", value=False)

        fig1, axes = plt.subplots(2, 2, figsize=(14, 8))

        dates_a_tracer = [
            (12, 21, "21 Décembre (Hiver)", axes[0, 0]),
            (3, 21, "21 Mars (Printemps)", axes[0, 1]),
            (6, 21, "21 Juin (Été)", axes[1, 0]),
            (9, 21, "21 Septembre (Automne)", axes[1, 1])
        ]

        handles_globaux = []
        labels_globaux = []

        for mois, jour, titre, ax in dates_a_tracer:
            journee = mon_tableau[
                (mon_tableau['Date&Time'].dt.month == mois) &
                (mon_tableau['Date&Time'].dt.day == jour)
            ]

            if journee.empty:
                ax.set_title(titre)
                ax.text(0.5, 0.5, "Aucune donnée", ha='center', va='center', transform=ax.transAxes)
                ax.grid(True, linestyle='--', alpha=0.6)
                continue

            x_dates = journee['Date&Time']
            x_num = mdates.date2num(x_dates)

            if len(x_num) < 2:
                ax.set_title(titre)
                ax.text(0.5, 0.5, "Pas assez de points", ha='center', va='center', transform=ax.transAxes)
                ax.grid(True, linestyle='--', alpha=0.6)
                continue

            x_dense_num = np.linspace(x_num.min(), x_num.max(), 300)
            x_dense_dates = mdates.num2date(x_dense_num)

            def lisser_courbe(y_vals):
                lisseur = PchipInterpolator(x_num, y_vals)
                return np.clip(lisseur(x_dense_num), 0, None)

            if afficher_prod:
                ax.plot(x_dense_dates, lisser_courbe(journee['Inverter Output']), label='Production', color='#FFD700', linewidth=2.5)
            if afficher_conso:
                ax.plot(x_dense_dates, lisser_courbe(journee['Consumption']), label='Consommation', color='#2196F3', linewidth=2.5)

            if afficher_auto:
                y_auto_directe = lisser_courbe(journee['Autoconso_Directe'])
                ax.fill_between(x_dense_dates, y_auto_directe, label='Autoconso directe', color="#67AD17", alpha=0.6)

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
            ax.set_ylabel('Puissance (W)')
            ax.grid(True, linestyle='--', alpha=0.6)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
            ax.tick_params(axis='x', rotation=45)

            if not handles_globaux:
                handles_globaux, labels_globaux = ax.get_legend_handles_labels()

        plt.tight_layout()

        if handles_globaux:
            fig1.legend(handles_globaux, labels_globaux, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=5, fontsize=11)
            fig1.subplots_adjust(top=0.88)

        st.pyplot(fig1, use_container_width=False)

# ==========================================
# ONGLET MENSUEL
# ==========================================

def afficher_onglet_mensuel(tab_mensuel, mon_tableau):
    with tab_mensuel:
        st.header("Bilan Énergétique Mensuel")

        bilan_mensuel = mon_tableau.groupby(mon_tableau['Date&Time'].dt.month)[
            ['Consumption', 'Inverter Output', 'Autoconsommation', 'Import_Reseau', 'Export_Reseau']
        ].sum() / 1000

        bilan_mensuel = bilan_mensuel.reindex(range(1, 13), fill_value=0)

        mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        x = np.arange(len(mois_noms))

        fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

        ax1.bar(x, bilan_mensuel['Autoconsommation'], width=0.6, label='Autoconsommation', color="#08CE5A")
        ax1.bar(
            x,
            bilan_mensuel['Import_Reseau'],
            width=0.6,
            bottom=bilan_mensuel['Autoconsommation'],
            label='Import réseau',
            color="#FFA600"
        )

        ax1.set_title("Répartition de la consommation", fontsize=16)
        ax1.set_ylabel("Énergie (kWh)", fontsize=14)
        ax1.set_xticks(x)
        ax1.set_xticklabels(mois_noms)
        ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2)
        ax1.grid(axis='y', linestyle='--', alpha=0.7)

        totaux_conso = bilan_mensuel['Autoconsommation'] + bilan_mensuel['Import_Reseau']
        for i, total in enumerate(totaux_conso):
            ax1.text(i, total + 5, f"{total:.0f}", ha='center', va='bottom', fontsize=9)

        ax2.bar(x, bilan_mensuel['Autoconsommation'], width=0.6, label='Autoconsommation', color="#08CE5A")
        ax2.bar(
            x,
            bilan_mensuel['Export_Reseau'],
            width=0.6,
            bottom=bilan_mensuel['Autoconsommation'],
            label='Export réseau',
            color="#00E1FF"
        )

        ax2.set_title("Répartition de la production", fontsize=16)
        ax2.set_ylabel("Énergie (kWh)", fontsize=14)
        ax2.set_xticks(x)
        ax2.set_xticklabels(mois_noms)
        ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2)
        ax2.grid(axis='y', linestyle='--', alpha=0.7)

        totaux_prod = bilan_mensuel['Autoconsommation'] + bilan_mensuel['Export_Reseau']
        for i, total in enumerate(totaux_prod):
            ax2.text(i, total + 5, f"{total:.0f}", ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        plt.subplots_adjust(hspace=0.4)
        st.pyplot(fig2, use_container_width=False)

# ==========================================
# ONGLET ANNUEL
# ==========================================

def afficher_onglet_annuel(tab_annuel, mon_tableau, indicateurs, capa_wh, activer_batterie):
    with tab_annuel:
        st.header("Flux d'Énergie Annuel")

        total_prod = indicateurs["total_prod"]
        total_conso = indicateurs["total_conso"]
        total_auto = indicateurs["total_auto"]
        total_import = indicateurs["total_import"]
        total_export = indicateurs["total_export"]
        total_ess = indicateurs["total_ess"]
        total_solaire_direct = indicateurs["total_solaire_direct"]
        taux_autoconso = indicateurs["taux_autoconso"]
        taux_autonomie = indicateurs["taux_autonomie"]
        nombre_cycles = indicateurs["nombre_cycles"]
        soc_moyen = indicateurs["soc_moyen"]
        total_conso_base = indicateurs["total_conso_base"]
        total_borne = indicateurs["total_borne"]
        total_chauffe_eau = indicateurs["total_chauffe_eau"]
        total_pac = indicateurs["total_pac"]
        total_chauffage = indicateurs["total_chauffage"]

        batterie_utilisee = total_ess > 0.1

        def polar_to_cartesian(cx, cy, r, angle_deg):
            import math
            angle_rad = math.radians(angle_deg - 90)
            return cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)

        def donut_arc(cx, cy, r, pct, color, bg="#E6E6E6", stroke=16):
            pct = max(0, min(100, pct))
            start_x, start_y = polar_to_cartesian(cx, cy, r, 0)
            end_x, end_y = polar_to_cartesian(cx, cy, r, pct * 3.6)
            large_arc = 1 if pct > 50 else 0

            bg_circle = f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{bg}" stroke-width="{stroke}" fill="none" />'

            if pct <= 0:
                fg_arc = ""
            elif pct >= 99.999:
                fg_arc = f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{color}" stroke-width="{stroke}" fill="none" stroke-linecap="butt" />'
            else:
                fg_arc = (
                    f'<path d="M {start_x:.2f} {start_y:.2f} '
                    f'A {r} {r} 0 {large_arc} 1 {end_x:.2f} {end_y:.2f}" '
                    f'stroke="{color}" stroke-width="{stroke}" fill="none" stroke-linecap="butt" />'
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
                return f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{color}" stroke-width="{stroke}" fill="none" />'

            return (
                f'<path d="M {x1:.2f} {y1:.2f} '
                f'A {r} {r} 0 {large_arc} 1 {x2:.2f} {y2:.2f}" '
                f'stroke="{color}" stroke-width="{stroke}" fill="none" />'
            )

        c_pv = "#FFAE00"
        c_batt = "#2B9930"
        c_grid = "#957CC5"
        c_direct = "#F5A623"
        c_text = "#303030"
        c_bg = "#FFFFFF"
        c_ring_bg = "#FFF27B"

        pv_pct = (total_auto / total_prod * 100) if total_prod > 0 else 0
        grid_pct = (total_import / (total_import + total_export) * 100) if (total_import + total_export) > 0 else 0
        batt_pct = soc_moyen if batterie_utilisee else 0

        direct_pct_charge = (total_solaire_direct / total_conso * 100) if total_conso > 0 else 0
        batt_pct_charge = (total_ess / total_conso * 100) if total_conso > 0 else 0
        grid_pct_charge = (total_import / total_conso * 100) if total_conso > 0 else 0

        pv_injection_pct = (total_export / total_prod * 100) if total_prod > 0 else 0
        pv_auto_pct = (total_auto / total_prod * 100) if total_prod > 0 else 0

        W = 1000
        H = 560
        x_shift = 40

        pv_x, pv_y = 500, 105 + x_shift
        batt_x, batt_y = 155, 245 + x_shift
        load_x, load_y = 500, 405 + x_shift
        grid_x, grid_y = 845, 245 + x_shift

        r_main = 68
        r_side = 58

        svg_parts = []
        svg_parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{c_bg}" rx="18"/>')

        svg_parts.append(f'''
            <path d="M {pv_x} {pv_y + 85} L {pv_x} {load_y - 85}"
                stroke="{c_direct}" stroke-width="4" fill="none" stroke-linecap="round"
                marker-end="url(#arrow-direct)"/>
        ''')

        if batterie_utilisee:
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

        svg_parts.append(donut_arc(pv_x, pv_y, r_main, pv_pct, c_pv, bg=c_ring_bg, stroke=16))
        svg_parts.append(f'''
            <text x="{pv_x}" y="{pv_y - 92}" text-anchor="middle" font-size="22" font-weight="700" fill="{c_text}">PV</text>
            <text x="{pv_x}" y="{pv_y - 4}" text-anchor="middle" font-size="30">☀️</text>
            <text x="{pv_x}" y="{pv_y + 22}" text-anchor="middle" font-size="18" fill="{c_text}">{total_prod:,.0f} kWh</text>
        '''.replace(",", " "))

        svg_parts.append(f'''
        <text x="{pv_x + 92}" y="{pv_y - 58}" text-anchor="start" font-size="15" font-weight="600" fill="{c_grid}">
            Injection : {pv_injection_pct:.1f}%
        </text>
        <text x="{pv_x + 92}" y="{pv_y - 34}" text-anchor="start" font-size="15" font-weight="600" fill="{c_direct}">
            Direct : {pv_auto_pct:.1f}%
        </text>
        '''.replace(",", " "))

        if batterie_utilisee:
            svg_parts.append(donut_arc(batt_x, batt_y, r_side, batt_pct, c_batt, bg="#E5EFE5", stroke=13))
            svg_parts.append(f'''
                <text x="{batt_x}" y="{batt_y + 4}" text-anchor="middle" font-size="28">🔋</text>
                <text x="{batt_x}" y="{batt_y + 28}" text-anchor="middle" font-size="17" fill="{c_text}">{total_ess:,.0f} kWh</text>
                <text x="{batt_x}" y="{batt_y + 94}" text-anchor="middle" font-size="18" font-weight="700" fill="{c_text}">Batterie</text>
            '''.replace(",", " "))

        svg_parts.append(donut_arc(grid_x, grid_y, r_side, grid_pct, c_grid, bg="#EEE6F5", stroke=13))
        svg_parts.append(f'''
            <text x="{grid_x}" y="{grid_y + 4}" text-anchor="middle" font-size="28">⚡</text>
            <text x="{grid_x}" y="{grid_y + 28}" text-anchor="middle" font-size="17" fill="{c_text}">{total_import:,.0f} kWh</text>
            <text x="{grid_x}" y="{grid_y + 94}" text-anchor="middle" font-size="18" font-weight="700" fill="{c_text}">Réseau</text>
        '''.replace(",", " "))

        svg_parts.append(
            f'<circle cx="{load_x}" cy="{load_y}" r="{r_main}" '
            f'stroke="{c_ring_bg}" stroke-width="16" fill="none" />'
        )

        start = 0
        svg_parts.append(add_segment(load_x, load_y, r_main, start, direct_pct_charge, c_direct, stroke=16))
        start += direct_pct_charge

        if batterie_utilisee:
            svg_parts.append(add_segment(load_x, load_y, r_main, start, batt_pct_charge, c_batt, stroke=16))
            start += batt_pct_charge

        svg_parts.append(add_segment(load_x, load_y, r_main, start, grid_pct_charge, c_grid, stroke=16))

        svg_parts.append(f'''
            <text x="{load_x}" y="{load_y - 2}" text-anchor="middle" font-size="30">🏠</text>
            <text x="{load_x}" y="{load_y + 24}" text-anchor="middle" font-size="18" fill="{c_text}">{total_conso:,.0f} kWh</text>
            <text x="{load_x}" y="{load_y + 96}" text-anchor="middle" font-size="18" font-weight="700" fill="{c_text}">Consommation</text>
        '''.replace(",", " "))

        svg_parts.append(f'''
        <text x="{load_x + 95}" y="{load_y + 28}" text-anchor="start" font-size="15" font-weight="600" fill="{c_batt}">
            Batterie : {batt_pct_charge:.1f}%
        </text>
        <text x="{load_x + 95}" y="{load_y + 52}" text-anchor="start" font-size="15" font-weight="600" fill="{c_direct}">
            PV : {direct_pct_charge:.1f}%
        </text>
        <text x="{load_x + 95}" y="{load_y + 76}" text-anchor="start" font-size="15" font-weight="600" fill="{c_grid}">
            Réseau : {grid_pct_charge:.1f}%
        </text>
        '''.replace(",", " "))

        svg_parts.append(f'''
            <text x="{pv_x + 10}" y="292" font-size="15" fill="{c_direct}">{total_solaire_direct:,.0f} kWh</text>
            <text x="650" y="200" font-size="15" fill="{c_grid}">{total_export:,.0f} kWh</text>
        '''.replace(",", " "))

        if batterie_utilisee:
            svg_parts.append(f'''
                <text x="285" y="390" font-size="15" fill="{c_batt}">{total_ess:,.0f} kWh</text>
            '''.replace(",", " "))

        svg_parts.append(f'''
            <text x="652" y="390" font-size="15" fill="{c_grid}">{total_import:,.0f} kWh</text>
        '''.replace(",", " "))

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

        st.divider()
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Taux autoconso", f"{taux_autoconso:.1f}%")
        c2.metric("Taux autonomie", f"{taux_autonomie:.1f}%")
        c3.metric("Solaire direct", f"{total_solaire_direct:,.0f} kWh".replace(",", " "))
        c4.metric("Via batterie", f"{total_ess:,.0f} kWh".replace(",", " "))
        c5.metric("Importé", f"{total_import:,.0f} kWh".replace(",", " "))
        c6.metric("Cycles / an", f"{nombre_cycles:.0f}")



        st.markdown("---")
        st.subheader("Détail de la consommation annuelle")

        d1, d2, d3 = st.columns(3)
        d1.metric("Consommation totale", f"{total_conso:,.0f} kWh".replace(",", " "))
        d2.metric("Consommation de base", f"{total_conso_base:,.0f} kWh".replace(",", " "))
        d3.metric("Borne", f"{total_borne:,.0f} kWh".replace(",", " "))

        d4, d5, d6 = st.columns(3)
        d4.metric("Chauffe-eau", f"{total_chauffe_eau:,.0f} kWh".replace(",", " "))
        d5.metric("Pompe à chaleur", f"{total_pac:,.0f} kWh".replace(",", " "))
        d6.metric("Chauffage électrique", f"{total_chauffage:,.0f} kWh".replace(",", " "))

        tableau_verification = creer_tableau_verification(mon_tableau, capa_wh)






        st.divider()
        st.subheader("Tableau horaire de vérification")
        st.markdown("Ce tableau permet de contrôler heure par heure les flux énergétiques calculés.")
        st.dataframe(tableau_verification, use_container_width=True, height=400)

        csv_verification = tableau_verification.to_csv(index=False, sep=';').encode('utf-8-sig')

        st.download_button(
            label="Télécharger le tableau de vérification (CSV)",
            data=csv_verification,
            file_name="tableau_verification_horaire.csv",
            mime="text/csv",
            key="download_verification_csv"
        )

# ==========================================
# ONGLET BUDGET 
# ==========================================

def afficher_onglet_budget(tab_budget, budget, puissance_crete, activer_batterie):
    with tab_budget:
        st.header("Investissement initial 📊")

        st.subheader("Activation des aides")

        c_aide1, c_aide2 = st.columns(2)

        with c_aide1:
            if "aide_pv_active" not in st.session_state:
                st.session_state["aide_pv_active"] = True

            st.checkbox(
                "Activer l'aide photovoltaïque",
                key="aide_pv_active"
            )

        with c_aide2:
            if "aide_batterie_active" not in st.session_state:
                st.session_state["aide_batterie_active"] = True

            st.checkbox(
                "Activer l'aide batterie",
                key="aide_batterie_active"
            )

        st.markdown("---")

        budget = calculer_budget(
            puissance_crete=puissance_crete,
            activer_batterie=activer_batterie,
            capa_kwh=budget["capacite_batterie_arrondie"],
            capa_wh=(budget["capacite_batterie_arrondie"] * 1000) if activer_batterie else 0.0,
            aide_pv_active=st.session_state["aide_pv_active"],
            aide_batterie_active=st.session_state["aide_batterie_active"]
        )

        aide_pv = budget["aide_pv"]
        aide_batterie = budget["aide_batterie"]
        aide_totale = budget["aide_totale"]
        texte_aide_pv = budget["texte_aide_pv"]
        texte_aide_batterie = budget["texte_aide_batterie"]
        capacite_batterie_arrondie = budget["capacite_batterie_arrondie"]
        puissance_crete_arrondie = budget["puissance_crete_arrondie"]
        cout_pv = budget["cout_pv"]
        cout_batterie = budget["cout_batterie"]
        cout_total_brut = budget["cout_total_brut"]
        cout_total_net = budget["cout_total_net"]

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

# ==========================================
# ONGLET ANALYSE FINANCIERE
# ==========================================

def afficher_onglet_finance(
    tab_finance,
    mon_tableau,
    budget,
    finance_pv,
    budget_pv,
    finance_pv_batt,
    budget_pv_batt,
    scenario_batterie_disponible,
    meilleur_reseau_pv,
    meilleur_reseau_pv_batt
):
    with tab_finance:
        st.markdown('<div class="finance-section-title">Analyse financière</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="finance-section-desc">Comparaison des scénarios de valorisation de l’énergie et projection des gains cumulés sur 10 ans.</div>',
            unsafe_allow_html=True
        )

        cout_total_net = budget["cout_total_net"]
        finance = calculer_analyse_financiere(mon_tableau, cout_total_net)

        with st.expander("⚙️ Hypothèses de calcul", expanded=False):
            h1, h2, h3, h4 = st.columns(4)
            h1.metric("Prix achat réseau", f"{finance['prix_electricite']:.2f} €/kWh")
            h2.metric("Prix vente réseau", f"{finance['prix_injection']:.2f} €/kWh")
            h3.metric("Prix achat communauté", f"{finance['prix_communaute_achat']:.2f} €/kWh")
            h4.metric("Prix vente communauté", f"{finance['prix_communaute_vente']:.2f} €/kWh")

        st.markdown("---")
        st.subheader("Comparaison des scénarios techniques")

        s1, s2, s3 = st.columns(3)

        with s1:
            components.html(f"""
            <div style="
                background: linear-gradient(180deg, #eef7ff, #e3f1ff);
                border: 1px solid #bcdcff;
                border-radius: 18px;
                padding: 18px 20px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.06);
                margin-bottom: 18px;
                font-family: Arial, sans-serif;
            ">
                <div style="font-size:22px; font-weight:700; color:#1f2c3a; margin-bottom:10px;">
                    ☀️ PV
                </div>

                <div style="font-size:15px; color:#4b5a68; margin-bottom:8px;">
                    Gain annuel estimé
                </div>

                <div style="font-size:26px; font-weight:800; color:#13283a; margin-bottom:10px;">
                    {f"{finance_pv['gain_normal']:,.2f} €".replace(",", " ")}
                </div>

                <div style="font-size:14px; color:#506070; line-height:1.6;">
                    Économie autoconsommation directe :
                    <strong>{f"{finance_pv['economie_auto_directe']:,.2f} €".replace(",", " ")}</strong>
                </div>

                <div style="font-size:14px; color:#506070; line-height:1.6;">
                    Économie batterie :
                    <strong>0.00 €</strong>
                </div>

                <div style="font-size:14px; color:#506070; line-height:1.6; margin-bottom:10px;">
                    Coût net :
                    <strong>{f"{budget_pv['cout_total_net']:,.2f} €".replace(",", " ")}</strong>
                </div>

                <hr style="border:none; border-top:1px solid #cfe0ef; margin:12px 0;">

                <div style="font-size:14px; color:#506070; line-height:1.6;">
                    <strong>Puissance de référence optimale :</strong>
                    {meilleur_reseau_pv["puissance_reference_kw"]} kW
                </div>

                <div style="font-size:14px; color:#506070; line-height:1.6;">
                    <strong>Frais réseau annuels :</strong>
                    {meilleur_reseau_pv["cout_total_reseau"]:.0f} €
                </div>
            </div>
            """, height=330)

        with s2:
            if scenario_batterie_disponible and finance_pv_batt is not None and budget_pv_batt is not None and meilleur_reseau_pv_batt is not None:
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
                    <div style="font-size:22px; font-weight:700; color:#1f2c3a; margin-bottom:10px;">
                        ☀️🔋 PV + batterie
                    </div>

                    <div style="font-size:15px; color:#4b5a68; margin-bottom:8px;">
                        Gain annuel estimé
                    </div>

                    <div style="font-size:26px; font-weight:800; color:#13283a; margin-bottom:10px;">
                        {f"{finance_pv_batt['gain_normal']:,.2f} €".replace(",", " ")}
                    </div>

                    <div style="font-size:14px; color:#506070; line-height:1.6;">
                        Économie autoconsommation directe :
                        <strong>{f"{finance_pv_batt['economie_auto_directe']:,.2f} €".replace(",", " ")}</strong>
                    </div>

                    <div style="font-size:14px; color:#506070; line-height:1.6;">
                        Économie batterie :
                        <strong>{f"{finance_pv_batt['economie_batterie']:,.2f} €".replace(",", " ")}</strong>
                    </div>

                    <div style="font-size:14px; color:#506070; line-height:1.6; margin-bottom:10px;">
                        Coût net :
                        <strong>{f"{budget_pv_batt['cout_total_net']:,.2f} €".replace(",", " ")}</strong>
                    </div>

                    <hr style="border:none; border-top:1px solid #cfe6d5; margin:12px 0;">

                    <div style="font-size:14px; color:#506070; line-height:1.6;">
                        <strong>Puissance de référence optimale :</strong>
                        {meilleur_reseau_pv_batt["puissance_reference_kw"]} kW
                    </div>

                    <div style="font-size:14px; color:#506070; line-height:1.6;">
                        <strong>Frais réseau annuels :</strong>
                        {meilleur_reseau_pv_batt["cout_total_reseau"]:.0f} €
                    </div>
                </div>
                """, height=330)
            else:
                components.html("""
                <div style="
                    background: linear-gradient(180deg, #effaf1, #e5f6e8);
                    border: 1px solid #bfe4c8;
                    border-radius: 18px;
                    padding: 18px 20px;
                    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
                    margin-bottom: 18px;
                    font-family: Arial, sans-serif;
                ">
                    <div style="font-size:22px; font-weight:700; color:#1f2c3a; margin-bottom:10px;">
                        ☀️🔋 PV + batterie
                    </div>

                    <div style="font-size:15px; color:#4b5a68; margin-bottom:8px;">
                        Scénario indisponible
                    </div>

                    <div style="font-size:14px; color:#506070; line-height:1.6;">
                        Veuillez activer la batterie dans la barre latérale et choisir un modèle
                        pour afficher ce scénario.
                    </div>
                </div>
                """, height=330)

        with s3:
            components.html("""
            <div style="
                background: linear-gradient(180deg, #fff6ec, #ffefdf);
                border: 1px solid #ffd4a8;
                border-radius: 18px;
                padding: 18px 20px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.06);
                margin-bottom: 18px;
                font-family: Arial, sans-serif;
            ">
                <div style="font-size:22px; font-weight:700; color:#1f2c3a; margin-bottom:10px;">
                     PV + batterie + EMS
                </div>

                <div style="font-size:15px; color:#4b5a68; margin-bottom:8px;">
                    Scénario à venir
                </div>
            </div>
            """, height=330)


        st.markdown("### Projection des gains cumulés par scénario")

        nb_annees_roi = 15
        annees_roi = np.arange(1, nb_annees_roi + 1)

        gains_cumules_pv = finance_pv["gain_normal"] * annees_roi
        cout_net_pv = budget_pv["cout_total_net"]

        fig_roi_scenarios, ax_roi = plt.subplots(figsize=(9, 4))

        ax_roi.plot(
            annees_roi,
            gains_cumules_pv,
            linewidth=2.5,
            marker='o',
            label="Avec PV",
            color="#2F87C8"
        )

        ax_roi.axhline(
            y=cout_net_pv,
            linewidth=2,
            linestyle='--',
            label="Coût net PV",
            color="#5FAEE3"
        )

        if scenario_batterie_disponible and finance_pv_batt is not None and budget_pv_batt is not None:
            gains_cumules_pv_batt = finance_pv_batt["gain_normal"] * annees_roi
            cout_net_pv_batt = budget_pv_batt["cout_total_net"]

            ax_roi.plot(
                annees_roi,
                gains_cumules_pv_batt,
                linewidth=2.5,
                marker='o',
                label="Avec PV + batterie",
                color="#43B581"
            )

            ax_roi.axhline(
                y=cout_net_pv_batt,
                linewidth=2,
                linestyle=':',
                label="Coût net PV + batterie",
                color="#7FD6A3"
            )

        ax_roi.set_title("Gains cumulés et coût net par scénario")
        ax_roi.set_xlabel("Année")
        ax_roi.set_ylabel("Montant (€)")
        ax_roi.set_xticks(annees_roi)
        ax_roi.grid(True, linestyle='--', alpha=0.6)
        ax_roi.legend(fontsize=8)

        st.pyplot(fig_roi_scenarios, use_container_width=False)


        r1, r2 = st.columns(2)

        with r1:
            st.metric(
                "ROI estimé - Avec PV",
                f"{finance_pv['tr_normal']:.1f} ans" if finance_pv["tr_normal"] is not None else "Non calculable"
            )

        with r2:
            if scenario_batterie_disponible and finance_pv_batt is not None:
                st.metric(
                    "ROI estimé - Avec PV + batterie",
                    f"{finance_pv_batt['tr_normal']:.1f} ans" if finance_pv_batt["tr_normal"] is not None else "Non calculable"
                )
            else:
                st.metric("ROI estimé - Avec PV + batterie", "—")

        st.markdown("---")

        st.subheader("Indicateurs clés")
        k1, k2, k3 = st.columns(3)

        with k1:
            st.markdown(f"""
            <div class="finance-card finance-card-blue">
                <div class="finance-title">📘 Mode normal</div>
                <div class="finance-subtitle">Gain annuel estimé</div>
                <div class="finance-big">{f"{finance['gain_normal']:,.2f} €".replace(",", " ")}</div>
                <div class="finance-small">Temps de retour : <strong>{f"{finance['tr_normal']:.1f} ans" if finance['tr_normal'] is not None else "Non calculable"}</strong></div>
                <div class="finance-small">Gain cumulé à 10 ans : <strong>{f"{finance['gain_10_ans_normal']:,.2f} €".replace(",", " ")}</strong></div>
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
                        ({finance['pct_gain_mix']:+.1f} % par rapport au mode normal)
                    </span>
                </div>

                <div style="font-size:26px; font-weight:800; color:#13283a; margin-bottom:8px;">
                    {f"{finance['gain_mix']:,.2f} €".replace(",", " ")}
                </div>

                <div style="font-size:14px; color:#506070; line-height:1.5;">
                    Temps de retour : <strong>{f"{finance['tr_mix']:.1f} ans" if finance['tr_mix'] is not None else "Non calculable"}</strong>
                </div>
                <div style="font-size:14px; color:#506070; line-height:1.5;">
                    Gain cumulé à 10 ans : <strong>{f"{finance['gain_10_ans_mix']:,.2f} €".replace(",", " ")}</strong>
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
                        ({finance['pct_gain_communaute']:+.1f} % par rapport au mode normal)
                    </span>
                </div>

                <div style="font-size:26px; font-weight:800; color:#13283a; margin-bottom:8px;">
                    {f"{finance['gain_communaute']:,.2f} €".replace(",", " ")}
                </div>

                <div style="font-size:14px; color:#506070; line-height:1.5;">
                    Temps de retour : <strong>{f"{finance['tr_communaute']:.1f} ans" if finance['tr_communaute'] is not None else "Non calculable"}</strong>
                </div>
                <div style="font-size:14px; color:#506070; line-height:1.5;">
                    Gain cumulé à 10 ans : <strong>{f"{finance['gain_10_ans_communaute']:,.2f} €".replace(",", " ")}</strong>
                </div>
            </div>
            """, height=220)

        st.markdown(f"""
        <div class="finance-roi-box">
            <div class="finance-title">⏱ Temps de retour estimé (mode normal)</div>
            <div class="finance-big">{f"{finance['tr_normal']:.1f} ans" if finance['tr_normal'] is not None else "Non calculable"}</div>
            <div class="finance-small">
                Économies annuelles via autoconsommation directe : <strong>{f"{finance['economie_auto_directe']:,.2f} €".replace(",", " ")}</strong><br>
                Économies annuelles via batterie : <strong>{f"{finance['economie_batterie']:,.2f} €".replace(",", " ")}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📈 Projection des gains cumulés sur 15 ans")

        nb_annees = 15
        annees = np.arange(1, nb_annees + 1)

        gains_cumules_normal = finance["gain_normal"] * annees
        gains_cumules_mix = finance["gain_mix"] * annees
        gains_cumules_communaute = finance["gain_communaute"] * annees

        fig_compare, ax = plt.subplots(figsize=(8, 4))
        ax.plot(annees, gains_cumules_normal, linewidth=2.5, marker='o', label="Mode normal")
        ax.plot(annees, gains_cumules_mix, linewidth=2.5, marker='o', label="Communauté 50 %")
        ax.plot(annees, gains_cumules_communaute, linewidth=2.5, marker='o', label="Communauté")
        ax.axhline(y=budget["cout_total_net"], linewidth=2, linestyle='--', label="Coût net après aides")

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
            c1.metric("Facture sans installation", f"{finance['cout_sans_installation']:,.2f} €".replace(",", " "))
            c2.metric("Coût imports", f"{finance['cout_import_normal']:,.2f} €".replace(",", " "))
            c3.metric("Revenu export", f"{finance['revenu_export_normal']:,.2f} €".replace(",", " "))
            c4.metric("Gain annuel estimé", f"{finance['gain_normal']:,.2f} €".replace(",", " "))

            c5, c6, c7 = st.columns(3)
            c5.metric("Économie autoconsommation directe", f"{finance['economie_auto_directe']:,.2f} €".replace(",", " "))
            c6.metric("Économie via batterie", f"{finance['economie_batterie']:,.2f} €".replace(",", " "))
            c7.metric("Solde annuel", f"{finance['solde_normal']:,.2f} €".replace(",", " "))

        with st.expander("📗 Détail – Communauté 50 %", expanded=False):
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Facture sans installation", f"{finance['cout_sans_installation']:,.2f} €".replace(",", " "))
            e2.metric("Coût imports mixte", f"{finance['cout_import_mix']:,.2f} €".replace(",", " "))
            e3.metric("Revenu ventes mixte", f"{finance['revenu_export_mix']:,.2f} €".replace(",", " "))
            e4.metric("Gain annuel estimé", f"{finance['gain_mix']:,.2f} €".replace(",", " "))

            e5, e6 = st.columns(2)
            e5.metric("Solde annuel mixte", f"{finance['solde_mix']:,.2f} €".replace(",", " "))
            e6.metric("Gain cumulé 10 ans", f"{finance['gain_10_ans_mix']:,.2f} €".replace(",", " "))

        with st.expander("📙 Détail – Communauté", expanded=False):
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Facture sans installation", f"{finance['cout_sans_installation']:,.2f} €".replace(",", " "))
            d2.metric("Coût imports communauté", f"{finance['cout_import_communaute']:,.2f} €".replace(",", " "))
            d3.metric("Revenu vente communauté", f"{finance['revenu_export_communaute']:,.2f} €".replace(",", " "))
            d4.metric("Gain annuel estimé", f"{finance['gain_communaute']:,.2f} €".replace(",", " "))

            d5, d6 = st.columns(2)
            d5.metric("Solde annuel communauté", f"{finance['solde_communaute']:,.2f} €".replace(",", " "))
            d6.metric("Gain cumulé 10 ans", f"{finance['gain_10_ans_communaute']:,.2f} €".replace(",", " "))

        st.markdown("---")
        st.subheader("Les frais d'utilisation du réseau")

        puissances_reference = [3, 7, 12, 17, 27, 43, 70, 100, 150, 200]
        liste_resultats = []

        for p_ref in puissances_reference:
            res = calcul_frais_reseau(mon_tableau, p_ref)
            liste_resultats.append({
                "Puissance de référence (kW)": p_ref,
                "Redevance fixe annuelle (€)": res["redevance_fixe_annuelle"],
                "Redevance volumétrique (€)": res["redevance_volumetrique"],
                "Coût du dépassement (€)": res["cout_depassement_total"],
                "Dépassement total (kWh)": res["depassement_total_kwh"],
                "Total frais réseau (€)": res["cout_total_reseau"]
            })

        df_frais_reseau = pd.DataFrame(liste_resultats)

        idx_min = df_frais_reseau["Total frais réseau (€)"].idxmin()
        meilleure_ligne = df_frais_reseau.loc[idx_min]
        meilleure_puissance = int(meilleure_ligne["Puissance de référence (kW)"])
        meilleur_cout = meilleure_ligne["Total frais réseau (€)"]

        st.success(
            f"Puissance de référence la plus avantageuse : {meilleure_puissance} kW "
            f"avec un coût total estimé de {meilleur_cout:.2f} € / an"
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Puissance optimale", f"{meilleure_puissance} kW")
        c2.metric("Redevance fixe", f"{meilleure_ligne['Redevance fixe annuelle (€)']:.2f} €")
        c3.metric("Coût dépassement", f"{meilleure_ligne['Coût du dépassement (€)']:.2f} €")
        c4.metric("Total frais réseau", f"{meilleur_cout:.2f} €")

        fig_reseau, ax_reseau = plt.subplots(figsize=(10, 4))
        ax_reseau.plot(
            df_frais_reseau["Puissance de référence (kW)"],
            df_frais_reseau["Total frais réseau (€)"],
            marker="o",
            linewidth=2
        )
        ax_reseau.set_title("Coût total des frais réseau selon la puissance de référence")
        ax_reseau.set_xlabel("Puissance de référence (kW)")
        ax_reseau.set_ylabel("Coût annuel (€)")
        ax_reseau.grid(True, linestyle="--", alpha=0.6)
        ax_reseau.scatter(meilleure_puissance, meilleur_cout, s=100, zorder=5)

        st.pyplot(fig_reseau)

        st.dataframe(
            df_frais_reseau.style.format({
                "Redevance fixe annuelle (€)": "{:.2f}",
                "Redevance volumétrique (€)": "{:.2f}",
                "Coût du dépassement (€)": "{:.2f}",
                "Dépassement total (kWh)": "{:.2f}",
                "Total frais réseau (€)": "{:.2f}",
            }),
            use_container_width=True
        )

# ==========================================
# ONGLET CONFIG
# ==========================================

def afficher_onglet_config(tab_config):
    with tab_config:
        st.header("Paramètres avancés")

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

            if st.button("Fermer l'accès"):
                st.session_state["acces_config"] = False
                st.rerun()

# ==========================================
# ONGLET SAUVEGARDE ET EXPORT
# ==========================================

def afficher_onglet_export(
    tab_export,
    data_import,
    sidebar_data,
    indicateurs,
    budget,
    finance_pv,
    finance_pv_batt,
    scenario_batterie_disponible,
    mon_tableau,
    budget_pv,
    budget_pv_batt
):
    with tab_export:
        st.subheader("Enregistrer un projet")

        nom_projet = st.text_input("Nom du fichier projet", value="projet_simulation", key="nom_projet_export")

        projet = construire_donnees_projet()
        projet_json = json.dumps(projet, ensure_ascii=False, indent=4)

        st.download_button(
            label="Télécharger le projet (JSON)",
            data=projet_json,
            file_name=f"{nom_projet}.json",
            mime="application/json"
        )

        st.markdown("---")
        st.subheader("Importer un projet")

        fichier_projet = st.file_uploader(
            "Choisir un fichier projet JSON",
            type=["json"],
            key="upload_projet_json"
        )

        if fichier_projet is not None:
            if st.button("Importer le projet", key="btn_import_projet"):
                charger_projet_json(fichier_projet)


        st.markdown("---")
        
        st.subheader("Informations du rapport")

        numero_projet = st.text_input("Numéro de projet", value="P-2026-001", key="numero_projet")
        nom_client = st.text_input("Nom du client", value="", key="nom_client")
        prenom_client = st.text_input("Prénom du client", value="", key="prenom_client")
        adresse_projet = st.text_input("Adresse du projet", value="", key="adresse_projet")

        st.subheader("Exporter un résumé PDF")

        pdf_buffer = generer_pdf_resume(
            data_import=data_import,
            sidebar_data=sidebar_data,
            indicateurs=indicateurs,
            budget=budget,
            finance_pv=finance_pv,
            finance_pv_batt=finance_pv_batt,
            scenario_batterie_disponible=scenario_batterie_disponible,
            numero_projet=numero_projet,
            nom_client=nom_client,
            prenom_client=prenom_client,
            adresse_projet=adresse_projet,
            mon_tableau=mon_tableau,
            budget_pv=budget_pv,
            budget_pv_batt=budget_pv_batt
        )

        st.download_button(
            label="Télécharger le résumé PDF",
            data=pdf_buffer,
            file_name=f"{nom_projet}_resume.pdf",
            mime="application/pdf"
        )

# ==========================================
# MAIN
# ==========================================

def main():
    initialiser_page()
    initialiser_session_state()



    if "projet_a_charger" in st.session_state:
        projet = st.session_state["projet_a_charger"]

        for cle, valeur in projet.items():
            st.session_state[cle] = valeur
            if "coeffs_mensuels_conso" in projet:
                for i, val in enumerate(projet["coeffs_mensuels_conso"]):
                    st.session_state[f"coeff_conso_{i}"] = val


        del st.session_state["projet_a_charger"]






    injecter_css()
    afficher_entete()

    tab_import, tab_saisons, tab_mensuel, tab_annuel, tab_budget, tab_finance, tab_export, tab_config = st.tabs([
        "Import & Paramètres",
        "Profils Journaliers",
        "Bilan Mensuel",
        "Résumé Annuel",
        "Budget",
        "Analyse financière",
        "Sauvegarde & Export",
        "Paramètres avancés"
    ])

    data_import = afficher_onglet_import(tab_import)
    sidebar_data = afficher_sidebar()

    mode_prod = data_import["mode_prod"]
    fichier_prod = data_import["fichier_prod"]

    if mode_prod in ["CSV SolarEdge", "Fichier simple Excel"] and fichier_prod is None:
        if mode_prod == "CSV SolarEdge":
            st.info("Veuillez importer le fichier CSV SolarEdge pour voir le reste de la simulation.")
        else:
            st.info("Veuillez importer le fichier Excel de production pour voir le reste de la simulation.")
        afficher_onglet_config(tab_config)
        st.stop()

    if mode_prod == "CSV SolarEdge" and fichier_prod is not None:
        fichier_prod.seek(0)

    mon_tableau = construire_tableau_principal(
        mode_prod=data_import["mode_prod"],
        fichier_prod=data_import["fichier_prod"],
        colonne_prod=data_import["colonne_prod"],
        puissance_crete=data_import["puissance_crete"],
        prod_specifique=data_import["prod_specifique"],
        df_repartition=data_import["df_repartition"],
        augmentation_prod_pct=sidebar_data["augmentation_prod_pct"],
        mode_conso=data_import["mode_conso"],
        donnees_conso=data_import["donnees_conso"],
        profil_choisi=data_import["profil_choisi"],
        profil_24h_custom=data_import["profil_24h_custom"],
        profil_24h_semaine=data_import["profil_24h_semaine"],
        profil_24h_weekend=data_import["profil_24h_weekend"],
        coeffs_mensuels_conso=data_import["coeffs_mensuels_conso"],
        borne_active=sidebar_data["borne_active"],
        puissance_borne_kw=sidebar_data["puissance_borne_kw"],
        horaires_borne=sidebar_data["horaires_borne"],
        jours_selectionnes=sidebar_data["jours_selectionnes"],
        activer_batterie=sidebar_data["activer_batterie"],
        chauffe_eau_actif=sidebar_data["chauffe_eau_actif"],
        puissance_chauffe_eau_kw=sidebar_data["puissance_chauffe_eau_kw"],
        horaires_chauffe_eau=sidebar_data["horaires_chauffe_eau"],
        jours_chauffe_eau=sidebar_data["jours_chauffe_eau"],
        pac_active=sidebar_data["pac_active"],
        puissance_pac_kw=sidebar_data["puissance_pac_kw"],
        horaires_pac=sidebar_data["horaires_pac"],
        jours_pac=sidebar_data["jours_pac"],
        chauffage_active=sidebar_data["chauffage_active"],
        puissance_chauffage_kw=sidebar_data["puissance_chauffage_kw"],
        horaires_chauffage=sidebar_data["horaires_chauffage"],
        jours_chauffage=sidebar_data["jours_chauffage"],
        capa_wh=sidebar_data["capa_wh"],
        puiss_w=sidebar_data["puiss_w"]
    )

    indicateurs = calculer_indicateurs_annuels(mon_tableau, sidebar_data["capa_wh"])

    budget = calculer_budget(
        puissance_crete=data_import["puissance_crete"],
        activer_batterie=sidebar_data["activer_batterie"],
        capa_kwh=sidebar_data["capa_kwh"],
        capa_wh=sidebar_data["capa_wh"],
        aide_pv_active=st.session_state["aide_pv_active"],
        aide_batterie_active=st.session_state["aide_batterie_active"]
    )

    # -----------------------------------------------------------
    # SCENARIO PV   
    # ----------------------------------------------------------

    if mode_prod == "CSV SolarEdge" and fichier_prod is not None:
        fichier_prod.seek(0)


    mon_tableau_pv = construire_tableau_principal(
        mode_prod=data_import["mode_prod"],
        fichier_prod=data_import["fichier_prod"],
        colonne_prod=data_import["colonne_prod"],
        puissance_crete=data_import["puissance_crete"],
        prod_specifique=data_import["prod_specifique"],
        df_repartition=data_import["df_repartition"],
        augmentation_prod_pct=sidebar_data["augmentation_prod_pct"],
        mode_conso=data_import["mode_conso"],
        donnees_conso=data_import["donnees_conso"],
        profil_choisi=data_import["profil_choisi"],
        profil_24h_custom=data_import["profil_24h_custom"],
        profil_24h_semaine=data_import["profil_24h_semaine"],
        profil_24h_weekend=data_import["profil_24h_weekend"],
        coeffs_mensuels_conso=data_import["coeffs_mensuels_conso"],
        borne_active=sidebar_data["borne_active"],
        puissance_borne_kw=sidebar_data["puissance_borne_kw"],
        horaires_borne=sidebar_data["horaires_borne"],
        jours_selectionnes=sidebar_data["jours_selectionnes"],
        chauffe_eau_actif=sidebar_data["chauffe_eau_actif"],
        puissance_chauffe_eau_kw=sidebar_data["puissance_chauffe_eau_kw"],
        horaires_chauffe_eau=sidebar_data["horaires_chauffe_eau"],
        jours_chauffe_eau=sidebar_data["jours_chauffe_eau"],
        pac_active=sidebar_data["pac_active"],
        puissance_pac_kw=sidebar_data["puissance_pac_kw"],
        horaires_pac=sidebar_data["horaires_pac"],
        jours_pac=sidebar_data["jours_pac"],
        chauffage_active=sidebar_data["chauffage_active"],
        puissance_chauffage_kw=sidebar_data["puissance_chauffage_kw"],
        horaires_chauffage=sidebar_data["horaires_chauffage"],
        jours_chauffage=sidebar_data["jours_chauffage"],
        activer_batterie=False,
        capa_wh=0.0,
        puiss_w=0.0
    )



    budget_pv = calculer_budget(
        puissance_crete=data_import["puissance_crete"],
        activer_batterie=False,
        capa_kwh=0.0,
        capa_wh=0.0,
        aide_pv_active=st.session_state["aide_pv_active"],
        aide_batterie_active=False
    )

    finance_pv = calculer_analyse_financiere(
        mon_tableau_pv,
        budget_pv["cout_total_net"]
    )



    # -----------------------------------------------------------
    # SCENARIO PV + BATTERIE    
    # ----------------------------------------------------------
    
    scenario_batterie_disponible = sidebar_data["activer_batterie"] and sidebar_data["capa_wh"] > 0 and sidebar_data["puiss_w"] > 0

    mon_tableau_pv_batt = None
    budget_pv_batt = None
    finance_pv_batt = None

    if scenario_batterie_disponible:
        if mode_prod == "CSV SolarEdge" and fichier_prod is not None:
            fichier_prod.seek(0)

        mon_tableau_pv_batt = construire_tableau_principal(
            mode_prod=data_import["mode_prod"],
            fichier_prod=data_import["fichier_prod"],
            colonne_prod=data_import["colonne_prod"],
            puissance_crete=data_import["puissance_crete"],
            prod_specifique=data_import["prod_specifique"],
            df_repartition=data_import["df_repartition"],
            augmentation_prod_pct=sidebar_data["augmentation_prod_pct"],
            mode_conso=data_import["mode_conso"],
            donnees_conso=data_import["donnees_conso"],
            profil_choisi=data_import["profil_choisi"],
            profil_24h_custom=data_import["profil_24h_custom"],
            profil_24h_semaine=data_import["profil_24h_semaine"],
            profil_24h_weekend=data_import["profil_24h_weekend"],
            coeffs_mensuels_conso=data_import["coeffs_mensuels_conso"],
            borne_active=sidebar_data["borne_active"],
            puissance_borne_kw=sidebar_data["puissance_borne_kw"],
            horaires_borne=sidebar_data["horaires_borne"],
            jours_selectionnes=sidebar_data["jours_selectionnes"],
            chauffe_eau_actif=sidebar_data["chauffe_eau_actif"],
            puissance_chauffe_eau_kw=sidebar_data["puissance_chauffe_eau_kw"],
            horaires_chauffe_eau=sidebar_data["horaires_chauffe_eau"],
            jours_chauffe_eau=sidebar_data["jours_chauffe_eau"],
            pac_active=sidebar_data["pac_active"],
            puissance_pac_kw=sidebar_data["puissance_pac_kw"],
            horaires_pac=sidebar_data["horaires_pac"],
            jours_pac=sidebar_data["jours_pac"],
            chauffage_active=sidebar_data["chauffage_active"],
            puissance_chauffage_kw=sidebar_data["puissance_chauffage_kw"],
            horaires_chauffage=sidebar_data["horaires_chauffage"],
            jours_chauffage=sidebar_data["jours_chauffage"],
            activer_batterie=True,
            capa_wh=sidebar_data["capa_wh"],
            puiss_w=sidebar_data["puiss_w"]
        )

        budget_pv_batt = calculer_budget(
            puissance_crete=data_import["puissance_crete"],
            activer_batterie=True,
            capa_kwh=sidebar_data["capa_kwh"],
            capa_wh=sidebar_data["capa_wh"],
            aide_pv_active=st.session_state["aide_pv_active"],
            aide_batterie_active=st.session_state["aide_batterie_active"]
        )

        finance_pv_batt = calculer_analyse_financiere(
            mon_tableau_pv_batt,
            budget_pv_batt["cout_total_net"]
        )


    df_reseau_pv, meilleur_reseau_pv = trouver_meilleure_puissance_reference(mon_tableau_pv)

    if scenario_batterie_disponible:
        df_reseau_pv_batt, meilleur_reseau_pv_batt = trouver_meilleure_puissance_reference(mon_tableau_pv_batt)
    else:
        df_reseau_pv_batt, meilleur_reseau_pv_batt = None, None




    afficher_onglet_saisons(tab_saisons, mon_tableau, sidebar_data["activer_batterie"])
    afficher_onglet_mensuel(tab_mensuel, mon_tableau)
    afficher_onglet_annuel(
        tab_annuel,
        mon_tableau,
        indicateurs,
        sidebar_data["capa_wh"],
        sidebar_data["activer_batterie"]
    )
    afficher_onglet_budget(tab_budget, budget, data_import["puissance_crete"], sidebar_data["activer_batterie"])
    afficher_onglet_finance(
        tab_finance=tab_finance,
        mon_tableau=mon_tableau,
        budget=budget,
        finance_pv=finance_pv,
        budget_pv=budget_pv,
        finance_pv_batt=finance_pv_batt,
        budget_pv_batt=budget_pv_batt,
        scenario_batterie_disponible=scenario_batterie_disponible,
        meilleur_reseau_pv=meilleur_reseau_pv,
        meilleur_reseau_pv_batt=meilleur_reseau_pv_batt
    )
    afficher_onglet_config(tab_config)




    afficher_onglet_export(
        tab_export=tab_export,
        data_import=data_import,
        sidebar_data=sidebar_data,
        indicateurs=indicateurs,
        budget=budget,
        finance_pv=finance_pv,
        finance_pv_batt=finance_pv_batt,
        scenario_batterie_disponible=scenario_batterie_disponible,
        mon_tableau=mon_tableau,
        budget_pv=budget_pv,
        budget_pv_batt=budget_pv_batt
    )


if __name__ == "__main__":
    main()