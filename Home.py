import streamlit as st
import pandas as pd
import trainline
import folium
import datetime
from streamlit_folium import st_folium

st.title("Planificateur d'évènements culturels")
grd_villes = ['Paris', 'Avignon', 'Bordeaux', 'Lille', 'Lyon', 'Marseille',
              'Montpellier', 'Nantes', 'Nice', 'Toulouse']

depart = st.selectbox('Départ', grd_villes, index=grd_villes.index('Paris'))
arrivee = st.selectbox('Arrivée', grd_villes + ['Toutes'])
date_depart = st.date_input('Date de départ', min_value=datetime.date.today())


@st.cache_data
def load_data():
    df = pd.read_csv("concerts.csv")
    return df

df = load_data()

latitude_moyenne = df['latitude'].mean()
longitude_moyenne = df['longitude'].mean()
carte = folium.Map(location=[latitude_moyenne, longitude_moyenne], zoom_start=7)

for idx, row in df.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=row['titre'],
        icon=folium.Icon(icon="cloud"),
    ).add_to(carte)

st_data = st_folium(carte, width=1000)
