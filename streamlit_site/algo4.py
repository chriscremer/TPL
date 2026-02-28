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
            if player not in player_bids:
                sample_players = list(player_bids.keys())[:20]
                print(f"[DEBUG] Missing player key in player_bids: {repr(player)}")
                print(f"[DEBUG] Team being evaluated: {repr(team)}")
                print(f"[DEBUG] player_bids size: {len(player_bids)}")
                print(f"[DEBUG] Sample player_bids keys: {sample_players}")
                raise KeyError(player)
            if team not in player_bids[player]:
                sample_teams = list(player_bids[player].keys())[:20]
                print(f"[DEBUG] Missing team key for player in player_bids: player={repr(player)}, team={repr(team)}")
                print(f"[DEBUG] Available teams for this player: {sample_teams}")
                raise KeyError(team)
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


def get_trade_happiness_change(team_1, player_1, team_2, player_2, player_bids, player_salaries):
    # Happiness is based on over/underbid deltas:
    # team happiness = (incoming bid - incoming salary) - (outgoing bid - outgoing salary)
    team1_incoming_diff = player_bids[player_2][team_1] - player_salaries[player_2]
    team1_outgoing_diff = player_bids[player_1][team_1] - player_salaries[player_1]
    team1_happiness_change = team1_incoming_diff - team1_outgoing_diff

    team2_incoming_diff = player_bids[player_1][team_2] - player_salaries[player_1]
    team2_outgoing_diff = player_bids[player_2][team_2] - player_salaries[player_2]
    team2_happiness_change = team2_incoming_diff - team2_outgoing_diff

    total_happiness_change = team1_happiness_change + team2_happiness_change
    return team1_happiness_change, team2_happiness_change, total_happiness_change

def trade(rosters, team_1, player_1, team_2, player_2, team_names):
    new_team_1_roster = [player_2 if player == player_1 else player for player in rosters[team_1]]
    new_team_2_roster = [player_1 if player == player_2 else player for player in rosters[team_2]]
    # update rosters
    new_rosters = {team: rosters[team].copy() for team in team_names}
    new_rosters[team_1] = new_team_1_roster
    new_rosters[team_2] = new_team_2_roster
    return new_rosters












