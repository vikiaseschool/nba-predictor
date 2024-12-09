import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams

def get_filtered_historical_21_25():
    def get_games_for_seasons(start_season, end_season):
        all_games = []
        for season in range(start_season, end_season + 1):
            season_str = f"{season}-{str(season + 1)[-2:]}"  #2021-22
            print(f"Stahuji data pro sezónu {season_str}...")

            gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season_str)
            games = gamefinder.get_data_frames()[0]
            all_games.append(games)

        return pd.concat(all_games, ignore_index=True)

    def add_is_home_column(games_df):
        is_home_list = []
        for _, row in games_df.iterrows():
            matchup = row['MATCHUP']
            if ' vs. ' in matchup:  #LAL vs BOS
                home_team, away_team = matchup.split(" vs. ")
            elif ' @ ' in matchup:  #LAL @ BOS
                away_team, home_team = matchup.split(" @ ")
            else:
                print(f"Neznámý formát MATCHUP: {matchup}")
                is_home_list.append(None)
                continue

            if row['TEAM_ABBREVIATION'] == home_team:
                is_home_list.append(1)
            elif row['TEAM_ABBREVIATION'] == away_team:
                is_home_list.append(0)
            else:
                print(f"Tým {row['TEAM_ABBREVIATION']} se neobjevuje v zápasu {matchup}")
                is_home_list.append(None)

        games_df['IS_HOME'] = is_home_list
        return games_df

    def filter_games_by_month(games_df):
        games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])

        games_df = games_df[games_df['GAME_DATE'].dt.month.isin([10, 11, 12, 1, 2, 3, 4, 5, 6])]
        games_df['WL'] = games_df['WL'].replace({'W': 1, 'L': 0})
        nba_teams = teams.get_teams()
        nba_team_ids = [team['id'] for team in nba_teams]
        games_df = games_df[games_df['TEAM_ID'].isin(nba_team_ids)]

        return games_df


    games_df = get_games_for_seasons(2021, 2024)
    games_df = add_is_home_column(games_df)
    games_df = filter_games_by_month(games_df)

    output_file = "historical_games_filtered_2021_2025.csv"
    games_df.to_csv(output_file, index=False)
    print(f"Data uložena do souboru {output_file}")

def get_combined():
    def combine_home_away(games_df):
        combined_games = []
        grouped = games_df.groupby(['GAME_DATE', 'GAME_ID'])
        for (game_date, game_id), group in grouped:
            if len(group) == 2:
                home_game = group[group['IS_HOME'] == 1].iloc[0]
                away_game = group[group['IS_HOME'] == 0].iloc[0]

                combined_game = home_game.copy()

                for col in games_df.columns:
                    if col not in ['SEASON_ID', 'GAME_ID', 'GAME_DATE', 'MATCHUP']:
                        combined_game[f"OPP_{col}"] = away_game[col]
                combined_games.append(combined_game)
            else:
                matchup = group['MATCHUP'].iloc[0] if 'MATCHUP' in group.columns else 'N/A'
                print(
                    f"Varování: Zápas na GAME_DATE {game_date} a GAME_ID {game_id} nemá protějšek. MATCHUP: {matchup}")

        combined_df = pd.DataFrame(combined_games)
        return combined_df


    games_df = pd.read_csv("historical_games_filtered_2021_2025.csv")
    combined_df = combine_home_away(games_df)

    output_file = "combined_games_2021_2025.csv"
    combined_df.to_csv(output_file, index=False)
    print(f"Data uložena do souboru {output_file}")

