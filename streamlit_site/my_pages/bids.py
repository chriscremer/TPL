import streamlit as st
import pandas as pd
import numpy as np
import random
from gspread_dataframe import set_with_dataframe, get_as_dataframe


from utils import get_connection
from data_utils import sliders_to_bids



def display_team2(team_name, rosters, player_salaries, max_salary, df_players, player_bids):

    # convert rosters to dataframe
    roster = rosters[team_name]
    team_df = pd.DataFrame(roster, columns=['Player'])
    team_df['Salary'] = [player_salaries[player] for player in roster]

    # merge with gender from df_players
    # print (df_players.columns)
    team_df = team_df.merge(df_players, left_on='Player', right_on='Full Name', how='left')


    team_df = team_df.sort_values(by=['Salary'], ascending=False)
    team_df = team_df.reset_index(drop=True)

    # print (team_df.columns)

    # display team
    # st.session_state['sliders_init'] = True
    for i, row in team_df.iterrows():
        player_name = row['Player']
        # if 'WILD' in player_name:
        #     continue
        salary = row['Salary']
        gender = row['Gender']
        cols = st.columns([1, 2, 1, 2, 1])

        if st.session_state['reset_button']:
            init_bid = salary
        else:
            init_bid = player_bids[player_name]

        with cols[1]:
            # st.markdown(f"Player: {player_name}<br>Salary: ${salary}", unsafe_allow_html=True)
            # color = '#ADD8E6' if player_name % 2 == 1 else '#FF69B4'
            color = '#ADD8E6' if gender == 'Male' else '#FF69B4'
            st.markdown(f"<span style='color:{color}'>{player_name}<br>Salary: ${salary}</span>", unsafe_allow_html=True)
        with cols[3]:
            if player_name in st.session_state['captains']  or 'WILD' in player_name:
                #disable slider
                my_bid = st.slider("Your Bid", 0, max_salary, init_bid, key=f"{team_name}-{player_name}", label_visibility='collapsed', disabled=True)
            else:
                my_bid = st.slider("Your Bid", 0, max_salary, init_bid, key=f"{team_name}-{player_name}", label_visibility='collapsed')

        with cols[2]:
            if my_bid > salary:
                st.markdown(f'<br><span style="color: green">↑</span> {my_bid - salary}', unsafe_allow_html=True)
            elif my_bid < salary:
                st.markdown(f'<br><span style="color: red">↓</span> {salary - my_bid}', unsafe_allow_html=True)

    st.markdown('<br><br>', unsafe_allow_html=True)




def get_salaries(df_players, player_names, max_salary):
    # get latest salary: "Week 0 - Salary", extact the int from the string
    df_cols = df_players.columns
    df_cols = [col for col in df_cols if 'Salary' in col]
    df_cols = [col.split(' - ')[0] for col in df_cols]
    df_cols = [int(col.split(' ')[1]) for col in df_cols]
    latest_week = max(df_cols)
    salary_col = f"Week {latest_week} - Salary"
    player_salaries = df_players.set_index('Full Name')[salary_col].to_dict()

    # if salary is above max, we'll need to scale it
    max_cap = max([player_salaries[player] for player in player_names])
    if max_cap > max_salary:
        scale = max_salary / max_cap
    else:
        scale = 1
    for player, salary in player_salaries.items():
        player_salaries[player] = int(salary * scale)

    return player_salaries, latest_week



def get_bids_from_sheet(conn, stss, bids_sheet_name, worksheets, your_team, player_salaries):

    
    # If bids_sheet_name does not exist, make it
    if not bids_sheet_name in [worksheet.title for worksheet in worksheets]:
        worksheet = conn.add_worksheet(title=bids_sheet_name, rows=200, cols=20)
        
        # Populate sheet with player names as rows, team names as columns, and salary as values
        # df = pd.DataFrame(player_bids).T
        df = pd.DataFrame(player_salaries, index=[0]).T
        df.index.name = 'Player'
        set_with_dataframe(worksheet, df, include_index=True, include_column_header=True, resize=True)
        print ('Created worksheet\n')

    # Load the bids from the sheet
    if 'player_bids' not in stss:
        print (f'Loading bids for {your_team}')
        sheet = conn.worksheet(bids_sheet_name)
        df_bids = get_as_dataframe(sheet)
        # convert to dict
        # player_bids = df_bids.to_dict(orient='index')[0]
        player_bids = {}
        for i, row in df_bids.iterrows():
            player_name = row['Player']
            player_bids[player_name] = row[your_team]
        stss['player_bids'] = player_bids
    player_bids = stss['player_bids']
    # print (len(player_bids))
    # print (len(player_salaries))
    # print (player_bids.keys())
    return player_bids, bids_sheet_name


