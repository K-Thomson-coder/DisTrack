# DisTrack : A Machine Learning Approach To Detecting User Distraction From Desktop Activity

DisTrack is a real-time desktop application that monitors user behavior and uses a trained machine learning model to detect moments of distraction. The system provides timely alerts to help users stay focused during work or study sessions. 

---

## Data/

```
^
|
|---raw_logs
|     |---activity_log.csv    # Recorded activities -> 1 record = 5 min
|
|---labeled_logs.csv          # Labeled dataset of activity_log.csv
```

---

## scripts/

```
^
|
|---labeler.py # Labels logged activity from activity_log.csv and save as labeled_logs.csv
|
|---logger.py      # Logs the user activity into activity_log.csv for model training
```

---

