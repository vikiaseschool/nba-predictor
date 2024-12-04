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

## Usage

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

### Making Predictions

1. Select the home team, away team, and game date, then click "Proceed" to get the predictions.

## Important Notes

- **Disclaimer:** This predictor is for educational purposes only. Do not use it for betting or any other financial decisions.
- The model has an average percentage deviation of approximately 25% for points predictions. This means the predictions can be off by about 25% on average.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
