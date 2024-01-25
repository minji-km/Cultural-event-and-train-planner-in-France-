import streamlit as st
from cultural_events import load_data
import datetime
import folium
from streamlit_folium import st_folium

grd_villes = ['Paris', 'Avignon', 'Bordeaux', 'Lille', 'Lyon', 'Marseille',
              'Montpellier', 'Nantes', 'Nice', 'Toulouse']

depart = st.selectbox('Départ', grd_villes, index=grd_villes.index('Paris'))
arrivee = st.selectbox('Arrivée', grd_villes + ['Toutes'])
date_depart = st.date_input('Date de départ', min_value=datetime.date.today(), max_value=datetime.date(2024, 12, 31))

# df = load_data()
