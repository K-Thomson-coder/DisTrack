import streamlit as st
import pandas as pd
import math
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
            all_dfs.append(df)

    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

def main() :
    st.title("Bulk Activity Labeler")

    df = load_all_data()
    
    if df.empty :
        st.warning("No data found to label.")
        return    
    
    previous_sl_no = set()
    if os.path.exists(LABELED_DATA_PATH) and os.path.getsize(LABELED_DATA_PATH) > 0 :
        labeled_df = pd.read_csv(LABELED_DATA_PATH)
        previous_sl_no = set(labeled_df['sl_no'])
        
    df = df[~df["sl_no"].isin(previous_sl_no)].reset_index(drop=True)
    
    st.session_state.length_data = len(df)

    if df.empty :
        st.success("All data has been labeled")
        return

    CHUNK_SIZE = 5
    if "page" not in st.session_state :
        st.session_state.page = 0
    if "labels" not in st.session_state :
        st.session_state.label = {}

    max_page = math.ceil(st.session_state.length_data / CHUNK_SIZE) - 1

    if st.session_state.page > max_page :
        st.session_state.page = max_page

    start = st.session_state.page * CHUNK_SIZE
    end = min(start + CHUNK_SIZE, st.session_state.length_data)
    chunk = df.iloc[start:end]

    st.markdown(f"### Labeling Records {start + 1} to {min(end, st.session_state.length_data)} of {st.session_state.length_data}")

    for idx, (row_index, row) in enumerate(chunk.iterrows()) :
            record_number = start + idx
            label_key = f'label_{record_number}'
            with st.expander(f"Record {record_number + 1} : {row['active_window'][:50]}") :
                st.code(f"Time : {row['timestamp']}\nWindow : {row['active_window']}", language='text')
                
                if label_key not in st.session_state :
                    st.session_state[label_key] = ""
                st.radio(
                    f"Label for record {record_number+1}",
                    ["", "Focused", "Neutral", "Distracted"],
                    index=["", "Focused", "Neutral", "Distracted"].index(st.session_state.get(label_key, "")),
                    key = label_key
                )

    all_labeled = all(st.session_state.get(f'label_{i}', "") != "" for i in range(start, end))

    if not chunk.empty :
        if st.button("Save/Next", disabled=not all_labeled) :
            labeled = []
            for idx, (row_index, row) in enumerate(chunk.iterrows()) :
                record_number = start + idx
                label_key = f'label_{record_number}'
                label = st.session_state.get(label_key, "")
                if label :
                    labeled.append({'sl_no': row['sl_no'],'timestamp': row['timestamp'], 'hour': row['hour'], 'min': row['min'], "active_window": row['active_window'], 'keystrokes': row['keystrokes'], 'mouse_clicks': row['mouse_clicks'],'idle__time_sec': row['idle_time_sec'], "label": label})
            if labeled :
                labeled_df = pd.DataFrame(labeled)
                labeled_df.to_csv(LABELED_DATA_PATH, mode='a', index=False, header=not os.path.exists(LABELED_DATA_PATH) or os.path.getsize(LABELED_DATA_PATH) == 0)

                st.success(f"{len(labeled)} labels saved.")
            else :
                st.warning("No labels were selected to save.")

            st.session_state.page += 1
            for i in range(start, end) :
                st.session_state.pop(f"label_{i}", None)
            st.rerun()


if __name__ == "__main__" :
    main()
