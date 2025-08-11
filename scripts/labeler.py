import streamlit as st
import pandas as pd
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

    if os.path.exists(LABELED_DATA_PATH) and os.path.getsize(LABELED_DATA_PATH) > 0 :
        labeled_df = pd.read_csv(LABELED_DATA_PATH)
        labeled_sl_no = set(labeled_df['sl_no'])
        df = df[~df["sl_no"].isin(labeled_sl_no)].reset_index(drop=True)

    if df.empty :
        st.success("All data has been labeled")
        return

    total_records = df["sl_no"].max()

    if "page" not in st.session_state :
        st.session_state.page = 0
    if "label" not in st.session_state :
        st.session_state.label = {}
    
    length_data = len(df)
    max_page = (length_data - 1) // CHUNK_SIZE

    if st.session_state.page > max_page :
        st.session_state.page = max_page

    start = st.session_state.page * CHUNK_SIZE
    end = min(start + CHUNK_SIZE, length_data)
    chunk = df.iloc[start:end]

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

    if not chunk.empty :
        if st.button("Save/Next", disabled=not all_labeled) :
            labeled = []
            for _, row in chunk.iterrows() :
                label = st.session_state.label[f"label_{row['sl_no']}"]
                if label :
                    labeled.append({'sl_no' : row['sl_no'], 'timestamp': row['timestamp'], 'hour': row['hour'], 'min': row['min'], "active_window": row['active_window'], 'keystrokes': row['keystrokes'], 'mouse_clicks': row['mouse_clicks'], "label": label})
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
