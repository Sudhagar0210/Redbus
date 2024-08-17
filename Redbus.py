import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import urllib
from streamlit_lottie import st_lottie
import json
import numpy as np

# Define the connection string
params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=Sudhakar\\SQLEXPRESS01;DATABASE=Local_database;UID=sa;PWD=123")
connection_url = f"mssql+pyodbc:///?odbc_connect={params}"

# Create the SQLAlchemy engine
engine = create_engine(connection_url)

# SQL Query Execution with parameters
def execute_query(query, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return result.fetchall()
    


def show_bus_details(state_name=None):
    query_state_name = "SELECT DISTINCT [State_name] FROM Redbus ORDER BY [State_name] ASC"
    df_state_name = pd.read_sql_query(query_state_name, engine)

    if state_name:
        query_route_name = f"SELECT DISTINCT [Route_name] FROM Redbus WHERE State_name = '{state_name}' ORDER BY [Route_name] ASC"
        df_route_name = pd.read_sql_query(query_route_name, engine)
    else:
        df_route_name = pd.DataFrame({'Route_name': []}) 
    return df_route_name, df_state_name



def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

st.title('Redbus Booking Details')

# Sidebar with a header and buttons
st.sidebar.header('Main Menu')
page = st.sidebar.selectbox('Select a page', ['Home', 'Select Bus Details'])

#Lottie animation
lottie_animation = load_lottiefile("C:\\Users\\sudha\\Downloads\\Animation.json")  

if page == 'Home':
    st.write('Welcome to Redbus Trip Booking')
    st_lottie(lottie_animation, height=425, key="home_animation")

elif page == 'Select Bus Details':
    st.write('Please select your bus details:')

    df_route_name, df_state_name = show_bus_details()    
   
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    # Dropdown options with "Select" as default
    start_time_option = {
        'Select': None,
        '01:00 - 12:00': ('01:00', '11:59'),
        '12:00 - 24:00': ('12:00', '23:59')        
    }
    
    fare_from_option = {
        'Select': None,
        '100 - 1000': ('100', '1000'),
        '1000 - 3000': ('1000', '3000'),
        '3000 - 5000': ('3000', '5000')
    }

    Rating_option = {
        'Select': None,
        '1': '1%',
        '2': '2%',
        '3': '3%',
        '4': '4%',
        '5': '5%'
    }

    Seat_option = {
        'Select': None,
        'A/C Sleeper': "'%A/C Sleeper%' AND bus_type NOT LIKE '%Non A/C Sleeper%'",
        'Non A/C Sleeper': "'%Non A/C Sleeper%'",
        'A/C Seater': "'%A/C Seater%'"
    }

    display_start_time = list(start_time_option.keys())
    display_fare_from = list(fare_from_option.keys())
    display_Rating = list(Rating_option.keys())
    display_Seat = list(Seat_option.keys())

    with col1:        
        state_name = st.selectbox('Select  State Name', ['Select'] + df_state_name['State_name'].tolist())        
       
        df_route_name, df_state_name = show_bus_details(state_name if state_name != 'Select' else None)

    with col2:
        route_name = st.selectbox('Select  Route Name', ['Select'] + df_route_name['Route_name'].tolist())

    with col3:
        bus_type = st.selectbox('Select Seat Type', display_Seat, key='bus_type')

    with col4:
        Rating = st.selectbox('Select The Rating', display_Rating, key='Rating')

    with col5:
        start_time = st.selectbox('Select Starting Time', display_start_time, key='start_time')

    with col6:
        fare_from = st.selectbox('Bus Fare From', display_fare_from, key='fare_from')

    search_button = st.button('Search Bus')

    st.markdown("""
        <style>
        .stButton button {
            width: 20%;
            height: 35px;
            margin-top: 25px;
        }
        </style>
    """, unsafe_allow_html=True)

    if search_button:
        conditions = []
        if state_name != 'Select':
            conditions.append(f"State_name = '{state_name}'")
        if route_name != 'Select':
            conditions.append(f"Route_name = '{route_name}'")
        if bus_type != 'Select':
            conditions.append(f"Bus_type LIKE {Seat_option[bus_type]}")
        if start_time != 'Select':
            start_time_values = start_time_option[start_time]
            conditions.append(f"Departure_time BETWEEN '{start_time_values[0]}' AND '{start_time_values[1]}'")
        if Rating != 'Select':
            Rating_value = Rating_option[Rating]
            conditions.append(f"Rating LIKE '{Rating_value}'")
        if fare_from != 'Select':
            fare_values = fare_from_option[fare_from]
            conditions.append(f"Fare BETWEEN {fare_values[0]} AND {fare_values[1]}")

        query = "SELECT * FROM Redbus"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY 1 ASC"

        #st.write(f"Executing Query: {query}")  # Debugging: display the query

        bus_details_fetching = execute_query(query)

        if bus_details_fetching:
            df_bus_details_fetching = pd.DataFrame(bus_details_fetching)
            df_bus_details_fetching1 = df_bus_details_fetching.set_index(pd.Index(range(1, len(df_bus_details_fetching) + 1)))
            st.dataframe(df_bus_details_fetching1)
        else:
            st.write('No bus details found for the selected Option.')

