import time
import datetime
import pandas as pd
import pygetwindow as gw
from pynput import keyboard, mouse
import os
import ctypes

LOG_INTERVAL = 60
OUTPUT_CSV = "data/raw_logs/activity_log.csv"

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
    _fields_ = [("cbSize", ctypes.c_uint, ctypes.sizeof(ctypes.c_uint)), ("dwTime", ctypes.c_uint)]

def get_idle_time() :
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
    millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis/1000.0

def get_active_window() :
    try :
        window = gw.getActiveWindow()
        return window.title if window else "Unknown"
    except :
        return "Error"
    
def collect_activity() :
    global key_count, mouse_clicks
    data = []

    print("[Logger] Press Ctrl+C to stop logging")

    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()

    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    try :
        while True :
            now = datetime.datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
            active_window = get_active_window()            
            idle_time = get_idle_time()

            data.append({
                'timestamp' : timestamp,
                'hour' : now.hour,
                'min' : now.minute,
                'active_window' : active_window,
                'keystrokes' : key_count,
                'mouse_clicks' : mouse_clicks,
                'idle_time_sec' : idle_time,
                'label' : ""  # to be added later manually
            })

            print(f"[{timestamp}] Active : {active_window} | key : {key_count} | click : {mouse_clicks} | Idle : {idle_time}s")
            key_count = 0 # reset
            mouse_clicks = 0

            time.sleep(LOG_INTERVAL)

    except KeyboardInterrupt :
        print("\n[Logger] Stopped. Saving data ....")
        df = pd.DataFrame(data)
        df = df.iloc[1:]

        if os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0 :
            existing_df = pd.read_csv(OUTPUT_CSV)
            if "sl_no" in existing_df.columns :
                last_sl_no = existing_df["sl_no"].max()
                if pd.isna(last_sl_no) :
                    last_sl_no = 0
                else :
                    last_sl_no = int(last_sl_no)
            else :
                last_sl_no = 0
        else :
            last_sl_no = 0

        df.insert(0, "sl_no", range(last_sl_no + 1, last_sl_no + 1 + len(df)))

        df.to_csv(OUTPUT_CSV, mode='a', header = os.path.getsize(OUTPUT_CSV) == 0, index=False)
        print(f"[Logger] Data saved to {OUTPUT_CSV}")


if __name__ == '__main__' :
    collect_activity()

