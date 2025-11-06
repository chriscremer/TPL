import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import concurrent.futures


# import time
# from sklearn.linear_model import LinearRegression
# from gspread_dataframe import set_with_dataframe, get_as_dataframe
# from utils import get_connection
# from data_utils import get_league_data, load_protected_players
# from my_pages.bids import get_rosters, get_salaries
from algo4 import run_algo
from utils import no_emoji


# def get_all_bids_from_sheet(conn, stss, bids_sheet_name, worksheets):
#     # If bids_sheet_name does not exist, make it
#     if not bids_sheet_name in [worksheet.title for worksheet in worksheets]:
#         raise Exception(f'No bids sheet found for {bids_sheet_name}')
#     sheet = conn.worksheet(bids_sheet_name)
#     df_bids = get_as_dataframe(sheet)
#     stss['all_player_bids'] = df_bids
#     return df_bids



# def accumulate_data(rosters, team_names, df_players, salary_col_name, player_names, all_player_bids):
        
#     # rosters_team_list is dict of team_name: list of player names
#     rosters_team_list = {}
#     for team_name in team_names:
#         rosters_team_list[team_name] = []
#         for player_name in rosters[team_name]:
#             rosters_team_list[team_name].append(player_name)

#     # convert all_player_bids df to player_bids where for each player there is a dict of team: bid
#     player_bids = {player: {} for player in player_names}
#     for i, row in all_player_bids.iterrows():
#         player_name = row['Player']
#         for team_name in team_names:
#             player_bids[player_name][team_name] = row[team_name]
#     # print (player_bids)

#     # make dict of player_name: gender
#     player_genders = {}
#     for player_name in player_names:
#         gender = df_players[df_players['Full Name'] == player_name]['Gender'].values[0]
#         player_genders[player_name] = gender


#     return player_bids, rosters_team_list, player_genders







def show_trades(trades, new_player_salaries): #df_players, salary_col_name):

    # st.markdown("<br><br><br><h2>Trades</h2> <hr>", unsafe_allow_html=True)
    st.markdown("<h2>Trades</h2> <hr>", unsafe_allow_html=True)

    cols_list = [st.columns([3,1]) for i in range(len(trades))]

    # show trades
    for i, trade in enumerate(trades):

        with cols_list[i][0]:
            # player1_salary = df_players[df_players['Full Name'] == trade['player_1']][salary_col_name].values[0]
            # player2_salary = df_players[df_players['Full Name'] == trade['player_2']][salary_col_name].values[0]
            player1_salary = new_player_salaries[trade['player_1']]
            player2_salary = new_player_salaries[trade['player_2']]
            # salary_diff = np.abs(player1_salary - player2_salary)

            st.markdown(f"<h4>Trade {i+1}</h4>", unsafe_allow_html=True)
            text = "<p>"
            # text += f"{trade['team_1']}: <b>{trade['player_1']}</b> ({player1_salary}) <br>"
            # text += f"{trade['team_2']}: <b>{trade['player_2']}</b> ({player2_salary})"
            text += f"<b style='color:green'>{trade['team_1']}</b> trades <b style='color:orange'>{trade['player_1']}</b> ({player1_salary}) to <b style='color:green'>{trade['team_2']}</b> for <b style='color:orange'>{trade['player_2']}</b> ({player2_salary})"
            # text += f"<br>Salary Change: {salary_diff}"
            t1_colour = 'green' #if player1_salary - player2_salary > 0 else 'deeppink'
            t2_colour = 'green' #if player2_salary - player1_salary > 0 else 'deeppink'
            # text += f"<br>Salary Change: {np.abs(player1_salary - player2_salary)}"
            # make the number orange
            text += f"<br>Salary Change: <span style='color:orange'>{np.abs(player2_salary - player1_salary)}</span>"
            # text += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;{trade['team_1']}: <span style='color:{t1_colour}'>{player2_salary - player1_salary}</span>"
            # text += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;{trade['team_2']}: <span style='color:{t2_colour}'>{player1_salary - player2_salary}</span>"
            # text += f"<br>Standard Deviation: {trade['team_costs_std']:.2f}"
            # text += f"<br>Team 1 Happiness Change: {trade['team1_happiness_change']}"
            # text += f"<br>Team 2 Happiness Change: {trade['team2_happiness_change']}"

            # text += f"<br>Team 1 Bid for Player Received - Bid for Player Traded Away: {trade['team1_happiness_change']}"
            # text += f"<br>Team 2 Bid for Player Received - Bid for Player Traded Away: {trade['team2_happiness_change']}"
            t1_colour = 'green' if trade['team1_happiness_change'] > 0 else 'red'
            t2_colour = 'green' if trade['team2_happiness_change'] > 0 else 'red'
            text += f"<br>Bid for Player Received minus Bid for Player Traded Away:"
            text += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;{trade['team_1']}: <span style='color:{t1_colour}'>{trade['team1_happiness_change']}</span>"
            text += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;{trade['team_2']}: <span style='color:{t2_colour}'>{trade['team2_happiness_change']}</span>"
            
            
            # if its positive, make it green
            if trade['happiness_change'] > 0:
                text += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;Total Change: <span style='color:green'>{trade['happiness_change']}</span>"
            # if its negative, make it red
            elif trade['happiness_change'] < 0:
                text += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;Total Change: <span style='color:red'>{trade['happiness_change']}</span>"
            else:
                text += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;Total Change: {trade['happiness_change']}"

            text += f"</p>"
            st.markdown(text, unsafe_allow_html=True)
            st.markdown('<br><br>', unsafe_allow_html=True)
            st.markdown('<hr>', unsafe_allow_html=True)

        with cols_list[i][1]:
            # show sum of salaries of all teams
            st.markdown(f"<br>New Team Salaries Relative To Average:", unsafe_allow_html=True)
            avg_team_cost = int(sum(trade['team_costs'].values()) / len(trade['team_costs']))
            # sort team_costs from largest to smallest
            team_costs = {k: v for k, v in sorted(trade['team_costs'].items(), key=lambda item: item[1], reverse=True)}
            txt = ''
            for team_name in team_costs.keys():
                # team_colour = 'orange' if team_costs[team_name] - avg_team_cost > 0 else 'deeppink'
                # team_colour = 'orange' if team_name == trade['team_1'] else 'black'
                # team_colour = 'deeppink' if team_name == trade['team_2'] else 'black'
                if team_name == trade['team_1']:
                    team_colour = 'orange'
                elif team_name == trade['team_2']:
                    team_colour = 'deeppink'
                else:
                    team_colour = 'black'
                # st.markdown(f"<b style='color:{team_colour}'>{team_name}</b>: {team_costs[team_name] - avg_team_cost}", unsafe_allow_html=True)
                if team_colour!= 'black':
                    txt += f"<b style='color:{team_colour}'>{team_name}</b>: {team_costs[team_name] - avg_team_cost}<br>"
                else:
                    txt += f"{team_name}: {team_costs[team_name] - avg_team_cost}<br>"
            st.markdown(txt, unsafe_allow_html=True)











