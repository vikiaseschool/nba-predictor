# NBA Results Predictor V2

## WARNING!
this application is only for educational purposes, please don't use it for betting. The model is not accurate enough and you may lose your money.

## Overview

This project is an NBA results predictor that uses machine learning models to predict the outcome of NBA games. The application provides predictions for the winning team and the expected scores for both teams. Additionally, it offers statistics on the last games played by the teams and their head-to-head matchups.

## Features

- **Match Data Generation**: Creates a CSV file with match information for the specified teams and date.
- **Statistics Calculation**: Retrieves and calculates statistics for the last games played by the teams and their head-to-head matchups.
- **Prediction Models**: Uses trained machine learning models to predict the winning team and the scores.
- **Web Interface**: A Flask-based web interface to input team names and date, and to display the predictions and statistics.

## Files

- `main.py`: Contains the core functions for retrieving team IDs, generating match data, calculating statistics, and making predictions.
- `GUI.py`: Flask application that provides a web interface for the user to input data and view predictions and statistics.
- `nba_data.py`: Functions to fetch and preprocess historical NBA game data.
- `results_training.py`: Script to train the machine learning models for predicting game outcomes and scores.
- `templates/web_gui.html`: HTML template for the main input form.
- `templates/result.html`: HTML template for displaying the prediction results.
- `templates/statistics.html`: HTML template for displaying the game statistics.

## Usage

1. **Data Preparation**:
   - Run `nba_data.py` to fetch and preprocess historical game data.
   - Run `results_training.py` to train the machine learning models.

2. **Web Interface**:
   - Start the Flask application by running `GUI.py`.
   - Open a web browser and navigate to `http://127.0.0.1:5000/`.
   - Select the home team, away team, and date, then click "Proceed" to get predictions.
   - View the prediction results and click "Statistics" to see detailed game statistics.

## Requirements

- Python 3.x
- pandas
- joblib
- nba_api
- Flask
- scikit-learn
- imbalanced-learn

## Model accuracy test results

- Accuracy of WL prediction: 58%
- false win/lose [190 202], correct win/lose [191 329]
- Mean Squared Error for PTS prediction: 163.0
- Mean Squared Error for PTS_O prediction: 162.3
- Average percentage deviation for PTS: 9.1%
- Average percentage deviation for PTS_O: 9.2%

## UPDATE DESCRIPTIONS
**V2 changes**
- made the project public via vercel
- added player points prediction

**V1.1 changes**
- repaired datasets, data are now more precise
- better trained model, accuracy increase + 2%
- added last 5 games stats

