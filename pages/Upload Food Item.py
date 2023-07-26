import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import mysql.connector
from dotenv import load_dotenv
import os
import json

load_dotenv()

def writeToDB(dfs_data, location):
    # Establish a connection to the database
    print("WRITING TO DB")
    cnx = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = cnx.cursor()

    sql_query = "INSERT INTO location_data (id, name, location, nutrients, ingredients, serving_size) " \
                "VALUES (null, %s, %s, %s, %s, %s)"
    
    for df_json in dfs_data:
        table_data = json.loads(df_json)
        for row in table_data:
            name = row.get('Name', '')
            energy = row.get('Energy (kcal)', '')
            protein = row.get('Protein (g)', '')
            carbs = row.get('Carbs (g)', '')
            fats = row.get('Fats (g)', '')
            nutrients = json.dumps({
                'Energy': energy,
                'Protein': protein,
                'Carbs': carbs,
                'Fats': fats
            })
            ingredients = ''
            serving_size = '[{"name": "Serving", "serving": 1, "type": "serving"}]'
            # Execute the query
            cursor.execute(sql_query, (name, location, nutrients, ingredients, serving_size))
            print("Inserted: "+ name)
    # Commit the transaction
    cnx.commit()
    
    # Close the cursor and connection
    cursor.close()
    cnx.close()


st.title('Food Item PDF Parser')
st.title('Make sure to reset before uploading a new PDF file')

uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
dfs = [] #dataframes
resetButton = st.button('Reset')
if resetButton:
    dfs = []
    st.session_state.clear()
    st.experimental_rerun()

if uploaded_file is not None:
    if 'pdf_tables' not in st.session_state:
        pdf = pdfplumber.open(BytesIO(uploaded_file.read()))
        tables = []
        for page in pdf.pages:
            tables += page.extract_tables()
        st.session_state['pdf_tables'] = tables  # save the tables in the session state

    tables = st.session_state['pdf_tables']  # retrieve the tables from the session state
    for i, table in enumerate(tables):
        column_names = [f'Column {j+1}' for j in range(len(table[0]))]
        df = pd.DataFrame(table, columns=column_names)
        st.header(f'Table {i+1}:')
        # Add a checkbox for each table
        include_table = st.checkbox(f'Include Table {i+1}', value=True)
        if include_table:

            # Allow renaming and removing columns
            columns_to_remove = []  # Store columns marked for removal
            for col in df.columns:
                options = ["Other", "Name","Energy (kcal)", "Protein (g)", "Carbs (g)", "Fats (g)"]
                new_name_option = st.selectbox(f'Rename "{col}" to', options=options, key=f'{i}_{col}_rename')

                if new_name_option == "Other":
                    new_name = st.text_input(f'Enter custom name for "{col}"', value=col, key=f'{i}_{col}_other_rename')
                else:
                    new_name = new_name_option

                remove_col = st.checkbox(f'Remove "{col}"', key=f'{i}_{col}_remove')
                if not remove_col:
                    # Update the column name in-place
                    df.rename(columns={col: new_name}, inplace=True)
                else:
                    columns_to_remove.append(col)  # Mark column for removal

            # Remove columns marked for removal
            df.drop(columns=columns_to_remove, inplace=True)

            # Filter rows for the "Energy (kcal)" column
            if "Energy (kcal)" in df.columns:
                df["Energy (kcal)"] = pd.to_numeric(df["Energy (kcal)"], errors='coerce')
                df = df.dropna(subset=["Energy (kcal)"])

            df["Include?"] = True
            # Reorder the columns to bring "Include?" to the front
            df = df[['Include?'] + [col for col in df.columns if col != 'Include?']]
            st.data_editor(
                df,
                column_config={
                    "Include?": st.column_config.CheckboxColumn(
                        "Include?",
                        help="Select rows to include",
                        default=True,
                    )
                },
                hide_index=True,
            )

            if i < len(dfs):
                # This is not the first time processing this DataFrame, so update it
                dfs[i] = df.to_json()
            else:
                # This is the first time processing this DataFrame, so append it
                dfs.append(df)

    locationName = st.text_input('Location Name')
    uploadButton = st.button('Submit')
    if uploadButton:
        json_dfs = [df.to_json(orient='records') for df in dfs]
        for i, json_df in enumerate(json_dfs):
            st.json(json_df)
        st.write(locationName + ' Data Added.')
        writeToDB(json_dfs, locationName)
            #st.session_state['pdf_tables'] = []
