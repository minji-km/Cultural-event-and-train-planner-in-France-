import streamlit as st
import pandas as pd

st.title("Planificateur d'évènements culturels")

grd_villes = ['Paris', 'Avignon', 'Bordeaux', 'Lille', 'Lyon', 'Marseille',
              'Montpellier', 'Nantes', 'Nice', 'Toulouse']

@st.cache_data
def load_data():
    df = pd.read_csv("concerts.csv")
    return df

df = load_data()
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)

tabs = st.tabs(grd_villes)

with tabs[0]:
    st.map(df[df['result_city']=='Paris'])

with tabs[1]:
    st.map(df[df['result_city']=='Avignon'])

with tabs[2]:
    st.map(df[df['result_city']=='Bordeaux'])



# i = 0
# for ville in grd_villes:
#     with tabs[i]:
#         st.map(df[df['result_city']==ville])
#     i+=1

