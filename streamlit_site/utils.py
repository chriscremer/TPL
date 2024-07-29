import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def get_connection(service_account_file = None, sheet_url=None):

    # if service_account_file is None:
    #     service_account_file = "/Users/chriscremer/Downloads/SVA/SVA/SVA/g_TPL/data/sports-365003-a0354cb71377.json"
    if sheet_url is None:
        sheet_url = 'https://docs.google.com/spreadsheets/d/1yUnn1IQ-EJJA_kdiHTswoh-4rbr8hflq1m66Z85Qp0g/edit#gid=0'


    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)

    #v2 - load json
    json_data = st.secrets['test']
    # json_data = json.load(open(service_account_file))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_data, scope)


    client = gspread.authorize(creds)
    conn = client.open_by_url(sheet_url)
    return conn
