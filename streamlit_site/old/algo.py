"""
python -m SVA.g_TPL.salary_simulator.simulate
python -m streamlit_site.algo
"""

import numpy as np
import random

# from SVA.Z_other_code.colours import blue, red, underline, magenta, cyan, bold, green, yellow
from streamlit_site.utils import blue, cyan, red, magenta, green, yellow, underline, bold, strikethrough, strike


random.seed(0)

n_teams = 10
n_players = 200
max_salary = 500

# convert number to letter
def number_to_letter(n):
    return chr(n + 65)
team_names = [number_to_letter(i) for i in range(n_teams)]


player_names = list(range(1, n_players+1))
player_bids = {player: {} for player in player_names}
for player, bids in player_bids.items():
    for team in team_names:
        bids[team] = random.randint(1, max_salary)

# make some special teams
# team A: all 100 bids
# team B: all avg bids
# team C: all 1 bids
for player, bids in player_bids.items():
    bids['A'] = max_salary
    bids['C'] = 1
    bids['D'] = 2

    # Make high value players and low value players
    if player < 20:
        for team in bids.keys():
            bids[team] = max_salary
    if player > 20 and player < 40:
        for team in bids.keys():
            bids[team] = 1

    bids['B'] = np.mean(list(bids.values()))


# randomly assign players to teams
rosters = {team: [] for team in team_names}
for player in player_names:
    # find all teams with the minimum number of players
    min_players = min([len(rosters[team]) for team in team_names])
    min_teams = [team for team in team_names if len(rosters[team]) == min_players]
    # randomly assign player to one of the teams
    team = random.choice(min_teams)
    rosters[team].append(player)





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


def get_team_self_values(rosters, player_bids):
    # Calculate how much each team thinks its own team is worth
    team_values = {}
    for team, roster in rosters.items():
        for player in roster:
            team_bid = player_bids[player][team]
            team_values[team] = team_values.get(team, 0) + team_bid
    # Sort alphabetically
    team_values = {k: v for k, v in sorted(team_values.items(), key=lambda item: item[0])}
    return team_values

def get_happiness_change(rosters_before, rosters_after, player_bids):
    before_values = get_team_self_values(rosters_before, player_bids)
    after_values = get_team_self_values(rosters_after, player_bids)
    happiness_change_dict = {team: after_values[team] - before_values[team] for team in team_names}
    # avg_happiness_change = np.mean([value for team, value in happiness_change.items()])
    happiness_change = np.sum([value for team, value in happiness_change_dict.items()])
    return happiness_change_dict, happiness_change

def trade(rosters, team_1, player_1, team_2, player_2):
    new_team_1_roster = [player_2 if player == player_1 else player for player in rosters[team_1]]
    new_team_2_roster = [player_1 if player == player_2 else player for player in rosters[team_2]]
    # update rosters
    new_rosters = {team: rosters[team].copy() for team in team_names}
    new_rosters[team_1] = new_team_1_roster
    new_rosters[team_2] = new_team_2_roster
    return new_rosters








player_salaries = compute_player_salaries(rosters, player_bids)
team_costs = get_team_costs(rosters, player_salaries)

print ('\nTeam Costs')
for team, cost in team_costs.items():
    print (f"{team}: {cost}")
print ()

initial_team_values = get_team_self_values(rosters, player_bids)


# How a trade is determined:
# 1. for each team, take the top n players with the highest difference in salary and owner bid
# 2. for each of those players, consider the top m teams with the highest offers
# 3. for each of those teams, consider trading that player with players on the offering team (excluding the top n players on the offering team which they value most relative to league)
# 4. pick the trade that minimizes the standard deviation of team costs

# what its missing: take into account how much a team wants to keep a player in step 3
# even if the offering maxes out a player on their team, they could lose them in step 3
# so: exclude the top n players on the offering team which they value most relative to league 



print ('\n###########################')
print ('Trading algorithm 3')
print ('###########################\n')

