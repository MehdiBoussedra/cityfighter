MODE D'EMPLOI - City Fighting

Prérequis :
Si vous utilisez Visual Studio Code :
    - Créez un environnement virtuel :
        python -m venv venv
    - Activez-le :
        - Sous Windows : venv\Scripts\activate
        - Sous Mac/Linux : source venv/bin/activate

- Installer les bibliothèques nécessaires : streamlit, pandas, plotly, openpyxl, requests, gdown, os

Commande: pip install -r requirements.txt

Structure du dossier :
- Base_data.py : traitement et nettoyage des données
- app.py : application Streamlit principale
- Tous les fichiers de données (.xlsx, .csv) nécessaires à l’exécution de l’application.
- Ce fichier mode_emploi.txt, requirements.txt et un rapport.pdf expliquant les choix techniques.

Fichiers de données nécessaires :
    - POPULATION_MUNICIPALE_COMMUNES_FRANCE.xlsx
    - base-cc-logement-2020.CSV
    - base-cc-emploi-pop-active-2020_v2.CSV
    - 20230823-communes-departement-region.csv
    - data-es.csv
    - base-des-lieux-et-des-equipements-culturels.csv

Étapes d'exécution :
1. Lancer Base_data.py pour générer les fichiers de données traitées :
   - Villes_regroupees_population_wiki_sport.xlsx
   - emploi_variables_utiles_grouped.xlsx
   - logement_variables_utiles_grouped.xlsx

2. Lancer l'application avec :
   streamlit run app.py

Navigation :
- Acceuil: Introduction de l'application
- Comparaison de villes : données population, emploi, logement
- Carte interactive : taille et localisation des villes
- Météo : température, humidité, prévisions à 3 jours
- Offre sportive : top équipements par catégorie avec emoji dynamique
- Données culturelles : nombres de musées, bibliothèques, cinémas, monuments...
- À propos : informations sur le projet

Lien Github :
https://github.com/MehdiBoussedra/cityfighter.git

Lien de l’application :
https://cityfighter.streamlit.app/ 


Fait par : Mehdi Boussedra et Clément Tang
BUT3 SD VCOD groupe 33
