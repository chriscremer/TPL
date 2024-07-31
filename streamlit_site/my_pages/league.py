import streamlit as st
import pandas as pd
import numpy as np
import random
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from utils import get_connection



def display_team2(team_name, rosters, player_salaries, max_salary, df_players, player_bids):

    # convert rosters to dataframe
    roster = rosters[team_name]
    team_df = pd.DataFrame(roster, columns=['Player'])
    team_df['Salary'] = [player_salaries[player] for player in roster]

    # merge with gender from df_players
    # print (df_players.columns)
    team_df = team_df.merge(df_players, left_on='Player', right_on='Full Name', how='left')


    team_df = team_df.sort_values(by=['Salary'], ascending=False)
    team_df = team_df.reset_index(drop=True)

    # print (team_df.columns)

    # display team
    for i, row in team_df.iterrows():
        player_name = row['Player']
        salary = row['Salary']
        gender = row['Gender']
        cols = st.columns([1, 2, 1, 2, 1])
        init_bid = player_bids[player_name]

        with cols[1]:
            # st.markdown(f"Player: {player_name}<br>Salary: ${salary}", unsafe_allow_html=True)
            # color = '#ADD8E6' if player_name % 2 == 1 else '#FF69B4'
            color = '#ADD8E6' if gender == 'Male' else '#FF69B4'
            st.markdown(f"<span style='color:{color}'>{player_name}<br>Salary: ${salary}</span>", unsafe_allow_html=True)
        with cols[3]:
            if 'Chris' in player_name or 'WILD' in player_name:
                #disable slider
                my_bid = st.slider("Your Bid", 0, max_salary, init_bid, key=f"{team_name}-{player_name}", label_visibility='collapsed', disabled=True)
            else:
                my_bid = st.slider("Your Bid", 0, max_salary, init_bid, key=f"{team_name}-{player_name}", label_visibility='collapsed')

        with cols[2]:
            if my_bid > salary:
                st.markdown(f'<br><span style="color: green">↑</span> {my_bid - salary}', unsafe_allow_html=True)
            elif my_bid < salary:
                st.markdown(f'<br><span style="color: red">↓</span> {salary - my_bid}', unsafe_allow_html=True)

    st.markdown('<br><br>', unsafe_allow_html=True)




def get_salaries(df_players, player_names, max_salary):
    # get latest salary: "Week 0 - Salary", extact the int from the string
    df_cols = df_players.columns
    df_cols = [col for col in df_cols if 'Salary' in col]
    df_cols = [col.split(' - ')[0] for col in df_cols]
    df_cols = [int(col.split(' ')[1]) for col in df_cols]
    latest_week = max(df_cols)
    salary_col = f"Week {latest_week} - Salary"
    player_salaries = df_players.set_index('Full Name')[salary_col].to_dict()

    # if salary is above max, we'll need to scale it
    max_cap = max([player_salaries[player] for player in player_names])
    if max_cap > max_salary:
        scale = max_salary / max_cap
    else:
        scale = 1
    for player, salary in player_salaries.items():
        player_salaries[player] = int(salary * scale)

    return player_salaries, latest_week



def get_bids(conn, stss, latest_week, worksheets, your_team, player_salaries):

    bids_sheet_name = f"Week {latest_week} - Bids"
    # If bids_sheet_name does not exist, make it
    if not bids_sheet_name in [worksheet.title for worksheet in worksheets]:
        worksheet = conn.add_worksheet(title=bids_sheet_name, rows=200, cols=20)
        
        # Populate sheet with player names as rows, team names as columns, and salary as values
        # df = pd.DataFrame(player_bids).T
        df = pd.DataFrame(player_salaries, index=[0]).T
        df.index.name = 'Player'
        set_with_dataframe(worksheet, df, include_index=True, include_column_header=True, resize=True)
        print ('Created worksheet\n')

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
    # print (len(player_bids))
    # print (len(player_salaries))
    # print (player_bids.keys())
    return player_bids, bids_sheet_name


