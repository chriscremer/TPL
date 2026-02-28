"""
Run trading algo locally without Streamlit UI or Google Sheets calls.

Examples:
  python -m streamlit_site.run_algo_local --no-bids
  python -m streamlit_site.run_algo_local
  python -m streamlit_site.run_algo_local --refresh-bids
  python -m streamlit_site.run_algo_local --team-bids ~/Downloads/team_bids.json
"""

import argparse
import concurrent.futures
import json
import os
from typing import Dict, Any

import pandas as pd
import gspread
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

try:
    from streamlit_site.algo4 import run_algo
except ImportError:
    from algo4 import run_algo


def no_emoji(text: str) -> str:
    new = ""
    for c in str(text):
        if c.isalpha() or c in [" ", "-", "'", '"', "(", ")", "!", "&", ":", ","]:
            new += c
    return new.strip().replace("  ", " ")


def parse_bid_value(raw_bid: Any) -> int:
    if raw_bid is None:
        return 0
    if isinstance(raw_bid, (int, float)):
        return int(raw_bid)
    text = str(raw_bid).strip().replace(",", "")
    if text == "":
        return 0
    if text.startswith("$"):
        text = text[1:]
    try:
        return int(float(text))
    except ValueError:
        return 0


def google_authenticate(service_account_file: str):
    scope = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)
    drive_service = build("drive", "v3", credentials=creds)
    sheets_client = gspread.authorize(creds)
    return drive_service, sheets_client


def get_gsheets_in_folder(drive_service, folder_id: str):
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])


def extract_bid_info(data):
    player_rows = [6, 19]
    name_col = 0
    first_bid_col = 3
    bid_col_interval = 6
    team_name_row = 4

    n_teams = 0
    while True:
        cur_name_col = name_col + n_teams * bid_col_interval
        if team_name_row >= len(data):
            break
        row_vals = data[team_name_row]
        if cur_name_col >= len(row_vals):
            break
        team_name = str(row_vals[cur_name_col]).strip()
        if team_name == "":
            break
        n_teams += 1

    def safe_get(row_i, col_i):
        if row_i >= len(data):
            return ""
        row = data[row_i]
        if col_i >= len(row):
            return ""
        return row[col_i]

    def is_numeric_like(raw_val):
        text = str(raw_val).strip().replace(",", "")
        if text.startswith("$"):
            text = text[1:]
        if text == "":
            return False
        try:
            float(text)
            return True
        except ValueError:
            return False

    bids = {}
    for team_i in range(n_teams):
        for player_row in range(player_rows[0], player_rows[1] + 1):
            cur_name_col = name_col + team_i * bid_col_interval
            player_name = safe_get(player_row, cur_name_col)
            if str(player_name).strip() == "":
                continue

            bid_col = first_bid_col + bid_col_interval * team_i
            raw_bid = safe_get(player_row, bid_col)
            if is_numeric_like(raw_bid):
                player_bid = parse_bid_value(raw_bid)
            else:
                # fallback to salary+0 if bid cell is non-numeric/blank
                player_bid = parse_bid_value(safe_get(player_row, bid_col - 2))
            bids[player_name] = player_bid

    protected_players_col = 4
    protected_players = []
    for player_row in range(player_rows[0], player_rows[1] + 1):
        player_name = safe_get(player_row, name_col)
        if str(player_name).strip() == "":
            continue
        value = str(safe_get(player_row, protected_players_col)).strip().lower()
        if value == "y":
            protected_players.append(player_name)

    return bids, protected_players


def fetch_and_save_team_bids(service_account_file: str, folder_id: str, output_path: str):
    drive_service, sheets_client = google_authenticate(service_account_file)
    existing_sheets = get_gsheets_in_folder(drive_service, folder_id)
    if not existing_sheets:
        raise RuntimeError(f"No Google Sheets found in folder {folder_id}")

    def fetch_sheet_data(sheet_dict):
        sheet_name = sheet_dict["name"]
        sheet_id = sheet_dict["id"]
        conn = sheets_client.open_by_key(sheet_id)
        sheet = conn.get_worksheet(0)
        data = sheet.get_all_values()
        return sheet_name, data

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch_sheet_data, existing_sheets))

    team_bids = {}
    for sheet_name, data in results:
        bids, protected_players = extract_bid_info(data)
        normalized_team_name = no_emoji(sheet_name).strip()
        team_bids[normalized_team_name] = {"bids": bids, "protected_players": protected_players}

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(team_bids, f, ensure_ascii=False, indent=2)
    print(f"Saved team bids to {output_path}")


def convert_col_to_int(df: pd.DataFrame, col: str) -> pd.DataFrame:
    out = df.copy()
    out[col] = out[col].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False)
    out[col] = out[col].astype(int)
    return out


def load_league_data_from_path(league_path: str) -> pd.DataFrame:
    df = pd.read_csv(league_path)
    df = convert_col_to_int(df, "Cap Impact")
    df["First"] = df["First"].astype(str).str.strip()
    df["Last"] = df["Last"].astype(str).str.strip()
    df["Full Name"] = df["First"] + " " + df["Last"]
    df = df[["Full Name", "Team", "Cap Impact", "Gender"]]
    return df


def load_standings_data_from_path(standings_path: str):
    df = pd.read_csv(standings_path)
    df["Team"] = df["Team"].apply(no_emoji)

    first_team_salary = int(str(df.iloc[0]["Salary"]).replace("$", "").replace(",", ""))
    first_team_over_under = int(str(df.iloc[0]["Over/under"]).replace("$", "").replace(",", ""))
    cap_ceiling = first_team_salary - first_team_over_under
    first_team_cap_floor = int(df.iloc[0]["Cap Floor"])
    cap_floor = cap_ceiling - first_team_cap_floor
    return cap_ceiling, cap_floor


