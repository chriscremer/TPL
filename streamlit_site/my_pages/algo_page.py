import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

from gspread_dataframe import set_with_dataframe, get_as_dataframe


from utils import get_connection
from data_utils import get_league_data, load_protected_players
from my_pages.bids import get_rosters, get_salaries
from algo4 import run_algo


def get_all_bids_from_sheet(conn, stss, bids_sheet_name, worksheets):
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

    # convert all_player_bids df to player_bids where for each player there is a dict of team: bid
    player_bids = {player: {} for player in player_names}
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


    return player_bids, rosters_team_list, player_genders


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
            t1_colour = 'green' if player1_salary - player2_salary > 0 else 'deeppink'
            t2_colour = 'green' if player2_salary - player1_salary > 0 else 'deeppink'
            text += f"<br>Salary Change:"
            text += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;{trade['team_1']}: <span style='color:{t1_colour}'>{player1_salary - player2_salary}</span>"
            text += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;{trade['team_2']}: <span style='color:{t2_colour}'>{player2_salary - player1_salary}</span>"
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
                likeness_matrix[team_name][other_team] += player_bids[player_name][team_name]

    # shift matrix down by avg salary
    for team_name in team_costs.keys():
        for other_team in team_costs.keys():
            likeness_matrix[team_name][other_team] -= avg_team_cost

    st.markdown("<hr>", unsafe_allow_html=True)
    # st.markdown('Likeness Matrix', unsafe_allow_html=True)
    st.markdown("This matrix shows how much each team likes each other team.<br>The number is how much the team on the row is bidding for players from the team in the column, minus the average salary.<br>Positive numbers mean the team likes the other team, negative numbers mean the team isn't interested in the players on the other team.", unsafe_allow_html=True)
    likeness_matrix_df = pd.DataFrame.from_dict(likeness_matrix, orient='index')
    # st.table(likeness_matrix_df)
    import matplotlib.pyplot as plt
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







def show_starting_info(team_costs, protected_players_dict, starting_rosters, player_bids): #, captain_salaries):

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

    cols_0 = st.columns([5,1,2])
    with cols_0[0]:
        st.markdown('Starting Team Salaries', unsafe_allow_html=True)
        st.table(team_costs_df)
        st.markdown(f'Average Team Salary: {avg_team_cost}', unsafe_allow_html=True)
   
    # with cols_0[2]:
    #     # display the captain salaries
    #     st.markdown('Captain Salaries', unsafe_allow_html=True)
    #     captain_salaries_df = pd.DataFrame.from_dict(captain_salaries, orient='index', columns=['Salary'])
    #     captain_salaries_df = captain_salaries_df.sort_values(by='Salary', ascending=False)
    #     st.table(captain_salaries_df)


    # # show protected players: dict of team_name: list of dicts of 'player_name' and 'value'
    # st.markdown('Protected Players', unsafe_allow_html=True)
    # # protected_players_dict_text = {team: [f"{player['player_name']} ({player['value']})" for player in protected_players_dict[team]] for team in protected_players_dict}
    # # n_protected_players_per_team = sum([len(protected_players_dict[team]) for team in protected_players_dict]) / len(protected_players_dict)
    # # cols_names = [f"Player {i+1} (bid - avg bid)" for i in range(int(n_protected_players_per_team))]
    # cols_names = ["Player 1", "Player 2", "Player 3"]
    # n_protected_players_per_team = 3
    # # protected_players_dict_text = {team: [f"{player['player_name']}" for player in protected_players_dict[team]] for team in protected_players_dict}
    # protected_players_for_df = {}
    # for team in protected_players_dict:
    #     protected_players_for_df[team] = [player['player_name'] for player in protected_players_dict[team]]
    #     while len(protected_players_for_df[team]) < n_protected_players_per_team:
    #         protected_players_for_df[team].append('')


    # protected_players_df = pd.DataFrame.from_dict(protected_players_for_df, orient='index', columns=cols_names)
    # st.table(protected_players_df)


    # show matrix of how much each team likes each other team
    make_likeness_matrix(team_costs, player_bids, starting_rosters, avg_team_cost)



def calc_teams_salaries(rosters, new_player_salaries):
    # calcutte new team costs
    # team_costs = {}
    # for team_name in team_names:
    #     team_costs[team_name] = 0
    #     for player in rosters[team_name]:
    #         salary = df_players[df_players['Full Name'] == player][salary_col_name].values[0]
    #         team_costs[team_name] += salary
    team_costs = {}
    for team_name in rosters:
        team_costs[team_name] = 0
        for player in rosters[team_name]:
            team_costs[team_name] += new_player_salaries[player]
    # sort largest to smallest
    team_costs = {k: v for k, v in sorted(team_costs.items(), key=lambda item: item[1], reverse=True)}
    return team_costs