def make_trades(rosters, player_salaries, max_trades, amount_above_avg_for_extra_trade, 
                protected_players_dict, player_bids, player_genders, captains,
                absolute_minimum_std_diff, top_trade_percent, stop_if_within_x_of_avg,
                cap_ceiling, cap_floor):
        

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
                        temp_rosters = trade(rosters, team_1, player_1, offering_team, player_2, team_names)
                        team1_happiness_change, team2_happiness_change, happiness_change = get_trade_happiness_change(
                            team_1, player_1, offering_team, player_2, player_bids, player_salaries
                        )

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
        
        print (f"-----------\nTrade {trade_i}")

        print (f"  Possible trades: {len(possible_trades)}")

        # stop if no possible trades
        if len(possible_trades) == 0:
            print ("No trades left")
            break


        # Sort trades by team_costs_std
        sorted_possible_trades = sorted(possible_trades, key=lambda x: x["team_costs_std"])
        # keep top x percent of trades
        n_top_trades = int(len(sorted_possible_trades) * top_trade_percent)
        n_top_trades = max(1, n_top_trades)
        possible_trades = sorted_possible_trades[:n_top_trades]
        print (f"  Possible trades, top {top_trade_percent*100:.2f}%: {len(possible_trades)}")



        # # if player salary dif is less than x, skip
        # new_possible_trades = []
        # if trade_i <= early_trade_rounds:
        #     # early trades should be big
        #     minimum_salary_change = early_minimum_salary_change
        # else:
        #     minimum_salary_change = late_minimum_salary_change
        # for trade1 in possible_trades:
        #     player_1 = trade1["player_1"]
        #     player_2 = trade1["player_2"]
        #     if abs(player_salaries[player_1] - player_salaries[player_2]) > minimum_salary_change:
        #         new_possible_trades.append(trade1)
        # if len(new_possible_trades) > 0 and len(new_possible_trades) < len(possible_trades):
        #     possible_trades = new_possible_trades
        #     print (f"  Possible trades, min salary change: {len(possible_trades)}")
                



        # # Make sure the standard deviation of team costs is decreasing, ie increasing parity
        # new_possible_trades = []
        # if trade_i <= early_trade_rounds:
        #     # early trades should be big
        #     minimum_std_diff = early_minimum_std_diff
        # else:
        #     minimum_std_diff = late_minimum_std_diff
        # for trade1 in possible_trades:
        #     this_trade_costs_std = trade1["team_costs_std"]
        #     team_costs_std_diff = prev_team_costs_std - this_trade_costs_std
        #     # if parity improvement is less than x, skip
        #     if team_costs_std_diff > minimum_std_diff:
        #         new_possible_trades.append(trade1)
        # if len(new_possible_trades) > 0 and len(new_possible_trades) < len(possible_trades):
        #     possible_trades = new_possible_trades
        #     print (f"  Possible trades, min std diff: {len(possible_trades)}")







        # Prioritize low-trade teams:
        # 1) if 1..5 teams are still at 0 trades, focus on them
        # 2) else if no team is at 0 and <=5 teams are at 1 trade, focus on those
        n_teams_at_0_trade = sum([1 for team in team_names if count_team_trades[team] == 0])
        n_teams_at_1_trade = sum([1 for team in team_names if count_team_trades[team] == 1])
        if 1 <= n_teams_at_0_trade <= 5:
            teams_that_must_trade = [team for team in team_names if count_team_trades[team] == 0]
            new_possible_trades = [trade1 for trade1 in possible_trades if trade1["team_1"] in teams_that_must_trade or trade1["team_2"] in teams_that_must_trade]
            if len(new_possible_trades) > 0:
                possible_trades = new_possible_trades
                print (f"\033[95m  Possible trades, low trade teams 0: {len(possible_trades)}\033[0m")
        elif n_teams_at_0_trade == 0 and n_teams_at_1_trade <= 5:
            teams_that_must_trade = [team for team in team_names if count_team_trades[team] == 1]
            new_possible_trades = [trade1 for trade1 in possible_trades if trade1["team_1"] in teams_that_must_trade or trade1["team_2"] in teams_that_must_trade]
            if len(new_possible_trades) > 0:
                possible_trades = new_possible_trades
                print (f"\033[95m  Possible trades, low trade teams 1: {len(possible_trades)}\033[0m")





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
                team1_score -= 1.6# 1.1
            if team1_bid_diff_on_player1 > 0:
                team1_score -= 1.6#1.1
            # team 2
            if team2_bid_diff_on_player1 > 0:
                team2_score += 1
            if team2_bid_diff_on_player2 < 0:
                team2_score += 1
            if team2_bid_diff_on_player1 < 0:
                team2_score -= 1.6#1.1
            if team2_bid_diff_on_player2 > 0:
                team2_score -= 1.6# 1.1
            # cap at 1.5
            team1_score = min(1.5, team1_score)
            team2_score = min(1.5, team2_score)
            score = team1_score + team2_score
            trade1["team1_score"] = team1_score
            trade1["team2_score"] = team2_score

            scored_trades.append([score, trade1])
        # sort by score
        scored_trades = sorted(scored_trades, key=lambda x: x[0], reverse=True)
        highest_score = scored_trades[0][0]
        # only keep trades with the highest score
        new_possible_trades = [trade1 for score, trade1 in scored_trades if score == highest_score]
        # if len(new_possible_trades) > 0 and len(new_possible_trades) < len(possible_trades):
        possible_trades = new_possible_trades
        if highest_score < 0:
            score_str = f"\033[91m{highest_score:.2f}\033[0m"
        elif abs(highest_score) < 1e-9:
            score_str = f"\033[93m{highest_score:.2f}\033[0m"
        else:
            score_str = f"\033[94m{highest_score:.2f}\033[0m"
        preview_trade = possible_trades[0]
        print (
            f"  Possible trades, highest score {score_str} "
            f"({preview_trade['team1_score']:.2f}, {preview_trade['team2_score']:.2f}): {len(possible_trades)}"
        )

        # If all teams have traded at least once and cap constraints are already met,
        # stop before taking non-positive-value trades.
        current_n_above_cap = sum(1 for cost in team_costs.values() if cost > cap_ceiling)
        current_n_below_floor = sum(1 for cost in team_costs.values() if cost < cap_floor)
        all_teams_have_one_trade = all(count_team_trades[team] >= 1 for team in team_names)
        if highest_score <= 0 and all_teams_have_one_trade and current_n_above_cap == 0 and current_n_below_floor == 0:
            print(f"Stopping before Trade {trade_i}: highest score is {highest_score:.2f} and all teams have at least one trade with cap constraints satisfied")
            break






        # Choose among highest-score trades by total happiness change.
        for trade1 in possible_trades:
            trade1["total_happiness_change"] = trade1["team1_happiness_change"] + trade1["team2_happiness_change"]
        possible_trades = sorted(
            possible_trades,
            key=lambda x: (x["total_happiness_change"], -x["team_costs_std"]),
            reverse=True,
        )
        trades_to_consider = possible_trades
        print(
            f"  top total happiness: {trades_to_consider[0]['total_happiness_change']:.2f} "
            f"({trades_to_consider[0]['team1_happiness_change']:.2f}, {trades_to_consider[0]['team2_happiness_change']:.2f})"
        )





        # # TODO review this because list might not be right... 
        # # # try to focus on most and least expensive teams
        # if len(trades_with_most_least_expansive_teams) > 0 and len(trades_with_most_least_expansive_teams) < len(trades_to_consider):
        #     trades_to_consider = trades_with_most_least_expansive_teams
        #     print (f"  Focusing on most/least expensive teams: {len(trades_to_consider)}")




        # take top trade by total happiness (tie-broken by lower team_costs_std)
        trade1 = trades_to_consider[0]
        
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
        rosters = trade(rosters, team_1, player_1, team_2, player_2, team_names)
        team1_happiness_change, team2_happiness_change, happiness_change = get_trade_happiness_change(
            team_1, player_1, team_2, player_2, player_bids, player_salaries
        )

        # new team salaries
        team_costs = get_team_costs(rosters, player_salaries)

        most_expensive_team = max(team_costs, key=team_costs.get)
        most_expensive_cost = team_costs[most_expensive_team]
        least_expensive_team = min(team_costs, key=team_costs.get)
        least_expensive_cost = team_costs[least_expensive_team]
        top_bot_diff = most_expensive_cost - least_expensive_cost
        n_above_cap = sum(1 for cost in team_costs.values() if cost > cap_ceiling)
        n_below_floor = sum(1 for cost in team_costs.values() if cost < cap_floor)

        green_trade_label = f"\033[92mTrade {trade_i} -\033[0m"
        cap_counts_str = f"above_cap: {n_above_cap}, below_floor: {n_below_floor}"
        if n_above_cap > 0 or n_below_floor > 0:
            cap_counts_str = f"\033[93m{cap_counts_str}\033[0m"
        else:
            cap_counts_str = f"\033[92m{cap_counts_str}\033[0m"
        print (f"{green_trade_label}   Std: {team_costs_std:.2f},  imprv: {team_costs_std_diff:.2f}\n    top_bot_diff: {top_bot_diff:.2f}, {cap_counts_str}")



        count_team_trades[team_1] += 1
        count_team_trades[team_2] += 1
        least_trades = min(count_team_trades.values())
        print(f"    least_trades: {least_trades}")
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

    # Confirm all team salaries are below cap ceiling and above cap floor
    fail = False
    for team, cost in team_costs.items():
        if cost > cap_ceiling:
            print (f"Team {team} is over cap ceiling: {cost}")
            fail = True
        if cost < cap_floor:
            print (f"Team {team} is below cap floor: {cost}")
            fail = True
    if not fail:
        print ("--- All teams are within cap ceiling and floor ---")
    # else:
    #     print ("########## FAIL ##########")


    return trades, count_team_trades, rosters, fail









