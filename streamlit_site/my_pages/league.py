import streamlit as st
import pandas as pd
import numpy as np
import random
# from gspread_dataframe import set_with_dataframe, get_as_dataframe
# from utils import get_connection
from data_utils import get_league_data#, convert_salaries


# from utils import get_connection
# from gspread_dataframe import get_as_dataframe


# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import pandas as pd

# def get_sheet(sheets_url, worksheet=None, skiprows=0):

#     # Make service_account_file:
#     # https://cloud.google.com/iam/docs/keys-create-delete

#     # Authenticate with Google Sheets
#     scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.readonly']
#     service_account_file = "/Users/chriscremer/Downloads/SVA/SVA/SVA/g_TPL/data/sports-365003-a0354cb71377.json"
#     credentials = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)
#     client = gspread.authorize(credentials)
#     spreadsheet = client.open_by_url(sheets_url)

#     # get the first worksheet
#     if worksheet:
#         sheet = spreadsheet.worksheet(worksheet)
#     else:
#         sheet = spreadsheet.sheet1

#     values = sheet.get_all_values()#[9:]
#     if skiprows:
#         values = values[skiprows:]

#     # Convert the values into a pandas DataFrame and display it
#     # First row is the header, so we remove it
#     print (len(values))
#     df = pd.DataFrame(values[2:], columns=values[1])
#     return df








def league_page():

    if 'df_league' not in st.session_state:
        get_league_data(st.session_state)

    df_league = st.session_state['df_league']
    cols1 = st.columns([1,7,1])
    with cols1[1]:
        st.table(df_league)
