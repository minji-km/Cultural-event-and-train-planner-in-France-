import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium

st.title("Planificateur d'évènements culturels")

# grd_villes = ['Avignon', 'Bordeaux', 'Lille', 'Lyon', 'Marseille',
#               'Montpellier', 'Nantes', 'Nice', 'Toulouse']

@st.cache_data
def load_data():
    df = pd.read_csv("concerts.csv")
    return df

df = load_data()

paris_data = df[df['result_city']=='Paris']

latitude_moyenne = paris_data['latitude'].mean()
longitude_moyenne = paris_data['longitude'].mean()
carte = folium.Map(location=[latitude_moyenne, longitude_moyenne], zoom_start=12)

for idx, row in df.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=row['titre'],
        icon=folium.Icon(icon="cloud"),
    ).add_to(carte)

st_data = st_folium(carte, width=1000)


# i = 0
# for ville in grd_villes:
#     with tabs[i]:
#         st.map(df[df['result_city']==ville])
#     i+=1