def make_likeness_matrix(team_costs, player_bids, rosters, avg_team_cost, starting_rosters=None):

    # sort team_costs into same order as starting_rosters
    if starting_rosters is not None:
        new_team_costs = {}
        for team_name in starting_rosters.keys():
            new_team_costs[team_name] = team_costs[team_name]
        team_costs = new_team_costs

    # make a matrix of how much each team likes another team
    # so for each team, sum the bids of the players on the other teams
    likeness_matrix = {}
    for team_name in team_costs.keys():
        likeness_matrix[team_name] = {}
        for other_team in team_costs.keys():
            likeness_matrix[team_name][other_team] = 0
            for player_name in rosters[other_team]:
                # print (player_name, team_name, player_bids[player_name][team_name])
                likeness_matrix[team_name][other_team] += player_bids[player_name][team_name]
    
    # print (likeness_matrix)
    # print (avg_team_cost)
    # shift matrix down by avg salary
    for team_name in team_costs.keys():
        for other_team in team_costs.keys():
            likeness_matrix[team_name][other_team] -= avg_team_cost

    st.markdown("<hr>", unsafe_allow_html=True)
    # st.markdown('Likeness Matrix', unsafe_allow_html=True)
    st.markdown("This matrix shows how much each team likes each other team.<br>The number is how much the team on the row is bidding for players from the team in the column, minus the average salary.<br>Positive numbers mean the team likes the other team, negative numbers mean the team isn't interested in the players on the other team.", unsafe_allow_html=True)
    likeness_matrix_df = pd.DataFrame.from_dict(likeness_matrix, orient='index')
    # st.table(likeness_matrix_df)
    
    fig, ax = plt.subplots()
    ax.matshow(likeness_matrix_df, cmap='coolwarm')
    # add numbers to the matrix
    for i in range(len(team_costs)):
        for j in range(len(team_costs)):
            ax.text(j, i, f"{likeness_matrix_df.iloc[i, j]:.0f}", ha='center', va='center', color='black', fontsize=4)
    # add a border around the diagonal squares
    for i in range(len(team_costs)):
        ax.add_patch(plt.Rectangle((i-0.5, i-0.5), 1, 1, fill=False, edgecolor='black', lw=1))

    ax.set_xticks(range(len(team_costs)))
    ax.set_yticks(range(len(team_costs)))
    short_team_names = [team_name[:7] for team_name in team_costs.keys()]
    ax.set_xticklabels(short_team_names)
    ax.set_yticklabels(short_team_names)
    plt.xticks(rotation=90)
    # smaller font size
    plt.xticks(fontsize=5)
    plt.yticks(fontsize=5)
    # chagne font style to not serif
    plt.xticks(fontname='serif')
    plt.yticks(fontname='serif')
    # plt.show()
    # st.pyplot(fig, use_container_width=False)
    #make figure smaller
    fig.set_size_inches(3, 3)
    st.pyplot(fig, use_container_width=False)




    # second matrix
    if starting_rosters is not None:
        # show change in likeness matrix from starting to ending roster
        starting_likeness_matrix = {}
        for team_name in team_costs.keys():
            starting_likeness_matrix[team_name] = {}
            for other_team in team_costs.keys():
                starting_likeness_matrix[team_name][other_team] = 0
                for player_name in starting_rosters[other_team]:
                    starting_likeness_matrix[team_name][other_team] += player_bids[player_name][team_name]
        # shift matrix down by avg salary
        for team_name in team_costs.keys():
            for other_team in team_costs.keys():
                starting_likeness_matrix[team_name][other_team] -= avg_team_cost

        # st.markdown('Change in Likeness Matrix', unsafe_allow_html=True)
        st.markdown("This matrix shows how much each team's interest in each other team has changed from the starting rosters to the ending rosters.<br>The diagonal squares show how much each team thinks it has improved or worsened.", unsafe_allow_html=True)
        change_in_likeness_matrix = {}
        for team_name in team_costs.keys():
            change_in_likeness_matrix[team_name] = {}
            for other_team in team_costs.keys():
                change_in_likeness_matrix[team_name][other_team] = likeness_matrix[team_name][other_team] - starting_likeness_matrix[team_name][other_team]
        
        change_in_likeness_matrix_df = pd.DataFrame.from_dict(change_in_likeness_matrix, orient='index')
        # st.table(change_in_likeness_matrix_df)
        fig, ax = plt.subplots()
        ax.matshow(change_in_likeness_matrix_df, cmap='coolwarm')
        # add numbers to the matrix
        for i in range(len(team_costs)):
            for j in range(len(team_costs)):
                ax.text(j, i, f"{change_in_likeness_matrix_df.iloc[i, j]:.0f}", ha='center', va='center', color='black', fontsize=4)
        # add a border around the diagonal squares
        for i in range(len(team_costs)):
            ax.add_patch(plt.Rectangle((i-0.5, i-0.5), 1, 1, fill=False, edgecolor='black', lw=1))


        ax.set_xticks(range(len(team_costs)))
        ax.set_yticks(range(len(team_costs)))
        short_team_names = [team_name[:7] for team_name in team_costs.keys()]
        ax.set_xticklabels(short_team_names)
        ax.set_yticklabels(short_team_names)
        plt.xticks(rotation=90)
        # smaller font size
        plt.xticks(fontsize=5)
        plt.yticks(fontsize=5)
        # chagne font style to not serif
        plt.xticks(fontname='serif')
        plt.yticks(fontname='serif')
        # plt.show()
        # st.pyplot(fig, use_container_width=False)
        #make figure smaller
        fig.set_size_inches(3, 3)
        st.pyplot(fig, use_container_width=False)