def run_algo(rosters, player_bids, player_genders, captains, player_salaries, 
             protected_players_dict, cap_ceiling, cap_floor):

    random.seed(0)
    
    # settings
    max_trades = 3 #4 # 3 # max trades per team
    amount_above_avg_for_extra_trade =  25000
    stop_if_within_x_of_avg = 35000
    absolute_minimum_std_diff = 100
    
    original_roster = rosters.copy()

    # keep top x percent of trades
    # top_trade_percent =  0.5
    # top_trade_percents = [.01, .25, .5, .75, .95]
    # top_trade_percents = [.95, .75, .5, .25, .01]
    top_trade_percents = [.95, .85, .75, .65, .55, .45, .35, .25, .1, .01]


    results = []
    n_passes_found = 0
    for top_trade_percent in top_trade_percents:
        print ('\n-------')
        print (f"\033[95mTop trade percent: {top_trade_percent}\033[0m")
        run_rng_state = random.getstate()

        trades, count_team_trades, rosters, fail = make_trades(original_roster, player_salaries, max_trades, amount_above_avg_for_extra_trade, 
                    protected_players_dict, player_bids, player_genders, captains,
                    absolute_minimum_std_diff, top_trade_percent, stop_if_within_x_of_avg,
                    cap_ceiling, cap_floor)
        passes = not fail
        score = np.sum([trade["highest_score"] for trade in trades])
        results.append({
            "top_trade_percent": top_trade_percent,
            "score": score,
            "trades": trades,
            "count_team_trades": count_team_trades,
            "rosters": rosters,
            "passes": passes,
            "rng_state": run_rng_state,
        })

        if passes:
            n_passes_found += 1
            if n_passes_found >= 4:
                print(f"Found {n_passes_found} passing runs; stopping sweep early")
                break

    print ('--------------')
    print ()
    # print top_trade_percent, score, and fail
    for i, result in enumerate(results):
        n_trades = len(result["trades"])
        total_happiness_change = np.sum([trade["happiness_change"] for trade in result["trades"]]) if result["trades"] else 0
        print (f"{i} Top trade percent: {result['top_trade_percent']:.2f}, Score: {result['score']:.2f}, Passes: {result['passes']}, Trades: {n_trades}, happy: {total_happiness_change:.2f}")
    print ()

    # Take one with highest score that passes
    best_i = 0
    best_score = None
    for i, result in enumerate(results):
        if result["passes"] and (best_score is None or result["score"] > best_score):
            best_i = i
            best_score = result["score"]
    
    print (f"Best: {best_i} -- {results[best_i]['top_trade_percent']:.2f}, Score: {results[best_i]['score']:.2f}, Passes: {results[best_i]['passes']}")

    # Replay the selected best run so its full trace is shown at the end.
    print("\n=== Replaying Best Run ===")
    random.setstate(results[best_i]["rng_state"])
    trades, count_team_trades, rosters, _ = make_trades(
        original_roster,
        player_salaries,
        max_trades,
        amount_above_avg_for_extra_trade,
        protected_players_dict,
        player_bids,
        player_genders,
        captains,
        absolute_minimum_std_diff,
        results[best_i]["top_trade_percent"],
        stop_if_within_x_of_avg,
        cap_ceiling,
        cap_floor,
    )
    print("\n=== Summary (Final) ===")
    for i, result in enumerate(results):
        n_trades = len(result["trades"])
        total_happiness_change = np.sum([trade["happiness_change"] for trade in result["trades"]]) if result["trades"] else 0
        print (f"{i} Top trade percent: {result['top_trade_percent']:.2f}, Score: {result['score']:.2f}, Passes: {result['passes']}, Trades: {n_trades}, happy: {total_happiness_change:.2f}")
    print (f"Best: {best_i} -- {results[best_i]['top_trade_percent']:.2f}, Score: {results[best_i]['score']:.2f}, Passes: {results[best_i]['passes']}")
    print("Trades per team:")
    for team in sorted(count_team_trades.keys()):
        trade_count = count_team_trades[team]
        trade_count_str = f"{trade_count}"
        if trade_count == 1:
            trade_count_str = f"\033[91m{trade_count}\033[0m"
        print(f"  {team}: {trade_count_str}")

    return rosters, count_team_trades, trades
