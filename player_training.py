from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import pandas as pd
import joblib

# Load data
df = pd.read_csv('test_dataset_players.csv')

# Features (X) and target variables (y)
X = df.drop(['SEASON_ID', 'GAME_ID', 'GAME_DATE', 'TEAM_NAME', 'PLAYER_NAME', 'TEAM_ID', 'WL', 'MIN',
             'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB',
             'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS', 'MATCH_TEAM_NAME', 'MATCH_WL',
             'MATCH_MIN', 'MATCH_PTS', 'MATCH_FGM', 'MATCH_FGA', 'MATCH_FG_PCT', 'MATCH_FG3M', 'MATCH_FG3A',
             'MATCH_FG3_PCT', 'MATCH_FTM', 'MATCH_FTA', 'MATCH_FT_PCT', 'MATCH_OREB', 'MATCH_DREB', 'MATCH_REB',
             'MATCH_AST', 'MATCH_STL', 'MATCH_BLK', 'MATCH_TOV', 'MATCH_PF', 'MATCH_PLUS_MINUS', 'MATCHUP'], axis=1)

y_pts = df['PTS']
y_reb = df['REB']
y_ast = df['AST']

# Train-test split
X_train, X_test, y_pts_train, y_pts_test, y_reb_train, y_reb_test, y_ast_train, y_ast_test = train_test_split(
    X, y_pts, y_reb, y_ast, test_size=0.2, random_state=42)

# Handle missing values
imputer = SimpleImputer(strategy='mean')
X_train_imputed = imputer.fit_transform(X_train)
X_test_imputed = imputer.transform(X_test)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_imputed)
X_test_scaled = scaler.transform(X_test_imputed)

# Initialize and train the model for Points, Rebounds, and Assists
model_pts = LinearRegression()
model_pts.fit(X_train_scaled, y_pts_train)

model_reb = LinearRegression()
model_reb.fit(X_train_scaled, y_reb_train)

model_ast = LinearRegression()
model_ast.fit(X_train_scaled, y_ast_train)

# Evaluate the models using R2 score
pts_pred = model_pts.predict(X_test_scaled)
reb_pred = model_reb.predict(X_test_scaled)
ast_pred = model_ast.predict(X_test_scaled)

pts_r2 = r2_score(y_pts_test, pts_pred) * 100
reb_r2 = r2_score(y_reb_test, reb_pred) * 100
ast_r2 = r2_score(y_ast_test, ast_pred) * 100

# Output the results
print(f"Points (PTS) R2 Score: {pts_r2:.2f}%")
print(f"Rebounds (REB) R2 Score: {reb_r2:.2f}%")
print(f"Assists (AST) R2 Score: {ast_r2:.2f}%")

# Save the models and preprocessing objects
joblib.dump(imputer, 'imputer_model_player.pkl')
joblib.dump(scaler, 'scaler_model_player.pkl')
joblib.dump(model_pts, 'linear_regression_pts_model.pkl')
joblib.dump(model_reb, 'linear_regression_reb_model.pkl')
joblib.dump(model_ast, 'linear_regression_ast_model.pkl')
joblib.dump(X.columns, 'columns.pkl')

