import pandas as pd
import joblib
from nba_api.stats.static import teams

def make_dataset(team1, team2, date):
    def get_team_name(team_id):
        all_teams = teams.get_teams()
        for team in all_teams:
            if team['id'] == team_id:
                return team['full_name']
        return f"Team with ID '{team_id}' not found"
    def get_team_id(team_name):
        all_teams = teams.get_teams()
        for team in all_teams:
            if team['full_name'] == team_name:
                return team['id']
        return f"Team '{team_name}' not found"

    def prepare_new_match_dataset(home_team_id, away_team_id, game_date):
        # Načtení historických dat
        data_2023_25 = pd.read_csv("final_dataset_23.csv")

        # Převod dat na datetime pro snadné filtrování
        data_2023_25['GAME_DATE'] = pd.to_datetime(data_2023_25['GAME_DATE'])

        # Funkce pro získání posledních N zápasů týmu
        def get_last_games(team_id, date, data, n=5):
            team_games = data[(data['TEAM_ID'] == team_id) & (data['GAME_DATE'] < date)]
            return team_games.sort_values('GAME_DATE', ascending=False).head(n)

        # Funkce pro získání posledních N vzájemných zápasů
        def get_last_head_to_head(team1_id, team2_id, date, data, n=5):
            h2h_games = data[((data['TEAM_ID'] == team1_id) & (data['TEAM_ID_OPP'] == team2_id)) |
                             ((data['TEAM_ID'] == team2_id) & (data['TEAM_ID_OPP'] == team1_id))]
            h2h_games = h2h_games[h2h_games['GAME_DATE'] < date]
            return h2h_games.sort_values('GAME_DATE', ascending=False).head(n)

        def calculate_averages_for_team(games, team_id):
            home_stats = []
            away_stats = []
            for _, game in games.iterrows():
                if game['TEAM_ID'] == team_id:  # Pokud je tým domácí nebo hostující
                    if game['IS_HOME'] == 1:  # Tým hraje doma
                        home_stats.append(game)
                    else:  # Tým hraje venku
                        away_stats.append(game)

            # Pokud máme domácí zápasy, spočítáme průměry pro domácí tým
            if home_stats:
                home_games_df = pd.DataFrame(home_stats)
                home_averages = {
                    "WL": home_games_df['WL'].mean(),
                    "PTS": home_games_df['PTS'].mean(),
                    "FGM": home_games_df['FGM'].mean(),
                    "FGA": home_games_df['FGA'].mean(),
                    "FG_PCT": home_games_df['FG_PCT'].mean(),
                    "FG3M": home_games_df['FG3M'].mean(),
                    "FG3A": home_games_df['FG3A'].mean(),
                    "FG3_PCT": home_games_df['FG3_PCT'].mean(),
                    "FTM": home_games_df['FTM'].mean(),
                    "FTA": home_games_df['FTA'].mean(),
                    "FT_PCT": home_games_df['FT_PCT'].mean(),
                    "OREB": home_games_df['OREB'].mean(),
                    "DREB": home_games_df['DREB'].mean(),
                    "REB": home_games_df['REB'].mean(),
                    "AST": home_games_df['AST'].mean(),
                    "STL": home_games_df['STL'].mean(),
                    "BLK": home_games_df['BLK'].mean(),
                    "TOV": home_games_df['TOV'].mean(),
                    "PF": home_games_df['PF'].mean(),
                    "PLUS_MINUS": home_games_df['PLUS_MINUS'].mean(),
                }
            else:
                home_averages = {key: 'NsN' for key in [
                    "WL", "PTS", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",
                    "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS"
                ]}

            # Pokud máme venkovní zápasy, spočítáme průměry pro hostující tým
            if away_stats:
                away_games_df = pd.DataFrame(away_stats)
                away_averages = {
                    "WL": away_games_df['WL_OPP'].mean(),
                    "PTS": away_games_df['PTS_O'].mean(),
                    "FGM": away_games_df['OPP_FGM'].mean(),
                    "FGA": away_games_df['OPP_FGA'].mean(),
                    "FG_PCT": away_games_df['OPP_FG_PCT'].mean(),
                    "FG3M": away_games_df['OPP_FG3M'].mean(),
                    "FG3A": away_games_df['OPP_FG3A'].mean(),
                    "FG3_PCT": away_games_df['OPP_FG3_PCT'].mean(),
                    "FTM": away_games_df['OPP_FTM'].mean(),
                    "FTA": away_games_df['OPP_FTA'].mean(),
                    "FT_PCT": away_games_df['OPP_FT_PCT'].mean(),
                    "OREB": away_games_df['OPP_OREB'].mean(),
                    "DREB": away_games_df['OPP_DREB'].mean(),
                    "REB": away_games_df['OPP_REB'].mean(),
                    "AST": away_games_df['OPP_AST'].mean(),
                    "STL": away_games_df['OPP_STL'].mean(),
                    "BLK": away_games_df['OPP_BLK'].mean(),
                    "TOV": away_games_df['OPP_TOV'].mean(),
                    "PF": away_games_df['OPP_PF'].mean(),
                    "PLUS_MINUS": away_games_df['OPP_PLUS_MINUS'].mean(),
                }
            else:
                away_averages = {key: 'NsN' for key in [
                    "WL", "PTS", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",
                    "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS"
                ]}

            # Pokud máme oba zápasy (domácí i venkovní), vrátíme průměry
            if home_stats and away_stats:
                final_averages = {key: (home_averages[key] + away_averages[key]) / 2 for key in home_averages}
                return final_averages

            # Pokud máme pouze domácí nebo pouze venkovní zápasy, vrátíme pouze průměry pro daný typ zápasu
            return home_averages if home_stats else away_averages

        # Funkce pro získání statistik pro vzájemné zápasy (H2H)
        def calculate_h2h_averages(games, team1_id, team2_id):
            team1_stats = calculate_averages_for_team(games, team1_id)
            team2_stats = calculate_averages_for_team(games, team2_id)

            return team1_stats, team2_stats

        # Získání statistik pro tým 1 (domácí) a tým 2 (hostující)
        last_games_team1 = get_last_games(home_team_id, game_date, data_2023_25)
        last_games_team2 = get_last_games(away_team_id, game_date, data_2023_25)
        h2h_games = get_last_head_to_head(home_team_id, away_team_id, game_date, data_2023_25)

        team1_averages = calculate_averages_for_team(last_games_team1, home_team_id)
        team2_averages = calculate_averages_for_team(last_games_team2, away_team_id)
        h2h_averages = calculate_h2h_averages(h2h_games, home_team_id, away_team_id)

        # Vytvoříme nový DataFrame s těmito sloupci (prázdný soubor)
        target_data = pd.DataFrame(columns=data_2023_25.columns)
        # Uložíme nový DataFrame (s pouze názvy sloupců) do cílového CSV souboru
        target_data.to_csv('match_info.csv', index=False)
        target_data.loc[0, 'GAME_DATE'] = game_date
        target_data.loc[0, 'TEAM_ID'] = home_team_id
        target_data.loc[0, 'TEAM_ID_OPP'] = away_team_id

        for stat in team1_averages:
            target_data.loc[0, f"LAST_5_{stat}_TEAM1"] = team1_averages[stat]
        for stat in team2_averages:
            target_data.loc[0, f"LAST_5_{stat}_TEAM2"] = team2_averages[stat]
        for stat in h2h_averages[0]:
            target_data.loc[0, f"H2H_{stat}_TEAM1"] = h2h_averages[0][stat]
        for stat in h2h_averages[1]:
            target_data.loc[0, f"H2H_{stat}_TEAM2"] = h2h_averages[1][stat]

        # Uložení do souboru
        target_data.to_csv("match_info.csv", index=False)
        print("Data byla spojena a uložena do 'match_info.csv'!")

    # Example usage:
    home_team_id = get_team_id(team1)
    away_team_id = get_team_id(team2)
    prepare_new_match_dataset(home_team_id, away_team_id, date)

