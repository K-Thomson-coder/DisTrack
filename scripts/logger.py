import time
import datetime
import pandas as pd
import psutil
import pygetwindow as gw
from pynput import keyboard

LOG_INTERVAL = 60
OUTPUT_CSV = "../data/raw_logs/activity_log.csv"

key_count =0

def on_press(key) :
    global key_count 
    key_count += 1

def get_idle_time() :
    idle_time = time.time() - psutil.boot_time()
    for proc in psutil.process_iter(['pid', 'name']) :
        try :
            if proc.name().lower() == 'explorer.exe' :
                idle_time = proc.create_time()
        except :
            continue
    return round((time.time() - idle_time), 2) 

def get_active_window() :
    try :
        window = gw.getActiveWindow()
        return window.title if window else "Unknown"
    except :
        return "Error"
    
def colect_activity() :
    global key_count
    data = []

    print("[Logger] Press Ctrl+C to stop logging")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try :
        while True :
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            active_window = get_active_window()
            idle_time = get_idle_time()

            data.append({
                'timestamp' : timestamp,
                'active_window' : active_window,
                'keystrokes' : key_count,
                'idle_time_sec' : idle_time,
                'label' : ""  # to be added later manually
            })

            print(f"[{timestamp}] Active : {active_window} | key : {key_count} | Idle : {idle_time}s")
            key_count = 0 # reset

            time.sleep(LOG_INTERVAL)

    except KeyboardInterrupt :
        print("\n[Logger] Stopped. Saving data ....")
        df = pd.DataFrame(data)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"[Logger] Data saved to {OUTPUT_CSV}")


if __name__ == '__main__' :
    colect_activity()

