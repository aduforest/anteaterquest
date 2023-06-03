import ast
import numpy as np
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import torch

# Initialize SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    embedding = model.encode(text)
    return embedding

DATA_URL = "courses_with_embeddings.csv"

@st.cache_data
def blending_wonders():
    df = pd.read_csv(DATA_URL, encoding='ISO-8859-1')

    # Convert the string representation of array to actual array
    df['embeddings'] = df['embedding'].apply(lambda x: np.fromstring(x, sep=' '))

    df['Min Units'], df['Max Units'] = zip(*df['Units'].apply(split_units))

    return df

def split_units(units_str):
    if isinstance(units_str, str):
        # Remove leading and trailing spaces
        units_str = units_str.strip()
        if '-' in units_str:
            min_units, max_units = units_str.split('-')
        else:
            min_units, max_units = units_str, units_str

        # If 'Unit' or 'Units' is not in the string, assume the entire string is a numeric value
        if 'Unit' not in units_str and 'Units' not in units_str:
            min_units = max_units = float(units_str)
        else:
            # Assuming 'Units' is in format like "4 Units" or "2-6 Units"
            min_units = float(min_units.split(" ")[0])
            max_units = float(max_units.split(" ")[0])
    else:
        min_units, max_units = None, None

    return min_units, max_units

@st.cache_data
def brewing_magic(search_query, df):
    # Check if the search query exactly matches a Class Name
    class_name_exact_matches = df[df['Class Name'].str.match(search_query, case=False)]

    if len(class_name_exact_matches) >= 10:
        # If there are at least 10 exact matches, sort by class name
        class_name_exact_matches.sort_values(by='Class Name', inplace=True)
        return class_name_exact_matches.head(10)

    # Check if the search query is in any Class Name
    class_name_partial_matches = df[df['Class Name'].str.contains(search_query, case=False)]

    # Filter out exact matches from partial matches
    class_name_partial_matches = class_name_partial_matches[~class_name_partial_matches['Class Name'].isin(class_name_exact_matches['Class Name'])]

    # Get the remaining number of results needed
    remaining_results = 10 - len(class_name_exact_matches)

    if len(class_name_partial_matches) >= remaining_results:
        # If there are at least the remaining number of partial matches, sort by class name
        class_name_partial_matches.sort_values(by='Class Name', inplace=True)
        return pd.concat([class_name_exact_matches.head(10), class_name_partial_matches.head(remaining_results)])

    # Check if the search query exactly matches a Class Description
    class_description_exact_matches = df[df['Class Description'].str.match(search_query, case=False)]

    # Filter out exact matches from class name partial matches
    class_description_exact_matches = class_description_exact_matches[~class_description_exact_matches['Class Name'].isin(class_name_exact_matches['Class Name'])]

    # Filter out exact matches from class name partial matches and class description exact matches
    class_description_exact_matches = class_description_exact_matches[~class_description_exact_matches['Class Name'].isin(class_name_partial_matches['Class Name'])]

    # Get the remaining number of results needed
    remaining_results = 10 - len(class_name_exact_matches) - len(class_name_partial_matches)

    if len(class_description_exact_matches) >= remaining_results:
        # If there are at least the remaining number of description exact matches, sort by class name
        class_description_exact_matches.sort_values(by='Class Name', inplace=True)
        return pd.concat([class_name_exact_matches.head(10), class_name_partial_matches.head(remaining_results), class_description_exact_matches.head(remaining_results)])

    # Use SentenceTransformer to get the embedding of the search query
    search_embedding = get_embedding(search_query)

    # Ensure the search_embedding has the same dimension as embeddings in the CSV file
    assert len(search_embedding) == 384, f'Expected 384, but got {len(search_embedding)}'

    # Reshape the search embedding to be (1, 384) instead of (384,)
    search_embedding = search_embedding.reshape(1, -1)

    embeddings = np.vstack(df["embeddings"].values)
    similarities = np.dot(embeddings, search_embedding.T) / (np.linalg.norm(embeddings, axis=1, keepdims=True) * np.linalg.norm(search_embedding))

    df["similarities"] = similarities
    df.sort_values(by="similarities", ascending=False, inplace=True)

    # Ensure there are at least 10 semantic search results
    if len(df) >= 10:
        return df.head(10)

    # If there are less than 10 results, return all results
    return df

