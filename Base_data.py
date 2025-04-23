import pandas as pd
import gdown
import os

# === 1. Télécharger les fichiers Google Drive dans le dossier actuel ===
fichiers_drive = {
    "base-cc-emploi-pop-active-2020_v2.CSV": "1ZSzHZwxcsoDn4VxyjsPbj7K0zmoJYPdL",
    "base-cc-logement-2020.CSV": "1LU57jvjNQSOGwnGM6_cNbENVYez1FKzP",
    "data-es.csv": "1nn1TT2_2hNXLyDFOlA7StDYLOR0UE3NN"
}

for nom_fichier, file_id in fichiers_drive.items():
    if not os.path.exists(nom_fichier):
        url = f"https://drive.google.com/uc?id={file_id}"
        print(f"📥 Téléchargement de {nom_fichier}...")
        gdown.download(url, nom_fichier, quiet=False)
    else:
        print(f"✅ {nom_fichier} déjà présent.")


# === 1. Population - Chargement et filtrage ===
df_pop = pd.read_excel("POPULATION_MUNICIPALE_COMMUNES_FRANCE.xlsx")
df_pop.rename(columns={"CODGEO": "codgeo", "LIBGEO": "libgeo"}, inplace=True)
df_pop["codgeo"] = df_pop["codgeo"].astype(str)

df_filtered = df_pop[df_pop["p21_pop"] >= 20000].copy()
colonnes_utiles = ["codgeo", "libgeo", "p13_pop", "p14_pop", "p15_pop", "p16_pop",
                   "p17_pop", "p18_pop", "p19_pop", "p20_pop", "p21_pop"]
df_filtered = df_filtered[colonnes_utiles]
df_filtered.to_excel("Villes_20000_plus_2013_2021.xlsx", index=False)

# === 2. Fonction pour regrouper les arrondissements ===
def regrouper_arrondissements(nom):
    if isinstance(nom, str):
        if "Paris" in nom:
            return "Paris"
        elif "Lyon" in nom:
            return "Lyon"
        elif "Marseille" in nom:
            return "Marseille"
        else:
            return nom.strip()
    return nom

df_filtered["ville_regroupee"] = df_filtered["libgeo"].apply(regrouper_arrondissements)

# === 3. Regroupement population ===
colonnes_pop = [col for col in df_filtered.columns if col.startswith("p") and "_pop" in col.lower()]
df_regroupe = df_filtered.groupby("ville_regroupee", as_index=False)[colonnes_pop].sum()

# Ajout des codgeo représentatifs
codes_representatifs = {
    "Paris": "75056",
    "Lyon": "69380",
    "Marseille": "13055"
}
df_regroupe["codgeo"] = df_regroupe["ville_regroupee"].map(codes_representatifs)

# Compléter codgeo pour les autres villes
autres = df_filtered[~df_filtered["libgeo"].str.contains("Paris|Lyon|Marseille", case=False, na=False)]
autres = autres[["libgeo", "codgeo"]].drop_duplicates()
autres["ville_regroupee"] = autres["libgeo"]
df_regroupe = pd.merge(df_regroupe, autres[["ville_regroupee", "codgeo"]],
                       on="ville_regroupee", how="left", suffixes=("", "_autre"))
df_regroupe["codgeo"] = df_regroupe["codgeo"].fillna(df_regroupe["codgeo_autre"])
df_regroupe.drop(columns=["codgeo_autre"], inplace=True)

# === 4. Coordonnées géographiques ===
df_coords = pd.read_csv("20230823-communes-departement-region.csv", sep=",")
df_coords.rename(columns={
    "code_commune_INSEE": "codgeo",
    "nom_commune": "libgeo",
    "latitude": "lat",
    "longitude": "lon"
}, inplace=True)
df_coords["codgeo"] = df_coords["codgeo"].astype(str)

df_regroupe = df_regroupe.merge(df_coords[["codgeo", "lat", "lon"]], on="codgeo", how="left")

# Ajouter manuellement les coordonnées manquantes
coords_manquantes = {
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Lyon": {"lat": 45.7640, "lon": 4.8357},
    "Marseille": {"lat": 43.2965, "lon": 5.3698}
}
for ville, coords in coords_manquantes.items():
    df_regroupe.loc[df_regroupe["ville_regroupee"] == ville, "lat"] = coords["lat"]
    df_regroupe.loc[df_regroupe["ville_regroupee"] == ville, "lon"] = coords["lon"]

df_regroupe.to_excel("Villes_regroupees_population.xlsx", index=False)

# === 5. LOGEMENT ===
df_logement_brut = pd.read_csv("base-cc-logement-2020.CSV", sep=";", encoding="utf-8", low_memory=False)
colonnes_logement = ["CODGEO", "P20_LOG", "P20_RP", "P20_LOGVAC", "P20_RP_PROP", "P20_RP_LOC"]
df_logement = df_logement_brut[colonnes_logement].copy()
df_logement.rename(columns={"CODGEO": "codgeo"}, inplace=True)
df_logement["libgeo"] = df_logement["codgeo"].map(df_pop.set_index("codgeo")["libgeo"])
df_logement["ville_regroupee"] = df_logement["libgeo"].apply(regrouper_arrondissements)

