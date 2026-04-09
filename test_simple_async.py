"""
Simple direct test of winsound with SND_ASYNC
"""
import winsound
import os
import time

alert_file = r"C:\Users\komal\Downloads\Real-Time-Drowsiness-Detection-System-main (1)\Real-Time-Drowsiness-Detection-System-main\Alert.wav"

print("Testing async sound playback...")
print(f"File: {alert_file}")
print(f"Exists: {os.path.exists(alert_file)}\n")

# Test 1: Simple async beep
print("1. Playing first alert (2 beeps with async)...")
try:
    winsound.PlaySound(alert_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    print("   ✓ First alert started")
    time.sleep(1)
    
    winsound.PlaySound(alert_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    print("   ✓ Second alert started")
    time.sleep(2)
    
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n2. Done! Alerts played in background.")
