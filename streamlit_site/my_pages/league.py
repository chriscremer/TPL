import streamlit as st
import pandas as pd
import numpy as np
import random
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from utils import get_connection


def compute_player_salaries(rosters, player_bids, team_names):
    player_salaries = {}
    for team, roster in rosters.items():
        for player in roster:
            bids = player_bids[player]
            # salary = max([bids[t] for t in team_names if t != team])
            # salary = np.mean([bids[t] for t in team_names if t != team])
            salary = np.mean([bids[t] for t in team_names])
            salary = int(salary)
            player_salaries[player] = salary
    return player_salaries


def get_team_costs(rosters, player_salaries, team_names):
    team_costs = {team: 0 for team in team_names}
    for team, roster in rosters.items():
        for player in roster:
            team_costs[team] += player_salaries[player]
    # sort by cost
    team_costs = {k: v for k, v in sorted(team_costs.items(), key=lambda item: item[1], reverse=True)} 
    return team_costs


def trade(rosters, team_1, player_1, team_2, player_2, team_names):
    new_team_1_roster = [player_2 if player == player_1 else player for player in rosters[team_1]]
    new_team_2_roster = [player_1 if player == player_2 else player for player in rosters[team_2]]
    # update rosters
    new_rosters = {team: rosters[team].copy() for team in team_names}
    new_rosters[team_1] = new_team_1_roster
    new_rosters[team_2] = new_team_2_roster
    return new_rosters


def display_team(team_name, rosters, player_salaries, max_salary):

    # convert rosters to dataframe
    roster = rosters[team_name]
    team_df = pd.DataFrame(roster, columns=['Player'])
    team_df['Salary'] = [player_salaries[player] for player in roster]
    team_df = team_df.sort_values(by=['Salary'], ascending=False)
    team_df = team_df.reset_index(drop=True)

    # display team
    for i, row in team_df.iterrows():
        player_name = row['Player']
        salary = row['Salary']
        cols = st.columns([1, 2, 1, 2, 1])
        with cols[1]:
            # st.markdown(f"Player: {player_name}<br>Salary: ${salary}", unsafe_allow_html=True)
            color = '#ADD8E6' if player_name % 2 == 1 else '#FF69B4'
            st.markdown(f"<span style='color:{color}'>Player: {player_name}<br>Salary: ${salary}</span>", unsafe_allow_html=True)
        with cols[3]:
            # st.number_input("Your Bid", value=salary, key=f"{team_name}-{player_name}", label_visibility='collapsed')
            my_bid = st.slider("Your Bid", 0, max_salary, salary, key=f"{team_name}-{player_name}", label_visibility='collapsed')

        with cols[2]:
            if my_bid > salary:
                st.markdown(f'<br><span style="color: green">↑</span> {my_bid - salary}', unsafe_allow_html=True)
            elif my_bid < salary:
                st.markdown(f'<br><span style="color: red">↓</span> {salary - my_bid}', unsafe_allow_html=True)

    st.markdown('<br><br>', unsafe_allow_html=True)


def display_team2(team_name, rosters, player_salaries, max_salary, df_players):

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

        with cols[1]:
            # st.markdown(f"Player: {player_name}<br>Salary: ${salary}", unsafe_allow_html=True)
            # color = '#ADD8E6' if player_name % 2 == 1 else '#FF69B4'
            color = '#ADD8E6' if gender == 'Male' else '#FF69B4'
            st.markdown(f"<span style='color:{color}'>{player_name}<br>Salary: ${salary}</span>", unsafe_allow_html=True)
        with cols[3]:
            if 'Chris' in player_name or 'WILD' in player_name:
                #disable slider
                my_bid = st.slider("Your Bid", 0, max_salary, salary, key=f"{team_name}-{player_name}", label_visibility='collapsed', disabled=True)
            else:
                my_bid = st.slider("Your Bid", 0, max_salary, salary, key=f"{team_name}-{player_name}", label_visibility='collapsed')

        with cols[2]:
            if my_bid > salary:
                st.markdown(f'<br><span style="color: green">↑</span> {my_bid - salary}', unsafe_allow_html=True)
            elif my_bid < salary:
                st.markdown(f'<br><span style="color: red">↓</span> {salary - my_bid}', unsafe_allow_html=True)

    st.markdown('<br><br>', unsafe_allow_html=True)




















def league_page():

    
    random_data = 0
    if random_data:

        random.seed(0)
        n_teams = 10
        n_players = n_teams * 14
        max_salary = 500
        your_team = 'Team C'

        # convert number to letter
        def number_to_letter(n):
            return chr(n + 65)
        team_names = [f"Team {number_to_letter(i)}" for i in range(n_teams)]

        # randomly assign bids to players
        player_names = list(range(1, n_players+1))
        player_bids = {player: {} for player in player_names}
        for player, bids in player_bids.items():
            for team in team_names:
                bids[team] = random.randint(1, max_salary)

        # randomly assign players to teams
        rosters = {team: [] for team in team_names}
        for player in player_names:
            # find all teams with the minimum number of players
            min_players = min([len(rosters[team]) for team in team_names])
            min_teams = [team for team in team_names if len(rosters[team]) == min_players]
            # randomly assign player to one of the teams
            team = random.choice(min_teams)
            rosters[team].append(player)


        player_salaries = compute_player_salaries(rosters, player_bids, team_names)
        # team_costs = get_team_costs(rosters, player_salaries, team_names)


    else:
        if 'conn' not in st.session_state:
            conn = get_connection()
            st.session_state['conn'] = conn

        conn = st.session_state['conn']
        worksheets = conn.worksheets()
        players_sheet = [worksheet for worksheet in worksheets if worksheet.title == 'Players'][0]
        df_players = get_as_dataframe(players_sheet)
        team_names = list(df_players['Team'].unique())

        max_cap = df_players['Cap Impact'].max()
        max_salary = 500
        scale = max_salary / max_cap
        your_team = team_names[0]

        player_names = df_players['Full Name'].tolist()
        player_bids = {player: {} for player in player_names}
        for player, bids in player_bids.items():
            for team in team_names:
                cap_impact = df_players.loc[df_players['Full Name'] == player]['Cap Impact'].values[0]
                scaled_salary = int(cap_impact * scale)
                bids[team] = scaled_salary
        
        rosters = {team: [] for team in team_names}
        for i, row in df_players.iterrows():
            team = row['Team']
            name = row['Full Name']
            rosters[team].append(name)

        player_salaries = compute_player_salaries(rosters, player_bids, team_names)


    # Add save button
    changes = False
    if changes:
        save = st.button('Save Changes')
    else:
        save = st.button('No Changes', disabled=True)
    if save:
        print ('Save')

    n_teams = len(team_names)
    teams_per_row = 3
    n_rows = n_teams // teams_per_row
    container_list = [st.container() for _ in range(n_rows*2)]
    cols_list = [st.columns(teams_per_row) for _ in range(n_rows*2)]

    # Put your team first
    team_names.remove(your_team)
    team_names = [your_team] + team_names
    # Display all teams
    for i, team_name in enumerate(team_names):

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
                display_team2(team_name, rosters, player_salaries, max_salary, df_players)


    # print (list(st.session_state.keys()))