def get_rosters(df_players, team_names):
    rosters = {team: [] for team in team_names}
    for i, row in df_players.iterrows():
        team = row['Team']
        name = row['Full Name']
        rosters[team].append(name)
    return rosters








def league_page():

    stss = st.session_state

    if 'conn' not in st.session_state:
        conn = get_connection()
        stss['conn'] = conn

    if 'df_players' not in stss:
        conn = stss['conn']
        worksheets = conn.worksheets()
        players_sheet = [worksheet for worksheet in worksheets if worksheet.title == 'Players'][0]
        df_players = get_as_dataframe(players_sheet)
        stss['worksheets'] = worksheets
        stss['df_players'] = df_players

    conn = stss['conn']
    worksheets = stss['worksheets']
    df_players = stss['df_players']
    your_team = stss['team_name']
    team_names = list(df_players['Team'].unique())
    player_names = df_players['Full Name'].tolist()
    max_salary = 500

    player_salaries, latest_week = get_salaries(df_players, player_names, max_salary)

    player_bids, bids_sheet_name = get_bids(conn, stss, latest_week, worksheets, your_team, player_salaries)

    rosters = get_rosters(df_players, team_names)
    
    # Figure out if changes have been made
    # check if bids are part of session state yet
    team0 = team_names[0]
    player0 = rosters[team0][0]
    if f"{team0}-{player0}" not in stss:
        changes = False
    else:
        # compare bids to player_salaries
        # actually compare to saved bids
        changes = False
        for team in team_names:
            for player in rosters[team]:
                if player_salaries[player] != stss[f"{team}-{player}"]:
                    changes = True
                    break
            if changes:
                break

    # Add save button
    if changes:
        save = st.button('Save Changes')

        # # print (list(st.session_state.keys()))
        # print ('keys1 ----')
        # for i, key in enumerate(st.session_state.keys()):
        #     print (key, st.session_state[key])
        #     if i > 10:
        #         break
        # print ('FaulklHore (Revenge of the Swift Version)-Maggie Chen' in list(st.session_state.keys()))
        # print (' ----')

    else:
        save = st.button('No Changes', disabled=True)
    if save:
        print ('Save')

        # Update col for this team with new bids
        col_name = your_team
        start_row_idx = 2
        end_row_idx = len(player_bids) + 1
        col_letter = chr(team_names.index(col_name) + 65 + 1) # +1 for the index column
        values = []
        for player_name in player_bids.keys():
            player_team = df_players.loc[df_players['Full Name'] == player_name]['Team'].values[0]
            bid = st.session_state[f"{player_team}-{player_name}"]
            values.append([bid])
        sheet = conn.worksheet(bids_sheet_name)
        sheet.update(range_name=f'{col_letter}{start_row_idx}:{col_letter}{end_row_idx}', values=values)

        # # Turn off button
        # save = False



    n_teams = len(team_names)
    teams_per_row = 3
    n_rows = n_teams // teams_per_row
    container_list = [st.container() for _ in range(n_rows*2)]
    cols_list = [st.columns(teams_per_row) for _ in range(n_rows*2)]

    # Put your team first
    display_team_names = team_names.copy()
    display_team_names.remove(your_team)
    display_team_names = [your_team] + display_team_names
    # Display all teams
    for i, team_name in enumerate(display_team_names):

        # Center your team
        if i == 0:
            row = 0
            col = 1
        else:
            idx = i - 1
            row = idx//teams_per_row +2
            col = idx%teams_per_row

        with container_list[row]:
            with cols_list[row][col]:
                st.markdown(f"<center><p style='font-size:20px; font-weight:bold'>{team_name}</p></center>", unsafe_allow_html=True)

        with container_list[row + 1]:
            with cols_list[row + 1][col]:
                display_team2(team_name, rosters, player_salaries, max_salary, df_players, player_bids)


