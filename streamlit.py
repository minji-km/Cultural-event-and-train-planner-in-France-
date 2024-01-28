import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import base64
from datetime import datetime
import trainline
import io

# I) Configuration de l'Arrière-plan
# ----------------------------------

# Fonction pour appliquer une image d'arrière-plan à l'application Streamlit
def set_bg_hack(main_bg):
    """Set the page background to the specified image file."""
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

# Fonction pour charger une image d'arrière-plan à partir d'un chemin donné
def load_bg_img(path: str):
    """Read an image file and encode it for Streamlit background."""
    with open(path, "rb") as file:
        bg_image = file.read()
    return base64.b64encode(bg_image).decode("utf-8")

# Ajout de CSS personnalisé en utilisant le markdown de Streamlit
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



# II) Préparation et Manipulation des Données
# -------------------------------------------

# Fonction pour convertir une chaîne de caractères de prix en nombre flottant
def convert_price(price_str):
    """Convert price string to float by removing currency symbol and replacing comma."""
    return float(price_str.replace('€', '').replace(',', '.'))

# Fonction pour trier le DataFrame en fonction du choix de l'utilisateur
def sort_dataframe(df, sort_by):
    """Sort the DataFrame based on the criteria chosen by the user."""
    df['has_reduction'] = ~df['reduction'].isna() 

    df['prix_num'] = df['prix'].apply(convert_price)
    if sort_by == 'Du Moins Cher au Plus Cher':
        return df.sort_values('prix_num', ascending=True)
    elif sort_by == 'Du Plus Cher au Moins Cher':
        return df.sort_values('prix_num', ascending=False)
    elif sort_by == 'Futurs Spectacles':
        return df.sort_values('start_date', ascending=False)
    elif sort_by == 'Bientôt sur Scène':
        return df.sort_values('start_date', ascending=True)
    elif sort_by == 'Réduction':
        return df.sort_values('has_reduction', ascending=False)
    else:
        return df

# Application de l'arrière-plan
main_bg = load_bg_img("background.png")  
set_bg_hack(main_bg)

# Fonction pour charger des données CSV avec des paramètres personnalisables
def load_csv_data(file_path, delimiter=',', encoding=None):
    """Load CSV data with specified delimiter and encoding."""
    try:
        return pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

# Chargement et préparation des données
df_concerts = load_csv_data('concerts.csv')
df_concerts['end_date'] = pd.to_datetime(df_concerts['end_date'])
today = datetime.today()
df_concerts = df_concerts[df_concerts['end_date'] >= today]

df_empreinte = load_csv_data('Empreinte_carbone_trajet_train.csv', delimiter=';', encoding='ISO-8859-1')
df_lieu_concert = load_csv_data('lieu_concert.geocoded.csv')
cities_to_keep = ['Avignon', 'Nice', 'Marseille', 'Paris', 'Lyon', 'Montpellier', 'Toulouse', 'Bordeaux', 'Nantes', 'Lille']
df_lieu_concert = df_lieu_concert[df_lieu_concert['result_city'].isin(cities_to_keep)]


# Dans cette section, on se concentre sur la préparation et la manipulation des données pour leur utilisation dans l'application. 
# Elle inclut une fonction `convert_price` pour convertir les chaînes de prix en format flottant, 
# et `sort_dataframe` pour trier les données en fonction des critères sélectionnés par l'utilisateur. La section gère également 
# le chargement de différents fichiers CSV tels que les données de concerts et les données environnementales. 
# Elle assure que les données sont dans le format correct, comme la conversion des chaînes de dates en objets datetime, 
# et filtre les données en fonction de certains critères, comme les événements à venir.




# III) Création de la Carte
# -------------------------

# Fonction pour créer une carte avec des marqueurs d'événements
def create_map(df):
    """Create a Folium map with event markers."""
    m = folium.Map(location=[46.2276, 2.2137], zoom_start=6)  # Center of France
    marker_cluster = MarkerCluster().add_to(m)

    for idx, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['titre'],
            icon=folium.Icon(color='red',icon='location-dot',prefix='fa')
        ).add_to(marker_cluster)
    return m

# Fonction pour nettoyer et préparer les données en vue du tri
def clean_and_prepare_data(df):
    """Clean DataFrame and prepare data for sorting."""
    df = df.drop(['currency', 'transportation_mean','bicycle_reservation'], axis=1)
    df['price'] = df['price'].str.replace(',', '.').astype(float)
    df['duration_in_minutes'] = df['duration'].apply(lambda x: int(x.split('h')[0])*60 + int(x.split('h')[1].replace('m', '')))
    return df


# L'objectif de cette section est de créer des cartes interactives en utilisant Folium. 
# La fonction `create_map` initialise une carte centrée sur la France et ajoute des marqueurs pour chaque événement. 
# Ces marqueurs sont regroupés en utilisant `MarkerCluster` pour gérer efficacement plusieurs marqueurs. 
# Cette section améliore l'expérience utilisateur en fournissant un moyen visuel et interactif d'explorer les événements.




# IV) Logique Principale de l'Application
# ---------------------------------------

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


# La fonction principale encapsule la logique centrale de l'application Streamlit.
# Elle orchestre l'interface utilisateur, gère les interactions avec les utilisateurs et intègre toutes les autres sections.
# C'est dans cette fonction que le titre de l'application, les filtres, les affichages de données et les composants interactifs sont définis,
# et où l'expérience utilisateur globale est façonnée. C'est le centre névralgique qui relie toutes les fonctionnalités de l'application.
