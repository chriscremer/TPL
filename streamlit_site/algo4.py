"""
python -m streamlit_site.algo4

goal is to make minimum 1 trade per team
so if 2 teams have made 0 trades, then the next trade must involve atleast one of those teams
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
        team_values[team] = 0
        for player in roster:
            # print (player_bids[player].keys())
            team_bid = player_bids[player][team]
            # team_value = team_values.get(team, 0)
            # print (team, player, team_bid, team_values[team])
            team_values[team] += team_bid
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





def run_algo(rosters, player_bids, player_genders, captains, player_salaries, protected_players_dict):

    random.seed(0)
    
    # settings
    max_trades = 3 #4 # 3 # max trades per team
    amount_above_avg_for_extra_trade =  25000
    stop_if_within_x_of_avg = 33000
    early_minimum_salary_change = 15000
    late_minimum_salary_change = 7000 #5000
    early_minimum_std_diff = 7000
    late_minimum_std_diff = 500 #700
    absolute_minimum_std_diff = 100
    early_trade_rounds = 6

    # compute salary of each team
    team_costs = get_team_costs(rosters, player_salaries)

    # get list of protected players
    protected_players = []
    for team, players in protected_players_dict.items():
        protected_players += [player_name for player_name in players]

    team_names = list(rosters.keys())
    n_teams = len(team_names)
    count_team_trades = {team: 0 for team in team_names} # keep track of number of trades per team
    prev_team_costs_std = np.std(list(team_costs.values()))
    trades = [] # list of trades
    traded_players = [] # avoid trading the same player twice
    max_trade_rounds = (n_teams * max_trades // 2) +1
    for trade_i in range(1, max_trade_rounds):

        already_considered_trades = [] # to avoid considering the same trade twice
        possible_trades = []
        for team_1 in team_names:

            # compute team_cost - avg team_cost
            team_cost_diff = np.abs(team_costs[team_1] - np.mean(list(team_costs.values())))
            # added this to allow teams to make more trades if they are still far from the average
            if team_cost_diff > amount_above_avg_for_extra_trade:
                this_max_trades = max_trades + 1
            else:
                this_max_trades = max_trades

            # skip if team has already made max_trades
            if count_team_trades[team_1] >= this_max_trades:
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

                    # compute team_cost - avg team_cost
                    team_cost_diff = np.abs(team_costs[offering_team] - np.mean(list(team_costs.values())))
                    if team_cost_diff > amount_above_avg_for_extra_trade:
                        this_max_trades2 = max_trades + 1
                    else:
                        this_max_trades2 = max_trades

                    # skip if team has already made max_trades
                    if count_team_trades[offering_team] >= this_max_trades2:
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

                    # print (f"Team 1: {team_1}, Player 1: {player_1}, Offering team: {offering_team}")

                    # consider trading this player with players on the offering team
                    for player_2 in offering_team_roster:
                        # trade player 1 from team 1 to team 2 for player 2
                        rosters_before = rosters.copy()
                        temp_rosters = trade(rosters, team_1, player_1, offering_team, player_2, team_names)
                        happiness_change_dict, happiness_change = get_happiness_change(rosters_before, temp_rosters, player_bids, team_names)
                        team1_happiness_change = happiness_change_dict[team_1]
                        team2_happiness_change = happiness_change_dict[offering_team]

                        team_1_bid_minus_salary = player_bids[player_2][team_1] - player_salaries[player_2]
                        team_2_bid_minus_salary = player_bids[player_1][offering_team] - player_salaries[player_1]
                        
                        # if both teams are worse off, skip
                        if team1_happiness_change < 0 and team2_happiness_change < 0:
                            continue

                        # Calculate the standard deviation of team costs
                        this_trade_team_costs = get_team_costs(temp_rosters, player_salaries)
                        this_trade_costs_std = np.std(list(this_trade_team_costs.values()))

                        # Make sure the standard deviation of team costs is decreasing, ie increasing parity
                        team_costs_std_diff = prev_team_costs_std - this_trade_costs_std
                        if team_costs_std_diff < absolute_minimum_std_diff:
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
                             "team_costs_std": this_trade_costs_std,
                            "team_costs_std_diff": team_costs_std_diff,
                            "team1_happiness_change": team1_happiness_change,
                            "team2_happiness_change": team2_happiness_change,
                            "team_1_bid_minus_salary": team_1_bid_minus_salary,
                            "team_2_bid_minus_salary": team_2_bid_minus_salary,
                            }
                        )
        
        print (f"Trade {trade_i}")

        print (f"  Possible trades: {len(possible_trades)}")

        # stop if no possible trades
        if len(possible_trades) == 0:
            print ("No trades left")
            break


        # if player salary dif is less than x, skip
        new_possible_trades = []
        if trade_i <= early_trade_rounds:
            # early trades should be big
            minimum_salary_change = early_minimum_salary_change
        else:
            minimum_salary_change = late_minimum_salary_change
        for trade1 in possible_trades:
            player_1 = trade1["player_1"]
            player_2 = trade1["player_2"]
            if abs(player_salaries[player_1] - player_salaries[player_2]) > minimum_salary_change:
                new_possible_trades.append(trade1)
        if len(new_possible_trades) > 0 and len(new_possible_trades) < len(possible_trades):
            possible_trades = new_possible_trades
            print (f"  Possible trades, min salary change: {len(possible_trades)}")
                



        # Make sure the standard deviation of team costs is decreasing, ie increasing parity
        new_possible_trades = []
        if trade_i <= early_trade_rounds:
            # early trades should be big
            minimum_std_diff = early_minimum_std_diff
        else:
            minimum_std_diff = late_minimum_std_diff
        for trade1 in possible_trades:
            this_trade_costs_std = trade1["team_costs_std"]
            team_costs_std_diff = prev_team_costs_std - this_trade_costs_std
            # if parity improvement is less than x, skip
            if team_costs_std_diff > minimum_std_diff:
                new_possible_trades.append(trade1)
        if len(new_possible_trades) > 0 and len(new_possible_trades) < len(possible_trades):
            possible_trades = new_possible_trades
            print (f"  Possible trades, min std diff: {len(possible_trades)}")



        # check if N or fewer teams are at 0 trades
        # if so, try to have the next trade involve atleast one of these teams
        if sum([1 for team in team_names if count_team_trades[team] == 0]) in [1, 2, 3]:
            teams_that_must_trade = [team for team in team_names if count_team_trades[team] == 0]
            new_possible_trades = [trade1 for trade1 in possible_trades if trade1["team_1"] in teams_that_must_trade or trade1["team_2"] in teams_that_must_trade]
            if len(new_possible_trades) > 0:
                possible_trades = new_possible_trades
                # print (f"  Teams that must trade 0: {[x[:10] for x in teams_that_must_trade]}")
                print (f"  Possible trades, low trade teams 0: {len(possible_trades)}")
        else:
            # check if two or fewer teams are at 1 trade and the rest have atleast 2
            # then try to have the next trade involve atleast one of the teams with 1 trade
            n_teams_at_1_trade = sum([1 for team in team_names if count_team_trades[team] == 1])
            n_teams_at_0_trade = sum([1 for team in team_names if count_team_trades[team] == 0])
            if n_teams_at_1_trade in [1, 2] and n_teams_at_0_trade == 0:
                teams_that_must_trade = [team for team in team_names if count_team_trades[team] == 1]
                new_possible_trades = [trade1 for trade1 in possible_trades if trade1["team_1"] in teams_that_must_trade or trade1["team_2"] in teams_that_must_trade]
                if len(new_possible_trades) > 0:
                    possible_trades = new_possible_trades
                    # print (f"  Teams that must trade 1: {[x[:10] for x in teams_that_must_trade]}")
                    print (f"  Possible trades, low trade teams 1: {len(possible_trades)}")





        # score each trade from -4 to 4
        # 1 point for each of the following:
        #  - receiving team is overbidding on player they are receiving
        #  - receiving team is underbidding on player they are giving
        #  - sending team is underbidding on player they are giving
        #  - sending team is overbidding on player they are receiving
        # -1 point for each of the following:
        #  - receiving team is underbidding on player they are receiving
        #  - receiving team is overbidding on player they are giving
        #  - sending team is overbidding on player they are giving
        #  - sending team is underbidding on player they are receiving
        # make a list of [score, trade]
        scored_trades = []
        for trade1 in possible_trades:
            team2_bid_diff_on_player1 = player_bids[trade1["player_1"]][trade1["team_2"]] - player_salaries[trade1["player_1"]]
            team1_bid_diff_on_player2 = player_bids[trade1["player_2"]][trade1["team_1"]] - player_salaries[trade1["player_2"]]
            team1_bid_diff_on_player1 = player_bids[trade1["player_1"]][trade1["team_1"]] - player_salaries[trade1["player_1"]]
            team2_bid_diff_on_player2 = player_bids[trade1["player_2"]][trade1["team_2"]] - player_salaries[trade1["player_2"]]
            
            # score = 0
            # # positive points
            # if team2_bid_diff_on_player1 > 0:
            #     score += 1
            # if team1_bid_diff_on_player2 > 0:
            #     score += 1
            # if team1_bid_diff_on_player1 < 0:
            #     score += 1
            # if team2_bid_diff_on_player2 < 0:
            #     score += 1
            # # negative points
            # if team2_bid_diff_on_player1 < 0:
            #     score -= 1
            # if team1_bid_diff_on_player2 < 0:
            #     score -= 1
            # if team1_bid_diff_on_player1 > 0:
            #     score -= 1
            # if team2_bid_diff_on_player2 > 0:
            #     score -= 1

            # compute for each team, cap at 1.5
            team1_score = 0
            team2_score = 0
            # team 1
            if team1_bid_diff_on_player2 > 0:
                team1_score += 1
            if team1_bid_diff_on_player1 < 0:
                team1_score += 1
            if team1_bid_diff_on_player2 < 0:
                team1_score -= 1
            if team1_bid_diff_on_player1 > 0:
                team1_score -= 1
            # team 2
            if team2_bid_diff_on_player1 > 0:
                team2_score += 1
            if team2_bid_diff_on_player2 < 0:
                team2_score += 1
            if team2_bid_diff_on_player1 < 0:
                team2_score -= 1
            if team2_bid_diff_on_player2 > 0:
                team2_score -= 1
            # cap at 1.5
            team1_score = min(1.5, team1_score)
            team2_score = min(1.5, team2_score)
            score = team1_score + team2_score

            scored_trades.append([score, trade1])
        # sort by score
        scored_trades = sorted(scored_trades, key=lambda x: x[0], reverse=True)
        highest_score = scored_trades[0][0]
        # only keep trades with the highest score
        new_possible_trades = [trade1 for score, trade1 in scored_trades if score == highest_score]
        if len(new_possible_trades) > 0 and len(new_possible_trades) < len(possible_trades):
            possible_trades = new_possible_trades
            print (f"  Possible trades, highest score {highest_score}: {len(possible_trades)}")






        # Now looking at bid for received and traded player to determine if trade is good
        trades_to_consider = []

        # get list of trades involving the most and least expensive teams
        most_expensive_team = max(team_costs, key=team_costs.get)
        least_expensive_team = min(team_costs, key=team_costs.get)
        most_expensive_team_cost = team_costs[most_expensive_team]
        least_expensive_team_cost = team_costs[least_expensive_team]
        # trades with most and least expensive teams
        most_expensive_team_trades = [trade1 for trade1 in possible_trades if trade1["team_1"] == most_expensive_team or trade1["team_2"] == most_expensive_team]
        least_expensive_team_trades = [trade1 for trade1 in possible_trades if trade1["team_1"] == least_expensive_team or trade1["team_2"] == least_expensive_team]
        # remove duplicates
        most_expensive_team_trades = [trade1 for trade1 in most_expensive_team_trades if trade1 not in least_expensive_team_trades]
        trades_with_most_least_expansive_teams = most_expensive_team_trades + least_expensive_team_trades

        # find trades where both teams are happy
        if len(trades_to_consider) == 0:
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
            # stop if teams are close to the average and only neutral trades left
            if most_expensive_team_cost - least_expensive_team_cost < stop_if_within_x_of_avg:
                print (f"Teams are {most_expensive_team_cost - least_expensive_team_cost} apart, neutral trades only, so stopping")
                break
            new_trades_to_consider = []
            for trade1 in possible_trades:
                if trade1["team1_happiness_change"] + trade1["team2_happiness_change"] == 0:
                    new_trades_to_consider.append(trade1)
            if len(new_trades_to_consider) > 0:
                trades_to_consider = new_trades_to_consider
                trade_type = "neutral"

        # all leftover trades, ie negative sum trades
        if len(trades_to_consider) == 0:
            # stop if teams are close to the average and only negative trades left
            if most_expensive_team_cost - least_expensive_team_cost < stop_if_within_x_of_avg:
                print (f"Teams are {most_expensive_team_cost - least_expensive_team_cost} apart, negative trades left, so stopping")
                break
            # only resort to this if most/least expensive team is involved
            elif len(trades_with_most_least_expansive_teams) > 0:
                trades_to_consider = trades_with_most_least_expansive_teams
                trade_type = "all"
            else:
                # trades_to_consider = possible_trades
                # trade_type = "all but not ideal"
                print ("Stopping because no good trades left and dont involve most/least expensive teams")
                break

        print (f"  {trade_type} trades: {len(trades_to_consider)}")





        # # TODO review this because list might not be right... 
        # # # try to focus on most and least expensive teams
        # if len(trades_with_most_least_expansive_teams) > 0 and len(trades_with_most_least_expansive_teams) < len(trades_to_consider):
        #     trades_to_consider = trades_with_most_least_expansive_teams
        #     print (f"  Focusing on most/least expensive teams: {len(trades_to_consider)}")




        # sort by team costs std, ie sort trades by how much how they increase parity
        trades_to_consider = sorted(trades_to_consider, key=lambda x: x["team_costs_std"])
        # pick the trade that minimizes the standard deviation of team costs, ie maximize parity
        trade1 = trades_to_consider[0]

        if trade1 in trades_with_most_least_expansive_teams:
            print ("  Trade with most/least expensive team")
        
        # extract trade info
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
        
        # trade player 1 from team 1 to team 2 for player 2
        rosters_before = rosters.copy()
        rosters = trade(rosters, team_1, player_1, team_2, player_2, team_names)
        happiness_change_dict, happiness_change = get_happiness_change(rosters_before, rosters, player_bids, team_names)
        team1_happiness_change = happiness_change_dict[team_1]
        team2_happiness_change = happiness_change_dict[team_2]

        # new team salaries
        team_costs = get_team_costs(rosters, player_salaries)

        most_expensive_team = max(team_costs, key=team_costs.get)
        most_expensive_cost = team_costs[most_expensive_team]
        least_expensive_team = min(team_costs, key=team_costs.get)
        least_expensive_cost = team_costs[least_expensive_team]
        top_bot_diff = most_expensive_cost - least_expensive_cost

        print (f"Trade {trade_i} -   Std: {team_costs_std:.2f},  imprv: {team_costs_std_diff:.2f}, top_bot_diff: {top_bot_diff:.2f}")



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
            'team_costs': team_costs.copy(),
            'highest_score': highest_score,
        })
        traded_players.append(player_1)
        traded_players.append(player_2)
    return rosters, count_team_trades, trades





















