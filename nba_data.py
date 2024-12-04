#precte vsechna potrebna data a upravi je, aby byla pripravena pro trenovani modelu.
import pandas as pd
import time
from nba_api.stats.endpoints import leaguegamefinder
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

def get_games_from_2021():
    # Funkce pro získání všech zápasů v dané sezóně
    def get_games_by_season(season):
        print(f"Zpracovávám zápasy za sezónu {season}...")
        gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
        games = gamefinder.get_data_frames()[0]
        return games

    # Zpracování sezón a uložení do CSV
    def process_seasons(seasons):
        all_games = []

        for season in seasons:
            try:
                # Získání zápasů pro aktuální sezónu
                games = get_games_by_season(season)
                games['SEASON'] = season  # Přidání informace o sezóně
                all_games.append(games)
                time.sleep(1)  # Pauza pro snížení rizika blokace API
            except Exception as e:
                print(f"Chyba při zpracování sezóny {season}: {e}")

        # Sloučení všech zápasů do jednoho datového rámce
        if all_games:
            combined_games = pd.concat(all_games, ignore_index=True)
            return combined_games
        else:
            return pd.DataFrame()  # Pokud nejsou data, vrátí prázdný DataFrame

    # Sezóny, které chceme zpracovat
    seasons = ['2021-22', '2022-23', '2023-24', '2024-25']

    # Získání dat a uložení do CSV
    games_data = process_seasons(seasons)

    if not games_data.empty:
        games_data.to_csv('nba_games_2021_25.csv', index=False)
        print("Data o zápasech byla úspěšně uložena do 'nba_games_2021_25.csv'!")
    else:
        print("Nepodařilo se získat žádná data.")

    input_file = 'nba_games_2021_25.csv'  # Nahraď názvem svého původního CSV souboru
    output_file = 'nba_games_filtered_21.csv'  # Název nového souboru s filtrováním

    # Načti data z CSV
    data = pd.read_csv(input_file)

    # Převod sloupce GAME_DATE na datetime
    data['GAME_DATE'] = pd.to_datetime(data['GAME_DATE'], errors='coerce')

    # Odfiltrování pouze platných dat
    data = data.dropna(subset=['GAME_DATE'])  # Odstraní řádky s neplatným datem

    # Filtrování podle měsíců (10 = říjen, 11 = listopad, ... 6 = červen)
    filtered_data = data[data['GAME_DATE'].dt.month.isin([10, 11, 12, 1, 2, 3, 4, 5, 6])]

    # Uložení výsledku do nového CSV souboru
    filtered_data.to_csv(output_file, index=False)

    print(f"Data byla vyfiltrována a uložena do {output_file}!")

    # Načteme vyfiltrovaná data
    data = pd.read_csv('nba_games_filtered_21.csv')

    # Převod sloupce GAME_DATE na datetime
    data['GAME_DATE'] = pd.to_datetime(data['GAME_DATE'], errors='coerce')

    # Odfiltrování pouze platných dat
    data = data.dropna(subset=['GAME_DATE'])

    # Filtrování podle měsíců
    data = data[data['GAME_DATE'].dt.month.isin([10, 11, 12, 1, 2, 3, 4, 5, 6])]

    # Převedení cílové proměnné 'WL' na binární (1 = výhra, 0 = prohra)
    data['WL'] = data['WL'].apply(lambda x: 1 if x == 'W' else 0)

    # Rozdělení na domácí a hostující tým
    data['HOME_TEAM'] = data['MATCHUP'].apply(lambda x: x.split(' ')[0])
    data['AWAY_TEAM'] = data['MATCHUP'].apply(lambda x: x.split(' ')[-1])

    # Přidání domácí výhody (1 = domácí tým, 0 = hostující tým)
    data['IS_HOME'] = data['MATCHUP'].apply(lambda x: 1 if 'vs.' in x else 0)

    # Klouzavé průměry pro posledních 5 zápasů (toto lze přizpůsobit podle potřeby)
    for stat in ['PTS', 'REB', 'AST', 'FG_PCT', 'FT_PCT']:
        data[f'{stat}_LAST_5'] = data.groupby('TEAM_ID')[stat].rolling(window=5).mean().reset_index(drop=True)

    # Statistiky soupeře
    opponent_stats = data.copy()
    opponent_stats.rename(
        columns=lambda col: f"OPP_{col}" if col not in ['GAME_ID', 'WL', 'MATCHUP', 'GAME_DATE', 'TEAM_ID'] else col,
        inplace=True)

    # Spojení domácí a hostující statistiky
    data = data.merge(opponent_stats, on='GAME_ID', suffixes=('', '_OPP'))

    # Přidání nové proměnné PTS_O, kde bude PTS - PLUS_MINUS pokud je PLUS_MINUS záporné
    data['PTS_O'] = data.apply(lambda row: row['PTS'] - row['PLUS_MINUS'] if row['PLUS_MINUS'] < 0 else row['PTS'], axis=1)

    # Vybereme numerické sloupce pro normalizaci
    numerical_columns = ['PTS', 'REB', 'AST', 'FG_PCT', 'FT_PCT', 'OREB', 'DREB', 'TOV', 'PTS_LAST_5', 'REB_LAST_5',
                         'AST_LAST_5', 'PTS_O']  # Přidáno PTS_O do seznamu numerických sloupců
    scaler = MinMaxScaler()

    # Normalizace číselných proměnných
    data[numerical_columns] = scaler.fit_transform(data[numerical_columns])

    import pickle
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)

    # Rozdělení na features a target
    X = data[['PTS', 'REB', 'AST', 'FG_PCT', 'FT_PCT', 'OREB', 'DREB', 'TOV', 'PTS_LAST_5', 'REB_LAST_5', 'AST_LAST_5',
               'OPP_REB', 'OPP_AST', 'OPP_FG_PCT', 'OPP_FT_PCT', 'OPP_OREB', 'OPP_DREB',
              'OPP_TOV', 'PTS_O']]  # Feature set, přidáno PTS_O

    y = data['WL']  # Target variable (1 = Win, 0 = Loss)

    # Rozdělení dat na trénovací a testovací sadu
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Uložení upraveného datasetu do nového CSV
    data.to_csv('final_dataset_21.csv', index=False)

    print("Úpravy byly úspěšně provedeny a data uložena do 'final_dataset_21.csv'!")