def display_result_card(result):
    card_style = """
    <style>
        .card {
            background-color: #222222;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-shadow: 1px 1px 4px rgba(0, 0, 0, 0.1);
            padding: 15px;
            margin-bottom: 15px;
        }
    </style>
    """

    class_name = f"{result['Class Name']}"
    class_code = f"Code: <a href='{result['Class URL']}'>{result['Class Code']}</a>"
    department = f"Department: {result['Department']}"
    units = f"{result['Units']}" if 'Unit' in result['Units'] else f"{result['Units']} unit{'s' if result['Units'] != '1' else ''}"

    card_content = f"""
    <a href='{result['Class URL']}' style='text-decoration: none; color: inherit;'>
        <div class="card">
            <h3>{class_name}</h3>
            <p>{units}  |  {class_code}</p>
            <p>{result['Class Description']}</p>
            <p style='font-size: 14px; color: #ccc;'>{department}</p>
        </div>
    </a>
    """

    st.markdown(card_style, unsafe_allow_html=True)
    st.markdown(card_content, unsafe_allow_html=True)

def main():
    st.markdown("<h1 style='text-align: center;'><a href='https://uci.streamlit.app/' style='text-decoration: none; color: inherit;'>AnteaterQuest 🚀</a></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-top: -10px; color: #ccc;'>Search your Fall 2023 courses using AI</p>", unsafe_allow_html=True)
    search_query = st.text_input("Search for courses", "")

    with st.expander('Add Filters'):
        st.write('Units:')
        col1, col2, col3, col4, col5 = st.columns(5)
        unit_filters = {
            '1 Units': False,
            '2 Units': False,
            '3 Units': False,
            '4 Units': False,
            '5 Units': False,
        }
        unit_filters['1 Units'] = col1.checkbox('1 Unit', value=unit_filters['1 Units'])
        unit_filters['2 Units'] = col2.checkbox('2 Units', value=unit_filters['2 Units'])
        unit_filters['3 Units'] = col3.checkbox('3 Units', value=unit_filters['3 Units'])
        unit_filters['4 Units'] = col4.checkbox('4 Units', value=unit_filters['4 Units'])
        unit_filters['5 Units'] = col5.checkbox('5+ Units', value=unit_filters['5 Units'])

    if search_query:
        df = blending_wonders()
            
        # Filter by the selected units
        selected_unit_filters = [int(unit.split(" ")[0]) for unit, value in unit_filters.items() if value]
        if selected_unit_filters:
            min_selected_unit = min(selected_unit_filters)
            max_selected_unit = max(selected_unit_filters)

            df = df[(df['Min Units'] <= max_selected_unit) & (df['Max Units'] >= min_selected_unit)]

            
        results = brewing_magic(search_query, df)

        
        for i in range(10): # Always display the first 10 entries
            if i < len(results):
                display_result_card(results.iloc[i])
    #st.markdown("<p style='text-align: center; margin-top: 10px; color: #ccc;'>🚨 If the text is illegible, set the theme to DARK: 3 lines on the top right > settings > theme: dark 🚨</p>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin-top: 5px;'><a href='mailto:duforesa@uci.edu?subject=Feedback%20-%20Anteater%20Quest'>Leave feedback</a></div>", unsafe_allow_html=True)
    #st.markdown("<p style='text-align: center; margin-top: 20px; color: #ccc;'>Currently in beta with upcoming features</p>", unsafe_allow_html=True)
    st.markdown("<hr margintop: 20px>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-top: 25;'>Made by Alexandre Duforest</p>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin-top: 10px;'><a href='https://bmc.link/asduforest' target='_blank'><img src='https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png' alt='Buy Me A Coffee' width='150' ></a></div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()