def pop_columns(file):
    df = pd.read_csv(file)
    columns = ['PTS_LAST_5', 'REB_LAST_5', 'AST_LAST_5', 'FG_PCT_LAST_5', 'FT_PCT_LAST_5', 'OPP_PTS_LAST_5',
               'OPP_REB_LAST_5', 'OPP_AST_LAST_5', 'OPP_FG_PCT_LAST_5', 'OPP_FT_PCT_LAST_5', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'MATCHUP', 'HOME_TEAM', 'AWAY_TEAM',
               'OPP_TEAM_ABBREVIATION', 'OPP_TEAM_NAME', 'MATCHUP_OPP', 'OPP_HOME_TEAM', 'OPP_AWAY_TEAM', 'GAME_DATE', 'GAME_DATE_OPP', 'SEASON', 'OPP_SEASON']
    df = df.drop(columns=columns)
    df.to_csv(file, index=False)

def get_prediction(team1, team2, date):
    make_dataset(team1, team2, date)
    pop_columns('match_info.csv')

    nba_data = pd.read_csv('nba_games_filtered_23.csv')
    min_pts = nba_data['PTS'].min()
    max_pts = nba_data['PTS'].max()

    df = pd.read_csv('match_info.csv')
    rf_wl = joblib.load('rf_wl_model.pkl')        # Model pro WL
    rf_pts = joblib.load('rf_pts_model.pkl')      # Model pro PTS
    rf_pts_o = joblib.load('rf_pts_o_model.pkl')  # Model pro PTS_O
    imputer = joblib.load('imputer_model.pkl')    # Imputace

    new_data = df.iloc[0:1].drop(['WL', 'PTS', 'PTS_O', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT',
                              'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS', 'WL_OPP', 'OPP_PTS', 'OPP_FGM',
                              'OPP_FGA', 'OPP_FG_PCT', 'OPP_FG3M', 'OPP_FG3A', 'OPP_FG3_PCT', 'OPP_FTM', 'OPP_FTA', 'OPP_FT_PCT',
                              'OPP_OREB', 'OPP_DREB', 'OPP_REB', 'OPP_AST', 'OPP_STL', 'OPP_BLK', 'OPP_TOV', 'OPP_PF', 'OPP_PLUS_MINUS'],
                              axis=1)
    new_data_imputed = imputer.transform(new_data)


    wl_prediction = rf_wl.predict(new_data_imputed)
    pts_prediction = rf_pts.predict(new_data_imputed)
    pts_o_prediction = rf_pts_o.predict(new_data_imputed)

    pts_prediction_denormalized = (pts_prediction[0] * (max_pts - min_pts)) + min_pts
    pts_o_prediction_denormalized = (pts_o_prediction[0] * (max_pts - min_pts)) + min_pts
    pts_prediction_transformed = max(min(int(round(pts_prediction_denormalized)), max_pts), min_pts)
    pts_o_prediction_transformed = max(min(int(round(pts_o_prediction_denormalized)), max_pts), min_pts)

    print(f"Predikce WL (výhra/prohra): {wl_prediction[0]}")
    print(f"Predikce PTS (body): {pts_prediction_denormalized:.2f}")
    print(f"Predikce PTS_O (body soupeře): {pts_o_prediction_denormalized:.2f}")
    print(f"Zaokrouhlená predikce PTS (body): {pts_prediction_transformed}")
    print(f"Zaokrouhlená predikce PTS_O (body soupeře): {pts_o_prediction_transformed}")
    wl_prediction_transformed = "Výhra" if wl_prediction[0] == 1 else "Prohra"
    print(f"Predikce W/L: {wl_prediction_transformed}")

    #pozor, podelky
    if wl_prediction == 0 and pts_prediction_transformed > pts_o_prediction_transformed:
        return team2, pts_o_prediction_transformed, pts_prediction_transformed
    elif wl_prediction == 0 and pts_prediction_transformed < pts_o_prediction_transformed:
        return team2, pts_prediction_transformed, pts_o_prediction_transformed
    elif wl_prediction == 1 and pts_prediction_transformed > pts_o_prediction_transformed:
        return team1, pts_prediction_transformed, pts_o_prediction_transformed
    elif wl_prediction == 1 and pts_prediction_transformed < pts_o_prediction_transformed:
        return team1, pts_o_prediction_transformed, pts_prediction_transformed



