import streamlit as st
import pandas as pd
import trainline
import folium
from streamlit_folium import st_folium

st.title("Planificateur d'évènements culturels")
df = pd.read_csv("concerts.csv")

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