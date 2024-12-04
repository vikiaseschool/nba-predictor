from flask import Flask, render_template, request, redirect, url_for
import main
app = Flask(__name__)
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

    # Renderování stránky výsledků s těmito informacemi
    return render_template('result.html', home_team=home_team, away_team=away_team, date=date,
                           wl_prediction=wl_prediction,
                           pts_prediction_transformed=pts_prediction_transformed,
                           pts_o_prediction_transformed=pts_o_prediction_transformed)

if __name__ == '__main__':
    app.run(debug=True)

