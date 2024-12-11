from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from scipy.stats import randint

df = pd.read_csv('test_dataset_players.csv')

X = df.drop(['SEASON_ID', 'GAME_ID', 'GAME_DATE', 'TEAM_NAME', 'PLAYER_NAME', 'TEAM_ID', 'WL', 'MIN',
                   'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB',
                   'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS', 'MATCH_TEAM_NAME', 'MATCH_WL',
                   'MATCH_MIN', 'MATCH_PTS', 'MATCH_FGM', 'MATCH_FGA', 'MATCH_FG_PCT', 'MATCH_FG3M', 'MATCH_FG3A',
                   'MATCH_FG3_PCT', 'MATCH_FTM', 'MATCH_FTA', 'MATCH_FT_PCT', 'MATCH_OREB', 'MATCH_DREB', 'MATCH_REB',
                   'MATCH_AST', 'MATCH_STL', 'MATCH_BLK', 'MATCH_TOV', 'MATCH_PF', 'MATCH_PLUS_MINUS'], axis=1)

y_pts = df['PTS']
y_reb = df['REB']
y_ast = df['AST']

X_train, X_test, y_pts_train, y_pts_test, y_reb_train, y_reb_test, y_ast_train, y_ast_test = train_test_split(
    X, y_pts, y_reb, y_ast, test_size=0.2, random_state=42)

imputer = SimpleImputer(strategy='mean')
X_train_imputed = imputer.fit_transform(X_train)
X_test_imputed = imputer.transform(X_test)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_imputed)
X_test_scaled = scaler.transform(X_test_imputed)

rf = RandomForestRegressor(random_state=42)

param_dist = {
    'n_estimators': randint(50, 200),
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2', None],  # Replace 'auto' with 'sqrt' or 'log2'
    'bootstrap': [True, False]
}

random_search_pts = RandomizedSearchCV(estimator=rf, param_distributions=param_dist, n_iter=10, cv=3, n_jobs=-1, verbose=2, random_state=42)
random_search_reb = RandomizedSearchCV(estimator=rf, param_distributions=param_dist, n_iter=10, cv=3, n_jobs=-1, verbose=2, random_state=42)
random_search_ast = RandomizedSearchCV(estimator=rf, param_distributions=param_dist, n_iter=10, cv=3, n_jobs=-1, verbose=2, random_state=42)

random_search_pts.fit(X_train_scaled, y_pts_train)
random_search_reb.fit(X_train_scaled, y_reb_train)
random_search_ast.fit(X_train_scaled, y_ast_train)

y_pts_pred = random_search_pts.predict(X_test_scaled)
y_reb_pred = random_search_reb.predict(X_test_scaled)
y_ast_pred = random_search_ast.predict(X_test_scaled)

pts_r2 = r2_score(y_pts_test, y_pts_pred) * 100
reb_r2 = r2_score(y_reb_test, y_reb_pred) * 100
ast_r2 = r2_score(y_ast_test, y_ast_pred) * 100

print(f"Efficiency and Accuracy of the Models:")
print(f"Points (PTS) Prediction R2 Score: {pts_r2:.2f}%")
print(f"Points (PTS) Mean Squared Error: {np.mean((y_pts_test - y_pts_pred)**2):.2f}")

print(f"Rebounds (REB) Prediction R2 Score: {reb_r2:.2f}%")
print(f"Rebounds (REB) Mean Squared Error: {np.mean((y_reb_test - y_reb_pred)**2):.2f}")

print(f"Assists (AST) Prediction R2 Score: {ast_r2:.2f}%")
print(f"Assists (AST) Mean Squared Error: {np.mean((y_ast_test - y_ast_pred)**2):.2f}")

import joblib #save models!!!
joblib.dump(random_search_pts, 'random_search_pts.pkl')
joblib.dump(random_search_reb, 'random_search_reb.pkl')
joblib.dump(random_search_ast, 'random_search_ast.pkl')
joblib.dump(imputer, 'imputer_model_player.pkl')