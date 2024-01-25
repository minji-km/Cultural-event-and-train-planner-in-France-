import streamlit as st
import pandas as pd

st.title("Planificateur d'évènements culturels")

@st.cache
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


tabs = st.tabs(coords.keys())

for i in len(coords):
    st.write(i)


# ville = st.selectbox('Choisissez une ville', list(coords.keys()))
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)
# st.map(df['latitude', 'longitude'])