def show_starting_info(team_costs, protected_players_dict, starting_rosters, player_bids, cap_ceiling, cap_floor):

    # show table of starting team costs

    team_costs_df = pd.DataFrame.from_dict(team_costs, orient='index', columns=['Salary'])
    # make salary column an int
    team_costs_df['Salary'] = team_costs_df['Salary'].astype(int)
    # sort by salary
    team_costs_df = team_costs_df.sort_values(by='Salary', ascending=False)

    # show avg team cost
    avg_team_cost = int(sum(team_costs.values()) / len(team_costs))


    # add column of dif from avg
    team_costs_df['Diff from Avg'] = team_costs_df['Salary'] - avg_team_cost
    # add column of dif from cap ceiling
    team_costs_df['Diff from Cap Ceiling'] = team_costs_df['Salary'] - cap_ceiling

    def add_colour(row):
        if row['Salary'] > cap_ceiling:
            return ['color: red' for _ in row]
        elif row['Salary'] < cap_floor:
            return ['color: yellow' for _ in row]
        else:
            return ['color: green' for _ in row]

    team_costs_df = team_costs_df.style.apply(add_colour, axis=1)


    cols_0 = st.columns([5,3])
    with cols_0[0]:
        st.markdown(f'Cap Ceiling: {cap_ceiling:,}<br>Avg Team Salary: {avg_team_cost:,}<br>Cap Floor: {cap_floor:,}', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)


        st.markdown('Starting Team Salaries', unsafe_allow_html=True)
        # st.table(team_costs_df)
        st.dataframe(team_costs_df)
   
        # with cols_0[2]:
        #     # display the captain salaries
        #     st.markdown('Captain Salaries', unsafe_allow_html=True)
        #     captain_salaries_df = pd.DataFrame.from_dict(captain_salaries, orient='index', columns=['Salary'])
        #     captain_salaries_df = captain_salaries_df.sort_values(by='Salary', ascending=False)
        #     st.table(captain_salaries_df)

        show_protected_players = 0
        if show_protected_players:
            # show protected players: dict of team_name: list of dicts of 'player_name' and 'value'
            st.markdown('<br>', unsafe_allow_html=True)
            st.markdown('Protected Players', unsafe_allow_html=True)
            # protected_players_dict_text = {team: [f"{player['player_name']} ({player['value']})" for player in protected_players_dict[team]] for team in protected_players_dict}
            # n_protected_players_per_team = sum([len(protected_players_dict[team]) for team in protected_players_dict]) / len(protected_players_dict)
            # cols_names = [f"Player {i+1} (bid - avg bid)" for i in range(int(n_protected_players_per_team))]
            cols_names = ["Player 1", "Player 2", "Player 3"]
            n_protected_players_per_team = 3
            # protected_players_dict_text = {team: [f"{player['player_name']}" for player in protected_players_dict[team]] for team in protected_players_dict}
            protected_players_for_df = {}
            for team in protected_players_dict:
                # protected_players_for_df[team] = [player['player_name'] for player in protected_players_dict[team]]
                protected_players_for_df[team] = [player_name for player_name in protected_players_dict[team]]
                while len(protected_players_for_df[team]) < n_protected_players_per_team:
                    protected_players_for_df[team].append('')
            protected_players_df = pd.DataFrame.from_dict(protected_players_for_df, orient='index', columns=cols_names)
            st.table(protected_players_df)


    # show matrix of how much each team likes each other team
    make_likeness_matrix(team_costs, player_bids, starting_rosters, avg_team_cost)















