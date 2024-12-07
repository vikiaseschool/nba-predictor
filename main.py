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
        # Filtrování zápasů pro daný tým (domácí nebo hostující)
        team_games = games_df[(games_df['TEAM_ID'] == team_id) | (games_df['OPP_TEAM_ID'] == team_id)]

        # Seřazení zápasů podle data (nejnovější zápas jako první)
        team_games = team_games.sort_values(by='GAME_DATE', ascending=False)

        # Vytvoření prázdného seznamu pro statistiky zápasů
        team_games_stats = []

        # Pro každý zápas zjistíme, zda byl tým domácí nebo hostující
        for _, game in team_games.iterrows():
            game_stats = {}

            # Pokud je tým domácí (IS_HOME == 1)
            if game['TEAM_ID'] == team_id:
                # Uložíme všechny požadované sloupce pro domácí tým
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS',
                            'IS_HOME']:
                    game_stats[col] = game[col]
                # Přidáme statistiky pro domácí tým do seznamu
                team_games_stats.append(game_stats)

            # Pokud je tým hostující (IS_HOME == 0)
            elif game['OPP_TEAM_ID'] == team_id:
                # Uložíme všechny požadované sloupce pro hostující tým s předponou OPP_
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS',
                            'IS_HOME']:
                    game_stats[col] = game[f"OPP_{col}"]
                # Přidáme statistiky pro hostující tým do seznamu
                team_games_stats.append(game_stats)

        # Vrácení posledních n zápasů (se statistikami)
        return team_games_stats[:n]

    # Funkce pro získání posledních n vzájemných zápasů mezi dvěma týmy
    def get_last_n_head_to_head_games(games_df, team_id_1, team_id_2, n=5):
        # Filtrování zápasů mezi týmy team_id_1 a team_id_2
        head_to_head_games = games_df[((games_df['TEAM_ID'] == team_id_1) & (games_df['OPP_TEAM_ID'] == team_id_2)) |
                                      ((games_df['TEAM_ID'] == team_id_2) & (games_df['OPP_TEAM_ID'] == team_id_1))]

        # Seřazení zápasů podle data (nejnovější zápas jako první)
        head_to_head_games = head_to_head_games.sort_values(by='GAME_DATE', ascending=False)

        # Vytvoření prázdných seznamů pro statistiky zápasů
        h2h_stats_team1 = []
        h2h_stats_team2 = []

        # Pro každý zápas zjistíme, zda byl team_id_1 domácí nebo hostující, a to samé pro team_id_2
        for _, game in head_to_head_games.iterrows():
            game_stats_team1 = {}
            game_stats_team2 = {}

            # Pokud team_id_1 byl domácí
            if game['TEAM_ID'] == team_id_1:
                # Uložíme všechny požadované sloupce pro domácí tým (team_id_1)
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS', 'IS_HOME']:
                    game_stats_team1[col] = game[col]
                # Uložíme statistiky pro tým 1
                h2h_stats_team1.append(game_stats_team1)

            # Pokud team_id_2 byl domácí
            if game['TEAM_ID'] == team_id_2:
                # Uložíme všechny požadované sloupce pro domácí tým (team_id_2)
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS', 'IS_HOME']:
                    game_stats_team2[col] = game[col]
                # Uložíme statistiky pro tým 2
                h2h_stats_team2.append(game_stats_team2)

            # Pokud je team_id_1 hostující tým
            if game['OPP_TEAM_ID'] == team_id_1:
                # Uložíme všechny požadované sloupce pro hostující tým (team_id_1) s předponou OPP_
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS', 'IS_HOME']:
                    game_stats_team1[col] = game[f"OPP_{col}"]
                # Uložíme statistiky pro tým 1
                h2h_stats_team1.append(game_stats_team1)

            # Pokud je team_id_2 hostující tým
            if game['OPP_TEAM_ID'] == team_id_2:
                # Uložíme všechny požadované sloupce pro hostující tým (team_id_2) s předponou OPP_
                for col in ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                            'PLUS_MINUS', 'IS_HOME']:
                    game_stats_team2[col] = game[f"OPP_{col}"]
                # Uložíme statistiky pro tým 2
                h2h_stats_team2.append(game_stats_team2)

        # Vrácení posledních n vzájemných zápasů mezi těmito dvěma týmy
        return h2h_stats_team1[:n], h2h_stats_team2[:n]

    def calculate_avg(last_5_games):
        avg_dict = {}
        for key in last_5_games[0]:
            # Sečteme hodnoty pro daný klíč z každého slovníku
            total = sum(float(d[key]) for d in last_5_games if key in d)
            # Vypočteme průměr
            avg_dict[key] = total / len(last_5_games)

        return avg_dict

    def add_avg_columns(games_df):
        last_5_columns = ['WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                          'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS']

        for idx, row in match_ready.iterrows():
            team_id = row['TEAM_ID']
            opp_team_id = row['OPP_TEAM_ID']

            # Získání posledních 5 zápasů pro tým a soupeře
            team_last_5_games = get_last_n_games(games_df, team_id)
            opp_team_last_5_games = get_last_n_games(games_df, opp_team_id)

            # Získání posledních 5 vzájemných zápasů
            h2h_last_5_team1, h2h_last_5_team2 = get_last_n_head_to_head_games(games_df, team_id, opp_team_id)

            # Výpočet průměrných hodnot
            last_5_avg = calculate_avg(team_last_5_games)
            opp_last_5_avg = calculate_avg(opp_team_last_5_games)
            last_h2h_avg_team1 = calculate_avg(h2h_last_5_team1)
            opp_last_h2h_avg_team2 = calculate_avg(h2h_last_5_team2)

            # Přidání průměrných hodnot do sloupců
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
    # Fetch team IDs
    team_id = get_id(team_name)
    opp_team_id = get_id(opp_team_name)

    # Format date
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    date = date_obj.strftime('%Y-%m-%d')

    # Generate match data
    make_match_csv(team_id, opp_team_id, date)
    get_match_csv_ready(team_name, opp_team_name, date)

    # Load models and imputer
    rf_wl = joblib.load('rf_wl_model.pkl')
    rf_pts = joblib.load('rf_pts_model.pkl')
    rf_pts_o = joblib.load('rf_pts_o_model.pkl')
    imputer = joblib.load('imputer_model.pkl')

    # Load and preprocess match data
    match_ready = pd.read_csv('match_ready.csv')
    required_features = imputer.feature_names_in_

    # Zajištění, že všechny požadované sloupce jsou přítomny
    for feature in required_features:
        if feature not in match_ready.columns:
            match_ready[feature] = 0

    # Zajištění, že sloupce jsou ve správném pořadí
    match_ready = match_ready[required_features]

    # Transformace dat pomocí imputace
    match_ready_imputed = imputer.transform(match_ready)

    # Generate predictions
    wl_prediction = rf_wl.predict(match_ready_imputed)
    pts_prediction = rf_pts.predict(match_ready_imputed)
    opp_pts_prediction = rf_pts_o.predict(match_ready_imputed)

    # Return predictions
    return int(wl_prediction[0]),round(float(pts_prediction[0])),round(float(opp_pts_prediction[0]))

def get_stats(team_name, opp_team_name, date):
    import pandas as pd

    # Načtení dat
    games_df = pd.read_csv('combined_games_2021_2025.csv')
    match_df = pd.read_csv('match_info.csv')

    # Získání ID týmů
    team_id = get_id(team_name)
    opp_team_id = get_id(opp_team_name)

    def get_last_n_games(games_df, team_id, date, n=5):
        # Filtrování zápasů pro daný tým (domácí nebo hostující) a před datem
        team_games = games_df[((games_df['TEAM_ID'] == team_id) | (games_df['OPP_TEAM_ID'] == team_id)) &
                              (games_df['GAME_DATE'] < date)]
        # Seřazení zápasů podle data (nejnovější zápas jako první)
        team_games = team_games.sort_values(by='GAME_DATE', ascending=False)
        return team_games[:n]

    def get_last_n_head_to_head_games(games_df, team_id_1, team_id_2, date, n=5):
        # Filtrování vzájemných zápasů před datem
        head_to_head_games = games_df[(((games_df['TEAM_ID'] == team_id_1) & (games_df['OPP_TEAM_ID'] == team_id_2)) |
                                       ((games_df['TEAM_ID'] == team_id_2) & (games_df['OPP_TEAM_ID'] == team_id_1))) &
                                      (games_df['GAME_DATE'] < date)]
        head_to_head_games = head_to_head_games.sort_values(by='GAME_DATE', ascending=False)
        return head_to_head_games[:n]

    def games_to_dict_list(games_df):
        """Převede DataFrame na seznam slovníků obsahujících požadované atributy."""
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

    # Získání posledních 5 zápasů pro tým a soupeře, před zadaným datem
    last_5_games_team = get_last_n_games(games_df, team_id, date)
    last_5_games_opp_team = get_last_n_games(games_df, opp_team_id, date)
    last_5_h2h = get_last_n_head_to_head_games(games_df, team_id, opp_team_id, date)

    # Konverze na seznamy slovníků
    last_5_games_team_dict = games_to_dict_list(last_5_games_team)
    last_5_games_opp_team_dict = games_to_dict_list(last_5_games_opp_team)
    last_5_h2h_dict = games_to_dict_list(last_5_h2h)

    return last_5_games_team_dict, last_5_games_opp_team_dict, last_5_h2h_dict

