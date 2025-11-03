"""
streamlit run streamlit_site/st.py
"""

print ('--------------')

import streamlit as st
# import pandas as pd
# import numpy as np
# import random

# from my_pages.bids import bids_page
# from my_pages.league import league_page
# from my_pages.rankings_page import rankings_page_func
from my_pages.algo_page import algo_page
from my_pages.settings import settings_page

# from gspread_dataframe import get_as_dataframe
from utils import google_authenticate #, get_connection
# from oauth2client.service_account import ServiceAccountCredentials
# import gspread




st.set_page_config(page_title="TPL", layout="wide", page_icon="🥏")
st.markdown("<h1 style='text-align: center;'>TPL</h1>", unsafe_allow_html=True)

stss = st.session_state
# print (f"stss: {stss}")

# if 'conn' not in st.session_state:
#     sheet_url = 'https://docs.google.com/spreadsheets/d/16NDz42ETaLIAroR2IwHsfZcjSeA2gm74da_Vf3ehrjI/edit?gid=0#gid=0'
#     conn = get_connection(sheet_url)
#     st.session_state['conn'] = conn

#     worksheets = conn.worksheets()
#     login_sheet = worksheets[0]
#     login_df = get_as_dataframe(login_sheet)

    # st.session_state['login_df'] = login_df

    # team_names = login_df['Username'].values
    # # remove Convenor
    # team_names = [team_name for team_name in team_names if team_name != 'Convenor']
    # st.session_state['team_names'] = team_names
    # week_sheet = [worksheet for worksheet in worksheets if worksheet.title == "Week 4 - Bids"][0]
    # week_df = get_as_dataframe(week_sheet)
    # cols = week_df.columns
    # cols_list = list(cols)
    # print (f"cols: {cols}")
    # teams = cols_list[1:]
    # st.session_state['team_names'] = teams

    # st.session_state['max_salary'] = 350000 #1000
    


if ('login_status' not in stss or stss['login_status'] == False): # and not stay_logged_in:
    stss['login_status'] = False
    # Make a form to get the team name and password
    form = st.form(key='my_form')
    # team_name = form.radio(
    #     "Team Name",
    #     # st.session_state['team_names'] + 
    #     ['Convenor'],
    # )

    password = form.text_input('Password', type='password')
    submitted = form.form_submit_button('Submit')
    if submitted:

        drive_service, sheets_client, sheets_service = google_authenticate()
        # conn, client = get_connection(sheet_url)
        # st.session_state['conn'] = conn
        st.session_state['client'] = sheets_client
        st.session_state['drive_service'] = drive_service
        st.session_state['sheets_service'] = sheets_service

        # password sheet
        # sheet_url = 'https://docs.google.com/spreadsheets/d/16NDz42ETaLIAroR2IwHsfZcjSeA2gm74da_Vf3ehrjI/edit?gid=0#gid=0'
        sheet_url = "https://docs.google.com/spreadsheets/d/1M_85kjvshOxvBtI-jdp9WTSmPurdUrKOHuDYwA_10ZI/edit?gid=0#gid=0" # nov 2025

        conn = sheets_client.open_by_url(sheet_url)
        worksheets = conn.worksheets()
        login_sheet = worksheets[0]
        # Get cell A1 from the first sheet
        first_cell = login_sheet.acell('A1').value
        # login_df = get_as_dataframe(login_sheet)


        # check to see if the team name and password are in the login sheet
        # login_df = st.session_state['login_df']
        # if team_name in login_df['Username'].values:
        # password_correct = login_df[login_df['Username'] == team_name]['Password'].values[0] == password
        if password == first_cell:
            stss['login_status'] = True
            # stss['team_name'] = team_name
            st.rerun()
        else:
            st.error('Password is incorrect')
        # else:
        #     st.error('Team name not found')

        

else:
    # if stss['team_name'] == "Convenor":
    # tabs_list = ['League', 'Algo', 'Settings']
    tabs_list = ['Algo', 'Settings']
    tabs = st.tabs(tabs_list)
    # with tabs[tabs_list.index('League')]:
    #     league_page()
    with tabs[tabs_list.index('Algo')]:
        algo_page()

    # else:
    #     # tabs_list = ['League', 'Bids', 'Settings']
    #     tabs_list = ['Bids', 'Rankings', 'Settings', ]
    #     tabs = st.tabs(tabs_list)
    #     # with tabs[tabs_list.index('League')]:
    #     #     league_page()
    #     with tabs[tabs_list.index('Bids')]:
    #         bids_page()
    #     with tabs[tabs_list.index('Rankings')]:
    #         rankings_page_func()

    with tabs[tabs_list.index('Settings')]:
        settings_page()



