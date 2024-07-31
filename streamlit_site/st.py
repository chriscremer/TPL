"""
streamlit run streamlit_site/st.py
"""

print ('--------------')

import streamlit as st
import pandas as pd
import numpy as np
import random

from my_pages.league import league_page

from gspread_dataframe import set_with_dataframe, get_as_dataframe
from utils import get_connection


st.set_page_config(page_title="TPL", layout="wide", page_icon="🥏")
st.markdown("<h1 style='text-align: center;'>TPL</h1>", unsafe_allow_html=True)

stss = st.session_state
stay_logged_in = 0
if stay_logged_in:
    stss['login_status'] = True
    stss['team_name'] = 'Team A'

if 'conn' not in st.session_state:
    conn = get_connection()
    st.session_state['conn'] = conn

    # conn = st.session_state['conn']
    worksheets = conn.worksheets()
    login_sheet = [worksheet for worksheet in worksheets if worksheet.title == 'Login'][0]
    login_df = get_as_dataframe(login_sheet)
    st.session_state['login_df'] = login_df


if ('login_status' not in stss or stss['login_status'] == False) and not stay_logged_in:
    stss['login_status'] = False
    # Make a form to get the team name and password
    form = st.form(key='my_form')
    team_name = form.text_input('Team Name')
    password = form.text_input('Password', type='password')
    submitted = form.form_submit_button('Submit')
    if submitted:
        # stss['login_status'] = True
        # stss['team_name'] = team_name

        # check to see if the team name and password are in the login sheet
        login_df = st.session_state['login_df']
        if team_name in login_df['Username'].values:
            password_correct = login_df[login_df['Username'] == team_name]['Password'].values[0] == password
            if password_correct:
                stss['login_status'] = True
                if team_name == 'a':
                    team_name = "FaulklHore (Revenge of the Swift Version)"
                stss['team_name'] = team_name
                st.rerun()
            else:
                st.error('Password is incorrect')
                # print ('Password is incorrect')
        else:
            st.error('Team name not found')
            # print ('Team name not found')

        

else:
    tabs_list = ['League', 'Settings'] #, 'Algo']
    tabs = st.tabs(tabs_list)

    with tabs[tabs_list.index('League')]:
        league_page()

    with tabs[tabs_list.index('Settings')]:
        st.write(f'Team: {stss["team_name"]}')
        logout = st.button('Logout')
        if logout:
            stss['login_status'] = False
            print (f"Logging out {stss['team_name']}")
            # erase session state
            for key in list(stss.keys()):
                del stss[key]
            st.rerun()

    # with tabs[tabs_list.index('Algo')]:
    #     algo_tabs_list = ['Run Algo', 'Team A', 'Team B', 'Team C']
    #     teams_tabs = st.tabs(algo_tabs_list)




