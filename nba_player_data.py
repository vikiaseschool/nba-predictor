import csv
from nba_api.stats.static import players, teams
import pandas as pd
import time
from nba_api.stats.endpoints import PlayerGameLog

#vytvori csv se startovnimi petkami
def get_starting_fives():
    players_data = [
        {"TEAM_NAME": "Atlanta Hawks", "PLAYERS": [
            {"PLAYER_NAME": "Trae Young", "POSITION": "PG"},
            {"PLAYER_NAME": "Dyson Daniels", "POSITION": "SG"},
            {"PLAYER_NAME": "Zaccharie Risacher", "POSITION": "SF"},
            {"PLAYER_NAME": "Jalen Johnson", "POSITION": "PF"},
            {"PLAYER_NAME": "Clint Capela", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Boston Celtics", "PLAYERS": [
            {"PLAYER_NAME": "Jrue Holiday", "POSITION": "PG"},
            {"PLAYER_NAME": "Derrick White", "POSITION": "SG"},
            {"PLAYER_NAME": "Jaylen Brown", "POSITION": "SF"},
            {"PLAYER_NAME": "Jayson Tatum", "POSITION": "PF"},
            {"PLAYER_NAME": "Kristaps Porziņģis", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Brooklyn Nets", "PLAYERS": [
            {"PLAYER_NAME": "Dennis Schröder", "POSITION": "PG"},
            {"PLAYER_NAME": "Cam Thomas", "POSITION": "SG"},
            {"PLAYER_NAME": "Cameron Johnson", "POSITION": "SF"},
            {"PLAYER_NAME": "Dorian Finney-Smith", "POSITION": "PF"},
            {"PLAYER_NAME": "Nic Claxton", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Charlotte Hornets", "PLAYERS": [
            {"PLAYER_NAME": "LaMelo Ball", "POSITION": "PG"},
            {"PLAYER_NAME": "Brandon Miller", "POSITION": "SG"},
            {"PLAYER_NAME": "Jaden Ivey", "POSITION": "SF"},
            {"PLAYER_NAME": "Miles Bridges", "POSITION": "PF"},
            {"PLAYER_NAME": "Mark Williams", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Chicago Bulls", "PLAYERS": [
            {"PLAYER_NAME": "Josh Giddey", "POSITION": "PG"},
            {"PLAYER_NAME": "Coby White", "POSITION": "SG"},
            {"PLAYER_NAME": "Zach LaVine", "POSITION": "SF"},
            {"PLAYER_NAME": "Patrick Williams", "POSITION": "PF"},
            {"PLAYER_NAME": "Nikola Vučević", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Cleveland Cavaliers", "PLAYERS": [
            {"PLAYER_NAME": "Darius Garland", "POSITION": "PG"},
            {"PLAYER_NAME": "Donovan Mitchell", "POSITION": "SG"},
            {"PLAYER_NAME": "Isaac Okoro", "POSITION": "SF"},
            {"PLAYER_NAME": "Evan Mobley", "POSITION": "PF"},
            {"PLAYER_NAME": "Jarrett Allen", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Dallas Mavericks", "PLAYERS": [
            {"PLAYER_NAME": "Luka Dončić", "POSITION": "PG"},
            {"PLAYER_NAME": "Kyrie Irving", "POSITION": "SG"},
            {"PLAYER_NAME": "Klay Thompson", "POSITION": "SF"},
            {"PLAYER_NAME": "P.J. Washington", "POSITION": "PF"},
            {"PLAYER_NAME": "Dereck Lively II", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Denver Nuggets", "PLAYERS": [
            {"PLAYER_NAME": "Jamal Murray", "POSITION": "PG"},
            {"PLAYER_NAME": "Christian Braun", "POSITION": "SG"},
            {"PLAYER_NAME": "Michael Porter Jr.", "POSITION": "SF"},
            {"PLAYER_NAME": "Aaron Gordon", "POSITION": "PF"},
            {"PLAYER_NAME": "Nikola Jokić", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Detroit Pistons", "PLAYERS": [
            {"PLAYER_NAME": "Cade Cunningham", "POSITION": "PG"},
            {"PLAYER_NAME": "Jaden Ivey", "POSITION": "SG"},
            {"PLAYER_NAME": "Tim Hardaway Jr.", "POSITION": "SF"},
            {"PLAYER_NAME": "Tobias Harris", "POSITION": "PF"},
            {"PLAYER_NAME": "Jalen Duren", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Golden State Warriors", "PLAYERS": [
            {"PLAYER_NAME": "Stephen Curry", "POSITION": "PG"},
            {"PLAYER_NAME": "Brandin Podziemski", "POSITION": "SG"},
            {"PLAYER_NAME": "Andrew Wiggins", "POSITION": "SF"},
            {"PLAYER_NAME": "Jonathan Kuminga", "POSITION": "PF"},
            {"PLAYER_NAME": "Kevon Looney", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Houston Rockets", "PLAYERS": [
            {"PLAYER_NAME": "Fred VanVleet", "POSITION": "PG"},
            {"PLAYER_NAME": "Jalen Green", "POSITION": "SG"},
            {"PLAYER_NAME": "Dillon Brooks", "POSITION": "SF"},
            {"PLAYER_NAME": "Jabari Smith Jr.", "POSITION": "PF"},
            {"PLAYER_NAME": "Alperen Sengun", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Indiana Pacers", "PLAYERS": [
            {"PLAYER_NAME": "Tyrese Haliburton", "POSITION": "PG"},
            {"PLAYER_NAME": "Andrew Nembhard", "POSITION": "SG"},
            {"PLAYER_NAME": "Bennedict Mathurin", "POSITION": "SF"},
            {"PLAYER_NAME": "Pascal Siakam", "POSITION": "PF"},
            {"PLAYER_NAME": "Myles Turner", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Los Angeles Clippers", "PLAYERS": [
            {"PLAYER_NAME": "James Harden", "POSITION": "PG"},
            {"PLAYER_NAME": "Kris Dunn", "POSITION": "SG"},
            {"PLAYER_NAME": "Norman Powell", "POSITION": "SF"},
            {"PLAYER_NAME": "Bones Hyland", "POSITION": "PF"},
            {"PLAYER_NAME": "Ivica Zubac", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Los Angeles Lakers", "PLAYERS": [
            {"PLAYER_NAME": "Austin Reaves", "POSITION": "PG"},
            {"PLAYER_NAME": "Dalton Knecht", "POSITION": "SG"},
            {"PLAYER_NAME": "Rui Hachimura", "POSITION": "SF"},
            {"PLAYER_NAME": "LeBron James", "POSITION": "PF"},
            {"PLAYER_NAME": "Anthony Davis", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Memphis Grizzlies", "PLAYERS": [
            {"PLAYER_NAME": "Ja Morant", "POSITION": "PG"},
            {"PLAYER_NAME": "Desmond Bane", "POSITION": "SG"},
            {"PLAYER_NAME": "Jaylen Wells", "POSITION": "SF"},
            {"PLAYER_NAME": "Jaren Jackson Jr.", "POSITION": "PF"},
            {"PLAYER_NAME": "Brandon Clarke", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Miami Heat", "PLAYERS": [
            {"PLAYER_NAME": "Tyler Herro", "POSITION": "PG"},
            {"PLAYER_NAME": "Duncan Robinson", "POSITION": "SG"},
            {"PLAYER_NAME": "Jimmy Butler", "POSITION": "SF"},
            {"PLAYER_NAME": "Haywood Highsmith", "POSITION": "PF"},
            {"PLAYER_NAME": "Bam Adebayo", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Milwaukee Bucks", "PLAYERS": [
            {"PLAYER_NAME": "Damian Lillard", "POSITION": "PG"},
            {"PLAYER_NAME": "Khris Middleton", "POSITION": "SG"},
            {"PLAYER_NAME": "Taurean Prince", "POSITION": "SF"},
            {"PLAYER_NAME": "Giannis Antetokounmpo", "POSITION": "PF"},
            {"PLAYER_NAME": "Brook Lopez", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Minnesota Timberwolves", "PLAYERS": [
            {"PLAYER_NAME": "Mike Conley", "POSITION": "PG"},
            {"PLAYER_NAME": "Anthony Edwards", "POSITION": "SG"},
            {"PLAYER_NAME": "Jaden Ivey", "POSITION": "SF"},
            {"PLAYER_NAME": "Julius Randle", "POSITION": "PF"},
            {"PLAYER_NAME": "Rudy Gobert", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "New Orleans Pelicans", "PLAYERS": [
            {"PLAYER_NAME": "Dejounte Murray", "POSITION": "PG"},
            {"PLAYER_NAME": "CJ McCollum", "POSITION": "SG"},
            {"PLAYER_NAME": "Trey Murphy III", "POSITION": "SF"},
            {"PLAYER_NAME": "Herbert Jones", "POSITION": "PF"},
            {"PLAYER_NAME": "Yves Missi", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "New York Knicks", "PLAYERS": [
            {"PLAYER_NAME": "Jalen Brunson", "POSITION": "PG"},
            {"PLAYER_NAME": "Matisse Thybulle", "POSITION": "SG"},
            {"PLAYER_NAME": "Josh Hart", "POSITION": "SF"},
            {"PLAYER_NAME": "OG Anunoby", "POSITION": "PF"},
            {"PLAYER_NAME": "Karl-Anthony Towns", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Oklahoma City Thunder", "PLAYERS": [
            {"PLAYER_NAME": "Shai Gilgeous-Alexander", "POSITION": "PG"},
            {"PLAYER_NAME": "Chet Holmgren", "POSITION": "SG"},
            {"PLAYER_NAME": "Luguentz Dort", "POSITION": "SF"},
            {"PLAYER_NAME": "Jalen Williams", "POSITION": "PF"},
            {"PLAYER_NAME": "Isaiah Hartenstein", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Orlando Magic", "PLAYERS": [
            {"PLAYER_NAME": "Jalen Suggs", "POSITION": "PG"},
            {"PLAYER_NAME": "Kentavious Caldwell-Pope", "POSITION": "SG"},
            {"PLAYER_NAME": "Tristan da Silva", "POSITION": "SF"},
            {"PLAYER_NAME": "Wendell Carter Jr.", "POSITION": "PF"},
            {"PLAYER_NAME": "Goga Bitadze", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Philadelphia 76ers", "PLAYERS": [
            {"PLAYER_NAME": "Tyrese Maxey", "POSITION": "PG"},
            {"PLAYER_NAME": "Kelly Oubre Jr.", "POSITION": "SG"},
            {"PLAYER_NAME": "Paul George", "POSITION": "SF"},
            {"PLAYER_NAME": "Guerschon Yabusele", "POSITION": "PF"},
            {"PLAYER_NAME": "Joel Embiid", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Phoenix Suns", "PLAYERS": [
            {"PLAYER_NAME": "Tyus Jones", "POSITION": "PG"},
            {"PLAYER_NAME": "Devin Booker", "POSITION": "SG"},
            {"PLAYER_NAME": "Bradley Beal", "POSITION": "SF"},
            {"PLAYER_NAME": "Kevin Durant", "POSITION": "PF"},
            {"PLAYER_NAME": "Jusuf Nurkić", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Portland Trail Blazers", "PLAYERS": [
            {"PLAYER_NAME": "Anfernee Simons", "POSITION": "PG"},
            {"PLAYER_NAME": "Shaedon Sharpe", "POSITION": "SG"},
            {"PLAYER_NAME": "Toumani Camara", "POSITION": "SF"},
            {"PLAYER_NAME": "Jerami Grant", "POSITION": "PF"},
            {"PLAYER_NAME": "Deandre Ayton", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Sacramento Kings", "PLAYERS": [
            {"PLAYER_NAME": "De'Aaron Fox", "POSITION": "PG"},
            {"PLAYER_NAME": "Malik Monk", "POSITION": "SG"},
            {"PLAYER_NAME": "DeMar DeRozan", "POSITION": "SF"},
            {"PLAYER_NAME": "Keegan Murray", "POSITION": "PF"},
            {"PLAYER_NAME": "Domantas Sabonis", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "San Antonio Spurs", "PLAYERS": [
            {"PLAYER_NAME": "Chris Paul", "POSITION": "PG"},
            {"PLAYER_NAME": "Devin Vassell", "POSITION": "SG"},
            {"PLAYER_NAME": "Harrison Barnes", "POSITION": "SF"},
            {"PLAYER_NAME": "Jeremy Sochan", "POSITION": "PF"},
            {"PLAYER_NAME": "Victor Wembanyama", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Toronto Raptors", "PLAYERS": [
            {"PLAYER_NAME": "Scottie Barnes", "POSITION": "PG"},
            {"PLAYER_NAME": "Gradey Dick", "POSITION": "SG"},
            {"PLAYER_NAME": "RJ Barrett", "POSITION": "SF"},
            {"PLAYER_NAME": "Ochai Agbaji", "POSITION": "PF"},
            {"PLAYER_NAME": "Jakob Pöltl", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Utah Jazz", "PLAYERS": [
            {"PLAYER_NAME": "Keyonte George", "POSITION": "PG"},
            {"PLAYER_NAME": "Collin Sexton", "POSITION": "SG"},
            {"PLAYER_NAME": "Lauri Markkanen", "POSITION": "SF"},
            {"PLAYER_NAME": "John Collins", "POSITION": "PF"},
            {"PLAYER_NAME": "Walker Kessler", "POSITION": "C"}
        ]},
        {"TEAM_NAME": "Washington Wizards", "PLAYERS": [
            {"PLAYER_NAME": "Jordan Poole", "POSITION": "PG"},
            {"PLAYER_NAME": "Malcolm Brogdon", "POSITION": "SG"},
            {"PLAYER_NAME": "Bilal Coulibaly", "POSITION": "SF"},
            {"PLAYER_NAME": "Kyle Kuzma", "POSITION": "PF"},
            {"PLAYER_NAME": "Alexandre Sarr", "POSITION": "C"}
        ]}
    ]

    def get_player_id(player_name):
        player_list = players.get_players()
        print(player_list)
        player = next((p for p in player_list if p['full_name'] == player_name), None)

        if player:
            player_id = player['id']
            return player_id
        else:
            print(f"Player {player_name} not found!")
            return None

    def get_id(team_name):
        nba_teams = teams.get_teams()
        team = [team for team in nba_teams if team['full_name'] == team_name][0]
        return team['id']

    csv_data = []

    for team in players_data:
        team_name = team["TEAM_NAME"]
        team_id = get_id(team_name)

        if not team_id:
            print(f"Team {team_name} not found!")
            continue

        for player in team["PLAYERS"]:
            player_name = player["PLAYER_NAME"]
            position = player["POSITION"]
            player_id = get_player_id(player_name)

            if player_id:
                csv_data.append({
                    "PLAYER_ID": player_id,
                    "PLAYER_NAME": player_name,
                    "TEAM_NAME": team_name,
                    "TEAM_ID": team_id,
                    "POSITION": position
                })
            else:
                print(f"Player {player_name} not found!")

    csv_file = "nba_starting_lineups.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["PLAYER_ID", "PLAYER_NAME", "TEAM_NAME", "TEAM_ID", "POSITION"])
        writer.writeheader()
        writer.writerows(csv_data)
    print(f"Data has been saved to {csv_file}")

#ziskava logy hracu za celou sezonu 2023-24 a 2024-25
def get_player_logs():
    def create_team_player_performance(input_csv, team_name):
        try:
            lineup_data = pd.read_csv(input_csv)
            team_players = lineup_data[lineup_data['TEAM_NAME'] == team_name]
            player_ids = team_players['PLAYER_ID'].tolist()
            team_id_map = team_players.set_index('PLAYER_ID')['TEAM_ID'].to_dict()  # Precompute mapping
        except Exception as e:
            print(f"Error reading input file: {e}")
            return None

        print(player_ids)

        seasons = ['2023-24', '2024-25']
        all_player_stats = []

        for player_id in player_ids:
            for season in seasons:
                for attempt in range(3):
                    try:
                        game_logs = PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
                        game_logs['TEAM_ID'] = team_id_map.get(player_id, None)  # Map TEAM_ID efficiently
                        all_player_stats.append(game_logs)
                        break
                    except Exception as e:
                        print(f"Error fetching data for Player ID {player_id}, Season {season}, attemp {attempt+1}: {e}")
                        time.sleep(5)

        if all_player_stats:
            return pd.concat(all_player_stats, ignore_index=True)
        else:
            print("No player data retrieved. Please check your inputs or API connectivity.")
            return None

    stats = []
    for team in teams.get_teams():
        team_name = team['full_name']
        print(f"Getting player logs for {team_name}")
        combined_stats = create_team_player_performance("nba_starting_lineups.csv", team_name)
        if combined_stats is not None:
            stats.append(combined_stats)

    # Save the final combined DataFrame to CSV
    if stats:
        final_stats = pd.concat(stats, ignore_index=True)
        final_stats.to_csv("team_player_performance.csv", index=False)
        print("All team player performances saved to CSV.")

def format_logs():
    def get_player_name(player_id):
        all_players = players.get_players()
        player = next((player for player in all_players if player['id'] == player_id), None)
        if player:
            return player['full_name']
        else:
            return "Player not found"

    logs = pd.read_csv("team_player_performance.csv")
    logs = logs.drop_duplicates()
    logs['PLAYER_NAME'] = logs['Player_ID'].apply(get_player_name)

    logs['GAME_DATE'] = pd.to_datetime(logs['GAME_DATE'], format='%b %d, %Y').dt.strftime('%Y-%m-%d')
    logs['WL'] = logs['WL'].replace({'W': 1, 'L': 0})

    logs = logs.drop(columns=['VIDEO_AVAILABLE', 'MATCHUP'])
    logs.rename(columns={'Player_ID': 'PLAYER_ID'}, inplace=True)
    logs.rename(columns={'Game_ID': 'GAME_ID'}, inplace=True)

    logs.to_csv("players_stats_24-25_final.csv", index=False)
    print("Logs formatted and saved to players_stats_24-25_final.csv")

def add_last_5():
    player_data = pd.read_csv("players_stats_24-25_final.csv")
    stats_to_average = [
        "WL", "MIN", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT",
        "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST", "STL",
        "BLK", "TOV", "PF", "PTS", "PLUS_MINUS"
    ]

    last_5_stats = pd.DataFrame(index=player_data.index)
    grouped = player_data.groupby("PLAYER_ID")
    #optimalized via GitHub Copilot
    for player_id, group in grouped:
        group = group.sort_values(by="GAME_DATE", ascending=False)
        rolling_stats = (group[stats_to_average].rolling(window=5, min_periods=1).mean().shift(0))
        for stat in stats_to_average:
            last_5_stats.loc[group.index, f"LAST_5_{stat}"] = rolling_stats[stat]
    #end of AI optimalization
    player_data = pd.concat([player_data, last_5_stats], axis=1)

    player_data.to_csv("players_stats_with_last_5.csv", index=False)
    print("Last 5 games averages added to players_stats_with_last_5.csv")

def merge_players_with_games():
    players = pd.read_csv("players_stats_with_last_5.csv")
    games = pd.read_csv("test_dataset.csv")

    # Filter games to only include data from 2023-10-01 and newer
    games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])
    games = games[games['GAME_DATE'] >= '2023-10-01']

    # Create an empty list for the final merged data
    merged_data = []

    # Iterate through the players
    for _, player_row in players.iterrows():
        player_team_id = player_row['TEAM_ID']
        player_game_date = player_row['GAME_DATE']

        # Filter matching games
        matched_games = games[(games['GAME_DATE'] == player_game_date) & (games['TEAM_ID'] == player_team_id)]

        if not matched_games.empty:
            # If TEAM_ID matches, add the stats as MATCH_{original_column_name}
            for _, game_row in matched_games.iterrows():
                new_row = player_row.copy()
                for col in game_row.index:
                    if 'OPP' not in col:
                        new_row[f'MATCH_{col}'] = game_row[col]
                merged_data.append(new_row)
        else:
            # If TEAM_ID does not match, add opponent's stats
            for _, game_row in matched_games.iterrows():
                new_row = player_row.copy()
                new_row['SEASON_ID'] = game_row['SEASON_ID']
                new_row['GAME_ID'] = game_row['GAME_ID']
                new_row['MATCHUP'] = game_row['MATCHUP']
                for col in game_row.index:
                    if 'OPP' in col:
                        new_row[f'MATCH_{col.replace("OPP_", "")}'] = game_row[col]
                merged_data.append(new_row)

    # Convert merged data into a DataFrame
    merged_df = pd.DataFrame(merged_data)

    # Save to CSV
    merged_df.to_csv('test_dataset_players.csv', index=False)

get_player_logs()
format_logs()
add_last_5()
merge_players_with_games()



