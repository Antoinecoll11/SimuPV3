import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analyse consommation", layout="wide")

jours_fr = {
    0: "Lundi",
    1: "Mardi",
    2: "Mercredi",
    3: "Jeudi",
    4: "Vendredi",
    5: "Samedi",
    6: "Dimanche"
}


def lire_fichier_excel(fichier):
    """
    Essaie plusieurs headers possibles et cherche une colonne date
    et une colonne consommation.
    """
    for header_test in [0, 1, 2, 3]:
        try:
            fichier.seek(0)
            df = pd.read_excel(fichier, header=header_test)
            df.columns = [str(c).strip() for c in df.columns]

            col_date = None
            col_conso = None

            for c in df.columns:
                c_low = c.lower()

                if col_date is None and (
                    "période statistique" in c_low
                    or "periode statistique" in c_low
                    or c_low == "date"
                    or "time" in c_low
                ):
                    col_date = c

                if col_conso is None and "consommation" in c_low:
                    col_conso = c

            if col_date is not None and col_conso is not None:
                df = df[[col_date, col_conso]].copy()
                df.columns = ["Période statistique", "Consommation (kWh)"]
                return df, header_test

        except Exception:
            pass

    return None, None


def preparer_donnees(df):
    df = df.copy()

    # affichage brut pour vérifier
    st.write("Aperçu brut des données lues :")
    st.dataframe(df.head(10), use_container_width=True)

    df["Période statistique"] = pd.to_datetime(
        df["Période statistique"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    # conversion conso
    df["Consommation (kWh)"] = (
        df["Consommation (kWh)"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )

    df["Consommation (kWh)"] = pd.to_numeric(
        df["Consommation (kWh)"],
        errors="coerce"
    )

    st.write("Dates valides :", df["Période statistique"].notna().sum())
    st.write("Dates invalides :", df["Période statistique"].isna().sum())
    st.write("Consommations valides :", df["Consommation (kWh)"].notna().sum())
    st.write("Consommations invalides :", df["Consommation (kWh)"].isna().sum())

    df = df.dropna(subset=["Période statistique", "Consommation (kWh)"])
    df = df.sort_values("Période statistique").reset_index(drop=True)

    if df.empty:
        return df

    # si données en 15 min -> passage en horaire
    if len(df) > 1:
        diff = df["Période statistique"].diff().dropna()
        if not diff.empty:
            pas = diff.mode().iloc[0]
            st.write("Pas de temps détecté :", pas)

            if pas == pd.Timedelta(minutes=15):
                df = df.set_index("Période statistique").resample("H").sum().reset_index()

    df["Date"] = df["Période statistique"].dt.date
    df["Heure"] = df["Période statistique"].dt.hour
    df["Jour_semaine_num"] = df["Période statistique"].dt.weekday
    df["Jour_semaine"] = df["Jour_semaine_num"].map(jours_fr)

    iso = df["Période statistique"].dt.isocalendar()
    df["ISO_Year"] = iso.year
    df["ISO_Week"] = iso.week
    df["Semaine_ID"] = df["ISO_Year"].astype(str) + "-S" + df["ISO_Week"].astype(str).str.zfill(2)

    return df


def tracer_jour_semaine(df, jour_num, titre):
    df_jour = df[df["Jour_semaine_num"] == jour_num].copy()

    fig, ax = plt.subplots(figsize=(10, 4))

    if df_jour.empty:
        ax.set_title(titre)
        ax.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", transform=ax.transAxes)
        ax.set_xlabel("Heure")
        ax.set_ylabel("Consommation (kWh)")
        return fig

    dates_uniques = sorted(df_jour["Date"].unique())

    for d in dates_uniques:
        sous_df = df_jour[df_jour["Date"] == d].sort_values("Heure")
        ax.plot(
            sous_df["Heure"],
            sous_df["Consommation (kWh)"],
            label=str(d)
        )

    ax.set_title(titre)
    ax.set_xlabel("Heure")
    ax.set_ylabel("Consommation (kWh)")
    ax.set_xticks(range(24))
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, ncol=2)

    return fig


def tracer_semaines(df, titre):
    fig, ax = plt.subplots(figsize=(12, 5))

    semaines = sorted(df["Semaine_ID"].unique())

    if len(semaines) == 0:
        ax.set_title(titre)
        ax.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", transform=ax.transAxes)
        ax.set_xlabel("Heure dans la semaine")
        ax.set_ylabel("Consommation (kWh)")
        return fig

    for semaine_id in semaines:
        df_sem = df[df["Semaine_ID"] == semaine_id].copy()
        df_sem["Position_semaine"] = df_sem["Jour_semaine_num"] * 24 + df_sem["Heure"]
        df_sem = df_sem.sort_values("Position_semaine")

        ax.plot(
            df_sem["Position_semaine"],
            df_sem["Consommation (kWh)"],
            label=semaine_id
        )

    ax.set_title(titre)
    ax.set_xlabel("Heure dans la semaine")
    ax.set_ylabel("Consommation (kWh)")
    ax.grid(True, alpha=0.3)

    positions = [0, 24, 48, 72, 96, 120, 144]
    labels = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)

    ax.legend(fontsize=8, ncol=2)

    return fig


def afficher_analyse_fichier(fichier, nom_onglet):
    st.subheader(f"Analyse - {nom_onglet}")

    if fichier is None:
        st.info("Importer un fichier Excel.")
        return

    df, header_utilise = lire_fichier_excel(fichier)

    if df is None:
        st.error("Impossible de trouver correctement les colonnes date et consommation.")
        return

    st.write("Header utilisé :", header_utilise)
    st.write("Colonnes retenues :", list(df.columns))

    df = preparer_donnees(df)

    if df.empty:
        st.warning("Aucune donnée exploitable trouvée.")
        return

    st.markdown(f"**Nombre de lignes retenues :** {len(df)}")
    st.markdown(f"**Consommation totale :** {df['Consommation (kWh)'].sum():.3f} kWh")
    st.markdown(f"**Début :** {df['Période statistique'].min()}")
    st.markdown(f"**Fin :** {df['Période statistique'].max()}")

    with st.expander("Voir les données préparées"):
        st.dataframe(df.head(200), use_container_width=True)

    st.markdown("## Courbes par jour de la semaine")

    col1, col2 = st.columns(2)

    for i in range(7):
        fig = tracer_jour_semaine(df, i, f"{jours_fr[i]} - toutes les courbes")
        if i % 2 == 0:
            with col1:
                st.pyplot(fig)
        else:
            with col2:
                st.pyplot(fig)

    st.markdown("## Courbes par semaine complète")
    fig_semaines = tracer_semaines(df, "Une courbe par semaine")
    st.pyplot(fig_semaines)


st.title("Analyse simple de consommation")

tab1, tab2, tab3 = st.tabs(["Fichier 1", "Fichier 2", "Fichier 3"])

with tab1:
    fichier1 = st.file_uploader("Importer le fichier Excel 1", type=["xlsx"], key="f1")
    afficher_analyse_fichier(fichier1, "Fichier 1")

with tab2:
    fichier2 = st.file_uploader("Importer le fichier Excel 2", type=["xlsx"], key="f2")
    afficher_analyse_fichier(fichier2, "Fichier 2")

with tab3:
    fichier3 = st.file_uploader("Importer le fichier Excel 3", type=["xlsx"], key="f3")
    afficher_analyse_fichier(fichier3, "Fichier 3")