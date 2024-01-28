import streamlit as st
import pandas as pd

import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

import base64

from datetime import datetime

import trainline
import io

# Function to set the background
def set_bg_hack(main_bg):
    # Set the page background to the image file
    main_bg_ext = "png"
    
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("data:image/{main_bg_ext};base64,{main_bg}");
             background-size: cover;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Load your background image
def load_bg_img(path: str):
    with open(path, "rb") as file:
        bg_image = file.read()
    return base64.b64encode(bg_image).decode("utf-8")

# Ajouter du CSS personnalisé via st.markdown
st.markdown("""
<style>
.streamlit-expanderHeader {
    background-color: white;
}
.streamlit-expanderContent {
    background-color: white;
}
</style>
""", unsafe_allow_html=True)

def convert_price(price_str):
    # Convertir la chaîne de prix en nombre
    # Enlever le symbole € et remplacer la virgule par un point
    return float(price_str.replace('€', '').replace(',', '.'))

# Trier le DataFrame en fonction des options choisies par l'utilisateur
def sort_dataframe(df, sort_by):
     # Vérifier et marquer les lignes avec des réductions
    df['has_reduction'] = ~df['reduction'].isna()  # True si 'reduction' n'est pas NaN

    if sort_by == 'Du Moins Cher au Plus Cher':
        df['prix_num'] = df['prix'].apply(convert_price)
        return df.sort_values('prix_num', ascending=True)
    elif sort_by == 'Du Plus Cher au Moins Cher':
        df['prix_num'] = df['prix'].apply(convert_price)
        return df.sort_values('prix_num', ascending=False)
    elif sort_by == 'Futurs Spectacles':
        return df.sort_values('start_date', ascending=False)
    elif sort_by == 'Bientôt sur Scène':
        return df.sort_values('start_date', ascending=True)
    elif sort_by == 'Réduction':
        # Trier d'abord par réduction puis par date ou prix
        return df.sort_values('has_reduction', ascending=False)
    else:
        return df

# Call the function to set the background
main_bg = load_bg_img("background.png")  # Replace this with your image's path
set_bg_hack(main_bg)

# Function to load CSV data with customizable parameters for delimiter and encoding
def load_csv_data(file_path, delimiter=',', encoding=None):
    try:
        return pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
    except Exception as e:
        print(f"Erreur lors du chargement du fichier {file_path}: {e}")
        return None

# Load data with specific parameters for each file
df_concerts = load_csv_data('concerts.csv')
# Convertir les colonnes de dates en datetime si ce n'est pas déjà le cas
df_concerts['end_date'] = pd.to_datetime(df_concerts['end_date'])
# Obtenir la date d'aujourd'hui
today = datetime.today()
# Filtrer les événements pour ne garder que ceux dont la date de fin est ultérieure à aujourd'hui
df_concerts = df_concerts[df_concerts['end_date'] >= today]

df_empreinte = load_csv_data('Empreinte_carbone_trajet_train.csv', delimiter=';', encoding='ISO-8859-1')
df_lieu_concert = load_csv_data('lieu_concert.geocoded.csv')
# Liste des villes à conserver
cities_to_keep = ['Avignon', 'Nice', 'Marseille', 'Paris', 'Lyon', 'Montpellier', 'Toulouse', 'Bordeaux', 'Nantes', 'Lille']
# Filtrer le DataFrame des lieux pour ne garder que les villes spécifiées
df_lieu_concert = df_lieu_concert[df_lieu_concert['result_city'].isin(cities_to_keep)]

def create_map(df):
    # Initialiser la carte avec un emplacement central
    m = folium.Map(location=[46.2276, 2.2137], zoom_start=6)  # Centre de la France

    # Utiliser MarkerCluster pour gérer plusieurs marqueurs
    marker_cluster = MarkerCluster().add_to(m)

    # Ajouter des marqueurs pour chaque événement
    for idx, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['titre'],
            icon=folium.Icon(color='red',icon='location-dot',prefix='fa')
                # ou toute autre information
        ).add_to(marker_cluster)
    
    return m

# Fonction pour nettoyer le DataFrame et préparer les données pour le tri
def clean_and_prepare_data(df):
    # Supprimer les colonnes non nécessaires
    df = df.drop(['currency', 'transportation_mean','bicycle_reservation'], axis=1)
    
    # Convertir le prix en format numérique
    df['price'] = df['price'].str.replace(',', '.').astype(float)
    
    # Convertir la durée en minutes totales pour faciliter le tri
    df['duration_in_minutes'] = df['duration'].apply(lambda x: int(x.split('h')[0])*60 + int(x.split('h')[1].replace('m', '')))
    
    return df

