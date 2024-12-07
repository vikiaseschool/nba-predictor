import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams

def get_filtered_historical_21_25():
    def get_games_for_seasons(start_season, end_season):
        all_games = []
        for season in range(start_season, end_season + 1):
            season_str = f"{season}-{str(season + 1)[-2:]}"  # Formát: 2021-22
            print(f"Stahuji data pro sezónu {season_str}...")

            # Získat zápasy pro danou sezónu
            gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season_str)
            games = gamefinder.get_data_frames()[0]
            all_games.append(games)

        # Sloučit všechny sezóny do jednoho DataFrame
        return pd.concat(all_games, ignore_index=True)

    def add_is_home_column(games_df):
        is_home_list = []

        # Smyčka přes všechny zápasy v games_df
        for _, row in games_df.iterrows():
            matchup = row['MATCHUP']

            # Ošetření různých formátů zápasu
            if ' vs. ' in matchup:  # Formát: "LAL vs BOS"
                home_team, away_team = matchup.split(" vs. ")
            elif ' @ ' in matchup:  # Formát: "LAL @ BOS"
                away_team, home_team = matchup.split(" @ ")
            else:
                # Pokud formát neodpovídá očekávánému (např. chyba v datech), pokračujeme dál
                print(f"Neznámý formát MATCHUP: {matchup}")
                is_home_list.append(None)
                continue

            # Zjištění, jestli je tým domácí nebo hostující
            if row['TEAM_ABBREVIATION'] == home_team:
                is_home_list.append(1)  # Domácí tým
            elif row['TEAM_ABBREVIATION'] == away_team:
                is_home_list.append(0)  # Hostující tým
            else:
                print(f"Tým {row['TEAM_ABBREVIATION']} se neobjevuje v zápasu {matchup}")
                is_home_list.append(None)

        # Přidání sloupce IS_HOME do DataFrame
        games_df['IS_HOME'] = is_home_list
        return games_df

    def filter_games_by_month(games_df):
        # Ujistíme se, že sloupec GAME_DATE je ve formátu datetime
        games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])

        # Filtrování pouze pro zápasy od října (10) do června (6)
        games_df = games_df[games_df['GAME_DATE'].dt.month.isin([10, 11, 12, 1, 2, 3, 4, 5, 6])]
        games_df['WL'] = games_df['WL'].replace({'W': 1, 'L': 0})
        # Získání seznamu týmů NBA (ID týmů)
        nba_teams = teams.get_teams()
        nba_team_ids = [team['id'] for team in nba_teams]

        # Filtrování zápasů, které obsahují pouze týmy z NBA
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
        # Seznam pro uložení sloučených zápasů
        combined_games = []

        # Projdeme všechny zápasy a najdeme páry podle GAME_DATE a GAME_ID
        grouped = games_df.groupby(['GAME_DATE', 'GAME_ID'])

        # Pro každý pár zápasů, sloučíme domácí a hostující tým
        for (game_date, game_id), group in grouped:
            if len(group) == 2:
                # Určujeme domácí a hostující tým
                home_game = group[group['IS_HOME'] == 1].iloc[0]
                away_game = group[group['IS_HOME'] == 0].iloc[0]

                # Vybereme sloupce pro domácí a hostující tým
                combined_game = home_game.copy()  # Základ je domácí zápas

                # Přidáme sloupce z hostujícího zápasu s předponou OPP_
                for col in games_df.columns:
                    if col not in ['SEASON_ID', 'GAME_ID', 'GAME_DATE', 'MATCHUP']:
                        combined_game[f"OPP_{col}"] = away_game[col]

                # Přidáme sloučený zápas do seznamu
                combined_games.append(combined_game)
            else:
                # Pokud zápas nemá protějšek, vypíšeme MATCHUP
                matchup = group['MATCHUP'].iloc[0] if 'MATCHUP' in group.columns else 'N/A'
                print(
                    f"Varování: Zápas na GAME_DATE {game_date} a GAME_ID {game_id} nemá protějšek. MATCHUP: {matchup}")

        # Vytvoření nového DataFrame z kombinovaných zápasů
        combined_df = pd.DataFrame(combined_games)
        return combined_df


    games_df = pd.read_csv("historical_games_filtered_2021_2025.csv")
    combined_df = combine_home_away(games_df)

    output_file = "combined_games_2021_2025.csv"
    combined_df.to_csv(output_file, index=False)
    print(f"Data uložena do souboru {output_file}")

def get_testing_data():
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

        for idx, row in games_df.iterrows():
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