def show_end_info(team_costs, count_team_trades, trades, player_bids, rosters, starting_rosters, original_team_costs, cap_ceiling, cap_floor):




    
    team_costs_df = pd.DataFrame.from_dict(team_costs, orient='index', columns=['Salary'])

    # add trade count to row
    count_team_trades_df = pd.DataFrame.from_dict(count_team_trades, orient='index', columns=['Trade Count'])
    team_costs_df['Trade Count'] = count_team_trades_df['Trade Count']
    # make salary column an int
    team_costs_df['Salary'] = team_costs_df['Salary'].astype(int)
    # sort by salary
    team_costs_df = team_costs_df.sort_values(by='Salary', ascending=False)

    
    avg_team_cost = int(sum(team_costs.values()) / len(team_costs))

    st.markdown(f'Cap Ceiling: {cap_ceiling:,}<br>Avg Team Salary: {avg_team_cost:,}<br>Cap Floor: {cap_floor:,}', unsafe_allow_html=True)


    # add column of dif from avg
    team_costs_df['Diff from Avg'] = team_costs_df['Salary'] - avg_team_cost

    # add column of salary dif from original
    team_costs_df['Change in Salary'] = [team_costs[team] - original_team_costs[team] for team in team_costs.keys()]

    # add column of dif from cap ceiling
    team_costs_df['Diff from Cap Ceiling'] = team_costs_df['Salary'] - cap_ceiling

    # reorder columns, salary, diff from avg, trade count
    team_costs_df = team_costs_df[['Salary', 'Diff from Avg', 'Diff from Cap Ceiling', 'Change in Salary', 'Trade Count']]

    # add colour to the table
    def add_colour(row):
        if row['Salary'] > cap_ceiling:
            return ['color: red' for _ in row]
        elif row['Salary'] < cap_floor:
            return ['color: yellow' for _ in row]
        else:
            return ['color: green' for _ in row]

    team_costs_df = team_costs_df.style.apply(add_colour, axis=1)


    st.markdown('New Team Salaries', unsafe_allow_html=True)
    cols = st.columns([5,1])
    with cols[0]:
        # st.table(team_costs_df)
        st.dataframe(team_costs_df)
    


    st.markdown(f'<br>', unsafe_allow_html=True)
    st.markdown(f'Average Team Salary: {avg_team_cost}', unsafe_allow_html=True)

    total_trades = len(trades)
    st.markdown(f'Number of Trades: {total_trades}', unsafe_allow_html=True)

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


    # Total score sum
    total_score_sum = 0
    for trade in trades:
        total_score_sum += trade['highest_score']
    st.markdown(f'Trade Score Sum: {total_score_sum}', unsafe_allow_html=True)





    # show matrix of how much each team likes each other team
    make_likeness_matrix(team_costs, player_bids, rosters, avg_team_cost, starting_rosters)








# def normalize(player_bids, player_salaries, rosters):

#     # NORMALIZATION
#     # Avg player salary
#     avg_player_salary = np.mean(list(player_salaries.values()))
#     # print (f"\nAvg player salary: {avg_player_salary}")
#     # Make the avg salary of the league be max_salary / 2, so scale all salaries by this factor
    
#     # scale = max_salary / 2 / avg_player_salary
#     max_salary = st.session_state['max_salary']
#     desired_avg_salary = max_salary /2 #200
#     scale = desired_avg_salary / avg_player_salary
#     # print (f"Scaling salaries by {scale:.2f}")
#     # round to nearest integer
#     player_salaries = {k: round(v * scale) for k, v in player_salaries.items()}
#     # scale bids as well
#     player_bids = {k: {team: round(v * scale) for team, v in bids.items()} for k, bids in player_bids.items()}
#     # Cap salaries at max_salary
#     new_player_salaries = {k: min(v, max_salary) for k, v in player_salaries.items()}
#     # print (f"new avg player salary: {np.mean(list(new_player_salaries.values()))}\n")
#     # Cap bids at max_salary
#     player_bids = {k: {team: min(v, max_salary) for team, v in bids.items()} for k, bids in player_bids.items()}
#     original_team_costs = calc_teams_salaries(rosters, new_player_salaries)
#     return player_bids, new_player_salaries, original_team_costs




# def show_player_salaries(player_salaries, player_bids):
#     salarylist = list(player_salaries.values())
#     max_salary = np.max(salarylist)
#     min_salary = np.min(salarylist)
#     avg_salary = np.mean(salarylist)
#     st.markdown(f"Max Salary: {max_salary}<br>Avg Salary: {round(avg_salary)}<br>Min Salary: {min_salary}", unsafe_allow_html=True)

