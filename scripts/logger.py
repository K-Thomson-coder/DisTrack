import time
import datetime
import pandas as pd
import pygetwindow as gw
from pynput import keyboard, mouse
import os
import ctypes

LOG_INTERVAL = 300  # seconds
OUTPUT_CSV = "data/raw_logs/activity_log.csv"

key_count = 0
mouse_clicks = 0

# Keyboard listener
def on_press(key):
    global key_count
    key_count += 1

# Mouse listener
def on_click(x, y, button, pressed):
    global mouse_clicks
    if pressed:
        mouse_clicks += 1

# Windows idle time structure
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

def get_idle_time():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
    millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0

def get_active_window():
    try:
        window = gw.getActiveWindow()
        return window.title if window else "Unknown"
    except:
        return "Error"

def collect_activity():
    global key_count, mouse_clicks
    data = []

    print("[Logger] Press Ctrl+C to stop logging")

    # Start listeners
    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()

    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    try:
        while True:
            now = datetime.datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
            active_window = get_active_window()
            idle_time = get_idle_time()

            data.append({
                'timestamp': timestamp,
                'hour': now.hour,
                'min': now.minute,
                'active_window': active_window,
                'keystrokes': key_count,
                'mouse_clicks': mouse_clicks,
                'idle_time_sec': idle_time,
                'label': ""  # to be added later manually
            })

            print(f"[{timestamp}] Active: {active_window} | Keys: {key_count} | Clicks: {mouse_clicks} | Idle: {idle_time:.2f}s")

            # Reset counters
            key_count = 0
            mouse_clicks = 0

            time.sleep(LOG_INTERVAL)

    except KeyboardInterrupt:
        print("\n[Logger] Stopped. Saving data ...")
        df = pd.DataFrame(data)

        # Ensure the CSV directory exists
        os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

        # Read existing CSV safely
        if os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0:
            try:
                existing_df = pd.read_csv(OUTPUT_CSV)
            except pd.errors.EmptyDataError:
                existing_df = pd.DataFrame()
        else:
            existing_df = pd.DataFrame()

        # Determine last sl_no
        last_sl_no = existing_df["sl_no"].max() if "sl_no" in existing_df.columns else 0
        if pd.isna(last_sl_no):
            last_sl_no = 0

        # Insert sl_no column
        df.insert(0, "sl_no", range(int(last_sl_no) + 1, int(last_sl_no) + 1 + len(df)))

        # Save to CSV (append if exists)
        df.to_csv(OUTPUT_CSV, mode='a', header=os.path.getsize(OUTPUT_CSV) == 0, index=False)
        print(f"[Logger] Data saved to {OUTPUT_CSV}")

if __name__ == '__main__':
    collect_activity()
