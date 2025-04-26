import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import gdown
import os

# === 1. Télécharger les fichiers Google Drive dans le dossier actuel ===
fichiers_drive = {
    "base-cc-emploi-pop-active-2020_v2.CSV": "1ZSzHZwxcsoDn4VxyjsPbj7K0zmoJYPdL",
    "base-cc-logement-2020.CSV": "1LU57jvjNQSOGwnGM6_cNbENVYez1FKzP",
    "data-es.csv": "1nn1TT2_2hNXLyDFOlA7StDYLOR0UE3NN",
    "base-des-lieux-et-des-equipements-culturels.csv":"1SAGJ_bxmCx4G4FdwD3hcXlQNwYaHC_OM"
}

for nom_fichier, file_id in fichiers_drive.items():
    if not os.path.exists(nom_fichier):
        url = f"https://drive.google.com/uc?id={file_id}"
        print(f"📥 Téléchargement de {nom_fichier}...")
        gdown.download(url, nom_fichier, quiet=False)
    else:
        print(f"✅ {nom_fichier} déjà présent.")


# === Configuration Streamlit ===
st.set_page_config(page_title="City Fighting", layout="wide")

# === Barre de navigation ===
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Aller à :", [
    "🏠 Accueil",
    "🏙️ Comparaison de villes",
    "🗺️ Carte interactive",
    "🌤️ Météo",
    "🏃 Offre sportive",
    "🎨 Données culturelles",
    "ℹ️ À propos"
])

# === Chargement des données ===
df_pop = pd.read_excel("Villes_regroupees_population_wiki_sport.xlsx")
df_emploi = pd.read_excel("emploi_variables_utiles_grouped.xlsx")
df_logement = pd.read_excel("logement_variables_utiles_grouped.xlsx")

df = df_pop.merge(df_emploi, on="ville_regroupee", how="left")
df = df.merge(df_logement, on="ville_regroupee", how="left")

# === Sélection de villes ===
villes = sorted(df["ville_regroupee"].unique())
ville1 = st.sidebar.selectbox("📍 Ville 1", villes, index=villes.index("Lille") if "Lille" in villes else 0)
ville2 = st.sidebar.selectbox("📍 Ville 2", villes, index=villes.index("Lyon") if "Lyon" in villes else 1)

if ville1 == ville2:
    st.warning("⚠️ Veuillez sélectionner deux villes différentes.")
    st.stop()

data1 = df[df["ville_regroupee"] == ville1].iloc[0]
data2 = df[df["ville_regroupee"] == ville2].iloc[0]

# === PAGE : ACCEUIL ===
if page == "🏠 Accueil":
    st.title("🏙️ Bienvenue sur City Fighting")
    st.markdown("""
        **City Fighting** est une application de comparaison entre les grandes villes françaises (plus de 20 000 habitants).  
        Elle vous permet de :
        - Comparer deux villes selon leur population, emploi, logement, équipements sportifs, infrastructures culturelles.
        - Visualiser ces villes sur une carte interactive.
        - Accéder à la météo en temps réel et aux prévisions.

        👉 Sélectionnez une rubrique dans le menu de gauche pour commencer.
    """)

# === PAGE : COMPARAISON ===
if page == "🏙️ Comparaison de villes":
    st.title("🏙️ Comparaison de Villes")
    st.subheader(f"📊 {ville1} vs {ville2} - Données générales (2021)")

    indicateurs = ["Population", "Emplois", "Chômeurs", "Logements"]
    val1 = [int(data1["p21_pop"]), int(data1["total_emplois"]), int(data1["total_chomeurs"]), int(data1["P20_LOG"])]
    val2 = [int(data2["p21_pop"]), int(data2["total_emplois"]), int(data2["total_chomeurs"]), int(data2["P20_LOG"])]
    txt1 = [f"{v:,}".replace(",", " ") for v in val1]
    txt2 = [f"{v:,}".replace(",", " ") for v in val2]

    fig = go.Figure(data=[
        go.Bar(name=ville1, x=indicateurs, y=val1, text=txt1, textposition='auto', marker_color='royalblue'),
        go.Bar(name=ville2, x=indicateurs, y=val2, text=txt2, textposition='auto', marker_color='tomato')
    ])
    fig.update_layout(barmode='group', template='plotly_white')
    st.plotly_chart(fig)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 📌 {ville1}")
        st.write(f"Taux de chômage : {data1['total_chomeurs'] / data1['total_actifs'] * 100:.1f} %")
        st.write(f"Logements vacants : {data1['P20_LOGVAC'] / data1['P20_LOG'] * 100:.1f} %")
        st.write(f"Propriétaires : {data1['P20_RP_PROP'] / data1['P20_RP'] * 100:.1f} %")
        st.write(f"Emplois pour 100 habitants : {data1['total_emplois'] / data1['p21_pop'] * 100:.1f}")
        st.markdown(f"[🔎 Voir sur Wikipédia]({data1['wikipedia_url']})")

    with col2:
        st.markdown(f"### 📌 {ville2}")
        st.write(f"Taux de chômage : {data2['total_chomeurs'] / data2['total_actifs'] * 100:.1f} %")
        st.write(f"Logements vacants : {data2['P20_LOGVAC'] / data2['P20_LOG'] * 100:.1f} %")
        st.write(f"Propriétaires : {data2['P20_RP_PROP'] / data2['P20_RP'] * 100:.1f} %")
        st.write(f"Emplois pour 100 habitants : {data2['total_emplois'] / data2['p21_pop'] * 100:.1f}")
        st.markdown(f"[🔎 Voir sur Wikipédia]({data2['wikipedia_url']})")