#     # remove Wildcards from list
#     player_salaries2 = {k: v for k, v in player_salaries.items() if 'WILD' not in k}

#     player_salaries_df = pd.DataFrame.from_dict(player_salaries2, orient='index', columns=['Salary'])
#     player_salaries_df = player_salaries_df.sort_values(by='Salary', ascending=False)
#     # Make first column be called 'Player'
#     player_salaries_df = player_salaries_df.reset_index()
#     player_salaries_df = player_salaries_df.rename(columns={'index': 'Player'})

#     # add a column of the bids for each player
#     player_bids_2 = {}
#     for player, bids in player_bids.items():
#         player_bids_2[player] = [bid for bid in bids.values()]
#     # sort each list of bids
#     player_bids_2 = {k: sorted(v) for k, v in player_bids_2.items()}
#     player_salaries_df['Bids'] = player_salaries_df['Player'].apply(lambda x: player_bids_2[x])

#     # add column of the std of the bids
#     player_salaries_df['Standard Deviation'] = player_salaries_df['Bids'].apply(lambda x: round(np.std(x),1))

#     st.table(player_salaries_df)




# def get_captain_salaries(stss, df_players, player_salaries, captains):
#     # print (stss['df_league'].columns)
#     # for each captain, we need to use linear regression to predict their salary given their stats
#     # then set everyones bid to that value
    
#     # get stats + salary of all non-captain players
#     # get salary from new_player_salaries
#     # get stats from stss['df_league']

#     # get stats of all players, except captains
#     df_players_no_captains = df_players[~df_players['Full Name'].isin(captains)]
#     # remove wildcards
#     df_players_no_captains = df_players_no_captains[~df_players_no_captains['Full Name'].str.contains('WILD')]
#     # convert to dict
#     df_players_no_captains = df_players_no_captains.set_index('Full Name').T.to_dict()
    
    


#     # for i, row in stats_df.iterrows():
#     #     if 'Gary' in row['Name']:
#     #         print (row)
#     #         fasdf

#     # # confirm stats_df has all the players of df_players_no_captains
#     # for player in df_players_no_captains.keys():
#     #     if player not in stats_df['Name'].values:
#     #         raise Exception(f'{player} not in stats_df')
        
#     if 'df_league' not in stss:
#         get_league_data(stss)


#     stats_df = stss['df_league']
#     stats_keys = ['G', 'A', '2A', 'D', 'TA', 'RE']
#     new_df_players_no_captains = {}
#     for player_name, v in df_players_no_captains.items():
#         stats = stats_df[stats_df['Name'] == player_name]
#         # check for nan values
#         skip_person = False
#         for key in stats_keys:
#             # print (stats[key].values)
#             if np.isnan(float(stats[key].values[0])):
#                 skip_person = True
#                 break
#         if skip_person:
#             continue

#         # if 'Jenni' in k:
#         #     print (stats)
#         #     fasdf


#         new_df_players_no_captains[player_name] = {}
#         for stat_key in stats_keys:
#             # print (stats[key].values)
#             stat_value = stats[stat_key].values[0]
#             new_df_players_no_captains[player_name][stat_key] = float(stat_value)
#             new_df_players_no_captains[player_name]['Salary'] = player_salaries[player_name]
#         # print (new_df_players_no_captains[player_name])
#         # fasd
    
#     # for k, v in df_players_no_captains.items():
#     #     print (k, v)
#     #     fasdfa

#     # print (len(new_df_players_no_captains))
#     # # find nans
#     # for k, v in df_players_no_captains.items():
#     #     print (k,v)
#     #     if np.isnan(v['G']):
#     #         print (k)


#     # make a matrix from df_players_no_captains
#     df_players_no_captains = pd.DataFrame.from_dict(new_df_players_no_captains, orient='index')
#     # print (len(df_players_no_captains))
#     X = df_players_no_captains[stats_keys]
#     # print (len(X))
#     y = df_players_no_captains['Salary']

#     X = X.values#.reshape(-1, 1) # reshape to 2d array
#     y = y.values.reshape(-1, 1) # reshape to 2d array
#     # print (X)
#     # print (y)

#     # print (X.shape, y.shape)
#     model = LinearRegression().fit(X, y) 

#     # print (f"Learned model: {model.coef_} {model.intercept_}")

#     # predict salary for each captain
#     captain_salaries = {}
#     for captain_name in captains:
#         stats = stats_df[stats_df['Name'] == captain_name]
#         stats = stats[stats_keys]
#         stats = stats.values.reshape(1, -1)
#         # print (stats.shape)
#         salary = model.predict(stats)
#         # print (f'{captain_name} predicted salary: {salary[0][0]}')
#         # round to nearest integer
#         captain_salaries[captain_name] = round(salary[0][0])

#     return captain_salaries






# def compute_player_salaries(player_bids, protected_players_dict):
#     """
#     salary is mean of bids
#     BUT if the player is protected, remove the bid from their team

#     player_bids: player_name: {team: bid}
#     """