def get_games_from_2023():
    # Funkce pro získání všech zápasů v dané sezóně
    def get_games_by_season(season):
        print(f"Zpracovávám zápasy za sezónu {season}...")
        gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
        games = gamefinder.get_data_frames()[0]
        return games

    # Zpracování sezón a uložení do CSV
    def process_seasons(seasons):
        all_games = []

        for season in seasons:
            try:
                # Získání zápasů pro aktuální sezónu
                games = get_games_by_season(season)
                games['SEASON'] = season  # Přidání informace o sezóně
                all_games.append(games)
                time.sleep(1)  # Pauza pro snížení rizika blokace API
            except Exception as e:
                print(f"Chyba při zpracování sezóny {season}: {e}")

        # Sloučení všech zápasů do jednoho datového rámce
        if all_games:
            combined_games = pd.concat(all_games, ignore_index=True)
            return combined_games
        else:
            return pd.DataFrame()  # Pokud nejsou data, vrátí prázdný DataFrame

    # Sezóny, které chceme zpracovat
    seasons = [ '2023-24', '2024-25']

    # Získání dat a uložení do CSV
    games_data = process_seasons(seasons)

    if not games_data.empty:
        games_data.to_csv('nba_games_2023_25.csv', index=False)
        print("Data o zápasech byla úspěšně uložena do 'nba_games_2023_25.csv'!")
    else:
        print("Nepodařilo se získat žádná data.")

    input_file = 'nba_games_2023_25.csv'  # Nahraď názvem svého původního CSV souboru
    output_file = 'nba_games_filtered_23.csv'  # Název nového souboru s filtrováním

    # Načti data z CSV
    data = pd.read_csv(input_file)

    # Převod sloupce GAME_DATE na datetime
    data['GAME_DATE'] = pd.to_datetime(data['GAME_DATE'], errors='coerce')

    # Odfiltrování pouze platných dat
    data = data.dropna(subset=['GAME_DATE'])  # Odstraní řádky s neplatným datem

    # Filtrování podle měsíců (10 = říjen, 11 = listopad, ... 6 = červen)
    filtered_data = data[data['GAME_DATE'].dt.month.isin([10, 11, 12, 1, 2, 3, 4, 5, 6])]

    # Uložení výsledku do nového CSV souboru
    filtered_data.to_csv(output_file, index=False)

    print(f"Data byla vyfiltrována a uložena do {output_file}!")

    # Načteme vyfiltrovaná data
    data = pd.read_csv('nba_games_filtered_23.csv')

    # Převod sloupce GAME_DATE na datetime
    data['GAME_DATE'] = pd.to_datetime(data['GAME_DATE'], errors='coerce')

    # Odfiltrování pouze platných dat
    data = data.dropna(subset=['GAME_DATE'])

    # Filtrování podle měsíců
    data = data[data['GAME_DATE'].dt.month.isin([10, 11, 12, 1, 2, 3, 4, 5, 6])]

    # Převedení cílové proměnné 'WL' na binární (1 = výhra, 0 = prohra)
    data['WL'] = data['WL'].apply(lambda x: 1 if x == 'W' else 0)

    # Rozdělení na domácí a hostující tým
    data['HOME_TEAM'] = data['MATCHUP'].apply(lambda x: x.split(' ')[0])
    data['AWAY_TEAM'] = data['MATCHUP'].apply(lambda x: x.split(' ')[-1])

    # Přidání domácí výhody (1 = domácí tým, 0 = hostující tým)
    data['IS_HOME'] = data['MATCHUP'].apply(lambda x: 1 if 'vs.' in x else 0)

    # Klouzavé průměry pro posledních 5 zápasů (toto lze přizpůsobit podle potřeby)
    for stat in ['PTS', 'REB', 'AST', 'FG_PCT', 'FT_PCT']:
        data[f'{stat}_LAST_5'] = data.groupby('TEAM_ID')[stat].rolling(window=5).mean().reset_index(drop=True)

    # Statistiky soupeře
    opponent_stats = data.copy()
    opponent_stats.rename(
        columns=lambda col: f"OPP_{col}" if col not in ['GAME_ID', 'WL', 'MATCHUP', 'GAME_DATE', 'TEAM_ID'] else col,
        inplace=True)

    # Spojení domácí a hostující statistiky
    data = data.merge(opponent_stats, on='GAME_ID', suffixes=('', '_OPP'))

    # Přidání nové proměnné PTS_O, kde bude PTS - PLUS_MINUS pokud je PLUS_MINUS záporné
    data['PTS_O'] = data.apply(lambda row: row['PTS'] - row['PLUS_MINUS'] if row['PLUS_MINUS'] < 0 else row['PTS'], axis=1)

    # Vybereme numerické sloupce pro normalizaci
    numerical_columns = ['PTS', 'REB', 'AST', 'FG_PCT', 'FT_PCT', 'OREB', 'DREB', 'TOV', 'PTS_LAST_5', 'REB_LAST_5',
                         'AST_LAST_5', 'PTS_O']  # Přidáno PTS_O do seznamu numerických sloupců
    scaler = MinMaxScaler()

    # Normalizace číselných proměnných
    data[numerical_columns] = scaler.fit_transform(data[numerical_columns])

    # Rozdělení na features a target
    X = data[['PTS', 'REB', 'AST', 'FG_PCT', 'FT_PCT', 'OREB', 'DREB', 'TOV', 'PTS_LAST_5', 'REB_LAST_5', 'AST_LAST_5',
               'OPP_REB', 'OPP_AST', 'OPP_FG_PCT', 'OPP_FT_PCT', 'OPP_OREB', 'OPP_DREB',
              'OPP_TOV', 'PTS_O']]  # Feature set, přidáno PTS_O

    y = data['WL']  # Target variable (1 = Win, 0 = Loss)

    # Rozdělení dat na trénovací a testovací sadu
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Uložení upraveného datasetu do nového CSV
    data.to_csv('final_dataset_23.csv', index=False)

    print("Úpravy byly úspěšně provedeny a data uložena do 'final_dataset_23.csv'!")