def show_end_info(team_costs, count_team_trades, trades, player_bids, rosters, starting_rosters, original_team_costs):

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

    # add column of salary dif from original
    team_costs_df['Change in Salary'] = [team_costs[team] - original_team_costs[team] for team in team_costs.keys()]

    # reorder columns, salary, diff from avg, trade count
    team_costs_df = team_costs_df[['Salary', 'Diff from Avg', 'Change in Salary', 'Trade Count']]


    cols = st.columns(2)
    with cols[0]:
        st.table(team_costs_df)
    
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




def show_player_salaries(player_salaries, player_bids):
    salarylist = list(player_salaries.values())
    max_salary = np.max(salarylist)
    min_salary = np.min(salarylist)
    avg_salary = np.mean(salarylist)
    st.markdown(f"Max Salary: {max_salary}<br>Avg Salary: {round(avg_salary)}<br>Min Salary: {min_salary}", unsafe_allow_html=True)

    # remove Wildcards from list
    player_salaries2 = {k: v for k, v in player_salaries.items() if 'WILD' not in k}

    player_salaries_df = pd.DataFrame.from_dict(player_salaries2, orient='index', columns=['Salary'])
    player_salaries_df = player_salaries_df.sort_values(by='Salary', ascending=False)
    # Make first column be called 'Player'
    player_salaries_df = player_salaries_df.reset_index()
    player_salaries_df = player_salaries_df.rename(columns={'index': 'Player'})

    # add a column of the bids for each player
    player_bids_2 = {}
    for player, bids in player_bids.items():
        player_bids_2[player] = [bid for bid in bids.values()]
    # sort each list of bids
    player_bids_2 = {k: sorted(v) for k, v in player_bids_2.items()}
    player_salaries_df['Bids'] = player_salaries_df['Player'].apply(lambda x: player_bids_2[x])

    # add column of the std of the bids
    player_salaries_df['Standard Deviation'] = player_salaries_df['Bids'].apply(lambda x: round(np.std(x),1))

    st.table(player_salaries_df)




def get_captain_salaries(stss, df_players, player_salaries, captains):
    # print (stss['df_league'].columns)
    # for each captain, we need to use linear regression to predict their salary given their stats
    # then set everyones bid to that value
    
    # get stats + salary of all non-captain players
    # get salary from new_player_salaries
    # get stats from stss['df_league']

    # get stats of all players, except captains
    df_players_no_captains = df_players[~df_players['Full Name'].isin(captains)]
    # remove wildcards
    df_players_no_captains = df_players_no_captains[~df_players_no_captains['Full Name'].str.contains('WILD')]
    # convert to dict
    df_players_no_captains = df_players_no_captains.set_index('Full Name').T.to_dict()
    
    


    # for i, row in stats_df.iterrows():
    #     if 'Gary' in row['Name']:
    #         print (row)
    #         fasdf

    # # confirm stats_df has all the players of df_players_no_captains
    # for player in df_players_no_captains.keys():
    #     if player not in stats_df['Name'].values:
    #         raise Exception(f'{player} not in stats_df')
        
    if 'df_league' not in stss:
        get_league_data(stss)


    stats_df = stss['df_league']
    stats_keys = ['G', 'A', '2A', 'D', 'TA', 'RE']
    new_df_players_no_captains = {}
    for player_name, v in df_players_no_captains.items():
        stats = stats_df[stats_df['Name'] == player_name]
        # check for nan values
        skip_person = False
        for key in stats_keys:
            # print (stats[key].values)
            if np.isnan(float(stats[key].values[0])):
                skip_person = True
                break
        if skip_person:
            continue

        # if 'Jenni' in k:
        #     print (stats)
        #     fasdf


        new_df_players_no_captains[player_name] = {}
        for stat_key in stats_keys:
            # print (stats[key].values)
            stat_value = stats[stat_key].values[0]
            new_df_players_no_captains[player_name][stat_key] = float(stat_value)
            new_df_players_no_captains[player_name]['Salary'] = player_salaries[player_name]
        # print (new_df_players_no_captains[player_name])
        # fasd
    
    # for k, v in df_players_no_captains.items():
    #     print (k, v)
    #     fasdfa

    # print (len(new_df_players_no_captains))
    # # find nans
    # for k, v in df_players_no_captains.items():
    #     print (k,v)
    #     if np.isnan(v['G']):
    #         print (k)


    # make a matrix from df_players_no_captains
    df_players_no_captains = pd.DataFrame.from_dict(new_df_players_no_captains, orient='index')
    # print (len(df_players_no_captains))
    X = df_players_no_captains[stats_keys]
    # print (len(X))
    y = df_players_no_captains['Salary']

    X = X.values#.reshape(-1, 1) # reshape to 2d array
    y = y.values.reshape(-1, 1) # reshape to 2d array
    # print (X)
    # print (y)

    # print (X.shape, y.shape)
    model = LinearRegression().fit(X, y) 

    # print (f"Learned model: {model.coef_} {model.intercept_}")

    # predict salary for each captain
    captain_salaries = {}
    for captain_name in captains:
        stats = stats_df[stats_df['Name'] == captain_name]
        stats = stats[stats_keys]
        stats = stats.values.reshape(1, -1)
        # print (stats.shape)
        salary = model.predict(stats)
        # print (f'{captain_name} predicted salary: {salary[0][0]}')
        # round to nearest integer
        captain_salaries[captain_name] = round(salary[0][0])

    return captain_salaries






