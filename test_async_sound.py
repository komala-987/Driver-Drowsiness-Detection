"""
Test the updated sound_alarm function with async playback
"""

import os
import sys
import winsound
import time
from threading import Thread

script_dir = os.path.dirname(os.path.abspath(__file__))
alert_file = os.path.join(script_dir, "Alert.wav")

USE_WINSOUND = True

def sound_alarm(path, beep_count=3):
    """Updated version with async (non-blocking) playback"""
    try:
        if not os.path.exists(path):
            print(f"Alert file not found: {path}")
            if USE_WINSOUND:
                for _ in range(beep_count):
                    winsound.Beep(1000, 500)
                    time.sleep(0.2)
            return
        
        if USE_WINSOUND:
            print(f"[ALARM] Playing alert ({beep_count} times)...")
            for i in range(beep_count):
                # SND_ASYNC makes it non-blocking
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                if i < beep_count - 1:
                    time.sleep(2.0)  # Wait for sound to finish
        print("[ALARM] Alert complete!")
    except Exception as e:
        print(f"Error playing sound: {e}")
        try:
            if USE_WINSOUND:
                for _ in range(beep_count):
                    winsound.Beep(1000, 500)
                    time.sleep(0.2)
        except:
            pass

print("🔊 SOUND ALERT TEST (Async Non-Blocking)")
print("=" * 60)

# Test 1: Single alert in foreground
print("\nTest 1: Single alert (3 beeps) - blocking thread")
print("This demonstrates the sound plays while message prints...")
start = time.time()
sound_alarm(alert_file, beep_count=3)
elapsed = time.time() - start
print(f"Total time: {elapsed:.1f}s\n")

time.sleep(2)

# Test 2: Alert in background thread (like the main program)
print("Test 2: Alert (2 beeps) in background thread")
print("Notice the program continues immediately...")
start = time.time()
t = Thread(target=sound_alarm, args=(alert_file, 2), daemon=True)
t.start()
print("Alert thread started, continuing immediately...")
for i in range(6):
    print(f"  Main loop continuing... {i+1}")
    time.sleep(0.5)
elapsed = time.time() - start
print(f"Total time: {elapsed:.1f}s\n")

print("=" * 60)
print("✓ Sound test complete!")
print("\nYour drowsiness_yawn.py now uses SND_ASYNC for non-blocking")
print("playback, so alerts won't freeze the video feed.")