n_players_to_consider = 7 # the players you value the least on your team
n_offering_teams_to_consider = 4 # the teams with the highest offers
n_offering_players_to_protect = 3 # the players you value the most on your team
max_trades = 3
count_team_trades = {team: 0 for team in team_names}
prev_team_costs_std = np.std(list(team_costs.values()))
for trade_i in range(n_teams * max_trades // 2):

    possible_trades = []
    for team_1 in team_names:

        # skip if already have 3 trades
        if count_team_trades[team_1] >= max_trades:
            continue

        # sort players on team by difference in offer and owner salary
        players = rosters[team_1]
        player_diffs = {player: player_salaries[player] - player_bids[player][team_1] for player in players}
        player_diffs = {k: v for k, v in sorted(player_diffs.items(), key=lambda item: item[1], reverse=True)}

        # take bot n players with the highest difference in salary and owner bid
        for player_1 in list(player_diffs.keys())[:n_players_to_consider]:

            # Offers from other teams
            offers = {team: player_bids[player_1][team] for team in team_names if team != team_1}
            offers = {k: v for k, v in sorted(offers.items(), key=lambda item: item[1], reverse=True)}

            # Remove offers if already have 3 trades
            offers = {k: v for k, v in offers.items() if count_team_trades[k] < max_trades}
            if len(offers) == 0:
                continue

            # consider top m offering teams
            for offering_team in list(offers.keys())[:n_offering_teams_to_consider]:

                offering_team_roster = rosters[offering_team]
                # exclude the top n players on the offering team which they value most relative to league
                offering_team_player_diffs = {player: player_salaries[player] - player_bids[player][offering_team] for player in offering_team_roster}
                offering_team_player_diffs = {k: v for k, v in sorted(offering_team_player_diffs.items(), key=lambda item: item[1], reverse=True)}
                available_offering_team_players = list(offering_team_player_diffs.keys())[n_offering_players_to_protect:]

                # consider trading this player with players on the offering team
                for player_2 in available_offering_team_players:
                    # trade player 1 from team 1 to team 2 for player 2
                    rosters_before = rosters.copy()
                    temp_rosters = trade(rosters, team_1, player_1, offering_team, player_2)
                    happiness_change_dict, happiness_change = get_happiness_change(rosters_before, temp_rosters, player_bids)
                    team1_happiness_change = happiness_change_dict[team_1]
                    team2_happiness_change = happiness_change_dict[offering_team]
                    # if both teams are worse off, skip
                    if team1_happiness_change <= 0 and team2_happiness_change <= 0:
                        continue

                    # Add trade to possible trades
                    team_costs = get_team_costs(temp_rosters, player_salaries)
                    team_costs_std = np.std(list(team_costs.values()))
                    possible_trades.append((team_1, player_1, offering_team, player_2, team_costs_std))
        
    # sort by team costs std
    possible_trades = sorted(possible_trades, key=lambda x: x[4])
    team_1, player_1, team_2, player_2, team_costs_std = possible_trades[0]
    team_costs_std_diff = prev_team_costs_std - team_costs_std
    prev_team_costs_std = team_costs_std

    # stop if std is not changing much
    if trade_i > 0 and team_costs_std_diff < 0.1:
        break    
    
    salary_diff = player_salaries[player_2] - player_salaries[player_1]
    print (blue(f"Trade {trade_i}: {team_1} trades {player_1} (${player_salaries[player_1]}) to {team_2} for {player_2} (${player_salaries[player_2]}): {salary_diff}"))
    rosters_before = rosters.copy()
    rosters = trade(rosters, team_1, player_1, team_2, player_2)
    happiness_change_dict, happiness_change = get_happiness_change(rosters_before, rosters, player_bids)
    team1_happiness_change = happiness_change_dict[team_1]
    team2_happiness_change = happiness_change_dict[team_2]

    # new team costs
    team_costs = get_team_costs(rosters, player_salaries)
    for team, cost in team_costs.items():
        print (f"{team}: {cost}")

    count_team_trades[team_1] += 1
    count_team_trades[team_2] += 1
    print (f"Team costs std: {team_costs_std:.2f} (dif: {team_costs_std_diff:.2f})")
    print (f"Total team self value change: {happiness_change:.1f}, {team_1}: {team1_happiness_change:.1f}, {team_2}: {team2_happiness_change:.1f}")
    print ('-----------------\n')


















print ('\n######################################')
print ('Team trades:')
for team, count in count_team_trades.items():
    print (f"{team}: {count}")

# Avg player salary
avg_player_salary = np.mean(list(player_salaries.values()))
print (f"\nAvg player salary: {avg_player_salary}")


# Make the avg salary of the league be max_salary / 2, so scale all salaries by this factor
scale = max_salary / 2 / avg_player_salary
print (f"Scaling salaries by {scale:.2f}\n")
# round to nearest integer
player_salaries = {k: round(v * scale) for k, v in player_salaries.items()}

# Cap salaries at max_salary
player_salaries = {k: min(v, max_salary) for k, v in player_salaries.items()}

team_costs = get_team_costs(rosters, player_salaries)
for team, cost in team_costs.items():
    print (f"{team}: {cost}")

avg_player_salary = np.mean(list(player_salaries.values()))
max_salary = max(list(player_salaries.values()))
min_salary = min(list(player_salaries.values()))

print (f"\nMax salary: {max_salary}")
print (f"Min salary: {min_salary}")
print (f"Avg player salary: {avg_player_salary}")


# Calculate how much each team thinks its own team is worth
final_team_values = get_team_self_values(rosters, player_bids)
print ('\nTeam self values difference')
for team, value in final_team_values.items():
    print (f"{team}: {value - initial_team_values[team]:.1f}")
# Avg happiness improvement
happiness_improvement = np.sum([value - initial_team_values[team] for team, value in final_team_values.items()])
print (f"Team self value improvement: {happiness_improvement:.1f}")
print ('######################################\n')



