import streamlit as st
import datetime
import pandas as pd
import pygetwindow as gw
import ctypes
import time
import base64
from pynput import keyboard, mouse
from utils.helper import load_file, cleaner

pipeline = load_file("model/pipeline.pkl")
labels = {0 : "Focused", 1 : "Neutral", 2 : "Distracted"}
with open("data/sound_effect/DisTrack-alert-1.wav", 'rb') as f :
    alert_audio = f.read()

key_count = 0
mouse_clicks = 0


if "data" not in st.session_state :
    st.session_state.data = []
if "status" not in st.session_state :
    st.session_state.status = 'stopped'

def on_press(key) :
    global key_count
    key_count += 1
def on_click(x, y, button, pressed) :
    global mouse_clicks
    if pressed :
        mouse_clicks += 1

class LASTINPUTINFO(ctypes.Structure) :
    _fields_ = [("cbsize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
def get_idle_time() :
    lastinputinfo = LASTINPUTINFO()
    lastinputinfo.cbSize = ctypes.sizeof(lastinputinfo)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastinputinfo))
    millis = ctypes.windll.kernel32.GetTickCount() - lastinputinfo.dwTime
    return millis / 1000.0

def get_active_window() :
    try :
        window = gw.getActiveWindow()
        return window.title if window else "unknown"
    except :
        return "Error"
    
def data_prediction(df) :
    return pipeline.predict(df)[0]

def alert() :
    b64 = base64.b64encode(alert_audio).decode()
    audio_html = f"""
        <audio autoplay="true" style="display:none" >
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

def collect_data() :
    global key_count, mouse_clicks

    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener.start()
    mouse_listener.start()

    while st.session_state.status :
        time.sleep(60)

        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        active_window = get_active_window()
        idle_time = get_idle_time()

        row = {
            'timestamp' : timestamp,
            'active_window' : active_window,
            'keystroke' : key_count,
            'mouse_clicks' : mouse_clicks,
            'idle_time_sec' : idle_time
        }

        if row :
            features = {
                'active_window' : cleaner(active_window),
                'keystrokes' : key_count,
                'mouse_clicks' : mouse_clicks,
                'idle_time_sec' : idle_time,

                'keystroke_per_sec' : key_count / 60,
                'mouse_clicks_per_sec' : mouse_clicks / 60,
                'activity_rate' : (key_count + mouse_clicks) / (60 - idle_time + 1),

                'idle_ratio' : idle_time / 60,
                'key_mouse_ratio' : key_count / (mouse_clicks + 1),
                'idle_to_active_ratio' : idle_time / (key_count + mouse_clicks + 1)
            }
            df_temp = pd.DataFrame([features])
            pred = data_prediction(df_temp)

            key_count, mouse_clicks = 0, 0

            row['label'] = labels[int(pred)]
            st.session_state.data.append(row)
            return pred
        
        key_count, mouse_clicks = 0, 0
        
        return None


st.set_page_config(page_title = "DisTrack", layout = "wide", page_icon='🧠')
st.title("Distraction Alert 🥴")
col_a, col_b, col_c = st.columns(3)
if col_b :
    col1, col2 = st.columns(2)
    if col1.button("▶ Start") :
        st.session_state.status = 'running'
        st.success("started monitoring")
    if col2.button("⏸ Stop") :
        st.session_state.status = 'stopped'
        st.warning("status stopped.")

placeholder = st.empty()

if st.session_state.status == 'running' :
    distracted_count = 0
    while st.session_state.status == 'running' :
        pred = collect_data()

        if pred == 2 :
            distracted_count += 1
            if distracted_count >= 2 :
                alert()
                # distracted_count = 0
        else :
            distracted_count = 0

        df_logs = pd.DataFrame(st.session_state.data)
        placeholder.dataframe(df_logs, use_container_width = True)


# if st.button("⏸ Stop status") :
#     st.session_state.status = False
#     st.warning("status stopped.")

# if st.button("🔄 Continue status") :
#     if not st.session_state.status :
#         st.session_state.status = True
#         threading.Thread(target=collect_data, daemon=True).start()
#         st.info("status resumed.")

# if st.button("Export Data to CSV") :
#     if st.session_state.data :
#         df_export = pd.DataFrame(st.session_state.data)
#         csv_data = df_export.to_csv(index = False).encode('utf-8')

#         st.download_button(
#             label="Download Data as CSV", 
#             data = csv_data, file_name = f"activity_log_{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.csv",
#             mime = ('text/csv')
#         )
#     else :
#         st.warning("No data to export yet.")

# st.subheader("Your Data")
# if st.session_state.data :
#     df_display = pd.DataFrame(st.session_state.data)
#     st.dataframe(df_display)
# else :
#     st.info("No data collected yet.")