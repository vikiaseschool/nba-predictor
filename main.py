import pandas as pd
import joblib
from nba_api.stats.static import teams
from datetime import datetime


def get_id(team_name):
    nba_teams = teams.get_teams()
    team = [team for team in nba_teams if team['full_name'] == team_name][0]
    return team['id']
def get_name(team_id):
    nba_teams = teams.get_teams()
    team = [team for team in nba_teams if team['id'] == team_id][0]
    return team['full_name']

def make_match_csv(team_id, opp_team_id, date):
    puvodni = pd.read_csv('combined_games_2021_2025.csv')
    match_df = pd.DataFrame(columns=puvodni.columns)

    new_row = {
        'TEAM_ID': team_id,
        'OPP_TEAM_ID': opp_team_id,
        'GAME_DATE': date,
        'IS_HOME': 1,
        'SEASON': 2024,
        'SEASON_ID': 22024
    }

    match_df = pd.concat([match_df, pd.DataFrame([new_row])], ignore_index=True)
    match_df.to_csv('match_info.csv', index=False)
def get_match_csv_ready(team_name, opp_team_name, date):
    games_df = pd.read_csv('combined_games_2021_2025.csv')
    match_df = pd.read_csv('match_info.csv')
    team_id = get_id(team_name)
    opp_team_id = get_id(opp_team_name)
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

            # Pokud je tým hostující (IS_HOME == 0)
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

        for idx, row in match_ready.iterrows():
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
                match_ready.at[idx, f'LAST_5_{col}'] = last_5_avg.get(col, None)
                match_ready.at[idx, f'OPP_LAST_5_{col}'] = opp_last_5_avg.get(col, None)
                match_ready.at[idx, f'LAST_H2H_{col}'] = last_h2h_avg_team1.get(col, None)
                match_ready.at[idx, f'OPP_LAST_H2H_{col}'] = opp_last_h2h_avg_team2.get(col, None)

        return games_df
    match_ready = pd.read_csv('match_info.csv')
    add_avg_columns(games_df)
    match_ready.to_csv('match_ready.csv', index=False)
def get_prediction(team_name, opp_team_name, date):
    team_id = get_id(team_name)
    opp_team_id = get_id(opp_team_name)

    date_obj = datetime.strptime(date, '%Y-%m-%d')
    date = date_obj.strftime('%Y-%m-%d')

    make_match_csv(team_id, opp_team_id, date)
    get_match_csv_ready(team_name, opp_team_name, date)

    rf_wl = joblib.load('rf_wl_model.pkl')
    rf_pts = joblib.load('rf_pts_model.pkl')
    rf_pts_o = joblib.load('rf_pts_o_model.pkl')
    imputer = joblib.load('imputer_model.pkl')

    match_ready = pd.read_csv('match_ready.csv')
    required_features = imputer.feature_names_in_

    for feature in required_features:
        if feature not in match_ready.columns:
            match_ready[feature] = 0

    match_ready = match_ready[required_features]
    match_ready_imputed = imputer.transform(match_ready)

    wl_prediction = rf_wl.predict(match_ready_imputed)
    pts_prediction = rf_pts.predict(match_ready_imputed)
    opp_pts_prediction = rf_pts_o.predict(match_ready_imputed)

    return int(wl_prediction[0]),round(float(pts_prediction[0])),round(float(opp_pts_prediction[0]))

def get_stats(team_name, opp_team_name, date):
    games_df = pd.read_csv('combined_games_2021_2025.csv')
    match_df = pd.read_csv('match_info.csv')

    team_id = get_id(team_name)
    opp_team_id = get_id(opp_team_name)

    def get_last_n_games(games_df, team_id, date, n=5):
        team_games = games_df[((games_df['TEAM_ID'] == team_id) | (games_df['OPP_TEAM_ID'] == team_id)) &
                              (games_df['GAME_DATE'] < date)]
        team_games = team_games.sort_values(by='GAME_DATE', ascending=False)
        return team_games[:n]

    def get_last_n_head_to_head_games(games_df, team_id_1, team_id_2, date, n=5):
        head_to_head_games = games_df[(((games_df['TEAM_ID'] == team_id_1) & (games_df['OPP_TEAM_ID'] == team_id_2)) |
                                       ((games_df['TEAM_ID'] == team_id_2) & (games_df['OPP_TEAM_ID'] == team_id_1))) &
                                      (games_df['GAME_DATE'] < date)]
        head_to_head_games = head_to_head_games.sort_values(by='GAME_DATE', ascending=False)
        return head_to_head_games[:n]

    def games_to_dict_list(games_df):
        games_list = []
        for _, row in games_df.iterrows():
            game_dict = {
                'GAME_DATE': row['GAME_DATE'],
                'TEAM_NAME': row['TEAM_NAME'],
                'OPP_TEAM_NAME': row['OPP_TEAM_NAME'],
                'PTS': row['PTS'],
                'OPP_PTS': row['OPP_PTS']
            }
            games_list.append(game_dict)
        return games_list

    last_5_games_team = get_last_n_games(games_df, team_id, date)
    last_5_games_opp_team = get_last_n_games(games_df, opp_team_id, date)
    last_5_h2h = get_last_n_head_to_head_games(games_df, team_id, opp_team_id, date)

    last_5_games_team_dict = games_to_dict_list(last_5_games_team)
    last_5_games_opp_team_dict = games_to_dict_list(last_5_games_opp_team)
    last_5_h2h_dict = games_to_dict_list(last_5_h2h)

    return last_5_games_team_dict, last_5_games_opp_team_dict, last_5_h2h_dict

