"""
streamlit run streamlit_site/st.py
"""

print ('--------------')

import streamlit as st
import pandas as pd
import numpy as np
import random

from my_pages.bids import bids_page
from my_pages.league import league_page
from my_pages.algo_page import algo_page
from my_pages.settings import settings_page

from gspread_dataframe import get_as_dataframe
from utils import get_connection


st.set_page_config(page_title="TPL", layout="wide", page_icon="🥏")
st.markdown("<h1 style='text-align: center;'>TPL</h1>", unsafe_allow_html=True)

stss = st.session_state

if 'conn' not in st.session_state:
    conn = get_connection()
    st.session_state['conn'] = conn

    worksheets = conn.worksheets()
    login_sheet = [worksheet for worksheet in worksheets if worksheet.title == 'Login'][0]
    login_df = get_as_dataframe(login_sheet)
    st.session_state['login_df'] = login_df


if ('login_status' not in stss or stss['login_status'] == False): # and not stay_logged_in:
    stss['login_status'] = False
    # Make a form to get the team name and password
    form = st.form(key='my_form')

    # team_name = form.text_input('Team Name')
    team_name = form.radio(
        "Team Name",
        ["FaulklHore (Revenge of the Swift Version)",
         "You Belong Whist Me",
            'I was cRyan on the staircase Meagging you "Please don\'t throw"',
            "Huck the PATriarchy",
            "DANti-Hero",
            "Sam's Cheer Captain And Chris' On The Bleachers",
            "Tam Mattgazine's Person of the Year",
            "Dear John Look what you made Lysh do",
            "Benny's Gonna Break Break Break Lexy's Gonna Fake Fake Fake",
            "kyraless nam's careful daughter",
            "Convenor",
        ],
    )

    password = form.text_input('Password', type='password')
    submitted = form.form_submit_button('Submit')
    if submitted:
        # check to see if the team name and password are in the login sheet
        login_df = st.session_state['login_df']
        if team_name in login_df['Username'].values:
            password_correct = login_df[login_df['Username'] == team_name]['Password'].values[0] == password
            if password_correct:
                stss['login_status'] = True
                stss['team_name'] = team_name
                st.rerun()
            else:
                st.error('Password is incorrect')
        else:
            st.error('Team name not found')

        

else:
    if stss['team_name'] == "Convenor":
        tabs_list = ['League', 'Algo', 'Settings']
        tabs = st.tabs(tabs_list)
        with tabs[tabs_list.index('League')]:
            league_page()
        with tabs[tabs_list.index('Algo')]:
            algo_page()

    else:
        tabs_list = ['League', 'Bids', 'Settings']
        tabs = st.tabs(tabs_list)
        with tabs[tabs_list.index('League')]:
            league_page()
        with tabs[tabs_list.index('Bids')]:
            bids_page()


    with tabs[tabs_list.index('Settings')]:
        settings_page()



