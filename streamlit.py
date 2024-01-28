import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import base64
from datetime import datetime
import trainline
import io

# I) : Background Setup
# --------------------------

# Function to apply a background image to the Streamlit app
def set_bg_hack(main_bg):
    """Set the page background to the specified image file."""
    main_bg_ext = "png"
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("data:image/{main_bg_ext};base64,{main_bg}");
             background-size: cover;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Function to load a background image from a given path
def load_bg_img(path: str):
    """Read an image file and encode it for Streamlit background."""
    with open(path, "rb") as file:
        bg_image = file.read()
    return base64.b64encode(bg_image).decode("utf-8")

# Adding custom CSS using Streamlit's markdown
st.markdown("""
<style>
.streamlit-expanderHeader {
    background-color: white;
}
.streamlit-expanderContent {
    background-color: white;
}
</style>
""", unsafe_allow_html=True)



# II) : Data Preparation and Manipulation
# ------------------------------------------

# Function to convert price string to float
def convert_price(price_str):
    """Convert price string to float by removing currency symbol and replacing comma."""
    return float(price_str.replace('€', '').replace(',', '.'))

# Function to sort DataFrame based on user's choice
def sort_dataframe(df, sort_by):
    """Sort the DataFrame based on the criteria chosen by the user."""
    df['has_reduction'] = ~df['reduction'].isna()  # True if 'reduction' is not NaN

    # Sorting logic based on user selection
    df['prix_num'] = df['prix'].apply(convert_price)
    if sort_by == 'Du Moins Cher au Plus Cher':
        return df.sort_values('prix_num', ascending=True)
    elif sort_by == 'Du Plus Cher au Moins Cher':
        return df.sort_values('prix_num', ascending=False)
    elif sort_by == 'Futurs Spectacles':
        return df.sort_values('start_date', ascending=False)
    elif sort_by == 'Bientôt sur Scène':
        return df.sort_values('start_date', ascending=True)
    elif sort_by == 'Réduction':
        return df.sort_values('has_reduction', ascending=False)
    else:
        return df

# Applying the background
main_bg = load_bg_img("background.png")  # Replace with your image path
set_bg_hack(main_bg)

# Function to load CSV data with customizable parameters
def load_csv_data(file_path, delimiter=',', encoding=None):
    """Load CSV data with specified delimiter and encoding."""
    try:
        return pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

# Loading and preparing data
df_concerts = load_csv_data('concerts.csv')
df_concerts['end_date'] = pd.to_datetime(df_concerts['end_date'])
today = datetime.today()
df_concerts = df_concerts[df_concerts['end_date'] >= today]

df_empreinte = load_csv_data('Empreinte_carbone_trajet_train.csv', delimiter=';', encoding='ISO-8859-1')
df_lieu_concert = load_csv_data('lieu_concert.geocoded.csv')
cities_to_keep = ['Avignon', 'Nice', 'Marseille', 'Paris', 'Lyon', 'Montpellier', 'Toulouse', 'Bordeaux', 'Nantes', 'Lille']
df_lieu_concert = df_lieu_concert[df_lieu_concert['result_city'].isin(cities_to_keep)]


# In this section, the code focuses on preparing and manipulating data for use in the app. 
# It includes a function `convert_price` to convert price strings into a float format, 
# and `sort_dataframe` to sort data based on user-selected criteria. The section also handles 
# the loading of different CSV files like concert data and environmental data. 
# It ensures that data is in the correct format, such as converting date strings to datetime objects, 
# and filters data based on certain criteria like upcoming events.




# III) : Map Creation
# ---------------------

# Function to create a map with event markers
def create_map(df):
    """Create a Folium map with event markers."""
    m = folium.Map(location=[46.2276, 2.2137], zoom_start=6)  # Center of France
    marker_cluster = MarkerCluster().add_to(m)

    # Adding markers for each event
    for idx, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['titre'],
            icon=folium.Icon(color='red',icon='location-dot',prefix='fa')
        ).add_to(marker_cluster)
    return m

# Function to clean and prepare data for sorting
def clean_and_prepare_data(df):
    """Clean DataFrame and prepare data for sorting."""
    df = df.drop(['currency', 'transportation_mean','bicycle_reservation'], axis=1)
    df['price'] = df['price'].str.replace(',', '.').astype(float)
    df['duration_in_minutes'] = df['duration'].apply(lambda x: int(x.split('h')[0])*60 + int(x.split('h')[1].replace('m', '')))
    return df


# The purpose of this section is to create interactive maps using Folium. 
# The `create_map` function initializes a map centered on France and adds markers for each event. 
# These markers are grouped using `MarkerCluster` to manage multiple markers effectively. 
# This section enhances the user's experience by providing a visual and interactive way to explore events.




# IV) : Main Application Logic
# -------------------------------

def main():
    """Main function to run the Streamlit app."""
    # Streamlit UI components and logic here

if __name__ == "__main__":
    main()


# The main function encapsulates the core logic of the Streamlit application. 
# It orchestrates the user interface, handles user interactions, and integrates all the other sections. 
# This function is where the app's title, filters, data displays, and interactive components are defined 
# and where the overall user experience is shaped. It's the central hub that ties together all the app's functionality.
