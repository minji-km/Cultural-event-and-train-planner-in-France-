import streamlit as st
import pandas as pd

st.title("Planificateur d'évènements culturels")

grd_villes = ['Avignon', 'Bordeaux', 'Lille', 'Lyon', 'Marseille',
              'Montpellier', 'Nantes', 'Nice', 'Toulouse']

@st.cache_data
def load_data():
    df = pd.read_csv("concerts.csv")
    return df

df = load_data()
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)

st.map(df[df['result_city']=='Paris'])

tabs = st.tabs(grd_villes)

with tabs[0]:
    st.map(df[df['result_city']=='Avignon'])

with tabs[1]:
    st.map(df[df['result_city']=='Bordeaux'])

with tabs[2]:
    st.map(df[df['result_city']=='Lille'])

with tabs[3]:
    st.map(df[df['result_city']=='Lyon'])
    
with tabs[4]:
    st.map(df[df['result_city']=='Marseille'])

with tabs[5]:
    st.map(df[df['result_city']=='Montpellier'])

with tabs[6]:
    st.map(df[df['result_city']=='Nantes'])

with tabs[7]:
    st.map(df[df['result_city']=='Nice'])

with tabs[8]:
    st.map(df[df['result_city']=='Toulouse'])

# i = 0
# for ville in grd_villes:
#     with tabs[i]:
#         st.map(df[df['result_city']==ville])
#     i+=1

