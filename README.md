# NBA Results Predictor

This project is an NBA results predictor that uses machine learning models to predict the outcome of NBA games. The project includes data fetching, processing, model training, and a web interface for user interaction.

## Project Structure

- `main.py`: Contains the main functions for dataset preparation and prediction.
- `nba_data.py`: Fetches and processes NBA game data.
- `results_training.py`: Trains the machine learning models.
- `GUI.py`: Flask web application for user interaction.
- `templates/`: Contains HTML templates for the web interface.
- `static/`: Contains static files such as team logos.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/vikiaseschool/nba-results-predictor.git
    cd nba-results-predictor
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage with datasets

### Data Preparation

1. Fetch and process NBA game data:
    ```sh
    python nba_data.py
    ```

2. Prepare the dataset for training:
    ```sh
    python main.py
    ```

### Model Training

1. Train the machine learning models:
    ```sh
    python results_training.py
    ```

### Running the Web Application

1. Start the Flask web application:
    ```sh
    python GUI.py
    ```

2. Open your web browser and go to `http://127.0.0.1:5000/`.

### Making Predictions (you can use when you don't have the proper datasets)

1. Select the home team, away team, and game date, then click "Proceed" to get the predictions.

## Important Notes

- **Disclaimer:** This predictor is for educational purposes only. Do not use it for betting or any other financial decisions.
- The model has an average percentage deviation of approximately 25% for points and wins predictions. This means the predictions can be off by about 25% on average.
## Model Testing Results
Accuracy of WL prediction: 0.569078947368421
F1 score for WL prediction: 0.6260704091341579
Precision for WL prediction: 0.6195856873822976
Recall for WL prediction: 0.6326923076923077
Confusion Matrix for WL prediction:
[[190 202]
 [191 329]]
Mean Squared Error for PTS prediction: 162.9600766765994
Mean Squared Error for PTS_O prediction: 162.2703266502108
Average percentage deviation for PTS: 9.103152069317767%
Average percentage deviation for PTS_O: 9.20247428308317%

