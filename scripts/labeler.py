import streamlit as st
import pandas as pd
import math
import os

RAW_DATA_PATH = os.path.join("data", "raw_logs")
LABELED_DATA_PATH = os.path.join("data", "labeled_logs.csv")
CHUNK_SIZE = 5

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
<<<<<<< HEAD
        previous_sl_no = set(labeled_df['sl_no'])
        
    df = df[~df["sl_no"].isin(previous_sl_no)].reset_index(drop=True)
    
    st.session_state.length_data = len(df)
=======
        labeled_sl_no = set(labeled_df['sl_no'])
        df = df[~df["sl_no"].isin(labeled_sl_no)].reset_index(drop=True)
>>>>>>> b73805286b2a81dbddd776d7e071a530d0ecd894

    if df.empty :
        st.success("All data has been labeled")
        return

    total_records = df["sl_no"].max()

    if "page" not in st.session_state :
        st.session_state.page = 0
    if "label" not in st.session_state :
        st.session_state.label = {}
<<<<<<< HEAD

    max_page = math.ceil(st.session_state.length_data / CHUNK_SIZE) - 1
=======
    
    length_data = len(df)
    max_page = (length_data - 1) // CHUNK_SIZE
>>>>>>> b73805286b2a81dbddd776d7e071a530d0ecd894

    if st.session_state.page > max_page :
        st.session_state.page = max_page

    start = st.session_state.page * CHUNK_SIZE
    end = min(start + CHUNK_SIZE, st.session_state.length_data)
    chunk = df.iloc[start:end]

<<<<<<< HEAD
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
=======
    first_record_num = chunk["sl_no"].iloc[0]
    last_record_num = chunk["sl_no"].iloc[-1]
    st.markdown(f"### Labeling Records {first_record_num} to {last_record_num} of {total_records}")

    for i, row in chunk.iterrows() :
            with st.expander(f"Record {row['sl_no']} : {row['active_window'][:50]}") :
                st.code(f"Time : {row['timestamp']}\nWindow : {row['active_window']}", language='text')
                
                label_key = f"label_{row['sl_no']}"

                if label_key not in st.session_state.label :
                    st.session_state.label[label_key] = ""

                st.session_state.label[label_key] = st.radio(
                    f"Label for record {row['sl_no']}",
                    ["", "Focused", "Neutral", "Distracted"],
                    index=["", "Focused", "Neutral", "Distracted"].index(st.session_state.label.get(label_key, "")),
                    key = label_key
                )

    all_labeled = all(st.session_state.label[f"label_{sl}"] != "" for sl in chunk["sl_no"])
>>>>>>> b73805286b2a81dbddd776d7e071a530d0ecd894

    if not chunk.empty :
        if st.button("Save/Next", disabled=not all_labeled) :
            labeled = []
<<<<<<< HEAD
            for idx, (row_index, row) in enumerate(chunk.iterrows()) :
                record_number = start + idx
                label_key = f'label_{record_number}'
                label = st.session_state.get(label_key, "")
                if label :
                    labeled.append({'sl_no': row['sl_no'],'timestamp': row['timestamp'], 'hour': row['hour'], 'min': row['min'], "active_window": row['active_window'], 'keystrokes': row['keystrokes'], 'mouse_clicks': row['mouse_clicks'],'idle__time_sec': row['idle_time_sec'], "label": label})
=======
            for _, row in chunk.iterrows() :
                label = st.session_state.label[f"label_{row['sl_no']}"]
                if label :
                    labeled.append({'sl_no' : row['sl_no'], 'timestamp': row['timestamp'], 'hour': row['hour'], 'min': row['min'], "active_window": row['active_window'], 'keystrokes': row['keystrokes'], 'mouse_clicks': row['mouse_clicks'], "label": label})
>>>>>>> b73805286b2a81dbddd776d7e071a530d0ecd894
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