# === PAGE : CARTE ===
elif page == "🗺️ Carte interactive":
    st.title("🗺️ Carte interactive des villes de plus de 20 000 habitants")
    indicateur = st.selectbox("Indicateur à visualiser", ["p21_pop", "total_emplois", "total_chomeurs", "P20_LOG"],
                              format_func=lambda x: {
                                  "p21_pop": "Population 2021",
                                  "total_emplois": "Nombre d'emplois",
                                  "total_chomeurs": "Nombre de chômeurs",
                                  "P20_LOG": "Nombre de logements"
                              }[x])

    df_map = df.copy()
    df_map["Valeur sélectionnée"] = df_map[indicateur].fillna(0).astype(int)
    df_map["Valeur sélectionnée"] = df_map["Valeur sélectionnée"].apply(lambda x: x if x > 0 else 1)
    df_map["Valeur"] = df_map["Valeur sélectionnée"].apply(lambda x: f"{x:,}".replace(",", " "))
    df_map["color"] = df_map["ville_regroupee"].apply(
        lambda x: "red" if x == ville1 else "blue" if x == ville2 else "#888")

    fig = px.scatter_mapbox(
        df_map, lat="lat", lon="lon", size="Valeur sélectionnée", color="color",
        hover_name="ville_regroupee",
        hover_data={"Valeur": True, "lat": False, "lon": False, "color": False},
        size_max=40, zoom=4.5, height=600
    )
    fig.update_layout(mapbox_style="open-street-map", showlegend=False,
                      margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

# === PAGE : MÉTÉO ===
elif page == "🌤️ Météo":
    st.title("🌤️ Météo & prévisions")

    API_KEY = "f146d243be7e411789390746251004"
    BASE_URL = "http://api.weatherapi.com/v1"

    def get_current_weather(ville):
        url = f"{BASE_URL}/current.json?key={API_KEY}&q={ville}&lang=fr"
        try:
            r = requests.get(url)
            d = r.json()
            if "current" not in d:
                return {"error": "Données indisponibles"}
            return {
                "temp": d["current"]["temp_c"],
                "condition": d["current"]["condition"]["text"],
                "humidity": d["current"]["humidity"],
                "wind_kph": d["current"]["wind_kph"],
                "icon": d["current"]["condition"]["icon"]
            }
        except:
            return {"error": "Erreur API"}

    def get_forecast(ville, days):
        url = f"{BASE_URL}/forecast.json?key={API_KEY}&q={ville}&days={days}&lang=fr"
        try:
            r = requests.get(url)
            d = r.json()
            return d.get("forecast", {}).get("forecastday", [])
        except:
            return []

    col_m1, col_m2 = st.columns(2)
    for col, ville, meteo in zip([col_m1, col_m2], [ville1, ville2],
                                  [get_current_weather(ville1), get_current_weather(ville2)]):
        with col:
            st.markdown(f"### {ville}")
            if "error" in meteo:
                st.error(meteo["error"])
            else:
                st.image("http:" + meteo["icon"], width=60)
                st.write(meteo["condition"])
                st.write(f"Température : {meteo['temp']}°C")
                st.write(f"Humidité : {meteo['humidity']}%")
                st.write(f"Vent : {meteo['wind_kph']} km/h")

    nb_jours = st.slider("Choisissez le nombre de jours de prévisions", min_value=1, max_value=3, value=2)

    st.subheader("📅 Prévisions météo")
    col_f1, col_f2 = st.columns(2)
    for col, ville, prev in zip([col_f1, col_f2], [ville1, ville2],
                                 [get_forecast(ville1, nb_jours), get_forecast(ville2, nb_jours)]):
        with col:
            st.markdown(f"#### {ville}")
            if not prev:
                st.write("❌ Données non disponibles")
            else:
                for day in prev:
                    st.image("http:" + day["day"]["condition"]["icon"], width=40)
                    st.write(f"**{day['date']}** – {day['day']['condition']['text']}")
                    st.write(f"Min : {day['day']['mintemp_c']}°C | Max : {day['day']['maxtemp_c']}°C")

# === PAGE : SPORT ===
elif page == "🏃 Offre sportive":
    st.title("🏃 Analyse de l'offre sportive")

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

    emojis_categorie = {
        "Sports collectifs": "⚽",
        "Raquettes": "🎾",
        "Urbains / libres": "🛹",
        "Piscines / natation": "🏊‍♂️",
        "Gymnases / multisports": "🏟️"
    }

    df_sport = pd.read_csv("data-es.csv", sep=None, engine="python")
    df_sport.rename(columns={"Commune INSEE": "codgeo"}, inplace=True)
    df_sport["codgeo"] = df_sport["codgeo"].astype(str)
    df_sport["ville_regroupee"] = df_sport["Commune Nom"].apply(regrouper_arrondissements)

    categorie_choisie = st.selectbox("Choisissez une catégorie à comparer", list(categories_sport.keys()))
    emoji = emojis_categorie.get(categorie_choisie, "🏅")
    activites = categories_sport[categorie_choisie]
    df_filtres = df_sport[df_sport["Type d'équipement sportif"].isin(activites)]

    sport_ville1 = df_filtres[df_filtres["ville_regroupee"] == ville1]
    sport_ville2 = df_filtres[df_filtres["ville_regroupee"] == ville2]

    top1 = sport_ville1["Type d'équipement sportif"].value_counts().head(5)
    top2 = sport_ville2["Type d'équipement sportif"].value_counts().head(5)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f"### {emoji} {ville1}")
        if top1.empty:
            st.write("Aucun équipement trouvé.")
        else:
            for i, (e, n) in enumerate(top1.items(), 1):
                st.write(f"{i}. **{e}** – {n} équipements")

    with col_s2:
        st.markdown(f"### {emoji} {ville2}")
        if top2.empty:
            st.write("Aucun équipement trouvé.")
        else:
            for i, (e, n) in enumerate(top2.items(), 1):
                st.write(f"{i}. **{e}** – {n} équipements")

