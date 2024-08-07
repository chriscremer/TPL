import streamlit as st
import pandas as pd
import numpy as np
import random
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from utils import get_connection

from my_pages.league import get_rosters, get_salaries
from algo2 import run_algo


def get_all_bids_from_sheet(conn, stss, bids_sheet_name, worksheets, player_salaries):

    
    # If bids_sheet_name does not exist, make it
    if not bids_sheet_name in [worksheet.title for worksheet in worksheets]:
        raise Exception(f'No bids sheet found for {bids_sheet_name}')
        # worksheet = conn.add_worksheet(title=bids_sheet_name, rows=200, cols=20)
        
        # # Populate sheet with player names as rows, team names as columns, and salary as values
        # # df = pd.DataFrame(player_bids).T
        # df = pd.DataFrame(player_salaries, index=[0]).T
        # df.index.name = 'Player'
        # set_with_dataframe(worksheet, df, include_index=True, include_column_header=True, resize=True)
        # print ('Created worksheet\n')

    # Load the bids from the sheet
    # if 'player_bids' not in stss:

        # print (f'Loading bids for {your_team}')
    sheet = conn.worksheet(bids_sheet_name)
    df_bids = get_as_dataframe(sheet)
    # convert to dict
    # player_bids = df_bids.to_dict(orient='index')[0]
    # player_bids = {}
    # for i, row in df_bids.iterrows():
    #     player_name = row['Player']
    #     player_bids[player_name] = row[your_team]
    stss['all_player_bids'] = df_bids
    # player_bids = stss['player_bids']
    # print (len(player_bids))
    # print (len(player_salaries))
    # print (player_bids.keys())
    return df_bids #player_bids, bids_sheet_name







def algo_page():

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
        stss['player_names'] = df_players['Full Name'].tolist()

    conn = stss['conn']
    worksheets = stss['worksheets']
    df_players = stss['df_players']
    # print (df_players.columns)
    your_team = stss['team_name']
    team_names = list(df_players['Team'].unique())
    player_names = df_players['Full Name'].tolist()
    rosters = get_rosters(df_players, team_names)
    max_salary = 500

    player_salaries, latest_week = get_salaries(df_players, player_names, max_salary)
    salary_col_name = f"Week {latest_week} - Salary"
    bids_sheet_name = f'Week {latest_week} - Bids'




    team_names_tabs = [team_name[:13] for team_name in team_names]
    algo_tabs_list = ['Run Algo'] #+ list(team_names_tabs)
    teams_tabs = st.tabs(algo_tabs_list)


    with teams_tabs[algo_tabs_list.index('Run Algo')]:

        run_algo_button = st.button('Run Algo')
        if run_algo_button:

            # if 'all_player_bids' not in stss:
            all_player_bids = get_all_bids_from_sheet(conn, stss, bids_sheet_name, worksheets, player_salaries)
            # else:
                # all_player_bids = stss['all_player_bids']

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

            player_bids = {player: {} for player in player_names}
            # for player, bids in player_bids.items():
            #     for team in team_names:
            #         bids[team] = random.randint(1, max_salary)
            # df_bids = all_player_bids
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




            rosters, count_team_trades, trades = run_algo(team_costs, rosters_team_list, player_salaries, player_bids, player_genders)








            for i, trade in enumerate(trades):
                # st.write(trade)
                player1_salary = df_players[df_players['Full Name'] == trade['player_1']][salary_col_name].values[0]
                player2_salary = df_players[df_players['Full Name'] == trade['player_2']][salary_col_name].values[0]
                salary_diff = player1_salary - player2_salary

                # st.markdown(f'Trade {i+1}', unsafe_allow_html=True)
                # make it larger
                st.markdown(f"<h4>Trade {i+1}</h4>", unsafe_allow_html=True)
                # st.markdown(f"{trade['team_1']}: {trade['player_1']} ({player1_salary})")
                # st.markdown(f"{trade['team_2']}: {trade['player_2']} ({player2_salary})")
                # st.markdown(f"Salary Diff: {salary_diff}")
                # st.markdown(f'Standard Deviation: {trade["team_costs_std"]:.2f}') # ({trade["team_costs_std_diff"]:.2f})')
                # st.markdown(f"<hr>", unsafe_allow_html=True)
                # st.markdown('<br>', unsafe_allow_html=True) 
                text = "<p>"
                # text += f"{trade['team_1']}: {trade['player_1']} ({player1_salary}) <br>"
                # text += f"{trade['team_2']}: {trade['player_2']} ({player2_salary})"
                # make player name bold
                text += f"{trade['team_1']}: <b>{trade['player_1']}</b> ({player1_salary}) <br>"
                text += f"{trade['team_2']}: <b>{trade['player_2']}</b> ({player2_salary})"
                text += f"<br>Salary Diff: {salary_diff}"
                text += f"<br>Standard Deviation: {trade['team_costs_std']:.2f}"
                text += f"<br>Team 1 Happiness Change: {trade['team1_happiness_change']}"
                text += f"<br>Team 2 Happiness Change: {trade['team2_happiness_change']}"
                # text += f"<br>Total Happiness Change: {trade['happiness_change']}"
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

            

#             "team_costs_std":65.91661399070799
# "team_costs_std_diff":16.28922521795164
# "happiness_change":"np.int64(742)"
# "team1_happiness_change":392
# "team2_happiness_change":350
                
            # st.markdown('<style> table {display: block; overflow-x: auto; white-space: nowrap;} </style>', unsafe_allow_html=True)
            # st.markdown('<style> th {text-align: center;} </style>', unsafe_allow_html=True)
            # st.markdown('<style> td {text-align: center;} </style>', unsafe_allow_html=True)
            # st.markdown('<style> table {width: 100%;} </style>', unsafe_allow_html=True)
            # start table
            # st.markdown('<table>', unsafe_allow_html=True)
            # for team_name in count_team_trades:
            #     # add row to table
            #     st.markdown('<tr>', unsafe_allow_html=True)
            #     # add team name to row
            #     st.markdown(f'<td>{team_name}</td>', unsafe_allow_html=True)
            #     # add trade count to row
            #     st.markdown(f'<td>{count_team_trades[team_name]}</td>', unsafe_allow_html=True)
            #     # close row
            #     st.markdown('</tr>', unsafe_allow_html=True)
            # # close table
            # st.markdown('</table>', unsafe_allow_html=True)

            # st.markdown('Number of Trades per Team', unsafe_allow_html=True)
            count_team_trades_df = pd.DataFrame.from_dict(count_team_trades, orient='index', columns=['Trade Count'])
            # cols = st.columns(2)
            # with cols[0]:
                # st.table(count_team_trades_df)

            # calcutte new team costs
            team_costs = {}
            for team_name in team_names:
                team_costs[team_name] = 0
                for player in rosters[team_name]:
                    salary = df_players[df_players['Full Name'] == player][salary_col_name].values[0]
                    team_costs[team_name] += salary
            
            st.markdown('New Team Salaries', unsafe_allow_html=True)
            team_costs_df = pd.DataFrame.from_dict(team_costs, orient='index', columns=['Salary'])

            # add trade count to row
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





