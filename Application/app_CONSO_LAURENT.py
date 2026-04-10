import pandas as pd
import matplotlib.pyplot as plt

# =========================
# PARAMÈTRES
# =========================
fichier_excel = "production.xlsx"
nom_colonne_date = "Date"
nom_colonne_prod = "Laurent D"
mois_filtre = 6   # juin

# =========================
# LECTURE
# =========================
df = pd.read_excel(fichier_excel)

df[nom_colonne_date] = pd.to_datetime(df[nom_colonne_date], dayfirst=True, errors="coerce")

df[nom_colonne_prod] = (
    df[nom_colonne_prod]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.replace(" ", "", regex=False)
)

df[nom_colonne_prod] = pd.to_numeric(df[nom_colonne_prod], errors="coerce")

df = df.dropna(subset=[nom_colonne_date, nom_colonne_prod])

# =========================
# FILTRE SUR JUIN
# =========================
df = df[df[nom_colonne_date].dt.month == mois_filtre].copy()

# =========================
# PRÉPARATION
# =========================
# Jour du mois
df["jour_mois"] = df[nom_colonne_date].dt.day

# Semaine dans le mois : 1, 2, 3, 4, 5
df["semaine_mois"] = ((df["jour_mois"] - 1) // 7) + 1

# Jour de semaine : lundi=0 ... dimanche=6
df["jour_semaine"] = df[nom_colonne_date].dt.weekday

# Heure et minute
df["heure"] = df[nom_colonne_date].dt.hour
df["minute"] = df[nom_colonne_date].dt.minute

# Position sur l'axe X en heures
# ex :
# lundi 00:00 = 0
# lundi 06:00 = 6
# mardi 00:00 = 24
# mercredi 12:15 = 60.25
df["x"] = df["jour_semaine"] * 24 + df["heure"] + df["minute"] / 60

# =========================
# GRAPHIQUE
# =========================
plt.figure(figsize=(16, 6))

semaines_disponibles = sorted(df["semaine_mois"].unique())

for semaine in semaines_disponibles:
    df_sem = df[df["semaine_mois"] == semaine].copy()
    df_sem = df_sem.sort_values(nom_colonne_date)

    plt.plot(df_sem["x"], df_sem[nom_colonne_prod], label=f"Semaine {semaine}")

# =========================
# AXE X
# =========================
jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

positions_xticks = []
labels_xticks = []

for j in range(7):
    for h in [0, 6, 12, 18]:
        positions_xticks.append(j * 24 + h)
        labels_xticks.append(f"{jours[j]} {h:02d}h")

plt.xticks(positions_xticks, labels_xticks, rotation=45)

plt.xlabel("Semaine")
plt.ylabel("Production")
plt.title("Production sur une semaine complète - comparaison des semaines de juin")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()