def get_ready_dataset():
    # Načtení dat
    data_2023_25 = pd.read_csv("final_dataset_23.csv")
    data_2021_25 = pd.read_csv("final_dataset_21.csv")

    # Převod dat na datetime pro snadné filtrování
    data_2023_25['GAME_DATE'] = pd.to_datetime(data_2023_25['GAME_DATE'])
    data_2021_25['GAME_DATE'] = pd.to_datetime(data_2021_25['GAME_DATE'])

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
        """Funkce pro výpočet průměrů pro daný tým a zápasy."""
        if games.empty:
            return {key: None for key in [
                "WL", "PTS", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",
                "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS"
            ]}

        # Inicializace proměnných pro součet statistik
        home_stats = []
        away_stats = []

        # Procházíme každý zápas a podle toho, zda je tým domácí nebo hostující
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
            home_averages = {key: None for key in [
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
            away_averages = {key: None for key in [
                "WL", "PTS", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",
                "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS"
            ]}

        # Pokud máme oba zápasy (domácí i venkovní), spočítáme celkový průměr
        if home_stats and away_stats:
            final_averages = {key: (home_averages[key] + away_averages[key]) / 2 for key in home_averages}
            return final_averages

        # Pokud máme pouze domácí nebo pouze venkovní zápasy, vrátíme pouze průměry pro daný typ zápasu
        return home_averages if home_stats else away_averages

    def calculate_last_5_team_stats(team_id, date, data):
        """Vypočítá průměrné statistiky pro tým na základě posledních 5 zápasů."""
        # Získáme poslední 5 zápasů pro tým
        last_5_games = get_last_games(team_id, date, data)

        # Spočítáme průměry pro tým
        team_averages = calculate_averages_for_team(last_5_games, team_id)

        return team_averages

    def calculate_h2h_averages(games, team1_id, team2_id):
        team1_stats = calculate_averages_for_team(games, team1_id)
        team2_stats = calculate_averages_for_team(games, team2_id)

        return team1_stats, team2_stats

    merged_data = data_2023_25.copy()

    # Vytvoření nových sloupců pro LAST_5_* průměry
    for idx, game in merged_data.iterrows():
        team1_id = game['TEAM_ID']
        team2_id = game['TEAM_ID_OPP']
        game_date = game['GAME_DATE']

        # Získáme průměrné statistiky pro oba týmy
        last_games_team1 = get_last_games(team1_id, game_date, data_2021_25)
        last_games_team2 = get_last_games(team2_id, game_date, data_2021_25)
        las_h2h_games = get_last_head_to_head(team1_id, team2_id, game_date, data_2021_25)

        team1_averages = calculate_last_5_team_stats(team1_id, game_date, last_games_team1)
        team2_averages = calculate_last_5_team_stats(team2_id, game_date, last_games_team2)
        h2h_averages = calculate_h2h_averages(las_h2h_games, team1_id, team2_id)

        # Přidáme nové sloupce do datasetu
        for stat in team1_averages:
            merged_data.loc[idx, f"LAST_5_{stat}_TEAM1"] = team1_averages[stat]
        for stat in team2_averages:
            merged_data.loc[idx, f"LAST_5_{stat}_TEAM2"] = team2_averages[stat]
        for stat in h2h_averages[0]:
            merged_data.loc[idx, f"H2H_{stat}_TEAM1"] = h2h_averages[0][stat]
        for stat in h2h_averages[1]:
            merged_data.loc[idx, f"H2H_{stat}_TEAM2"] = h2h_averages[1][stat]

    # Uložení do nového souboru
    merged_data.to_csv("merged_dataset.csv", index=False)
    print("Data byla spojena a uložena do 'merged_dataset.csv'!")


def pop_columns(file):
    df = pd.read_csv(file)
    columns = ['PTS_LAST_5', 'REB_LAST_5', 'AST_LAST_5', 'FG_PCT_LAST_5', 'FT_PCT_LAST_5', 'OPP_PTS_LAST_5',
               'OPP_REB_LAST_5', 'OPP_AST_LAST_5', 'OPP_FG_PCT_LAST_5', 'OPP_FT_PCT_LAST_5', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'MATCHUP', 'HOME_TEAM', 'AWAY_TEAM',
               'OPP_TEAM_ABBREVIATION', 'OPP_TEAM_NAME', 'MATCHUP_OPP', 'OPP_HOME_TEAM', 'OPP_AWAY_TEAM', 'GAME_DATE', 'GAME_DATE_OPP', 'SEASON', 'OPP_SEASON']
    df = df.drop(columns=columns)
    df.to_csv('dataset_for_training.csv', index=False)
    print(f'Columns {columns} were removed from the dataset.')
    print(f'Dataset was saved to dataset_for_training.csv\nIt is ready for model training!!')

get_games_from_2021()
get_games_from_2023()
get_ready_dataset()
pop_columns('merged_dataset.csv')