def get_rosters(df_players, team_names):
    rosters = {team: [] for team in team_names}
    for i, row in df_players.iterrows():
        team = row['Team']
        name = row['Full Name']
        rosters[team].append(name)
    return rosters


def check_for_changes(stss, team_names, rosters):
    changes = False
    team0 = team_names[0]
    player0 = rosters[team0][0]
    # see if sliders have initialized
    if f"{team0}-{player0}" in stss:
        for team in team_names:
            for player in rosters[team]:
                current_bid = stss[f"{team}-{player}"]
                original_bid = stss["player_bids"][player]
                # original_bid = stss["original_bids"][player]
                # if player_salaries[player] != stss[f"{team}-{player}"]:
                if current_bid != original_bid:
                    # print (f"{team}-{player} has changed")
                    changes = True
                    break
            if changes:
                break
    # in case of reset
    if 'Reset' in stss and stss['Reset'] == True:
        changes = True
    # if 'stats_applied' in stss and stss['stats_applied'] == True:
    #     changes = True
    #     stss['stats_applied'] = False

    return changes



def save_uploaded_bids(conn, stss, your_team, player_bids, bids_sheet_name, team_names):
    values = []
    for player_name in stss['player_names']:
        bid = player_bids[player_name]
        values.append([bid])
    # Update col for this team with new bids
    col_name = your_team
    start_row_idx = 2
    end_row_idx = len(player_bids) + 1
    col_letter = chr(team_names.index(col_name) + 65 + 1) # +1 for the index column
    sheet = conn.worksheet(bids_sheet_name)
    sheet.update(range_name=f'{col_letter}{start_row_idx}:{col_letter}{end_row_idx}', values=values)





def load_data(stss):

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

        captains_sheet = [worksheet for worksheet in worksheets if worksheet.title == 'Captains'][0]
        df_captains = get_as_dataframe(captains_sheet)
        # convert to list
        stss['captains'] = df_captains['Captain'].tolist()



def save_bids(conn, stss, your_team, player_bids, bids_sheet_name, team_names, df_players, rosters):
    # Update col for this team with new bids
    col_name = your_team
    start_row_idx = 2
    end_row_idx = len(player_bids) + 1
    col_letter = chr(team_names.index(col_name) + 65 + 1) # +1 for the index column
    values = []
    for player_name in stss['player_names']:
        player_team = df_players.loc[df_players['Full Name'] == player_name]['Team'].values[0]
        bid = st.session_state[f"{player_team}-{player_name}"]
        values.append([bid])
    sheet = conn.worksheet(bids_sheet_name)
    sheet.update(range_name=f'{col_letter}{start_row_idx}:{col_letter}{end_row_idx}', values=values)

    # Update player_bids in session state
    player_bids = {player: st.session_state[f"{team}-{player}"] for team in team_names for player in rosters[team]}
    stss['player_bids'] = player_bids
    print ('Saved')
    st.rerun()










