import streamlit as st
import pandas as pd

st.title("Planificateur d'évènements culturels")

# grd_villes = ['Avignon', 'Bordeaux', 'Lille', 'Lyon', 'Marseille',
#               'Montpellier', 'Nantes', 'Nice', 'Toulouse']

@st.cache_data
def load_data():
    df = pd.read_csv("concerts.csv")
    return df

df = load_data()
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)

# st.map(df[df['result_city']=='Paris'])


# i = 0
# for ville in grd_villes:
#     with tabs[i]:
#         st.map(df[df['result_city']==ville])
#     i+=1

