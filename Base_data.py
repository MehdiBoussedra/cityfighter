import pandas as pd


df_pop = pd.read_excel("POPULATION_MUNICIPALE_COMMUNES_FRANCE.xlsx")
df_pop.rename(columns={"CODGEO": "codgeo", "LIBGEO": "libgeo"}, inplace=True)
df_pop["codgeo"] = df_pop["codgeo"].astype(str)
df_filtered = df_pop[df_pop["p21_pop"] >= 20000].copy()
colonnes_utiles = ["codgeo", "libgeo", "p13_pop", "p14_pop", "p15_pop", "p16_pop", "p17_pop", "p18_pop", "p19_pop", "p20_pop", "p21_pop"]
df_filtered = df_filtered[colonnes_utiles]
df_filtered.to_excel("Villes_20000_plus_2013_2021.xlsx", index=False)


df = pd.read_excel("Villes_20000_plus_2013_2021.xlsx")

df = df_pop.merge(df_emploi, on="ville_regroupee", how="left")
df = df.merge(df_logement, on="ville_regroupee", how="left")


def regrouper_arrondissements(nom):
    if "Paris" in nom:
        return "Paris"
    elif "Lyon" in nom:
        return "Lyon"
    elif "Marseille" in nom:
        return "Marseille"
    else:
        return nom.strip()

df["ville_regroupee"] = df["libgeo"].apply(regrouper_arrondissements)
colonnes_pop = [col for col in df.columns if col.startswith("p") and "_pop" in col.lower()]
df_regroupe = df.groupby("ville_regroupee", as_index=False)[colonnes_pop].sum()

#  Ajouter un code INSEE principal pour chaque ville regroupée
codes_representatifs = {
    "Paris": "75056",
    "Lyon": "69380",
    "Marseille": "13055"
}

df_regroupe["codgeo"] = df_regroupe["ville_regroupee"].map(codes_representatifs)

#  Compléter pour les autres villes avec les codes d'origine
autres = df_filtered[~df_filtered["libgeo"].str.contains("Paris|Lyon|Marseille", case=False, na=False)]
autres = autres[["libgeo", "codgeo"]].drop_duplicates()
autres["ville_regroupee"] = autres["libgeo"]

df_regroupe = pd.merge(df_regroupe, autres[["ville_regroupee", "codgeo"]], on="ville_regroupee", how="left", suffixes=("", "_autre"))
df_regroupe["codgeo"] = df_regroupe["codgeo"].fillna(df_regroupe["codgeo_autre"])
df_regroupe.drop(columns=["codgeo_autre"], inplace=True)

df_regroupe.to_excel("Villes_regroupees_population.xlsx", index=False)


df_brut = pd.read_csv("base-cc-logement-2020.CSV", sep=";", encoding="utf-8", low_memory=False)
colonnes_logement = ["CODGEO", "P20_LOG", "P20_RP", "P20_LOGVAC", "P20_RP_PROP", "P20_RP_LOC"]
logement_variables_utiles = df_brut[colonnes_logement].copy()
logement_variables_utiles.rename(columns={"CODGEO": "codgeo"}, inplace=True)
logement_variables_utiles.to_excel("logement_variables_utiles.xlsx", index=False)



df_emploi_brut = pd.read_csv("base-cc-emploi-pop-active-2020_v2.CSV", sep=";", encoding="utf-8", low_memory=False)
colonnes_emploi = ["CODGEO", "P20_ACT15P", "P20_CHOM1564", "P20_EMPLT"]
emploi_variables_utiles = df_emploi_brut[colonnes_emploi].copy()
emploi_variables_utiles.rename(columns={"CODGEO": "codgeo"}, inplace=True)
emploi_variables_utiles.to_excel("emploi_variables_utiles.xlsx", index=False)

emploi_variables_utiles["total_emplois"] = emploi_variables_utiles["P20_EMPLT"]
emploi_variables_utiles["total_actifs"] = emploi_variables_utiles["P20_ACT15P"]
emploi_variables_utiles["total_chomeurs"] = emploi_variables_utiles["P20_CHOM1564"]



def lien_wikipedia(ville):
    ville_formatee = ville.replace(" ", "_")
    return f"https://fr.wikipedia.org/wiki/{ville_formatee}"

df_regroupe["wikipedia_url"] = df_regroupe["ville_regroupee"].apply(lien_wikipedia)
df_regroupe.to_excel("Villes_regroupees_population_wiki.xlsx", index=False)

print("Colonnes df_pop :", df_regroupe.columns.tolist())
print("Colonnes df_emploi :", emploi_variables_utiles.columns.tolist())
