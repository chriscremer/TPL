import streamlit as st
import pandas as pd
import numpy as np
import random
from gspread_dataframe import set_with_dataframe, get_as_dataframe


from utils import get_connection
from data_utils import sliders_to_bids, load_protected_players



def get_rosters(df_players, team_names):
    rosters = {team: [] for team in team_names}
    for i, row in df_players.iterrows():
        team = row['Team']
        name = row['Full Name']
        rosters[team].append(name)
    return rosters


# def load_data(stss):

#     if 'conn' not in st.session_state:
#         conn = get_connection()
#         stss['conn'] = conn

#     if 'df_players' not in stss:
#         conn = stss['conn']
#         worksheets = conn.worksheets()
#         players_sheet = [worksheet for worksheet in worksheets if worksheet.title == 'Players'][0]
#         df_players = get_as_dataframe(players_sheet)
#         stss['worksheets'] = worksheets
#         stss['df_players'] = df_players
#         stss['player_names'] = df_players['Full Name'].tolist()

#         captains_sheet = [worksheet for worksheet in worksheets if worksheet.title == 'Captains'][0]
#         df_captains = get_as_dataframe(captains_sheet)
#         # convert to list
#         stss['captains'] = df_captains['Captain'].tolist()



def get_bids_from_sheet(conn, stss, bids_sheet_name, your_team):

    # Load the bids from the sheet
    if 'player_bids' not in stss:
        print (f'Loading bids for {your_team}')
        sheet = conn.worksheet(bids_sheet_name)
        df_bids = get_as_dataframe(sheet)
        # convert to dict
        # player_bids = df_bids.to_dict(orient='index')[0]
        player_bids = {}
        for i, row in df_bids.iterrows():
            player_name = row['Player']
            player_bids[player_name] = row[your_team]
        stss['player_bids'] = player_bids
    player_bids = stss['player_bids']
    return player_bids












def rankings_page_func():

    stss = st.session_state
    # load_data(stss)

    conn = stss['conn']
    # worksheets = stss['worksheets']
    df_players = stss['df_players']
    your_team = stss['team_name']
    # team_names = list(df_players['Team'].unique())
    team_names = stss['team_names']
    # player_names = df_players['Full Name'].tolist()
    rosters = get_rosters(df_players, team_names)
    # max_salary = stss['max_salary']

    roster = rosters[your_team]

    week = 4
    player_bids = get_bids_from_sheet(conn, stss, f'Week {week} - Bids', your_team)

    cols = st.columns([1,2,1,2,1])
    # on the left, display sorted males
    # on the right, display sorted females, based on bids

    # sort the players by bids
    sorted_players = sorted(player_bids.items(), key=lambda x: x[1], reverse=True)
    # remove Wildcard
    sorted_players = [player_bid for player_bid in sorted_players if "WILD" not in player_bid[0]]

    # st.markdown("<b style='text-align: center;'>Rankings</b>", unsafe_allow_html=True)

    with cols[1]:
        # st.write('Sorted Players')

        data = []
        for player, bid in sorted_players:
            # st.write(f'{player}: {bid}')
            # check if male
            # gender = df_players[df_players['Full Name'] == 
            # print (df_players[df_players['Full Name'] == player])
            row = df_players[df_players['Full Name'] == player]
            gender = row['Gender'].values[0]
            # print (player, gender)
            if gender == "Male":
                # st.write(f'{player}: {bid}')
                # st.markdown(f'{player}: {bid}', unsafe_allow_html=True)
                data.append([player, bid])
        
        df = pd.DataFrame(data, columns=['Player', 'Bid'])
        st.table(df)




    with cols[3]:
        data = []
        for player, bid in sorted_players:
            # check 
            row = df_players[df_players['Full Name'] == player]
            gender = row['Gender'].values[0]
            if gender == "Female":
                # st.write(f'{player}: {bid}')
                data.append([player, bid])
        df = pd.DataFrame(data, columns=['Player', 'Bid'])
        st.table(df)


    