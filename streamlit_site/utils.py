import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def get_connection(service_account_file = None, sheet_url=None):

    # if service_account_file is None:
    #     service_account_file = "/Users/chriscremer/Downloads/SVA/SVA/SVA/g_TPL/data/sports-365003-a0354cb71377.json"
    if sheet_url is None:
        sheet_url = 'https://docs.google.com/spreadsheets/d/1yUnn1IQ-EJJA_kdiHTswoh-4rbr8hflq1m66Z85Qp0g/edit#gid=0'


    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)

    #v2 - load json
    json_data = st.secrets['test']
    # json_data = json.load(open(service_account_file))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_data, scope)


    client = gspread.authorize(creds)
    conn = client.open_by_url(sheet_url)
    return conn



# def compute_player_salaries(rosters, player_bids, team_names):
#     player_salaries = {}
#     for team, roster in rosters.items():
#         for player in roster:
#             bids = player_bids[player]
#             # salary = max([bids[t] for t in team_names if t != team])
#             # salary = np.mean([bids[t] for t in team_names if t != team])
#             salary = np.mean([bids[t] for t in team_names])
#             salary = int(salary)
#             player_salaries[player] = salary
#     return player_salaries


# def get_team_costs(rosters, player_salaries, team_names):
#     team_costs = {team: 0 for team in team_names}
#     for team, roster in rosters.items():
#         for player in roster:
#             team_costs[team] += player_salaries[player]
#     # sort by cost
#     team_costs = {k: v for k, v in sorted(team_costs.items(), key=lambda item: item[1], reverse=True)} 
#     return team_costs


# def trade(rosters, team_1, player_1, team_2, player_2, team_names):
#     new_team_1_roster = [player_2 if player == player_1 else player for player in rosters[team_1]]
#     new_team_2_roster = [player_1 if player == player_2 else player for player in rosters[team_2]]
#     # update rosters
#     new_rosters = {team: rosters[team].copy() for team in team_names}
#     new_rosters[team_1] = new_team_1_roster
#     new_rosters[team_2] = new_team_2_roster
#     return new_rosters
