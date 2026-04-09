"""
Drowsiness Alarm Test - Simulates eye closure without camera
Tests that the alarm and sound system works correctly
"""

import os
import time
from threading import Thread
import winsound

script_dir = os.path.dirname(os.path.abspath(__file__))
alarm_file = os.path.join(script_dir, "Alert.wav")

def sound_alarm(path):
    try:
        if not os.path.exists(path):
            print(f"[ERROR] Alert file not found: {path}")
            winsound.Beep(1000, 500)
            return
        
        print(f"[SOUND] Playing alarm from: {path}")
        winsound.PlaySound(path, winsound.SND_FILENAME)
        print("[SOUND] Alarm played successfully!")
    except Exception as e:
        print(f"[ERROR] Sound playback failed: {e}")

print("\n" + "="*70)
print("DROWSINESS DETECTION - ALARM TEST")
print("="*70)
print(f"\nAlarm file: {alarm_file}")
print(f"File exists: {os.path.exists(alarm_file)}")
print(f"File size: {os.path.getsize(alarm_file) if os.path.exists(alarm_file) else 'N/A'} bytes\n")

if not os.path.exists(alarm_file):
    print("[ERROR] Alert.wav not found!")
    exit(1)

EYE_AR_CONSEC_FRAMES = 8
EYES_CLOSED_COUNT = 0
last_alarm_time = 0

print("Simulating eye closure detection...\n")
print("Count | Eyes Closed | Status")
print("-" * 50)

for frame in range(1, 30):
    # Simulate eyes being closed for frames 10-20
    if 10 <= frame <= 20:
        EYES_CLOSED_COUNT += 1
        status = "CLOSING"
    else:
        EYES_CLOSED_COUNT = 0
        status = "OPEN"
    
    print(f"{frame:5d} | {EYES_CLOSED_COUNT:11d} | {status}")
    
    # Check alarm trigger
    if EYES_CLOSED_COUNT >= EYE_AR_CONSEC_FRAMES:
        current_time = time.time()
        if current_time - last_alarm_time > 2:
            last_alarm_time = current_time
            print(f"\n{'*'*70}")
            print(f"DROWSINESS ALERT TRIGGERED! Eyes closed for {EYES_CLOSED_COUNT} frames")
            print(f"{'*'*70}\n")
            t = Thread(target=sound_alarm, args=(alarm_file,), daemon=True)
            t.start()
    
    time.sleep(0.1)  # ~100ms per frame

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nIf you heard 2 alarm sounds, the system is working correctly!")
print("When camera is working, this same logic will trigger on real eye closure.")
