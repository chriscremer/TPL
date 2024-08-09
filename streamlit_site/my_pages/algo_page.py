import streamlit as st
import pandas as pd
import numpy as np
import random
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from utils import get_connection

from my_pages.league import get_rosters, get_salaries
from algo3 import run_algo


def get_all_bids_from_sheet(conn, stss, bids_sheet_name, worksheets, player_salaries):
    # If bids_sheet_name does not exist, make it
    if not bids_sheet_name in [worksheet.title for worksheet in worksheets]:
        raise Exception(f'No bids sheet found for {bids_sheet_name}')
    sheet = conn.worksheet(bids_sheet_name)
    df_bids = get_as_dataframe(sheet)
    stss['all_player_bids'] = df_bids
    return df_bids


def accumulate_data(rosters, team_names, df_players, salary_col_name, player_names, all_player_bids):
        
    # rosters_team_list is dict of team_name: list of player names
    rosters_team_list = {}
    for team_name in team_names:
        rosters_team_list[team_name] = []
        for player_name in rosters[team_name]:
            rosters_team_list[team_name].append(player_name)

    # team_costs is dict of team_name: sum of team salaries
    team_costs = {}
    for team_name in team_names:
        # team_costs[team_name] = rosters[team_name]['Salary'].sum()
        team_costs[team_name] = 0
        for player in rosters_team_list[team_name]:
            salary = df_players[df_players['Full Name'] == player][salary_col_name].values[0]
            team_costs[team_name] += salary

    # player_bids is dict of player_name: dict of team_name: bid
    player_bids = {player: {} for player in player_names}

    # convert all_player_bids df to player_bids where for each player there is a dict of team: bid
    for i, row in all_player_bids.iterrows():
        player_name = row['Player']
        for team_name in team_names:
            player_bids[player_name][team_name] = row[team_name]
    # print (player_bids)

    # make dict of player_name: gender
    player_genders = {}
    for player_name in player_names:
        gender = df_players[df_players['Full Name'] == player_name]['Gender'].values[0]
        player_genders[player_name] = gender


    return player_bids, team_costs, rosters_team_list, player_genders


def show_trades(trades, df_players, salary_col_name):
    # show trades
    for i, trade in enumerate(trades):
        player1_salary = df_players[df_players['Full Name'] == trade['player_1']][salary_col_name].values[0]
        player2_salary = df_players[df_players['Full Name'] == trade['player_2']][salary_col_name].values[0]
        salary_diff = player1_salary - player2_salary

        st.markdown(f"<h4>Trade {i+1}</h4>", unsafe_allow_html=True)
        text = "<p>"
        text += f"{trade['team_1']}: <b>{trade['player_1']}</b> ({player1_salary}) <br>"
        text += f"{trade['team_2']}: <b>{trade['player_2']}</b> ({player2_salary})"
        text += f"<br>Salary Diff: {salary_diff}"
        text += f"<br>Standard Deviation: {trade['team_costs_std']:.2f}"
        text += f"<br>Team 1 Happiness Change: {trade['team1_happiness_change']}"
        text += f"<br>Team 2 Happiness Change: {trade['team2_happiness_change']}"
        # if its positive, make it green
        if trade['happiness_change'] > 0:
            text += f"<br>Total Happiness Change: <span style='color:green'>{trade['happiness_change']}</span>"
        # if its negative, make it red
        elif trade['happiness_change'] < 0:
            text += f"<br>Total Happiness Change: <span style='color:red'>{trade['happiness_change']}</span>"
        else:
            text += f"<br>Total Happiness Change: {trade['happiness_change']}"

        text += f"</p>"
        st.markdown(text, unsafe_allow_html=True)
        st.markdown('<hr>', unsafe_allow_html=True)


def show_starting_info(team_costs):

    # show table of starting team costs
    st.markdown('Starting Team Salaries', unsafe_allow_html=True)
    team_costs_df = pd.DataFrame.from_dict(team_costs, orient='index', columns=['Salary'])
    # make salary column an int
    team_costs_df['Salary'] = team_costs_df['Salary'].astype(int)
    # sort by salary
    team_costs_df = team_costs_df.sort_values(by='Salary', ascending=False)

    # show avg team cost
    avg_team_cost = int(sum(team_costs.values()) / len(team_costs))
    st.markdown(f'Average Team Salary: {avg_team_cost}', unsafe_allow_html=True)

    # add column of dif from avg
    team_costs_df['Diff from Avg'] = team_costs_df['Salary'] - avg_team_cost

    cols_0 = st.columns(2)
    with cols_0[0]:
        st.table(team_costs_df)


