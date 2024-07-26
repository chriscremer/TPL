"""
streamlit run streamlit/st.py
"""

print ('--------------')

import streamlit as st
import pandas as pd
import numpy as np
import random
import os
import sys

# to deal with ModuleNotFoundError: No module named 'SVA'
# sys.path.append(os.getcwd())
# from SVA.Z_other_code.colours import blue, red, underline, magenta, cyan, bold, green, yellow




# make it wide
st.set_page_config(page_title="TPL", layout="wide", page_icon="🎯")

random.seed(0)

n_teams = 10
n_players = n_teams  *14
max_salary = 500


# convert number to letter
def number_to_letter(n):
    return chr(n + 65)
team_names = [number_to_letter(i) for i in range(n_teams)]

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

# for team, roster in rosters.items():
#     print (f"{team}: {roster}")
# print ()





def compute_player_salaries(rosters, player_bids):
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



def get_team_costs(rosters, player_salaries):
    team_costs = {team: 0 for team in team_names}
    for team, roster in rosters.items():
        for player in roster:
            team_costs[team] += player_salaries[player]
    # sort by cost
    team_costs = {k: v for k, v in sorted(team_costs.items(), key=lambda item: item[1], reverse=True)} 
    return team_costs


def trade(rosters, team_1, player_1, team_2, player_2):
    new_team_1_roster = [player_2 if player == player_1 else player for player in rosters[team_1]]
    new_team_2_roster = [player_1 if player == player_2 else player for player in rosters[team_2]]
    # update rosters
    new_rosters = {team: rosters[team].copy() for team in team_names}
    new_rosters[team_1] = new_team_1_roster
    new_rosters[team_2] = new_team_2_roster

    # # print trade
    # salary_1 = player_salaries[player_1]
    # salary_2 = player_salaries[player_2]
    # salary_diff = salary_2 - salary_1
    # print (f"{team_1} trades {player_1} (${player_salaries[player_1]}) to {team_2} for {player_2} (${player_salaries[player_2]}): {salary_diff}")
    return new_rosters


# Trade player 1 from team D to A for player 2
# rosters = trade(rosters, 'D', 1, 'A', 2)


# Compute cost of each team
# Team cost = sum of player costs
# Player Cost = max bid of non-owner team

player_salaries = compute_player_salaries(rosters, player_bids)
team_costs = get_team_costs(rosters, player_salaries)

# print ('\nTeam Costs')
# for team, cost in team_costs.items():
#     print (f"{team}: {cost}")
# print ()










n_teams = len(team_names)
teams_per_row = 3
n_rows = n_teams // teams_per_row
container_list = [st.container() for _ in range(n_rows*2)]
cols_list = [st.columns(teams_per_row) for _ in range(n_rows*2)]

for i, team_name in enumerate(team_names):
    # print (i//teams_per_row, i//teams_per_row +1, i%5, )

    # # to align the last two tables
    # if i >= 8:
    #     i+=1

    with container_list[i//teams_per_row]:
        with cols_list[i//teams_per_row][i%teams_per_row]:
            # st.markdown(team_name, unsafe_allow_html=True)
            # bold font
            st.markdown(f"<center><p style='font-size:20px; font-weight:bold'>{team_name}</p></center>", unsafe_allow_html=True)


    with container_list[i//teams_per_row +1]:
        with cols_list[i//teams_per_row+1][i%teams_per_row]:

            # convert rosters to dataframe
            roster = rosters[team_name]
            team_df = pd.DataFrame(roster, columns=['Player'])
            team_df['Salary'] = [player_salaries[player] for player in roster]
            team_df = team_df.sort_values(by=['Salary'], ascending=False)
            team_df = team_df.reset_index(drop=True)


            # # Color the men blue and women red
            # table_text = "<center><table>"
            # for i, row in team_df.iterrows():
            #     table_text += "<tr>"
            #     player_name = row['Player']
            #     gender = 'Male' if player_name % 2 == 1 else 'Female'
            #     # print (team_df.columns)
            #     for col in team_df.columns:
            #         # if col == 'Gender':
            #         #     continue
            #         if col in ['Player', 'Salary']:
            #             if gender == 'Male':
            #                 table_text += f"<td style='color:#ADD8E6'>{row[col]}</td>"
            #             else:
            #                 table_text += f"<td style='color:#FF69B4'>{row[col]}</td>"
                
            #     # number = st.number_input("Insert a number", value=0, key=f"{team_name}-{player_name}")

            #     table_text += "</tr>"
            # table_text += "</table></center>"
            # st.markdown(table_text, unsafe_allow_html=True)

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













# st.markdown('<br><br>', unsafe_allow_html=True)
# st.markdown('<br><br>', unsafe_allow_html=True)
# st.markdown('<br><br>', unsafe_allow_html=True)
# st.markdown('<br><br>', unsafe_allow_html=True)

# # st.markdown("<h1 style='text-align: center;'>Teams</h1>", unsafe_allow_html=True)
# st.markdown("<h1 style='text-align: left;'>Teams</h1>", unsafe_allow_html=True)
# for team in team_names:
#     st.markdown(f'[{team}](#team-{team.lower()})', unsafe_allow_html=True)
#     # center
#     # st.markdown(f"<center><a href='#team-{team.lower()}'>{team}</a></center>", unsafe_allow_html=True)
# st.markdown('<br><br>', unsafe_allow_html=True)
# # st.markdown('<span name="pookie">hey</span>', unsafe_allow_html=True)

# st.markdown("<h1 style='text-align: left;'>Player Salaries</h1>", unsafe_allow_html=True)

# # cols = [st.columns(2) for i in range(n_teams)]
# for i, team in enumerate(team_names):
#     roster = rosters[team]
#     # sort by salary
#     roster = sorted(roster, key=lambda player: player_salaries[player], reverse=True)
#     st.markdown (f"## Team: {team}", unsafe_allow_html=True)
#     # cols = st.columns([1, 1, 1])
#     containder_list = [st.container() for _ in range(len(roster))]
#     cols_list = [st.columns([1, 1, 1, 1]) for _ in range(len(roster))]
#     for j, player in enumerate(roster):
#         with containder_list[j]:
#             with cols_list[j][0]:
#                 st.markdown(f"Player: {player}<br>Current Salary: ${player_salaries[player]}", unsafe_allow_html=True)
#             with cols_list[j][2]:
#                 if player < 4: # GMs
#                     your_bid = st.slider (f"Player {player}", 0, max_salary, player_salaries[player], label_visibility="hidden", disabled=True)
#                 else:
#                     your_bid = st.slider (f"Player {player}", 0, max_salary, player_salaries[player], label_visibility="hidden")
#             with cols_list[j][1]:
#                 # st.markdown (f"Your Bid: ${your_bid}")
#                 # if bid > current salary then add an up arrow
#                 if your_bid > player_salaries[player]:
#                     st.markdown (f'<br><span style="color: green">↑</span>Your Bid: {your_bid} (+ {your_bid - player_salaries[player]})', unsafe_allow_html=True)
#                 elif your_bid < player_salaries[player]:
#                     st.markdown (f'<br><span style="color: red">↓</span>Your Bid: {your_bid} (- {player_salaries[player] - your_bid})', unsafe_allow_html=True)
#     st.markdown ('---')
