import pandas as pd

files = ["distracted.csv", "neutral.csv", "focussed.csv"]

dfs = []

for f in files :
    df = pd.read_csv(f)
    if "sl_no" in df.columns :
        df = df.drop(columns = "sl_no")
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index = True)
combined_df.to_csv("1minDataset.csv", index = False)

print("Combined file saved as 1minDataset.csv")