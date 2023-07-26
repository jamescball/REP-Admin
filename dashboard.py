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


def main():
    st.title('Food Item Dashboard')

    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    total_food_items, total_restaurants, verified_food_items, third_party_food_items = get_stats()
    col1.metric('Total Food Items:', total_food_items, delta=None, delta_color="normal", help=None, label_visibility="visible")
    col2.metric('Total Restaurants:', total_restaurants, delta=None, delta_color="normal", help=None, label_visibility="visible")
    col3.metric('Verified Food Items:', verified_food_items, delta=None, delta_color="normal", help=None, label_visibility="visible")
    col4.metric('3rd Party Food Items:', third_party_food_items, delta=None, delta_color="normal", help=None, label_visibility="visible")

    
if __name__ == '__main__':
    main()
