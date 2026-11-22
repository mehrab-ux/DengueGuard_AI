# DengueGuard AI — System Architecture

## 1. System Overview

DengueGuard AI is a machine learning-based application that predicts dengue risk categories using historical dengue case data and weather-related information.

The system consists of four main components:

1. Data preprocessing
2. Feature engineering
3. Machine learning model training and prediction
4. Streamlit dashboard

## 2. System Workflow

```text
          Historical Dataset
                  |
                  v
        Data Preprocessing
                  |
                  v
          Feature Engineering
                  |
                  v
        Model Training
                  |
                  v
          Trained Model
                  |
                  v
       Streamlit Dashboard
                  |
                  v
        User Input (14 Features)
                  |
                  v
          Prediction Pipeline
                  |
                  v
       Dengue Risk Classification
                  |
                  v
       Risk Level + Recommendations
```

## 3. Data Preprocessing

The project uses historical dengue and weather-related data.

The preprocessing stage prepares the dataset for machine learning by:

- Cleaning the raw dataset
- Handling missing or unsuitable records
- Preparing the required columns
- Organizing records for feature engineering

The cleaned dataset is stored in:

`Dataset/cleaned_dengue_data.csv`

## 4. Feature Engineering

Feature engineering creates additional information from historical records to help the model identify patterns.

The target variable is created using:

`next_week_cases`

This represents the next week's dengue case count for the corresponding ward.

The model uses 14 input features:

| Feature | Description |
|---|---|
| ward_id | Ward identifier |
| cases_lag_1 | Previous week's dengue cases |
| avg_temp_c_lag_1 to 4 | Temperature over previous four weeks |
| rainfall_mm_lag_1 to 4 | Rainfall over previous four weeks |
| relative_humidity_pct_lag_1 to 4 | Humidity over previous four weeks |

## 5. Model Training

The project experiments with multiple classification algorithms:

- Random Forest Classifier
- Weighted Random Forest Classifier
- Balanced Random Forest Classifier
- SMOTENC + Balanced Random Forest Classifier

### Data splitting

A chronological train-test split is used to evaluate the model on later observations.

- Training data: 24,840 rows
- Testing data: 6,180 rows
- Split date: January 1, 2024

### Class imbalance handling

SMOTENC is used in one experiment to address class imbalance while considering categorical features.

Balanced Random Forest and class weighting are also evaluated as alternative approaches.

### Model evaluation

Models are compared using:

- Accuracy
- Precision
- Recall
- F1-score
- Classification report

## 6. Prediction Pipeline

The prediction module is located at:

`Dataset/src/predict.py`

The prediction process:

1. Loads the saved machine learning model.
2. Loads the required feature information and risk thresholds.
3. Receives the 14 input features.
4. Applies the required preprocessing.
5. Generates a risk category prediction.
6. Returns one of four categories:
   - Low
   - Medium
   - High
   - Critical

The model predicts a risk category rather than an exact number of future dengue cases.

## 7. Streamlit Dashboard

The main application is:

`app.py`

The dashboard provides:

- Interactive user input
- Dengue risk prediction
- Risk category display
- Risk-related recommendations
- Project information
- Explanation of the prediction process

The dashboard communicates with the prediction module to generate results.

## 8. Technologies and Libraries

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Pandas | Data processing |
| NumPy | Numerical operations |
| Scikit-learn | Machine learning and preprocessing |
| Imbalanced-learn | Handling class imbalance |
| Joblib | Saving and loading trained models |
| Streamlit | Interactive dashboard |

## 9. Project Directory Structure

```text
DengueGuard_AI/
│
├── app.py
├── README.md
├── ARCHITECTURE.md
├── .gitignore
│
└── Dataset/
    ├── dengue_data.csv
    ├── cleaned_dengue_data.csv
    │
    ├── models/
    │   └── Trained model files
    │
    └── src/
        ├── data_preprocessing.py
        ├── features.py
        ├── test_features.py
        ├── train_model.py
        ├── train_model_backup.py
        └── predict.py
```

## 10. Limitations and Future Improvements

### Current limitations

- Predictions depend on the quality and availability of historical data.
- Model performance may vary on unseen real-world data.
- Risk categories are dataset-derived and are not medically validated.
- The system does not replace official public health information or medical advice.

### Future improvements

- Integrate regularly updated dengue and weather datasets.
- Improve model performance for the Critical category.
- Add geographical risk visualization.
- Develop automated data updates.
- Evaluate the model using additional real-world datasets.

## 11. Model Selection Rationale

Multiple machine learning approaches were evaluated to address class imbalance and improve dengue risk classification.

The experiments included:

- Original Random Forest
- Balanced Random Forest
- Weighted Random Forest
- SMOTENC + Balanced Random Forest

SMOTENC + Balanced Random Forest was selected for the current prediction pipeline because it achieved the highest observed test accuracy among the evaluated models (approximately 76.99%).

However, the Weighted Random Forest achieved better Critical-class recall. Therefore, model selection involves a trade-off between overall accuracy and detecting high-risk cases.

The selected model is an experimental decision-support model and requires further validation before real-world public health deployment.

## 12. Compute and API Cost Efficiency

### Model Serialization

Trained machine learning models are saved using Joblib serialization.

This avoids retraining the model whenever the Streamlit application starts.

The prediction pipeline loads the saved model and reuses it for user predictions.

### API Minimization

The current system performs local inference using the saved machine learning model.

It does not require external AI APIs or paid inference services for predictions.

Historical datasets and trained models are stored locally during development.

### LLM and Token Cost Controls

The current application does not depend on an LLM for dengue predictions. Therefore, it does not incur LLM token costs.

Future integrations should use limited API calls, caching, and controlled token usage to minimize operational expenses.

---

**DengueGuard AI — Exploring AI for Dengue Risk Awareness in Bangladesh.**