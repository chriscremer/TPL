"""
python -m streamlit_site.algo2
python streamlit_site/algo2.py
"""

import numpy as np
import random


def get_team_costs(rosters, player_salaries):
    team_names = list(rosters.keys())
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

def get_happiness_change(rosters_before, rosters_after, player_bids, team_names):
    before_values = get_team_self_values(rosters_before, player_bids)
    after_values = get_team_self_values(rosters_after, player_bids)
    happiness_change_dict = {team: after_values[team] - before_values[team] for team in team_names}
    happiness_change = np.sum([value for team, value in happiness_change_dict.items()])
    return happiness_change_dict, happiness_change

def trade(rosters, team_1, player_1, team_2, player_2, team_names):
    new_team_1_roster = [player_2 if player == player_1 else player for player in rosters[team_1]]
    new_team_2_roster = [player_1 if player == player_2 else player for player in rosters[team_2]]
    # update rosters
    new_rosters = {team: rosters[team].copy() for team in team_names}
    new_rosters[team_1] = new_team_1_roster
    new_rosters[team_2] = new_team_2_roster
    return new_rosters





def run_algo(rosters, player_bids, player_genders, captains, player_salaries):

    debug = 1
    random.seed(0)

    # compute salary of each team
    team_costs = get_team_costs(rosters, player_salaries)

    # for each team, find the top n players that they value most relative to the league
    # value: player_bid - avg_bid
    n_players_to_protect = 2
    protected_players = []
    protected_players_dict = {}
    for team, roster in rosters.items():
        player_diffs = {player: player_bids[player][team] - player_salaries[player] for player in roster}
        player_diffs = {k: v for k, v in sorted(player_diffs.items(), key=lambda item: item[1], reverse=True)}
        # remove captains
        player_diffs = {k: v for k, v in player_diffs.items() if k not in captains}
        # remove players that have 'WILD' in their name
        player_diffs = {k: v for k, v in player_diffs.items() if 'WILD' not in k}
        # add top n players to protected players
        protected_players += list(player_diffs.keys())[:n_players_to_protect]
        protected_players_dict[team] = []
        for player in list(player_diffs.keys())[:n_players_to_protect]:
            protected_players_dict[team].append({'player_name': player, 'value': player_diffs[player]})

    # sort protected players by team_costs
    protected_players_dict = {k: v for k, v in sorted(protected_players_dict.items(), key=lambda item: team_costs[item[0]], reverse=True)}


    max_trades = 3 # max trades per team
    min_std_diff = 1 # minimum change in standard deviation of team salaries

    team_names = list(rosters.keys())
    n_teams = len(team_names)
    count_team_trades = {team: 0 for team in team_names} # keep track of number of trades per team
    prev_team_costs_std = np.std(list(team_costs.values()))
    trades = [] # list of trades
    traded_players = [] # avoid trading the same player twice
    for trade_i in range(n_teams * max_trades // 2):

        already_considered_trades = [] # to avoid considering the same trade twice
        possible_trades = []
        for team_1 in team_names:

            # skip if team has already made max_trades
            if count_team_trades[team_1] >= max_trades:
                continue
            
            team_1_players_to_trade = rosters[team_1]
            # remove players that have 'WILD' in their name
            team_1_players_to_trade = [player for player in team_1_players_to_trade if 'WILD' not in player]
            # remove players that have already been traded
            team_1_players_to_trade = [player for player in team_1_players_to_trade if player not in traded_players]
            # remove captains
            team_1_players_to_trade = [player for player in team_1_players_to_trade if player not in captains]
            # remove protected players
            team_1_players_to_trade = [player for player in team_1_players_to_trade if player not in protected_players]

            # shuffle players in case of ties
            random.shuffle(team_1_players_to_trade)

            # consider trading this player with players on other teams
            for player_1 in team_1_players_to_trade:
                # find teams to consider trading to
                teams_to_consider_trading_to = [team for team in team_names if team != team_1]
                player_1_gender = player_genders[player_1]
                for offering_team in teams_to_consider_trading_to:

                    # skip if team has already made max_trades
                    if count_team_trades[offering_team] >= max_trades:
                        continue

                    offering_team_roster = rosters[offering_team]
                    # remove players that have 'WILD' in their name
                    offering_team_roster = [player for player in offering_team_roster if 'WILD' not in player]
                    # only keep players of the same gender
                    offering_team_roster = [player for player in offering_team_roster if player_1_gender == player_genders[player]]
                    # remove players that have already been traded
                    offering_team_roster = [player for player in offering_team_roster if player not in traded_players]
                    # remove captains
                    offering_team_roster = [player for player in offering_team_roster if player not in captains]
                    # remove protected players
                    offering_team_roster = [player for player in offering_team_roster if player not in protected_players]

                    # shuffle players in case of ties
                    random.shuffle(offering_team_roster)

                    # consider trading this player with players on the offering team
                    for player_2 in offering_team_roster:
                        # trade player 1 from team 1 to team 2 for player 2
                        rosters_before = rosters.copy()
                        temp_rosters = trade(rosters, team_1, player_1, offering_team, player_2, team_names)
                        happiness_change_dict, happiness_change = get_happiness_change(rosters_before, temp_rosters, player_bids, team_names)
                        team1_happiness_change = happiness_change_dict[team_1]
                        team2_happiness_change = happiness_change_dict[offering_team]
                        # if both teams are worse off, skip
                        if team1_happiness_change <= 0 and team2_happiness_change <= 0:
                            continue

                        # Calculate the standard deviation of team costs
                        team_costs = get_team_costs(temp_rosters, player_salaries)
                        team_costs_std = np.std(list(team_costs.values()))

                        # Make sure the standard deviation of team costs is decreasing
                        team_costs_std_diff = prev_team_costs_std - team_costs_std
                        if team_costs_std_diff < min_std_diff:
                            continue

                        # check if this trade has already been considered
                        if sorted([player_1, player_2]) in already_considered_trades:
                            continue
                        already_considered_trades.append(sorted([player_1, player_2]))

                        # Add trade to possible trades
                        possible_trades.append(
                            {"team_1": team_1, 
                             "player_1": player_1, 
                             "team_2": offering_team, 
                             "player_2": player_2, 
                             "team_costs_std": team_costs_std,
                            "team_costs_std_diff": team_costs_std_diff,
                            "team1_happiness_change": team1_happiness_change,
                            "team2_happiness_change": team2_happiness_change,
                            }
                            
                        )
        

        
        # stop if no possible trades
        if len(possible_trades) == 0:
            if debug:
                print ("No trades left")
            break

        trades_to_consider = []

        # find trades where both teams are happy
        for trade1 in possible_trades:
            if trade1["team1_happiness_change"] > 0 and trade1["team2_happiness_change"] > 0:
                trades_to_consider.append(trade1)
                trade_type = "happy"

        # if no happy, find trades where sum of happiness is positive
        if len(trades_to_consider) == 0:
            for trade1 in possible_trades:
                if trade1["team1_happiness_change"] + trade1["team2_happiness_change"] > 0:
                    trades_to_consider.append(trade1)
                    trade_type = "somewhat happy"

        # neutral trades
        if len(trades_to_consider) == 0:
            for trade1 in possible_trades:
                if trade1["team1_happiness_change"] + trade1["team2_happiness_change"] == 0:
                    trades_to_consider.append(trade1)
                    trade_type = "neutral"

        # all leftover trades
        if len(trades_to_consider) == 0:
            trades_to_consider = possible_trades
            trade_type = "all"

        if debug:
            print (f"{trade_i+1} - {trade_type} trades: {len(trades_to_consider)}")

        # sort by team costs std
        trades_to_consider = sorted(trades_to_consider, key=lambda x: x["team_costs_std"])

        # pick the trade that minimizes the standard deviation of team costs
        trade1 = trades_to_consider[0]
        team_1 = trade1["team_1"]
        player_1 = trade1["player_1"]
        team_2 = trade1["team_2"]
        player_2 = trade1["player_2"]
        team_costs_std = trade1["team_costs_std"]
        team_costs_std_diff = trade1["team_costs_std_diff"]
        team1_happiness_change = trade1["team1_happiness_change"]
        team2_happiness_change = trade1["team2_happiness_change"]

        # update prev_team_costs_std
        prev_team_costs_std = team_costs_std

        # stop if std is not changing much
        if trade_i > 0 and team_costs_std_diff < min_std_diff:
            if debug:
                print (f"std diff is less than {min_std_diff}")
            break    
        
        # trade player 1 from team 1 to team 2 for player 2
        rosters_before = rosters.copy()
        rosters = trade(rosters, team_1, player_1, team_2, player_2, team_names)
        happiness_change_dict, happiness_change = get_happiness_change(rosters_before, rosters, player_bids, team_names)
        team1_happiness_change = happiness_change_dict[team_1]
        team2_happiness_change = happiness_change_dict[team_2]

        # new team salaries
        team_costs = get_team_costs(rosters, player_salaries)

        count_team_trades[team_1] += 1
        count_team_trades[team_2] += 1
        trades.append({
            'team_1': team_1,
            'player_1': player_1,
            'team_2': team_2,
            'player_2': player_2,
            'team_costs_std': team_costs_std,
            'team_costs_std_diff': team_costs_std_diff,
            'happiness_change': happiness_change,
            'team1_happiness_change': team1_happiness_change,
            'team2_happiness_change': team2_happiness_change,
        })
        traded_players.append(player_1)
        traded_players.append(player_2)
    return rosters, count_team_trades, trades, protected_players_dict





