df_logement_grouped = df_logement.groupby("ville_regroupee", as_index=False)[
    ["P20_LOG", "P20_RP", "P20_LOGVAC", "P20_RP_PROP", "P20_RP_LOC"]
].sum()
df_logement_grouped.to_excel("logement_variables_utiles_grouped.xlsx", index=False)

# === 6. EMPLOI ===
df_emploi_brut = pd.read_csv("base-cc-emploi-pop-active-2020_v2.CSV", sep=";", encoding="utf-8", low_memory=False)
colonnes_emploi = ["CODGEO", "P20_ACT15P", "P20_CHOM1564", "P20_EMPLT"]
df_emploi = df_emploi_brut[colonnes_emploi].copy()
df_emploi.rename(columns={"CODGEO": "codgeo"}, inplace=True)
df_emploi["libgeo"] = df_emploi["codgeo"].map(df_pop.set_index("codgeo")["libgeo"])
df_emploi["ville_regroupee"] = df_emploi["libgeo"].apply(regrouper_arrondissements)

df_emploi["total_emplois"] = df_emploi["P20_EMPLT"]
df_emploi["total_actifs"] = df_emploi["P20_ACT15P"]
df_emploi["total_chomeurs"] = df_emploi["P20_CHOM1564"]

df_emploi_grouped = df_emploi.groupby("ville_regroupee", as_index=False)[
    ["total_emplois", "total_actifs", "total_chomeurs"]
].sum()
df_emploi_grouped.to_excel("emploi_variables_utiles_grouped.xlsx", index=False)

# === 7. LIEN WIKIPÉDIA ===
def lien_wikipedia(ville):
    ville_formatee = ville.replace(" ", "_")
    return f"https://fr.wikipedia.org/wiki/{ville_formatee}"

df_regroupe["wikipedia_url"] = df_regroupe["ville_regroupee"].apply(lien_wikipedia)
df_regroupe.to_excel("Villes_regroupees_population_wiki.xlsx", index=False)


# === 1. Chargement de la base DATA ES ===
df_sport = pd.read_csv("data-es.csv", sep=None, engine="python")

# Vérification du nom exact de la colonne code INSEE
df_sport.rename(columns={"Commune INSEE": "codgeo"}, inplace=True)
df_sport["codgeo"] = df_sport["codgeo"].astype(str)

# === 2. Définition des catégories d’équipements ===

categories_sport = {
    "Sports collectifs": [
        "Terrain de football", "Terrain de basket-ball", "Terrain de handball", "Terrain de rugby", "Salle de volley-ball"
    ],
    "Raquettes": [
        "Court de tennis", "Salle ou terrain de badminton", "Salle ou terrain de squash", "Salle de tennis de table"
    ],
    "Urbains / libres": [
        "Skatepark", "Multisports/City-stades", "Aire de fitness/street workout", "Parkour/blocpark"
    ],
    "Piscines / natation": [
        "Bassin sportif de natation", "Bassin ludique de natation", "Piscine", "Fosse à plongeon"
    ],
    "Gymnases / multisports": [
        "Salle multisports (gymnase)", "Dojo / Salle d'arts martiaux", "Salle de danse", "Salle de musculation/cardiotraining"
    ]
}

# === 3. Calcul du nombre d’équipements par catégorie et par ville ===

# Initialisation d’un DataFrame regroupé
df_sport_grouped = pd.DataFrame()
df_sport_grouped["codgeo"] = df_sport["codgeo"].unique()

for cat_name, liste_types in categories_sport.items():
    df_cat = df_sport[df_sport["Type d'équipement sportif"].isin(liste_types)]
    df_count = df_cat.groupby("codgeo").size().reset_index(name=f"nb_{cat_name.lower().replace(' ', '_')}")
    df_sport_grouped = df_sport_grouped.merge(df_count, on="codgeo", how="left")

# Remplacer les NaN par 0
df_sport_grouped.fillna(0, inplace=True)
df_sport_grouped[df_sport_grouped.columns[1:]] = df_sport_grouped[df_sport_grouped.columns[1:]].astype(int)

# === 4. Fusion avec la base principale ===

# Assurer que le code INSEE est bien en str pour les deux bases
df_regroupe["codgeo"] = df_regroupe["codgeo"].astype(str)
df_sport_grouped["codgeo"] = df_sport_grouped["codgeo"].astype(str)

# Fusion
df_regroupe = df_regroupe.merge(df_sport_grouped, on="codgeo", how="left")

# Remplacer les NaN restants (villes sans équipement) par 0
cols_sport = [col for col in df_sport_grouped.columns if col != "codgeo"]
df_regroupe[cols_sport] = df_regroupe[cols_sport].fillna(0).astype(int)

# === 5. Sauvegarde de la base enrichie
df_regroupe.to_excel("Villes_regroupees_population_wiki_sport.xlsx", index=False)

print("✅ Données sportives par catégorie intégrées avec succès.")

# === 8. DEBUG CHECKS ===
print("✅ Colonnes population :", df_regroupe.columns.tolist())
print("✅ Coordonnées manquantes :", df_regroupe[df_regroupe["lat"].isna()])
print("✅ Colonnes emploi :", df_emploi_grouped.columns.tolist())
print("✅ Colonnes logement :", df_logement_grouped.columns.tolist())

