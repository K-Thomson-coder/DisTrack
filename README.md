# An Exploration of Machine Learning Models for Predicting Focus Levels

## # Overview
This project explores the use of different Machine Learning models to **predict user focus levels** based on activity data.  
Instead of building a full application, our goal is to **experiment with multiple models**, compare their performance, and understand which approaches work best for this task.

---

## # Problem Statement
Maintaining focus is essential in education and workplace productivity.  
However, measuring focus objectively is challenging. This project investigates whether **user activity data** can be used to classify levels of focus (e.g., *focused, neutral, distracted*) using Machine Learning.

---

## # Objectives
- Collect and preprocess user activity data.  
- Train and evaluate multiple ML models for focus prediction.  
- Compare models using standard metrics (accuracy, precision, recall, F1-score).  
- Identify the most effective model for this problem.  

---

## # Dataset
- **Source:** The dataset was collected **manually** using two custom scripts :

  - `logger.py` – A Python script that runs in the terminal and records raw user activity (without labels). The data is stored in `data/raw_logs/activity_log.csv`.

  - `labeler.py` – A Streamlit-based labeling tool that loads the raw activity logs and allows manual labeling of each entry. The labeled dataset is saved in `data/labeled_logs.csv`.

  - The labeled logs are then organized into fixed 1-minute intervals and saved as `data/1minDataset.csv`, which serves as the final labeled dataset used for training and evaluation.

- **Features:**  
  - timestamp – Exact time of the recorded activity.
  - hour, min – Extracted from timestamp to capture time-of-day patterns.
  - active_window – The application/window in focus at the time of logging.
  - keystrokes – Number of key presses recorded within the interval.
  - mouse_clicks – Number of mouse clicks recorded within the interval.
  - idle_time_sec – Duration (in seconds) of inactivity during the interval.
  - label – Manually assigned focus level.
- **Labels:** `Focused`, `Neutral`, `Distracted`.  
- **Preprocessing:** Before training, the final labeled dataset (1minDataset.csv) undergoes the following preprocessing and feature engineering steps:

  1. Label encoding :
    - Map text labels (Focused, Neutral, Distracted) to numeric values (0, 1, 2).
  2. Feature cleanup :
    - Dropped unused columns (timestamp, hour, min, label) while retaining informative features.
  3. Derived features :
  Additional features were engineered to better capture user activity patterns:
    - keystroke_per_sec, mouse_clicks_per_sec – activity rates normalized over time.
    - activity_rate – combined activity of keystrokes + clicks adjusted by idle time.
    - idle_ratio – proportion of idle time to total time.
    - key_mouse_ratio – balance between keystrokes and mouse clicks.
    - idle_to_active_ratio – relative inactivity compared to activity.
  4. Time features (cyclical encoding) :
    - Converted hour and minute into sine/cosine pairs (hour_sin, hour_cos, minute_sin, minute_cos) to preserve cyclic nature of time.
  5. Text and numeric feature processing :
    - active_window (categorical text) → transformed using TF–IDF vectorizer.
    - Numeric features → passed directly.
    - Combined via a ColumnTransformer to ensure consistent preprocessing.
  6. Train-test preparation :
    - Preprocessing pipeline integrated with a classifier to ensure transformations are applied consistently during training and inference.

---

## # Methodology
We experimented with the following models:
- Decision Tree
- KNN
- Logistic Regression  
- Naive Bayes
- Random Forest  
- Support Vector Machine (SVM)    

All models were implemented in **Python** using **scikit-learn** and other standard ML libraries.

---

## # Results
The models were evaluated using Accuracy, Precision, Recall, and F1-score.

| Model               | Accuracy | Precision | Recall | F1-score |
|---------------------|----------|-----------|--------|----------|
| Decision Tree       | 0.90     | 0.92      | 0.91   | 0.90     |
| KNN                 | 0.62     | 0.63      | 0.62   | 0.62     |
| Logistic Regression | 0.93     | 0.93      | 0.93   | 0.76     |
| Naive Bayes         | 0.95     | 0.95      | 0.95   | 0.95     |
| Random Forest       | 0.88     | 0.90      | 0.88   | 0.88     |
| SVM                 | 0.57     | 0.49      | 0.54   | 0.47     |


Visualizations:  
- Classification report  

---

## # Discussion
#### Model Comparison:
- Naive Bayes achieved the highest overall accuracy (0.95) and balanced precision/recall/F1-score. This suggests that the features in the dataset are relatively well-separated and that the conditional independence assumption of Naive Bayes worked reasonably well.

- Logistic Regression also performed strongly (0.93 accuracy), but its lower F1-score (0.76) suggests imbalance in performance across classes.

- Random Forest performed competitively (0.88 accuracy, 0.88 F1-score) and is more robust to non-linear patterns, but may have been limited by the dataset size, leading to slight overfitting.

- Decision Tree showed decent performance (0.90 accuracy), but lower generalization compared to Random Forest, consistent with the known instability of single trees.

- KNN (0.62 accuracy) and SVM (0.57 accuracy) performed poorly, possibly because the dataset size is small and the feature space is not well-scaled or separable for these models.

#### Impact of Dataset Characteristics:

- The dataset is relatively small and manually labeled, which limits model generalization.

- The distribution of classes may have affected metrics — for example, the F1-score differences suggest that minority classes were harder to classify.

- Engineered features (keystrokes, mouse activity, idle time, etc.) seem to be predictive, but additional contextual features (e.g., application type, session duration) could improve performance.

#### Key Insights:

- Simpler probabilistic models (Naive Bayes, Logistic Regression) worked surprisingly well.

- Tree-based methods (Decision Tree, Random Forest) are promising but may need more data to fully leverage their power.

- Distance-based (KNN) and margin-based (SVM) models are less suitable here without further feature scaling/engineering.

#### Limitations & Future Work:

- Small dataset size — larger, more diverse logs would improve reliability.

- Manual labeling introduces subjectivity; semi-supervised labeling could help.

- Further preprocessing (feature scaling, dimensionality reduction) might improve KNN and SVM performance.

- Exploring deep learning or ensemble stacking could yield better results with larger datasets. 

---

## # Conclusion & Future Work
- Machine Learning shows potential for predicting focus levels.  
- Future improvements could include:  
  - Larger and more diverse datasets.  
  - Testing Deep Learning models.  
  - Real-time focus prediction in practical applications.  

---

## # How to Run
Clone the repository and install dependencies:
```bash
git clone https://github.com/K-Thomson-coder/DisTrack-A-Machine-Learning-Approach-to-Detecting-User-Distraction-from-Desktop-Activity.git
cd DisTrack-A-Machine-Learning-Approach-to-Detecting-User-Distraction-from-Desktop-Activity
pip install -r requirements.txt
```
### Demo application
A simple demo interface was created using **Streamlit** (`app.py`).
It loads the trained **Naive Bayes model** and allows testing predictions interactively.
This demo app includes an alert mechanism that plays a sound when the user is detected as distracted in consecutive predictions.

Run with :
```bash
streamlit run app.py
```

## # Technologies Used
- Python
- scikit-learn
- pandas, numpy

For the full list of dependencies and versions, see [`requirements.txt`](requirements.txt).

## # Contributors
- [Kangujam Thomson Singh](https://github.com/K-Thomson-coder)
- [Ricky Yumnam](https://github.com/Ricky-123497)
- [Thongratabam Rishikesh Sharma](https://github.com/Rishikesh-Sharma29)