def default_captains():
    return [
        "James Shimoda",
        "Vikki Shimoda",
        "Robert Stalker",
        "Sam Esteves",
        "Daniel Eisner",
        "Helen O'Sullivan",
        "Anders Whist",
        "Sabrina Paez-Parent",
        "Yubai Liu",
        "Michael Pham-Hung",
        "Wendy Li",
        "Dylan Cattanach",
        "Daniel Quinto",
        "Cat Pelletier",
        "Marc Hodges",
        "Nancy Warren",
        "Ofer Shai",
    ]


def build_inputs(df_league: pd.DataFrame, team_bids: Dict[str, Any] | None):
    data_league = df_league.to_dict(orient="records")

    team_rosters: Dict[str, list[str]] = {}
    for player in data_league:
        team = no_emoji(player["Team"])
        team_rosters.setdefault(team, []).append(player["Full Name"])
    team_names = list(team_rosters.keys())

    player_salaries = {player["Full Name"]: int(player["Cap Impact"]) for player in data_league}
    player_genders = {player["Full Name"]: player["Gender"] for player in data_league}

    protected_players_dict = {team: [] for team in team_names}
    player_bids: Dict[str, Dict[str, int]] = {}

    if team_bids is not None:
        for team, payload in team_bids.items():
            clean_team = no_emoji(team).strip()
            protected_players = payload.get("protected_players", [])
            protected_players = [p for p in protected_players if "WILD" not in p]
            protected_players_dict[clean_team] = protected_players[:3]

            for player, bid in payload.get("bids", {}).items():
                player_bids.setdefault(player, {})
                player_bids[player][clean_team] = parse_bid_value(bid)

    # Fill missing bids with salary baseline.
    for player in player_salaries:
        player_bids.setdefault(player, {})
        for team in team_names:
            player_bids[player].setdefault(team, player_salaries[player])

    return team_rosters, player_bids, player_genders, player_salaries, protected_players_dict


def parse_args():
    default_base = os.path.dirname(os.path.abspath(__file__))
    default_league = os.path.join(default_base, "saved_data", "League_page.csv")
    default_standings = os.path.join(default_base, "saved_data", "Standings_page.csv")
    default_team_bids = os.path.join(os.path.expanduser("~"), "Downloads", "team_bids.json")
    default_service_account = os.path.join(
        os.path.dirname(os.path.dirname(default_base)),
        "SVA",
        "SVA",
        "g_TPL",
        "tpl_trader2",
        "tpltrader-project-5964a2ad23f0.json",
    )
    default_folder_id = "1CUtQ61Dya1X37y3h6uhpIsGh2W43srah"

    parser = argparse.ArgumentParser(description="Run TPL algo locally without Streamlit UI.")
    parser.add_argument("--league", default=default_league, help="Path to League_page.csv")
    parser.add_argument("--standings", default=default_standings, help="Path to Standings_page.csv")
    parser.add_argument(
        "--team-bids",
        default=default_team_bids,
        help="Path to team_bids JSON file shaped like {team: {bids: {...}, protected_players: [...]}}",
    )
    parser.add_argument("--refresh-bids", action="store_true", help="Refresh bids from Google Sheets before running.")
    parser.add_argument("--folder-id", default=default_folder_id, help="Google Drive folder id containing team sheets.")
    parser.add_argument("--service-account", default=default_service_account, help="Path to service account JSON for fetching bids.")
    parser.add_argument(
        "--no-bids",
        action="store_true",
        help="Ignore team-bids and use salary-as-bid baseline for all players/teams.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.exists(args.league):
        raise FileNotFoundError(f"League CSV not found: {args.league}")
    if not os.path.exists(args.standings):
        raise FileNotFoundError(f"Standings CSV not found: {args.standings}")

    team_bids = None
    if not args.no_bids:
        if args.refresh_bids or not os.path.exists(args.team_bids):
            print(f"Fetching latest bids from Google Sheets -> {args.team_bids}")
            if not os.path.exists(args.service_account):
                raise FileNotFoundError(
                    f"Service account JSON not found: {args.service_account}\n"
                    "Provide --service-account <path> or use --no-bids."
                )
            fetch_and_save_team_bids(args.service_account, args.folder_id, args.team_bids)
        else:
            print(f"Using local bids file -> {args.team_bids}")

        if not os.path.exists(args.team_bids):
            raise FileNotFoundError(
                f"team_bids JSON not found: {args.team_bids}\n"
                "Provide --team-bids <path> or use --no-bids."
            )
        with open(args.team_bids, "r", encoding="utf-8") as f:
            team_bids = json.load(f)

    df_league = load_league_data_from_path(args.league)
    cap_ceiling, cap_floor = load_standings_data_from_path(args.standings)

    team_rosters, player_bids, player_genders, player_salaries, protected_players_dict = build_inputs(df_league, team_bids)

    rosters, count_team_trades, trades = run_algo(
        team_rosters,
        player_bids,
        player_genders,
        default_captains(),
        player_salaries,
        protected_players_dict,
        cap_ceiling,
        cap_floor,
    )

    print("\n=== Local Algo Summary ===")
    print(f"Trades: {len(trades)}")
    for team in sorted(count_team_trades):
        print(f"  {team}: {count_team_trades[team]}")
    print("Done.")


if __name__ == "__main__":
    main()