#     player_salaries = {}
#     # player_bids_copy = player_bids.copy()
#     for player_name, bids in player_bids.items():
#         player_bids = []
#         for team, bid in bids.items():
#             # if the player is protected, remove the bid
#             this_team_protected_players = [player['player_name'] for player in protected_players_dict[team]]
#             if player_name in this_team_protected_players:
#                 # print (f"{player_name} is protected by {team}")
#                 continue
#             player_bids.append(bid)
#         player_salaries[player_name] = round(np.mean(player_bids))

#     return player_salaries























def calc_teams_salaries(rosters, new_player_salaries):
    # calcutte new team costs
    # team_costs = {}
    # for team_name in team_names:
    #     team_costs[team_name] = 0
    #     for player in rosters[team_name]:
    #         salary = df_players[df_players['Full Name'] == player][salary_col_name].values[0]
    #         team_costs[team_name] += salary
    team_costs = {}
    for team_name, roster in rosters.items():
        team_costs[team_name] = 0
        for player_name in roster:
            # print (player_name)
            team_costs[team_name] += new_player_salaries[player_name]
    # sort largest to smallest
    team_costs = {k: v for k, v in sorted(team_costs.items(), key=lambda item: item[1], reverse=True)}
    return team_costs




def convert_col_to_int(df, col):
    df[col] = df[col].str.replace('$', '', regex=False)
    df[col] = df[col].str.replace(',', '')
    df[col] = df[col].astype(int)
    return df



def load_league_data(client, tpl_url):
    worksheet = 'League'
    skiprows = 8    
    spreadsheet = client.open_by_url(tpl_url)
    sheet = spreadsheet.worksheet(worksheet)
    values = sheet.get_all_values()
    values = values[skiprows:]
    df = pd.DataFrame(values[2:], columns=values[1])
    df = convert_col_to_int(df, 'Cap Impact')
    df['First'] = df['First'].str.strip()
    df['Last'] = df['Last'].str.strip()
    df['Full Name'] = df['First'] + ' ' + df['Last']
    df = df[['Full Name', 'Team', 'Cap Impact', 'Gender']]
    return df

def load_league_data_from_path(league_path):
    df = pd.read_csv(league_path)
    df = convert_col_to_int(df, 'Cap Impact')
    df['First'] = df['First'].str.strip()
    df['Last'] = df['Last'].str.strip()
    df['Full Name'] = df['First'] + ' ' + df['Last']
    df = df[['Full Name', 'Team', 'Cap Impact', 'Gender']]
    return df


def load_standings_data(client, tpl_url):
    worksheet = 'Standings'
    # skiprows = 0
    spreadsheet = client.open_by_url(tpl_url)
    sheet = spreadsheet.worksheet(worksheet)
    values = sheet.get_all_values()
    df_Standings = pd.DataFrame(values[2:], columns=values[1])
    # cap_floor = df.iloc[20]['Cap Status']
    # cap_floor = cap_floor.replace('$', '').replace(',', '')
    # cap_floor = cap_floor.split('.')[0]
    # cap_floor = int(cap_floor)
    # df_Standings['Cap Floor'] = cap_floor
    # df_Standings = df_Standings.iloc[:8] # only keep the rows of the standings
    # df_Standings = convert_col_to_int(df_Standings, 'Over/under')
    # df_Standings = convert_col_to_int(df_Standings, 'Salary')
    df_Standings['Team'] = df_Standings['Team'].apply(no_emoji)
    # only keep the columns we need: Team, Salary, Cap Status
    df_Standings = df_Standings[['Team', 'Salary', 'Cap Status']]
    return df_Standings



def load_standings_data_from_path(standings_path):
    df_Standings = pd.read_csv(standings_path)
    df_Standings['Team'] = df_Standings['Team'].apply(no_emoji)

    # print (df_Standings.columns)
    # print (df_Standings['Salary'])
    # print (df_Standings['Cap Floor'])
    # print (df_Standings['Over/under'])
    
    # Get the cap floor and cap ceiling
    for team_i in range(1):
        # print (team_i)
        # extract the cap floor and cap ceiling
        # just need first row, take salary and compare to over/under
        first_team_salary = df_Standings.iloc[team_i]['Salary']
        # convert to int
        first_team_salary = first_team_salary.replace('$', '').replace(',', '')
        first_team_salary = int(first_team_salary)
        # print (first_team_salary)
        first_team_over_under = df_Standings.iloc[team_i]['Over/under']
        # convert to int
        first_team_over_under = first_team_over_under.replace('$', '').replace(',', '')
        first_team_over_under = int(first_team_over_under)
        # print (first_team_over_under)
        cap_ceiling = first_team_salary - first_team_over_under
        # print (cap_ceiling)
        # extract the cap floor
        first_team_cap_floor = df_Standings.iloc[team_i]['Cap Floor']
        # convert to int
        # first_team_cap_floor = first_team_cap_floor.replace('$', '').replace(',', '')
        first_team_cap_floor = int(first_team_cap_floor)
        # print (first_team_cap_floor)
        cap_floor = cap_ceiling + first_team_cap_floor
        # print (cap_floor)
        break



    # only keep the columns we need: Team, Salary, Cap Status
    df_Standings = df_Standings[['Team', 'Salary']] #, 'Cap Status']]
    return df_Standings, cap_ceiling, cap_floor