def calc_teams_salaries(rosters, team_names, df_players, salary_col_name):
    # calcutte new team costs
    team_costs = {}
    for team_name in team_names:
        team_costs[team_name] = 0
        for player in rosters[team_name]:
            salary = df_players[df_players['Full Name'] == player][salary_col_name].values[0]
            team_costs[team_name] += salary
    return team_costs




def show_end_info(team_costs, count_team_trades, trades):

    st.markdown('New Team Salaries', unsafe_allow_html=True)
    team_costs_df = pd.DataFrame.from_dict(team_costs, orient='index', columns=['Salary'])

    # add trade count to row
    count_team_trades_df = pd.DataFrame.from_dict(count_team_trades, orient='index', columns=['Trade Count'])
    team_costs_df['Trade Count'] = count_team_trades_df['Trade Count']
    # make salary column an int
    team_costs_df['Salary'] = team_costs_df['Salary'].astype(int)
    # sort by salary
    team_costs_df = team_costs_df.sort_values(by='Salary', ascending=False)

    # add column of dif from avg
    avg_team_cost = int(sum(team_costs.values()) / len(team_costs))
    team_costs_df['Diff from Avg'] = team_costs_df['Salary'] - avg_team_cost

    # reorder columns, salary, diff from avg, trade count
    team_costs_df = team_costs_df[['Salary', 'Diff from Avg', 'Trade Count']]


    cols = st.columns(2)
    with cols[0]:
        st.table(team_costs_df)
    
    st.markdown(f'Average Team Salary: {avg_team_cost}', unsafe_allow_html=True)

    # Total happiness change
    total_happiness_change = 0
    for trade in trades:
        total_happiness_change += trade['happiness_change']
    # st.markdown(f'Total Happiness Change: {total_happiness_change}', unsafe_allow_html=True)
    # if its positive, make it green
    if total_happiness_change > 0:
        st.markdown(f'Total Happiness Change: <span style="color:green">{total_happiness_change}</span>', unsafe_allow_html=True)
    # if its negative, make it red
    elif total_happiness_change < 0:
        st.markdown(f'Total Happiness Change: <span style="color:red">{total_happiness_change}</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'Total Happiness Change: {total_happiness_change}', unsafe_allow_html=True)






def algo_page():

    stss = st.session_state

    run_algo_button = st.button('Run Algo')
    if run_algo_button:

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
            stss['player_names'] = df_players['Full Name'].tolist()

        conn = stss['conn']
        worksheets = stss['worksheets']
        df_players = stss['df_players']

        # your_team = stss['team_name']
        team_names = list(df_players['Team'].unique())
        player_names = df_players['Full Name'].tolist()
        rosters = get_rosters(df_players, team_names)
        max_salary = 500

        player_salaries, latest_week = get_salaries(df_players, player_names, max_salary)
        salary_col_name = f"Week {latest_week} - Salary"
        bids_sheet_name = f'Week {latest_week} - Bids'

        all_player_bids = get_all_bids_from_sheet(conn, stss, bids_sheet_name, worksheets, player_salaries)
        player_bids, team_costs, rosters_team_list, player_genders = accumulate_data(rosters, team_names, df_players, salary_col_name, player_names, all_player_bids)

        if 'captains' not in stss:
            captains_sheet = [worksheet for worksheet in worksheets if worksheet.title == 'Captains'][0]
            df_captains = get_as_dataframe(captains_sheet)
            # convert to list
            stss['captains'] = df_captains['Captain'].tolist()
        captains = stss['captains']

        original_team_costs = team_costs.copy()
        # RUN TRADING ALORITHM
        rosters, count_team_trades, trades = run_algo(team_costs, rosters_team_list, player_salaries, player_bids, player_genders, captains)
        new_team_costs = calc_teams_salaries(rosters, team_names, df_players, salary_col_name)


        # Display info
        show_starting_info(original_team_costs)
        show_trades(trades, df_players, salary_col_name)
        show_end_info(new_team_costs, count_team_trades, trades)






