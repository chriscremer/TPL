
from gspread_dataframe import get_as_dataframe
import pandas as pd
import streamlit as st
import numpy as np

from utils import get_connection
# from my_pages.league import convert_salaries




def convert_salaries(df_league, max_salary):
    # convert to string
    df_league['Cap Impact'] = df_league['Cap Impact'].astype(str)
    # "818,579.3373" to 818579.3373
    df_league['Cap Impact'] = df_league['Cap Impact'].str.replace(',', '').astype(float)
    # get the max salary
    largest_salary = df_league['Cap Impact'].max()
    # normalize the salaries
    scale = max_salary / largest_salary
    df_league['Cap Impact'] = df_league['Cap Impact'] * scale
    # convert to int
    df_league['Cap Impact'] = df_league['Cap Impact'].astype(int)
    # sort by salary
    df_league = df_league.sort_values('Cap Impact', ascending=False)

    # strip() the first and last names
    df_league['First'] = df_league['First'].str.strip()
    df_league['Last'] = df_league['Last'].str.strip()
    # combine First and Last names
    df_league['Name'] = df_league['First'] + ' ' + df_league['Last']
    # drop the First and Last columns
    df_league = df_league.drop(columns=['First', 'Last'])
    # put name as first column
    cols = list(df_league.columns)
    cols.remove('Name')
    df_league = df_league[['Name'] + cols]


    # remove rows with WILD in the name
    df_league = df_league[~df_league['Name'].str.contains("WILD")]
    # remove 0 GP rows
    df_league = df_league[df_league['GP'] != '0']

    # reset the index
    df_league = df_league.reset_index(drop=True)

    # scale G	A	2A	D	TA	RE by GPs
    cols = ['G', 'A', '2A', 'D', 'TA', 'RE']
    for col in cols:
        df_league[col] = df_league[col] / df_league['GP']
        # df_league[col] = df_league[col].round(1)
        # convert to string with 1 decimal place
        df_league[col] = df_league[col].apply(lambda x: f"{x:.1f}")

    return df_league


def get_league_data(stss):

    if 'df_league' not in stss:

        # sheets_url = 'https://docs.google.com/spreadsheets/d/1U4T-r7DsfWZI9VXsa7Ul38XDDLpE-7Sz1TFzd29EEVw/edit#gid=0'
        sheets_url = "https://docs.google.com/spreadsheets/d/1l-7P9YuQ_2FCrWEYYUKhgiD1FBWFZ5wjW3B5RxtiYpM/edit?gid=9#gid=9"
        league_conn = get_connection(sheet_url=sheets_url)
        
        worksheets = league_conn.worksheets()
        league_sheet = [worksheet for worksheet in worksheets if worksheet.title == 'League'][0]
        df_league = get_as_dataframe(league_sheet, evaluate_formulas=True)
        # make the df start at row 9, and drop first column
        df_league = df_league.iloc[8:, 1:]
        # make the first row the column names
        df_league.columns = df_league.iloc[0]
        # drop the first row
        df_league = df_league.iloc[1:]

        cols_to_keep = [
            "First",
            "Last",
            "Team",
            "Cap Impact",
            "GP",
            "G",
            "A",
            "2A",
            "D",
            "TA",
            "RE",
        ]
        df_league = df_league[cols_to_keep]

        # convert to dict
        df_league = df_league.to_dict(orient='records')
        # convert to df
        df_league = pd.DataFrame(df_league)

        df_league = convert_salaries(df_league, stss['max_salary'])
        stss['df_league'] = df_league

        # print (df_league.head())






def sliders_to_bids(stss):
    # print (list(stss.keys()))
    if 'df_league' not in stss:
        get_league_data(stss)
    player_stats = stss['df_league']

    weights = {
        'G': stss['goal_slider'],
        'A': stss['assist_slider'],
        '2A': stss['second_assist_slider'],
        'D': stss['d_slider'],
        'TA': -stss['ta_slider'],
        'RE': -stss['drop_slider'],
    }

    salary_spread = stss['salary_spread_slider']
    # change range of 0-10 to 0-.3
    salary_spread = salary_spread / 10 * .3

    
    # print (player_stats.head())
    player_bids = {}
    for i, row in player_stats.iterrows():
        # if 'WILD' in row['Name']:
        #     continue
        bid = 0
        for col, weight in weights.items():
            # print (type(row[col]))
            # print (type(weight))
            bid += float(row[col]) * weight
        # check for NaN
        if bid != bid:
            bid = 0
        player_bids[row['Name']] = bid
    
    all_bids = list(player_bids.values())
    # print (np.mean(all_bids))
    # scale so that average bid is 250
    

    # set mean to 0
    shift = np.mean(all_bids)
    player_bids = {k: v - shift for k, v in player_bids.items()}
    # print (np.mean(list(player_bids.values())))
    # set std to x% of max_salary
    all_bids = list(player_bids.values())
    scale = np.std(all_bids) / (stss['max_salary'] * salary_spread)
    player_bids = {k: v / scale for k, v in player_bids.items()}
    # print (np.mean(list(player_bids.values())))
    # set mean to max_salary / 2
    all_bids = list(player_bids.values())
    # scale = stss['max_salary']/2 / np.mean(all_bids)
    shift = stss['max_salary']/2
    # player_bids = {k: int(v * scale) for k, v in player_bids.items()}
    player_bids = {k: int(v + shift) for k, v in player_bids.items()}
    # print (np.mean(list(player_bids.values())))
    # set min to 0 and max to max_salary
    player_bids = {k: min(max(v, 0), stss['max_salary']) for k, v in player_bids.items()}


    # scale = stss['max_salary']/2 / np.mean(all_bids)
    # for player in player_bids:
    #     player_bids[player] = int(player_bids[player] * scale)
    #     player_bids[player] = min(player_bids[player], stss['max_salary'])
    #     player_bids[player] = max(player_bids[player], 0)
    # print (np.mean(list(player_bids.values())))

    # add wildcards from stss['player_bids'] to player_bids
    for player in stss['player_bids']:
        if player not in player_bids:
            player_bids[player] = stss['player_bids'][player]

    stss['player_bids'] = player_bids

    