def get_gsheets_in_folder(drive_service, folder_id):
    """ Search for Google Sheets files in the given folder """
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files


def extract_bid_info(data):
    # total_bid_cell = [1,2]
    # within_range_cell = [1,3]
    # total_bid = data[total_bid_cell[0]][total_bid_cell[1]]
    # within_range = data[within_range_cell[0]][within_range_cell[1]]
    # print (f"\nTotal bid: {total_bid}")
    # print (f"Within range: {within_range}\n")

    player_rows = [6,19]
    name_col = 0
    first_bid_col = 3
    bid_col_interval = 6
    n_teams = 8
    bids = {} # player_name: bid
    for team_i in range(n_teams):
        for player_row in range(player_rows[0], player_rows[1]+1):
            cur_name_col = name_col + team_i*bid_col_interval
            # print (team_i, player_row, cur_name_col)
            # print (f"len(data) = {len(data)}")
            # print (f"len(data[player_row]) = {len(data[player_row])}")

            player_name = data[player_row][cur_name_col]
            # bid plus salary
            player_bid = data[player_row][first_bid_col + bid_col_interval*team_i]
            try:
                player_bid = int(player_bid)
            except:
                # print (f"Error with {player_name} - {player_bid}")
                # take their salary, ignore the bid
                player_bid = data[player_row][first_bid_col + bid_col_interval*team_i - 2]
                player_bid = int(player_bid)
                # print (f"Using salary: {player_bid}")
            bids[player_name] = player_bid
            # print (team_i, player_name, player_bid)
    # print (f"Number of players: {len(bids)}")

    protected_players_col = 4
    protected_players = []
    for player_row in range(player_rows[0], player_rows[1]+1):
        player_name = data[player_row][name_col]
        value = data[player_row][protected_players_col]
        try:
            lowercase_value = value.lower()
            if lowercase_value == 'y':
                protected_players.append(player_name)
        except:
            pass
    # print (f"Protected players: {protected_players}\n")
    return bids, protected_players

