def compute_player_salaries(player_bids, protected_players_dict):
    """
    salary is mean of bids
    BUT if the player is protected, remove the bid from their team

    player_bids: player_name: {team: bid}
    """

    player_salaries = {}
    # player_bids_copy = player_bids.copy()
    for player_name, bids in player_bids.items():
        player_bids = []
        for team, bid in bids.items():
            # if the player is protected, remove the bid
            this_team_protected_players = [player['player_name'] for player in protected_players_dict[team]]
            if player_name in this_team_protected_players:
                # print (f"{player_name} is protected by {team}")
                continue
            player_bids.append(bid)
        player_salaries[player_name] = round(np.mean(player_bids))

    return player_salaries














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

        team_names = list(df_players['Team'].unique())
        player_names = df_players['Full Name'].tolist()
        rosters = get_rosters(df_players, team_names)
        max_salary = st.session_state['max_salary']

        player_salaries, latest_week = get_salaries(df_players, player_names, max_salary)
        
        latest_week = 4
        salary_col_name = f"Week {latest_week} - Salary"
        bids_sheet_name = f'Week {latest_week} - Bids'
        protect_sheet_name = f'Week {latest_week} - Protect'
        print (f"\n{bids_sheet_name}")

        protected_players_dict = load_protected_players(conn, protect_sheet_name)

        all_player_bids = get_all_bids_from_sheet(conn, stss, bids_sheet_name, worksheets)
        player_bids, rosters_team_list, player_genders = accumulate_data(rosters, team_names, df_players, salary_col_name, player_names, all_player_bids)

        # compute player salaries by taking the average of the bids
        # player_salaries = {player: round(np.mean(list(bids.values()))) for player, bids in player_bids.items()}
        # player_salaries = compute_player_salaries(player_bids, protected_players_dict)
        # for now keep salaries unchanged
        # just salary to int
        player_salaries = {k: int(v) for k, v in player_salaries.items()}



        # get list of captains
        if 'captains' not in stss:
            captains_sheet = [worksheet for worksheet in worksheets if worksheet.title == 'Captains'][0]
            df_captains = get_as_dataframe(captains_sheet)
            stss['captains'] = df_captains['Captain'].tolist()
        captains = stss['captains']

        # # get captain salaries
        # captain_salaries = get_captain_salaries(stss, df_players, player_salaries, captains)
        # # make all bids for the captains be their predicted salary
        # for captain in captains:
        #     player_bids[captain] = {team: captain_salaries[captain] for team in team_names}
        #     player_salaries[captain] = captain_salaries[captain]

        # normalize salaries and bids
        # player_bids, new_player_salaries, original_team_costs = normalize(player_bids, player_salaries, rosters)
        new_player_salaries = player_salaries
        original_team_costs = calc_teams_salaries(rosters, new_player_salaries)
        # sort roster into the same order as original_team_costs, so highest to lowest salary
        rosters = {k: v for k, v in sorted(rosters.items(), key=lambda item: original_team_costs[item[0]], reverse=True)}
        starting_rosters = rosters.copy()

        # RUN TRADING ALORITHM
        rosters, count_team_trades, trades = run_algo(rosters_team_list, player_bids, player_genders, captains, new_player_salaries, protected_players_dict)
        new_team_costs = calc_teams_salaries(rosters, new_player_salaries)


        # Display info
        with st.expander("Pre Trade Info"):
            show_starting_info(original_team_costs, protected_players_dict, starting_rosters, player_bids) #, captain_salaries)
        # with st.expander("Player Salaries"):
        #     show_player_salaries(new_player_salaries, player_bids)
        with st.expander("Trades"):
            show_trades(trades, new_player_salaries)
        with st.expander("Post Trade Info"):
            show_end_info(new_team_costs, count_team_trades, trades, player_bids, rosters, starting_rosters, original_team_costs)






