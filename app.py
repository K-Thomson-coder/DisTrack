import streamlit as st
import threading
import datetime
import pandas as pd
import numpy as np
import pygetwindow as gw
import ctypes
import time
from pynput import keyboard, mouse
from utils.helper import load_file

pipeline = load_file("model/pipeline.pkl")
labels = {0 : "Focused", 1 : "Neutral", 2 : "Distracted"}

key_count = 0
mouse_clicks = 0

def on_press(key) :
    global key_count
    key_count += 1
def on_click(x, y, button, pressed) :
    global mouse_clicks
    if pressed :
        mouse_clicks += 1

class LASTINPUTINFO(ctypes.Structure) :
    _fields_ = [("cbsize", ctypes.c_uint, ctypes.sizeof(ctypes.c_uint)), ("dwTime", ctypes.c_uint)]
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
    X = df.drop(["label", "timestamp"], axis=1, errors='ignore')  
    pred = pipeline.predict(X)
    return pred

if "data" not in st.session_state :
    st.session_state.data = []
if "monitoring" not in st.session_state :
    st.session_state.monitoring = False

def collect_data() :
    global key_count, mouse_clicks

    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    while st.session_state.monitoring :
        time.sleep(30)

        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        active_window = get_active_window()
        idle_time = get_idle_time()

        row = {
            'timestamp' : timestamp,
            'active_window' : active_window,
            'keystroke' : key_count,
            'mouse_clicks' : mouse_clicks,
            'idle_time_sec' : idle_time,
            'hour_sin' : np.sin(2 * np.pi * now.hour / 24),
            'hour_cos' : np.cos(2 * np.pi * now.hour / 24),
            'minute_sin' : np.sin(2 * np.pi * now.minute / 60),
            'minute_cos' : np.cos(2 * np.pi * now.minute / 60)
        }

        df_temp = pd.DataFrame([row])
        row['label'] = labels[int(data_prediction(df_temp)[0])]
        st.session_state.data.append(row)

        key_count = 0
        mouse_clicks = 0

st.set_page_config(page_title = "DisTrack", layout = "wide", page_icon='🧠')
st.title("Distraction Alert 🥴")

if st.button("▶ Start Monitoring") :
    if not st.session_state.monitoring :
        st.session_state.monitoring = True
        threading.Thread(target=collect_data, daemon=True).start()
        st.success("Monitoring started!")

if st.button("⏸ Stop Monitoring") :
    st.session_state.monitoring = False
    st.warning("Monitoring stopped.")

if st.button("🔄 Continue Monitoring") :
    if not st.session_state.monitoring :
        st.session_state.monitoring = True
        threading.Thread(target=collect_data, daemon=True).start()
        st.info("Monitoring resumed.")

if st.button("Export Data to CSV") :
    if st.session_state.data :
        df_export = pd.DataFrame(st.session_state.data)
        csv_data = df_export.to_csv(index = False).encode('utf-8')

        st.download_button(
            label="Download Data as CSV", 
            data = csv_data, file_name = f"activity_log_{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.csv",
            mime = ('text/csv')
        )
    else :
        st.warning("No data to export yet.")

st.subheader("Your Data")
if st.session_state.data :
    df_display = pd.DataFrame(st.session_state.data)
    st.dataframe(df_display)
else :
    st.info("No data collected yet.")