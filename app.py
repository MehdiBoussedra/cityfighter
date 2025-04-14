import streamlit as st
import pandas as pd

# === Données (à charger avec tes fichiers préparés) ===
df_pop = pd.read_excel("Villes_regroupees_population.xlsx")
df_emploi = pd.read_excel("emploi_variables_utiles.xlsx")
df_logement = pd.read_excel("logement_variables_utiles.xlsx")

# Fusion (sur 'ville_regroupee' ou 'codgeo' selon structure)
df = df_pop.merge(df_emploi, on="codgeo", how="left")
df = df.merge(df_logement, on="codgeo", how="left")

# === Interface utilisateur ===
st.title("🏙️ City Fighting - Comparaison de Villes")

# Sélection des villes
villes = df["ville_regroupee"].unique()
ville1 = st.selectbox("Sélectionner la première ville", villes)
ville2 = st.selectbox("Sélectionner la deuxième ville", villes)

# Extraire les données
data1 = df[df["ville_regroupee"] == ville1].iloc[0]
data2 = df[df["ville_regroupee"] == ville2].iloc[0]

# === Affichage ===
st.subheader(f"📊 Comparaison entre {ville1} et {ville2}")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### {ville1}")
    st.write(f"Population 2021 : {int(data1['p21_pop'])}")
    st.write(f"Total emplois : {int(data1['total_emplois'])}")
    st.write(f"Chômeurs : {int(data1['total_chomeurs'])}")
    st.write(f"Logements : {int(data1['P20_LOG'])}")
    

with col2:
    st.markdown(f"### {ville2}")
    st.write(f"Population 2021 : {int(data2['p21_pop'])}")
    st.write(f"Total emplois : {int(data2['total_emplois'])}")
    st.write(f"Chômeurs : {int(data2['total_chomeurs'])}")
    st.write(f"Logements : {int(data2['P20_LOG'])}")

