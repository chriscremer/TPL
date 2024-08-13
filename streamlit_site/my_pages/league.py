import streamlit as st
import pandas as pd
import numpy as np
import random
# from gspread_dataframe import set_with_dataframe, get_as_dataframe
# from utils import get_connection



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


def convert_salaries(df_league, max_salary):
    # convert to string
    df_league['Cap Impact'] = df_league['Cap Impact'].astype(str)
    # "818,579.3373" to 818579.3373
    df_league['Cap Impact'] = df_league['Cap Impact'].str.replace(',', '').astype(float)
    # get the max salary
    largest_salary = df_league['Cap Impact'].max()
    # normalize the salaries
    scale = max_salary / largest_salary
    df_league['Cap Impact'] = df_league['Cap Impact'] * scale
    # convert to int
    df_league['Cap Impact'] = df_league['Cap Impact'].astype(int)
    # sort by salary
    df_league = df_league.sort_values('Cap Impact', ascending=False)

    # strip() the first and last names
    df_league['First'] = df_league['First'].str.strip()
    df_league['Last'] = df_league['Last'].str.strip()
    # combine First and Last names
    df_league['Name'] = df_league['First'] + ' ' + df_league['Last']
    # drop the First and Last columns
    df_league = df_league.drop(columns=['First', 'Last'])
    # put name as first column
    cols = list(df_league.columns)
    cols.remove('Name')
    df_league = df_league[['Name'] + cols]


    # remove rows with WILD in the name
    df_league = df_league[~df_league['Name'].str.contains("WILD")]
    # remove 0 GP rows
    df_league = df_league[df_league['GP'] != '0']

    # reset the index
    df_league = df_league.reset_index(drop=True)

    # scale G	A	2A	D	TA	RE by GPs
    cols = ['G', 'A', '2A', 'D', 'TA', 'RE']
    for col in cols:
        df_league[col] = df_league[col] / df_league['GP']
        # df_league[col] = df_league[col].round(1)
        # convert to string with 1 decimal place
        df_league[col] = df_league[col].apply(lambda x: f"{x:.1f}")

    return df_league






from utils import get_connection
from gspread_dataframe import get_as_dataframe




def league_page():

    if 'df_league' not in st.session_state:

        sheets_url = 'https://docs.google.com/spreadsheets/d/1U4T-r7DsfWZI9VXsa7Ul38XDDLpE-7Sz1TFzd29EEVw/edit#gid=0'
        league_conn = get_connection(sheet_url=sheets_url)
        
        worksheets = league_conn.worksheets()
        league_sheet = [worksheet for worksheet in worksheets if worksheet.title == 'League'][0]
        df_league = get_as_dataframe(league_sheet, evaluate_formulas=True)
        # make the df start at row 9, and drop first column
        df_league = df_league.iloc[8:, 1:]
        # make the first row the column names
        df_league.columns = df_league.iloc[0]
        # drop the first row
        df_league = df_league.iloc[1:]

        cols_to_keep = [
            "First",
            "Last",
            "Team",
            "Cap Impact",
            "GP",
            "G",
            "A",
            "2A",
            "D",
            "TA",
            "RE",
        ]
        df_league = df_league[cols_to_keep]

        # convert to dict
        df_league = df_league.to_dict(orient='records')
        # convert to df
        df_league = pd.DataFrame(df_league)

        df_league = convert_salaries(df_league, 500)
        st.session_state['df_league'] = df_league


    df_league = st.session_state['df_league']
    cols1 = st.columns([1,7,1])
    with cols1[1]:
        st.table(df_league)
