import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, f1_score, precision_score, recall_score, confusion_matrix
from imblearn.over_sampling import SMOTE
from sklearn.impute import SimpleImputer
import numpy as np

# Načtení dat
df = pd.read_csv('test_dataset.csv')

X = df.drop(['GAME_ID', 'TEAM_NAME', 'TEAM_ABBREVIATION','GAME_DATE','MATCHUP', 'WL', 'MIN','PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
             'FT_PCT', 'OREB', 'DREB', 'REB', 'AST','STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS', 'OPP_TEAM_NAME','OPP_TEAM_ABBREVIATION','OPP_WL', 'OPP_MIN', 'OPP_PTS', 'OPP_FGM', 'OPP_FGA', 'OPP_FG_PCT', 'OPP_FG3M',
             'OPP_FG3A', 'OPP_FG3_PCT', 'OPP_FTM', 'OPP_FTA', 'OPP_FT_PCT', 'OPP_OREB', 'OPP_DREB', 'OPP_REB', 'OPP_AST', 'OPP_STL', 'OPP_BLK', 'OPP_TOV', 'OPP_PF',
             'OPP_PLUS_MINUS'], axis=1)
y_wl = df['WL']  # Cílová proměnná pro výhru/prohru
y_pts = df['PTS']  # Cílová proměnná pro body
y_pts_o = df['OPP_PTS']  # Cílová proměnná pro body soupeře

# Rozdělení na trénovací a testovací data
X_train, X_test, y_wl_train, y_wl_test, y_pts_train, y_pts_test, y_pts_o_train, y_pts_o_test = train_test_split(
    X, y_wl, y_pts, y_pts_o, test_size=0.2, random_state=42)

# Použití imputace pro nahrazení NaN hodnot
imputer = SimpleImputer(strategy='mean')

# Aplikace imputace na trénovací a testovací data
X_train_imputed = imputer.fit_transform(X_train)
X_test_imputed = imputer.transform(X_test)

# Použití SMOTE pro vyvážení tříd pro WL
smote = SMOTE(sampling_strategy='auto', random_state=42)
X_train_res, y_wl_train_res = smote.fit_resample(X_train_imputed, y_wl_train)

# Trénování modelu pro WL (výhru/prohru)
rf_wl = RandomForestClassifier(random_state=42)
rf_wl.fit(X_train_res, y_wl_train_res)

# Predikce pro WL na testovacích datech
y_wl_pred = rf_wl.predict(X_test_imputed)

# Výpočet metrik pro WL
accuracy_wl = accuracy_score(y_wl_test, y_wl_pred)
f1_wl = f1_score(y_wl_test, y_wl_pred)
precision_wl = precision_score(y_wl_test, y_wl_pred)
recall_wl = recall_score(y_wl_test, y_wl_pred)
conf_matrix_wl = confusion_matrix(y_wl_test, y_wl_pred)

# Predikce pro PTS a PTS_O
rf_pts = RandomForestRegressor(random_state=42)
rf_pts.fit(X_train_imputed, y_pts_train)
y_pts_pred = rf_pts.predict(X_test_imputed)

rf_pts_o = RandomForestRegressor(random_state=42)
rf_pts_o.fit(X_train_imputed, y_pts_o_train)
y_pts_o_pred = rf_pts_o.predict(X_test_imputed)



# Výpočet MSE pro PTS a PTS_O
mse_pts = mean_squared_error(y_pts_test, y_pts_pred)
mse_pts_o = mean_squared_error(y_pts_o_test, y_pts_o_pred)

# Výstupy pro WL
print(f"Accuracy of WL prediction: {accuracy_wl}")
print(f"F1 score for WL prediction: {f1_wl}")
print(f"Precision for WL prediction: {precision_wl}")
print(f"Recall for WL prediction: {recall_wl}")
print("Confusion Matrix for WL prediction:")
print(conf_matrix_wl)

# Výstupy pro PTS a PTS_O
print(f"Mean Squared Error for PTS prediction: {mse_pts}")
print(f"Mean Squared Error for PTS_O prediction: {mse_pts_o}")

# Výpočet procentuální odchylky pro PTS a PTS_O
pts_diff = np.abs(y_pts_test - y_pts_pred) / (y_pts_test + 1e-5) * 100  # Přidání malého epsilon pro vyhnutí se dělení nulou
pts_o_diff = np.abs(y_pts_o_test - y_pts_o_pred) / (y_pts_o_test + 1e-5) * 100  # Stejně pro PTS_O

# Průměrná procentuální odchylka
avg_pts_diff = np.mean(pts_diff)
avg_pts_o_diff = np.mean(pts_o_diff)

print(f"Average percentage deviation for PTS: {avg_pts_diff}%")
print(f"Average percentage deviation for PTS_O: {avg_pts_o_diff}%")


import joblib
# Uložení modelu pro predikci WL (výhra/prohra)
joblib.dump(rf_wl, 'rf_wl_model.pkl')
# Uložení modelu pro predikci PTS (body)
joblib.dump(rf_pts, 'rf_pts_model.pkl')
# Uložení modelu pro predikci PTS_O (body soupeře)
joblib.dump(rf_pts_o, 'rf_pts_o_model.pkl')
# Uložení imputace
joblib.dump(imputer, 'imputer_model.pkl')
