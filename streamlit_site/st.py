"""
streamlit run streamlit_site/st.py
"""

print ('--------------')

import streamlit as st
import pandas as pd
import numpy as np
import random

# to deal with ModuleNotFoundError
import os, sys
sys.path.append(os.getcwd())
from streamlit_site.my_pages.league import leage_page




# make it wide
st.set_page_config(page_title="TPL", layout="wide", page_icon="🎯")
st.markdown("<h1 style='text-align: center;'>TPL</h1>", unsafe_allow_html=True)

stss = st.session_state
if 'login_status' not in stss or stss['login_status'] == False:
    stss['login_status'] = False
    # Make a form to get the team name and password
    form = st.form(key='my_form')
    team_name = form.text_input('Team Name')
    password = form.text_input('Password', type='password')
    submitted = form.form_submit_button('Submit')
    if submitted:
        stss['login_status'] = True
        stss['team_name'] = team_name
        print (f"2 stss['login_status']: {stss['login_status']}")
        st.rerun()

else:
    tabs_list = ['League', 'Settings']
    tabs = st.tabs(tabs_list)

    with tabs[tabs_list.index('League')]:
        leage_page()
    with tabs[tabs_list.index('Settings')]:
        st.write(f'Team: {stss["team_name"]}')
        logout = st.button('Logout')
        if logout:
            stss['login_status'] = False
            st.rerun()











