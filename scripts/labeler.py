import streamlit as st
import pandas as pd
import os

RAW_DATA_PATH = os.path.join("data", "raw_logs")
LABELED_DATA_PATH = os.path.join("data", "labeled_logs.csv")

def load_all_data() :
    if not os.path.exists(RAW_DATA_PATH) :
        st.error("Raw log folder not found! ")
        return pd.DataFrame()
    
    all_dfs = []
    for file in os.listdir(RAW_DATA_PATH) :
        if file.endswith(".csv") :
            df = pd.read_csv(os.path.join(RAW_DATA_PATH, file))
            df["source_file"] = file
            all_dfs.append(df)

    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

def main() :
    st.title("Bulk Activity Labeler")

    df = load_all_data()
    
    if df.empty :
        st.warning("No data found to label.")
        return    

    if os.path.exists(LABELED_DATA_PATH) and os.path.getsize(LABELED_DATA_PATH) > 0 :
        labeled_df = pd.read_csv(LABELED_DATA_PATH)
        labeled_timestamp = set(labeled_df['timestamp'])
        df = df[~df["timestamp"].isin(labeled_timestamp)].reset_index(drop=True)
    
    df_1 = df.copy()
    length_data = len(df)

    if df.empty :
        st.success("All data has been labeled")
        return

    CHUNK_SIZE = 5
    if "page" not in st.session_state :
        st.session_state.page = 0
    if "labels" not in st.session_state :
        st.session_state.label = {}

    max_page = (length_data - 1)

    if st.session_state.page > max_page :
        st.session_state.page = max_page

    start = st.session_state.page * CHUNK_SIZE
    end = min(start + CHUNK_SIZE, length_data)
    chunk = df_1.iloc[start:end]

    st.markdown(f"### Labeling Records {start + 1} to {min(end, length_data)} of {length_data}")

    for i, row in chunk.iterrows() :
            with st.expander(f"Record {i+1} : {row['active_window'][:50]}") :
                st.code(f"Time : {row['timestamp']}\nWindow : {row['active_window']}", language='text')
                label_key = f"label_{start + i}"
                if label_key not in st.session_state.label :
                    st.session_state.label[label_key] = ""
                st.session_state.label[i] = st.radio(
                    f"Label for record {i+1}",
                    ["", "Focused", "Neutral", "Distracted"],
                    index=["", "Focused", "Neutral", "Distracted"].index(st.session_state.label.get(i, "")),
                    key = label_key
                )

    all_labeled = all(st.session_state.label[i] != "" for i in range(start, end))

    if not chunk.empty :
        if st.button("Save/Next", disabled=not all_labeled) :
            labeled = []
            for i, row in chunk.iterrows() :
                label = st.session_state.label.get(i, "")
                if label :
                    labeled.append({"timestamp": row['timestamp'], "active_window": row['active_window'], "source_file": row['source_file'], "label": label})
            if labeled :
                labeled_df = pd.DataFrame(labeled)
                labeled_df.to_csv(LABELED_DATA_PATH, mode='a', index=False, header=not os.path.exists(LABELED_DATA_PATH) or os.path.getsize(LABELED_DATA_PATH) == 0)

                st.success(f"{len(labeled)} labels saved.")
            else :
                st.warning("No labels were selected to save.")

            st.session_state.page += 1
            st.session_state.label.clear()
            st.rerun()


if __name__ == "__main__" :
    main()