# === PAGE : CULTURE ===
elif page == "🎨 Données culturelles":
    st.title("🎨 Analyse de l'offre culturelle")

    categories_culture = {
        "nb_musées": "Musées",
        "nb_bibliothèques": "Bibliothèques",
        "nb_cinémas": "Cinémas",
        "nb_salles_de_spectacles": "Salles de spectacles",
        "nb_patrimoine___monuments": "Patrimoine / Monuments"
    }

    st.subheader(f"🏛️ {ville1} vs {ville2} - Équipements culturels")

    total1 = int(data1["nb_equipements_culturels"])
    total2 = int(data2["nb_equipements_culturels"])

    st.markdown(f"### 🎯 Nombre total d'équipements culturels")
    st.write(f"**{ville1}** : {total1} équipements")
    st.write(f"**{ville2}** : {total2} équipements")

    labels = list(categories_culture.values())
    values1 = [int(data1[col]) for col in categories_culture.keys()]
    values2 = [int(data2[col]) for col in categories_culture.keys()]
    txt1 = [str(v) for v in values1]
    txt2 = [str(v) for v in values2]

    fig = go.Figure(data=[
        go.Bar(name=ville1, x=labels, y=values1, text=txt1, textposition='auto', marker_color='royalblue'),
        go.Bar(name=ville2, x=labels, y=values2, text=txt2, textposition='auto', marker_color='tomato')
    ])
    fig.update_layout(barmode='group', template='plotly_white')
    st.plotly_chart(fig)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 🖼️ Détail pour {ville1}")
        for key, label in categories_culture.items():
            st.write(f"{label} : {int(data1[key])} équipements")

    with col2:
        st.markdown(f"### 🖼️ Détail pour {ville2}")
        for key, label in categories_culture.items():
            st.write(f"{label} : {int(data2[key])} équipements")

# === PAGE : À PROPOS ===
elif page == "ℹ️ À propos":
    st.title("ℹ️ À propos de City Fighting")
    st.markdown("""
    Cette application a été développée dans le cadre du projet **SAE Outils Décisionnels**.  
    Elle permet de comparer les grandes villes françaises selon :
    - Données générales (population, emploi, logement)
    - Indicateurs météo
    - Présence d’équipements sportifs
    - Présence d’infrastructures culturelles
    - Carte interactive

    **Sources de données** :
    - INSEE (population, emploi, logement)
    - Data Gouv (lecture des coordonnées, donnée culturelle)
    - Data ES (équipements sportifs)
    - WeatherAPI (météo)

    **Développé par :**  
    - [Mehdi Boussedra](https://www.linkedin.com/in/mehdi-boussedra-203127258/)  
    - [Clément Tang](https://www.linkedin.com/in/clementtang-in/)

    BUT3 SD VCOD groupe 33
    """)
