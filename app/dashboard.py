import streamlit as st
import pandas as pd
import mysql.connector
import json
from dotenv import load_dotenv
import os

load_dotenv()


# Function to connect to the MySQL database
def get_database_connection():
    db_connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return db_connection

# Function to fetch statistics from the database
def get_stats():
    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM store_data")
    total_food_items = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT id) FROM location_data")
    total_restaurants = cursor.fetchone()[0]

    verified_food_items = total_restaurants + total_food_items

    third_party_food_items = 0

    cursor.close()
    conn.close()

    return total_food_items, total_restaurants, verified_food_items, third_party_food_items

# Function to add a new food item to the database
def add_food_item(name, location, nutrients, ingredients, serving_data):
    conn = get_database_connection()
    cursor = conn.cursor()

    # Your SQL query to insert the new food item
    # Modify this according to your table schema
    sql_query = "INSERT INTO location_data (id, name, location, nutrients, ingredients, serving_size) " \
                "VALUES (null, %s, %s, %s, %s, %s)"
    
    cursor.execute(sql_query, (name, location, json.dumps(nutrients), ingredients, json.dumps(serving_data)))

    conn.commit()
    cursor.close()
    conn.close()

def get_restaurant_locations():
    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT location FROM location_data")
    locations = [location[0] for location in cursor.fetchall()]

    cursor.close()
    conn.close()

    return locations

def main():
    st.title('Food Item Dashboard')

    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    total_food_items, total_restaurants, verified_food_items, third_party_food_items = get_stats()
    col1.metric('Total Food Items:', total_food_items, delta=None, delta_color="normal", help=None, label_visibility="visible")
    col2.metric('Total Restaurants:', total_restaurants, delta=None, delta_color="normal", help=None, label_visibility="visible")
    col3.metric('Verified Food Items:', verified_food_items, delta=None, delta_color="normal", help=None, label_visibility="visible")
    col4.metric('3rd Party Food Items:', third_party_food_items, delta=None, delta_color="normal", help=None, label_visibility="visible")

    # Form to add a new food item
    st.header('Add Food Item')
    name = st.text_input('Name')

    # Autocomplete text input for the "Location" field
    restaurant_locations = get_restaurant_locations()
    location_option = st.selectbox('Location', restaurant_locations + ['Other'], index=0)

    # If "Other" is selected, display a text input to enter a custom location
    if location_option == 'Other':
        location = st.text_input('Custom Location')
    else:
        location = location_option

    # Nutrients input
    st.subheader('Nutrients')
    nutrient_forms = st.session_state.setdefault('nutrient_forms', [])

    for idx, nutrient_form in enumerate(nutrient_forms):
        nutrient_name = st.text_input(f'Nutrient Name ({idx})', value=nutrient_form.get('name', ''))
        per_100g = st.text_input(f'Per 100g ({idx})', value=nutrient_form.get('per100g', ''))
        per_serving = st.text_input(f'Per Serving ({idx})', value=nutrient_form.get('perServing', ''))
        nutrient_forms[idx] = {"name": nutrient_name, "per100g": per_100g, "perServing": per_serving}

    if st.button('Add Nutrient'):
        nutrient_forms.append({"name": "", "per100g": "", "perServing": ""})
        # Rerun the app to refresh the nutrient forms section immediately
        st.experimental_rerun()

    # Display the nutrients list in a table format
    if nutrient_forms:
        nutrient_df = pd.DataFrame(nutrient_forms)
        st.write("Nutrients Summary:")
        st.table(nutrient_df)

    ingredients = st.text_area('Ingredients', 'Enter ingredients here')

    serving_name = st.text_input('Serving Name')
    serving_amount = st.number_input('Serving Amount', min_value=0, step=1)
    #per_100g_amount = st.number_input('Per X Grams Amount', min_value=0, step=1)
    serving_data = [{"name":serving_name,"serving":serving_amount,"type":"serving"}] # {"name":"grams","serving":per_100g_amount,"type":"per100g"}

    if st.button('Submit'):
        add_food_item(name, location, nutrient_forms, ingredients, serving_data)
        st.success('Food item added successfully!')

if __name__ == '__main__':
    main()