def get_testing_data():
    def get_last_n_games(games_df, team_id, n=5):
        team_games = games_df[(games_df['TEAM_ID'] == team_id) | (games_df['OPP_TEAM_ID'] == team_id)]

        team_games = team_games.sort_values(by='GAME_DATE', ascending=False)

        team_games_stats = []

        for _, game in team_games.iterrows():
            game_stats = {}

            if game['TEAM_ID'] == team_id:
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS',
                            'IS_HOME']:
                    game_stats[col] = game[col]
                team_games_stats.append(game_stats)

            elif game['OPP_TEAM_ID'] == team_id:
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS',
                            'IS_HOME']:
                    game_stats[col] = game[f"OPP_{col}"]
                team_games_stats.append(game_stats)

        return team_games_stats[:n]

    def get_last_n_head_to_head_games(games_df, team_id_1, team_id_2, n=5):
        head_to_head_games = games_df[((games_df['TEAM_ID'] == team_id_1) & (games_df['OPP_TEAM_ID'] == team_id_2)) |
                                      ((games_df['TEAM_ID'] == team_id_2) & (games_df['OPP_TEAM_ID'] == team_id_1))]

        head_to_head_games = head_to_head_games.sort_values(by='GAME_DATE', ascending=False)

        h2h_stats_team1 = []
        h2h_stats_team2 = []

        for _, game in head_to_head_games.iterrows():
            game_stats_team1 = {}
            game_stats_team2 = {}


            if game['TEAM_ID'] == team_id_1:
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS', 'IS_HOME']:
                    game_stats_team1[col] = game[col]
                h2h_stats_team1.append(game_stats_team1)

            if game['TEAM_ID'] == team_id_2:
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS', 'IS_HOME']:
                    game_stats_team2[col] = game[col]
                h2h_stats_team2.append(game_stats_team2)

            if game['OPP_TEAM_ID'] == team_id_1:
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS', 'IS_HOME']:
                    game_stats_team1[col] = game[f"OPP_{col}"]
                h2h_stats_team1.append(game_stats_team1)

            if game['OPP_TEAM_ID'] == team_id_2:
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS', 'IS_HOME']:
                    game_stats_team2[col] = game[f"OPP_{col}"]
                h2h_stats_team2.append(game_stats_team2)
        return h2h_stats_team1[:n], h2h_stats_team2[:n]

    def calculate_avg(last_5_games):
        avg_dict = {}
        for key in last_5_games[0]:
            total = sum(float(d[key]) for d in last_5_games if key in d)
            avg_dict[key] = total / len(last_5_games)
        return avg_dict

    def add_avg_columns(games_df):
        last_5_columns = ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                          'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS']

        for idx, row in games_df.iterrows():
            team_id = row['TEAM_ID']
            opp_team_id = row['OPP_TEAM_ID']

            team_last_5_games = get_last_n_games(games_df, team_id)
            opp_team_last_5_games = get_last_n_games(games_df, opp_team_id)

            h2h_last_5_team1, h2h_last_5_team2 = get_last_n_head_to_head_games(games_df, team_id, opp_team_id)

            last_5_avg = calculate_avg(team_last_5_games)
            opp_last_5_avg = calculate_avg(opp_team_last_5_games)
            last_h2h_avg_team1 = calculate_avg(h2h_last_5_team1)
            opp_last_h2h_avg_team2 = calculate_avg(h2h_last_5_team2)

            for col in last_5_columns:
                games_df.at[idx, f'LAST_5_{col}'] = last_5_avg.get(col, None)
                games_df.at[idx, f'OPP_LAST_5_{col}'] = opp_last_5_avg.get(col, None)
                games_df.at[idx, f'LAST_H2H_{col}'] = last_h2h_avg_team1.get(col, None)
                games_df.at[idx, f'OPP_LAST_H2H_{col}'] = opp_last_h2h_avg_team2.get(col, None)

        return games_df

    input_file = "combined_games_2021_2025.csv"
    games_df = pd.read_csv(input_file)
    games_df_with_avgs = add_avg_columns(games_df)
    output_file = "test_dataset.csv"
    games_df_with_avgs.to_csv(output_file, index=False)
    print(f"Data byla uložena do souboru {output_file}")

get_filtered_historical_21_25()
get_combined()
get_testing_data()


