from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import main

app = Flask(__name__)
app.secret_key = 'mysecretkey_not_generated_with_AI'

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

@app.route('/nextpage', methods=['POST', 'GET'])
def next_page():
    if request.method == 'GET':
        flash("Please fill out the form before proceeding.", "error")
        return redirect(url_for('home'))

    home_team = request.form.get('team1')
    away_team = request.form.get('team2')
    date = request.form.get('date')

    try:
        wl_prediction, pts_prediction_transformed, pts_o_prediction_transformed, player_pts, player_ast, player_reb, player_names, is_home = (
            main.get_prediction(home_team, away_team, date)
        )
        wl_prediction = home_team if wl_prediction == 1 else away_team
        if wl_prediction == home_team and pts_prediction_transformed < pts_o_prediction_transformed:
            wl_prediction = away_team
        if wl_prediction == away_team and pts_prediction_transformed > pts_o_prediction_transformed:
            wl_prediction = home_team
    except Exception:
        flash("Invalid Date, please try again.", "error")
        return redirect(url_for('home'))
    print(player_names)
    return render_template('result.html', home_team=home_team, away_team=away_team, date=date,
                           wl_prediction=wl_prediction, pts_prediction_transformed=pts_prediction_transformed,pts_o_prediction_transformed=pts_o_prediction_transformed,
                           player_pts=player_pts, player_ast=player_ast, player_reb=player_reb, player_names=player_names, is_home=is_home)

@app.route('/statistics')
def statistics():
    home_team = request.args.get('home_team')
    away_team = request.args.get('away_team')
    date = request.args.get('date')

    last_games_team1_stats, last_games_team2_stats, last_h2h_stats = main.get_stats(home_team, away_team, date)

    date_obj = datetime.strptime(date, '%Y-%m-%d')
    date = date_obj.strftime('%Y-%m-%d')

    last_5_games_home = []
    for game in last_games_team1_stats:
        game_date = game['GAME_DATE']
        team1 = game['TEAM_NAME']
        pts1 = game['PTS']
        team2 = game['OPP_TEAM_NAME']
        pts2 = game['OPP_PTS']
        result = 'W' if pts1 > pts2 else 'L'
        game_info = [game_date, team1, pts1, team2, pts2, result]
        last_5_games_home.append(game_info)

    last_5_games_away = []
    for game in last_games_team2_stats:
        game_date = game['GAME_DATE']
        team1 = game['TEAM_NAME']
        pts1 = game['PTS']
        team2 = game['OPP_TEAM_NAME']
        pts2 = game['OPP_PTS']
        result = 'W' if pts1 > pts2 else 'L'
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

    return render_template('statistics.html',
                           home_team=home_team,
                           away_team=away_team,
                           date=date,
                           last_5_games_home=last_5_games_home,
                           last_5_games_away=last_5_games_away,
                           last_5_h2h=last_5_h2h)

@app.route('/player_prediction')
def player_prediction():
    home_team = request.args.get('home_team')
    away_team = request.args.get('away_team')
    date = request.args.get('date')
    player_pts = request.args.getlist('player_pts')
    player_ast = request.args.getlist('player_ast')
    player_reb = request.args.getlist('player_reb')
    player_names = request.args.getlist('player_names')
    is_home = request.args.get('is_home', default=False)
    is_home = is_home in ['True']

    if is_home:
        home_players = player_names[:5]
        away_players = player_names[5:]
        home_pts = player_pts[:5]
        away_pts = player_pts[5:]
        home_reb = player_reb[:5]
        away_reb = player_reb[5:]
        home_ast = player_ast[:5]
        away_ast = player_ast[5:]
    else:
        home_players = player_names[5:]
        away_players = player_names[:5]
        home_pts = player_pts[5:]
        away_pts = player_pts[:5]
        home_reb = player_reb[5:]
        away_reb = player_reb[:5]
        home_ast = player_ast[5:]
        away_ast = player_ast[:5]

    return render_template('player_prediction.html', home_team=home_team, away_team=away_team, date=date,
                            home_players=home_players, away_players=away_players, home_pts=home_pts, away_pts=away_pts,
                            home_reb=home_reb, away_reb=away_reb, home_ast=home_ast, away_ast=away_ast, is_home=is_home)

if __name__ == '__main__':
    app.run(debug=True)
