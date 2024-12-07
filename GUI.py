from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import main

app = Flask(__name__)

# Seznam týmů
teams = [
    'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 'Chicago Bulls',
    'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons', 'Golden State Warriors',
    'Houston Rockets', 'Indiana Pacers', 'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies',
    'Miami Heat', 'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
    'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns', 'Portland Trail Blazers',
    'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors', 'Utah Jazz', 'Washington Wizards'
]

@app.route('/')
def home():
    return render_template('web_gui.html', teams=teams)

@app.route('/nextpage', methods=['POST'])
def next_page():
    home_team = request.form.get('team1')
    away_team = request.form.get('team2')
    date = request.form.get('date')

    # Zavolání funkce pro získání predikce
    wl_prediction, pts_prediction_transformed, pts_o_prediction_transformed = main.get_prediction(home_team, away_team, date)
    if wl_prediction == 1:
        wl_prediction = home_team
    else:
        wl_prediction = away_team

    # Renderování stránky výsledků
    return render_template('result.html', home_team=home_team, away_team=away_team, date=date,
                           wl_prediction=wl_prediction,
                           pts_prediction_transformed=pts_prediction_transformed,
                           pts_o_prediction_transformed=pts_o_prediction_transformed)

@app.route('/statistics')
def statistics():
    # Get the home and away team names from the URL query parameters
    home_team = request.args.get('home_team')
    away_team = request.args.get('away_team')
    date = request.args.get('date')

    # Fetch the last game stats and H2H stats using the 'main.get_stats' function
    last_games_team1_stats, last_games_team2_stats, last_h2h_stats = main.get_stats(home_team, away_team, date)

    date_obj = datetime.strptime(date, '%Y-%m-%d')
    date = date_obj.strftime('%Y-%m-%d')

    # Get the last 5 games of the home tea
    last_5_games_home = []
    for game in last_games_team1_stats:
        game_date = game['GAME_DATE']
        team1 = game['TEAM_NAME']
        pts1 = game['PTS']
        team2 = game['OPP_TEAM_NAME']
        pts2 = game['OPP_PTS']
        if team1 == home_team:
            result = 'W' if pts1 > pts2 else 'L'
        else:
            result = 'W' if pts2 > pts1 else 'L'
        game_info = [game_date, team1, pts1, team2, pts2, result]
        last_5_games_home.append(game_info)

    last_5_games_away = []
    for game in last_games_team2_stats:
        game_date = game['GAME_DATE']
        team1 = game['TEAM_NAME']
        pts1 = game['PTS']
        team2 = game['OPP_TEAM_NAME']
        pts2 = game['OPP_PTS']
        if team1 == away_team:
            result = 'W' if pts1 > pts2 else 'L'
        else:
            result = 'W' if pts2 > pts1 else 'L'
        game_info = [game_date, team1, pts1, team2, pts2, result]
        last_5_games_away.append(game_info)

    last_5_h2h = []
    for game in last_h2h_stats:
        game_date = game['GAME_DATE']
        team1 = game['TEAM_NAME']
        pts1 = game['PTS']
        team2 = game['OPP_TEAM_NAME']
        pts2 = game['OPP_PTS']
        game_info = [game_date, team1, pts1, team2, pts2]
        last_5_h2h.append(game_info)

    #game_info = [game_date, team1, pts1, team2, pts2, result]
    # Pass the necessary data to the statistics.html template
    return render_template('statistics.html',
                           home_team=home_team,
                           away_team=away_team,
                           date = date,
                           last_5_games_home=last_5_games_home,
                           last_5_games_away=last_5_games_away,
                           last_5_h2h=last_5_h2h)


if __name__ == '__main__':
    app.run(debug=True)
