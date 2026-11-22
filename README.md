# 🦟 DengueGuard AI
### AI-Powered Dengue Risk Prediction System

DengueGuard AI is a machine learning-based system designed to predict dengue risk levels using historical dengue cases and weather-related data. It aims to support early awareness and help identify areas that may require closer attention.

## 🚀 Project Overview

Dengue is a major public health concern in Bangladesh. DengueGuard AI uses historical data and machine learning techniques to classify dengue risk into four categories:

- 🟢 **Low**
- 🟡 **Medium**
- 🟠 **High**
- 🔴 **Critical**

The system provides an interactive dashboard built with Streamlit, allowing users to enter relevant environmental and historical dengue information and receive a predicted risk category.

## ✨ Key Features

- Machine learning-based dengue risk classification.
- Four risk categories: Low, Medium, High, and Critical.
- Historical dengue case information.
- Weather-based features, including temperature, rainfall, and humidity.
- Lag-based feature engineering.
- Interactive Streamlit dashboard.
- Risk-specific recommendations.
- Model comparison and experimentation.

## 🧠 Machine Learning Approach

The project uses historical dengue and weather data to predict the next week's dengue risk category.

### Features Used

The model uses 14 input features:

- Ward ID
- Previous week's dengue cases
- Average temperature from the previous four weeks
- Rainfall from the previous four weeks
- Relative humidity from the previous four weeks

### Data Processing

- Data cleaning and preprocessing
- Feature engineering
- Historical lag feature generation
- Chronological train-test splitting
- Categorical feature encoding

### Models Experimented With

1. Random Forest Classifier
2. Weighted Random Forest Classifier
3. Balanced Random Forest Classifier
4. SMOTENC + Balanced Random Forest Classifier

Multiple models were evaluated to compare classification performance, particularly their ability to identify higher-risk categories.

## 📊 Dashboard

The application is developed using Streamlit and provides:

- Interactive prediction form
- Dengue risk classification
- Risk-level explanations
- Recommendations
- Project information
- Insights into the prediction process

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Imbalanced-learn
- Joblib
- Streamlit

## 📁 Project Structure

```text
DengueGuard_AI/
│
├── app.py
├── README.md
├── .gitignore
│
└── Dataset/
    ├── dengue_data.csv
    ├── cleaned_dengue_data.csv
    │
    ├── models/
    │
    └── src/
        ├── data_preprocessing.py
        ├── features.py
        ├── test_features.py
        ├── train_model.py
        ├── train_model_backup.py
        └── predict.py
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/mehrab-ux/DengueGuard_AI.git
```

### 2. Navigate to the project directory

```bash
cd DengueGuard_AI
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install pandas numpy scikit-learn imbalanced-learn joblib streamlit
```

### 6. Prepare the trained model

The trained model files are excluded from GitHub because of their large size.

A compatible trained model must be placed in `Dataset/models/` using the filename configured in `Dataset/src/predict.py`.

Alternatively, train a model using the available training script:

```bash
python Dataset/src/train_model.py
```

Check the model filename and output path in the training and prediction scripts to ensure they match.

### 7. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## ⚠️ Important Disclaimer

DengueGuard AI is an experimental machine learning project developed for educational and research purposes.

- Predictions are based on the available dataset and trained model.
- Risk categories are dataset-derived and are not medically validated thresholds.
- Predictions are not medical diagnoses.
- The system should not replace professional medical advice or official public health alerts.
- Model performance may vary when used with new or real-world data.

## 🎯 Project Goal

The goal of DengueGuard AI is to explore how machine learning can contribute to dengue risk awareness and support data-driven public health initiatives in Bangladesh.

---

**Developed as a machine learning and AI project for dengue risk prediction.**