def algo_page():

    # debug = 1

    stss = st.session_state

    run_algo_button = st.button('Run Algo')
    if run_algo_button:
    # if 1:

        # only load previous data if in debug mode
        if 'team_bids' not in stss: # or 1: # or not debug:
            with st.spinner("Loading Data"): #, show_time=True):
                print ("Loading data...")

                client = stss['client']
                drive_service = stss['drive_service']


                # # Load league data
                # tpl_url = "https://docs.google.com/spreadsheets/d/18I5ljv7eL6E8atN7Z6w9wmm6CBwOGsStmW5UJNB0rrg/edit?gid=9#gid=9"
                # print (f"Loading league data")
                # df_League = load_league_data(client, tpl_url)
                # # print (len(df_League))
                # # print (df_League.columns)
                # # Load standings data
                # print (f"Loading standings data")
                # df_Standings = load_standings_data(client, tpl_url)
                # # print (len(df_Standings))
                # # print (df_Standings.columns)



                # Load from path instead
                # league_path = "/Users/chriscremer/code/TPL/streamlit_site/saved_data/League_page.csv"
                # standings_path = "/Users/chriscremer/code/TPL/streamlit_site/saved_data/Standings_page.csv"
                # When in streamlit cloud, path needs to be different
                # league_path = "saved_data/League_page.csv"
                # standings_path = "saved_data/Standings_page.csv"
                # make the path relative to this file
                this_dir = os.path.dirname(os.path.abspath(__file__))
                next_dir = os.path.dirname(this_dir)
                league_path = os.path.join(next_dir, "saved_data/League_page.csv")
                standings_path = os.path.join(next_dir, "saved_data/Standings_page.csv")
                df_League = load_league_data_from_path(league_path)
                df_Standings, cap_ceiling, cap_floor = load_standings_data_from_path(standings_path)

                                
                
                
                

                # Load each team's bids
                # folder_id = '1LycfBlMWQNsCB9rmKEtZwqCvo1jXIJ6N'
                folder_id = "12XTqjwaAW_UsuXcpcE5AiY1nMQj4NhDF" # nov 2025, week 4
                existing_sheets = get_gsheets_in_folder(drive_service, folder_id)
                # print ("Sheets in folder:")
                # for file_name in existing_sheets:
                #     print (file_name)
                # existing_sheet_names = [file['name'] for file in existing_sheets]
                
                
                
                
                


                # import time
                # team_bids = {}
                # for sheet_dict in existing_sheets:
                #     sheet_name = sheet_dict['name']
                #     print (f" - {sheet_name}")
                #     sheet_id = sheet_dict['id']
                #     start_time = time.time()
                #     conn = client.open_by_key(sheet_id)
                #     print (f"Time to load sheet 1: {time.time() - start_time:.2f}")
                #     start_time = time.time()
                #     sheet = conn.get_worksheet(0)
                #     print (f"Time to load sheet 2: {time.time() - start_time:.2f}")
                #     start_time = time.time()
                #     data = sheet.get_all_values()
                #     print (f"Time to load sheet 3: {time.time() - start_time:.2f}")

                #     bids, protected_players = extract_bid_info(data)
                #     team_bids[sheet_name] = {'bids': bids, 'protected_players': protected_players}



                # trying parallel
                def fetch_sheet_data(sheet_dict):
                    sheet_name = sheet_dict['name']
                    sheet_id = sheet_dict['id']
                    conn = client.open_by_key(sheet_id)
                    sheet = conn.get_worksheet(0)
                    data = sheet.get_all_values()
                    # print (f" - {sheet_name}")
                    # bids, protected_players = extract_bid_info(data)
                    return [sheet_name, data]

                
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                    results = executor.map(fetch_sheet_data, existing_sheets)
                results = list(results)

                team_bids = {}
                for result in results:
                    sheet_name, data = result
                    bids, protected_players = extract_bid_info(data)
                    team_bids[sheet_name] = {'bids': bids, 'protected_players': protected_players}

                stss["team_bids"] = team_bids
                stss["df_League"] = df_League
                # stss["df_Standings"] = df_Standings
                stss['cap_ceiling'] = cap_ceiling
                stss['cap_floor'] = cap_floor

        team_bids = stss['team_bids']
        df_League = stss['df_League']
        # df_Standings = stss['df_Standings']

        # for i, (k, v) in enumerate(team_bids.items()):
        #     print (f"\n{k}")
        #     bids = v['bids']
        #     for player, bid in bids.items():
        #         print (player, bid)
        #     fdsa

        print ('ready')

        # captains = [
        #     "Vincent Poon",
        #     "Cat Pelletier",
        #     "Marc Hodges",
        #     "Jamie Hoo-fatt",
        #     "James Ho",
        #     "Vanessa Mensink",
        #     "Ryan Sherriff",
        #     "Alexa Skinner",
        #     "Benjamin St.Louis",
        #     "Sam Esteves",
        #     "Robert Stalker",
        #     "Brendan Howarth",
        #     "Caterina Cazzetta",
        #     "Yubai Liu",
        # ]

        # nov 2025
        captains = [
            "Rebecca Minielly",
            "Nathan Killoran",
            "Robert Stalker",
            "Wendy Chong",
            "Brittany Heath",
            "Patrick Russell",
            "Daniel Quinto",
            "Meagan Newman",
            "Joanne Ukposidolo",
            "Martin Sieniawski",
            "Hailey Murl",
            "Sanjay Parker",
            "Amir Aschner",
            "Daniel Eisner",
            "Helen O'Sullivan",
        ]

        # Make roster dict
        data_league = df_League.to_dict(orient='records')
        # print (f"number of players data_league: {len(data_league)}")
        team_rosters = {}
        for player_dict in data_league:
            team = no_emoji(player_dict['Team'])
            # team = team
            # print (team)
            player_name = player_dict['Full Name']
            if team not in team_rosters:
                team_rosters[team] = []
            team_rosters[team].append(player_name)
        # # Sort each player by Cap Impact
        # for team in team_rosters:
        #     team_rosters[team] = sorted(team_rosters[team], key=lambda x: x['Cap Impact'], reverse=True)
        starting_rosters = team_rosters.copy()
        team_names = list(team_rosters.keys())
        # print (team_names)

        # Player salaries: dict of player_name: salary
        player_salaries = {player['Full Name']: player['Cap Impact'] for player in data_league}
        # Player genders: dict of player_name: gender
        player_genders = {player['Full Name']: player['Gender'] for player in data_league}
        # original_team_costs is sum of all player salaries for each team
        original_team_costs = calc_teams_salaries(team_rosters, player_salaries)
        # protected_players_dict: dict of team_name: list of players that are protected
        protected_players_dict = {team: [] for team in team_names}
        for team in team_bids:
            protected_players_list = team_bids[team]['protected_players']
            # remove captains
            protected_players_list = [player for player in protected_players_list if player not in captains]
            # remove wildcards
            protected_players_list = [player for player in protected_players_list if 'WILD' not in player]
            if len(protected_players_list) > 3:
                protected_players_list = protected_players_list[:2]
            protected_players_dict[team] = protected_players_list
        # player bids: dict of player_name: {team: bid}
        player_bids = {}
        for team in team_bids:
            for player, bid in team_bids[team]['bids'].items():
                if player not in player_bids:
                    player_bids[player] = {}
                player_bids[player][team] = int(bid)
        # print (f"number of players player_bids: {len(player_bids)}")


        with st.spinner("Running Algorithm"):

            # RUN TRADING ALORITHM
            rosters, count_team_trades, trades = run_algo(team_rosters, player_bids, 
                                                        player_genders, captains, 
                                                        player_salaries, protected_players_dict,
                                                        stss['cap_ceiling'], stss['cap_floor'])
            new_team_costs = calc_teams_salaries(rosters, player_salaries)


            # Display info
            with st.expander("Pre Trade Info"):
                show_starting_info(original_team_costs, protected_players_dict, starting_rosters, player_bids, stss['cap_ceiling'], stss['cap_floor'])
            with st.expander("Trades"):
                show_trades(trades, player_salaries)
            with st.expander("Post Trade Info"):
                show_end_info(new_team_costs, count_team_trades, trades, player_bids, rosters, starting_rosters, original_team_costs, stss['cap_ceiling'], stss['cap_floor'])