def bids_page():

    stss = st.session_state
    load_data(stss)

    conn = stss['conn']
    worksheets = stss['worksheets']
    df_players = stss['df_players']
    your_team = stss['team_name']
    # team_names = list(df_players['Team'].unique())
    team_names = stss['team_names']
    player_names = df_players['Full Name'].tolist()
    rosters = get_rosters(df_players, team_names)
    max_salary = stss['max_salary']

    player_salaries, latest_week = get_salaries(df_players, player_names, max_salary)
    bids_sheet_name = f"Week {latest_week} - Bids"

    if 'player_bids' not in stss:
        player_bids, bids_sheet_name = get_bids_from_sheet(conn, stss, bids_sheet_name, worksheets, your_team, player_salaries)
    else:
        player_bids = stss['player_bids']


    
    
    st.markdown(f"<center><h3>Week {latest_week+1} Bids</h3></center>", unsafe_allow_html=True)
    cols = st.columns([1, 2, 1])

    # Save button
    changes = check_for_changes(stss, team_names, rosters)
    with cols[0]:
        if changes:
            save = st.button('Save Changes')
        else:
            save = st.button('No Changes', disabled=True)
        if save:
            print ('Save')
            save_bids(conn, stss, your_team, stss['player_bids'], bids_sheet_name, team_names, df_players, rosters)


        # Reset button
        reset = st.button('Reset to Previous Week', key='Reset') 
        if reset:
            print ('Reset')
            stss['reset_button'] = True
        else:
            stss['reset_button'] = False


        # Line break
        st.markdown('<br>', unsafe_allow_html=True)

        # Download button
        def convert_df():
            # convert player bids to dataframe
            player_bids_df = []
            for player_name in stss['player_names']:
                # doesnt matter what they bid on for wildcards
                if 'WILD' in player_name:
                    continue
                # bid = player_bids[player_name]
                bid = stss['player_bids'][player_name]
                player_bids_df.append({'Player': player_name, 'Bid': bid})
            player_bids_df = pd.DataFrame(player_bids_df)
            return player_bids_df.to_csv().encode("utf-8")
        st.download_button(
            label="Download file",
            data=convert_df(),
            file_name="player_bids.csv",
            mime="text/csv",
        )

        # Upload
        with st.expander("Upload File"):
            uploaded_file = st.file_uploader("Upload")
            if uploaded_file is not None:
                dataframe = pd.read_csv(uploaded_file)
                # convert df to player_bids dict
                player_bids = {row['Player']: row['Bid'] for i, row in dataframe.iterrows()}
                stss['player_bids'] = player_bids
                
                save_uploaded_bids(conn, stss, your_team, player_bids, bids_sheet_name, team_names)
                print ('Uploaded')
                # popup to confirm it worked
                st.success('Uploaded') #, please refresh the page to see changes')







    with cols[2]:

        # collapsable area
        with st.expander("Stat Sliders"):

            # Set salaries based on stats
            goal_slider = st.slider("Goal", 0, 10, 5, key='goal_slider')
            assist_slider = st.slider("Assist", 0, 10, 5, key='assist_slider')
            second_assist_slider = st.slider("2nd Assist", 0, 10, 3, key='second_assist_slider')
            d_slider = st.slider("D", 0, 10, 5, key='d_slider')
            ta_slider = st.slider("Throwaway", 0, 10, 3, key='ta_slider')
            drop_slider = st.slider("Drop", 0, 10, 3, key='drop_slider')
            salart_spread_slider = st.slider("Salary Spread", 0, 10, 5, key='salary_spread_slider')

            # Button to apply to bids
            apply_stats = st.button('Apply to Bids')
            if apply_stats:
                sliders_to_bids(stss)
                save_uploaded_bids(conn, stss, your_team, stss['player_bids'], bids_sheet_name, team_names)
                st.rerun()








    # Display all teams
    n_teams = len(team_names)
    teams_per_row = 3
    n_rows = 1 + n_teams // teams_per_row
    container_list = [st.container() for _ in range(n_rows*2)]
    cols_list = [st.columns(teams_per_row) for _ in range(n_rows*2)]

    # Put your team first
    display_team_names = team_names.copy()
    display_team_names.remove(your_team)
    display_team_names = [your_team] + display_team_names
    for i, team_name in enumerate(display_team_names):
        # Center your team
        if i == 0:
            row = 0
            col = 1
        else:
            idx = i - 1
            row = idx//teams_per_row +2
            col = idx%teams_per_row

        with container_list[row]:
            with cols_list[row][col]:
                st.markdown(f"<center><p style='font-size:20px; font-weight:bold'>{team_name}</p></center>", unsafe_allow_html=True)

        with container_list[row + 1]:
            with cols_list[row + 1][col]:
                display_team2(team_name, rosters, player_salaries, max_salary, df_players, player_bids)

    if st.session_state['reset_button']:
        st.session_state['reset_button'] = False
