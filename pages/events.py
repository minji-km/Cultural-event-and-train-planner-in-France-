import streamlit as st
from Home import load_data
import datetime
import folium
from streamlit_folium import st_folium

grd_villes = ['Paris', 'Avignon', 'Bordeaux', 'Lille', 'Lyon', 'Marseille',
              'Montpellier', 'Nantes', 'Nice', 'Toulouse']

depart = st.selectbox('Départ', grd_villes, index=grd_villes.index('Paris'))
arrivee = st.selectbox('Arrivée', grd_villes + ['Toutes'])
date_depart = st.date_input('Date de départ', min_value=datetime.date.today())

df = load_data()

for ville in grd_villes:
    tab = st.beta_expander(ville)
    
    with tab:
        # Filtrez le DataFrame en fonction de la ville
        tab_df = df[df['result_city'] == ville]

        # Calculez la latitude et la longitude moyennes
        latitude_moyenne = tab_df['latitude'].mean()
        longitude_moyenne = tab_df['longitude'].mean()

        # Créez la carte
        carte = folium.Map(location=[latitude_moyenne, longitude_moyenne], zoom_start=7)

        # Ajoutez des marqueurs à la carte
        for idx, row in tab_df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=row['titre'],
                icon=folium.Icon(icon="cloud"),
            ).add_to(carte)

        # Affichez la carte
        st_folium(carte, width=1000)
