import streamlit as st
import pandas as pd
import trainline
import folium
from streamlit_folium import st_folium
import ipywidgets as widgets
from IPython.display import display

st.title("Planificateur d'évènements culturels")

@st.cache_data
def load_data():
    df = pd.read_csv("concerts.csv")
    return df

df = load_data()

coords = {
    'Paris': [48.8566, 2.3522],
    'Avignon': [43.9493, 4.8055],
    'Bordeaux': [44.8378, -0.5792],
    'Lille': [50.6292, 3.0573],
    'Lyon': [45.75, 4.85],
    'Marseille': [43.2965, 5.3698],
    'Montpellier': [43.6108, 3.8767],
    'Nantes': [47.2186, -1.5536],
    'Nice': [43.7034, 7.2663],
    'Toulouse': [43.6043, 1.4437]
}

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