def main():
    # Titre et sous-titre
    st.title("Planifier son Voyage Culturel")
    st.subheader("Train & Culture sur Mesure: Organiser son Voyage Culturel dans les Grandes Villes Françaises selon son Budget")

    # Calculer le nombre d'événements et de villes
    total_events = len(df_concerts)
    unique_cities = df_concerts['result_city'].nunique()

    # Affichage des statistiques
    st.subheader(f"Sélection de {total_events} expériences uniques dans {unique_cities} destinations emblématiques")

    # Création de la carte
    m = create_map(df_concerts)

    # Affichage de la carte
    st.header("Votre Carte Interactive des Événements Culturels 🗺️")
    folium_static(m)

    # Sidebar for city filter
    st.sidebar.header('Choisissez votre destination culturelle')
    city_list = df_lieu_concert['result_city'].unique().tolist()
    selected_city = st.sidebar.selectbox('Sélectionnez votre destination', city_list)

    # Filter the dataframe based on the selected city
    df_city_concerts = df_concerts[df_concerts['result_city'] == selected_city]

    if not df_city_concerts.empty:
        # Create a map centered on the selected city
        city_location = df_lieu_concert[df_lieu_concert['result_city'] == selected_city].iloc[0]
        m = folium.Map(location=[city_location['latitude'], city_location['longitude']], zoom_start=12)

        # Add markers for each event in the city
        for idx, row in df_city_concerts.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=row['titre'],
                icon=folium.Icon(color='red',icon='location-dot',prefix='fa')  # or other relevant information
            ).add_to(m)

        # Display the map
        st.header(f"Zoom sur {selected_city}")
        folium_static(m)
        with st.expander("⏬ Voir détails"):
            # Ajout des options de tri
            sort_option = st.selectbox(
            'Trier par:',   
                ('Du Moins Cher au Plus Cher', 'Du Plus Cher au Moins Cher', 'Futurs Spectacles', 'Bientôt sur Scène', 'Réduction')
                )   

            # Trier le DataFrame
            df_sorted = sort_dataframe(df_city_concerts, sort_option)
            df_sorted_renamed = df_sorted.rename(
                columns={
                'titre': "Nom de l'Événement",
                'description': 'Description',
                'start_date': 'Date de Début',
                'end_date': 'Date de Fin',
                'prix': 'Prix',
                'reduction': 'Réduction'
                    }
                    )
            # Convertir le DataFrame renommé en HTML et l'écrire dans Streamlit
            st.write(df_sorted_renamed[["Nom de l'Événement", 'Description','lieu', 'Date de Début', 'Date de Fin', 'Prix', 'Réduction']].to_html(index=False), unsafe_allow_html=True)
        
        
        # Sélection de l'événement
        event_titles = df_city_concerts['titre'].tolist()
        selected_event_title = st.sidebar.selectbox('Quelle expérience vous inspire ? 🎭', event_titles)
    
        # Trouver l'événement sélectionné dans le DataFrame
        selected_event = df_city_concerts[df_city_concerts['titre'] == selected_event_title].iloc[0]

        # Liste des villes de départ, en excluant la ville filtrée
        departure_cities = [city for city in cities_to_keep if city != selected_city]

        # Filtre pour la ville de départ
        selected_departure_city = st.sidebar.selectbox('Votre point de départ ', departure_cities)
        if isinstance(selected_event['start_date'], datetime):
            default_date = selected_event['start_date']
        else:
            # Sinon, tenter de convertir la chaîne en datetime
            try:
                default_date = pd.to_datetime(selected_event['start_date'])
            except ValueError as e:
                st.error(f"Erreur de format de date: {e}")
                # Utiliser une date par défaut ou sortir de la fonction
                default_date = datetime.today()

        # Utiliser la date de début de l'événement sélectionné comme date par défaut
        #default_date = selected_event['start_date'].strftime('%d/%m/%Y')

        # Filtres pour les dates et heures de départ et d'arrivée
        from_date = st.sidebar.date_input('Date de départ', value=default_date)
        from_time = st.sidebar.time_input('Heure de départ', value=pd.to_datetime('08:00').time())
        to_date = st.sidebar.date_input('Date de retour', value=default_date)
        to_time = st.sidebar.time_input('Heure de retour', value=pd.to_datetime('16:00').time())

        # Initialiser les résultats de recherche dans le state de la session si ce n'est pas déjà fait
        if 'df_trains' not in st.session_state:
            st.session_state['df_trains'] = pd.DataFrame()

        # Bouton pour lancer la recherche
        if st.sidebar.button('Trouvez vos Billets de Train🎫🚆'):
            # Utiliser les valeurs sélectionnées pour la recherche
            departure = f"{from_date.strftime('%d/%m/%Y')} {from_time.strftime('%H:%M')}"
            arrival = f"{to_date.strftime('%d/%m/%Y')} {to_time.strftime('%H:%M')}"

            # Ici, remplacez par votre appel réel à l'API Trainline
            results = trainline.search(
                departure_station=selected_departure_city,
                arrival_station=selected_event['result_city'],
                from_date=departure,
                to_date=arrival
            )
            results_csv = results.csv()
            st.session_state['df_trains'] = clean_and_prepare_data(pd.read_csv(io.StringIO(results_csv), delimiter=';'))

        if 'df_trains' in st.session_state and not st.session_state['df_trains'].empty:
            # Travailler avec une copie pour éviter les modifications en place
            df_trains = st.session_state['df_trains'].copy()

            # Renommer les colonnes
            df_trains = df_trains.rename(columns={
                'departure_date': 'Date de départ',
                'arrival_date': 'Date d\'arrivée',
                'duration': 'Durée',
                'price': 'Prix'
            })
            if not df_trains['Prix'].astype(str).str.contains('€').any():
                # Formater la colonne des prix pour ajouter le symbole de l'euro
                df_trains['Prix'] = df_trains['Prix'].apply(lambda x: f"{x} €")

            # Vérifier si les colonnes existent avant de les supprimer
            cols_to_drop = ['duration_in_minutes', 'number_of_segments']
            cols_to_drop = [col for col in cols_to_drop if col in df_trains.columns]
            df_trains.drop(cols_to_drop, axis=1, inplace=True)

            # Mettre à jour le DataFrame dans l'état de session
            st.session_state['df_trains'] = df_trains

            st.header("Résultats de la Recherche des Billets de Train")
            # Créer deux clés de recherche pour les deux sens possibles du trajet
            search_key1 = f"{selected_departure_city} - {selected_city}"
            search_key2 = f"{selected_city} - {selected_departure_city}"

            # Rechercher l'empreinte carbone pour le trajet spécifique dans les deux sens
            empreinte_specifique = df_empreinte[
                (df_empreinte['Trajet'].str.contains(search_key1, case=False, na=False)) |
                (df_empreinte['Trajet'].str.contains(search_key2, case=False, na=False))
            ]
            if not empreinte_specifique.empty:
                # Extraction de la valeur moyenne des émissions de CO2
                co2_emission = empreinte_specifique['CO2 emis en kg'].iloc[0]  # Supposons qu'il y a une seule ligne correspondante
                st.markdown(
                    f"<p style='color: #609060; font-size: 16px;'>"
                    f"Pour un voyage de <span style='font-weight:bold; font-size: 20px;'>{selected_departure_city}</span> "
                    f"à <span style='font-weight:bold; font-size: 20px;'>{selected_city}</span>, "
                    f"l'empreinte carbone moyenne est de <span style='font-weight:bold; font-size: 22px;'>{co2_emission} kg</span> "
                    f"de CO2."
                    f"</p>", 
                    unsafe_allow_html=True
                )

             # Informer l'utilisateur qu'il peut filtrer directement dans le tableau
            st.info("Astuce : Utilisez les en-têtes de colonnes pour filtrer et trier les résultats selon vos préférences.")
            # Afficher le DataFrame trié ou le DataFrame par défaut
            st.dataframe(st.session_state['df_trains'], width=1000)
        else:
            st.header("Résultats de la Recherche des Billets de Train")
            # Ici, vous pouvez choisir de ne rien faire ou d'afficher un message indiquant que le tableau est vide
            st.write("Aucun résultat à afficher. Veuillez lancer une recherche.")
    else:
        st.error(f"Aucun événement trouvé pour la ville sélectionnée : {selected_city}")

if __name__ == "__main__":
    main()

