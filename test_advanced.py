"""
Advanced Drowsiness Detection - Simulation Test
Tests:
1. Continuous eye closure for 5 seconds
2. Frequent blinking (>25 blinks/minute)
"""

import os
import time
from threading import Thread
import winsound

script_dir = os.path.dirname(os.path.abspath(__file__))
alarm_file = os.path.join(script_dir, "Alert.wav")

def sound_alarm(path, beep_count=3):
    try:
        if not os.path.exists(path):
            for _ in range(beep_count):
                winsound.Beep(1000, 500)
                time.sleep(0.2)
            return
        
        print(f"[ALARM] Playing alert ({beep_count} sound(s))...")
        for i in range(beep_count):
            winsound.PlaySound(path, winsound.SND_FILENAME)
            if i < beep_count - 1:
                time.sleep(0.3)
        print("[ALARM] Alert complete!\n")
    except Exception as e:
        print(f"[ERROR] {e}")

print("\n" + "="*80)
print("DROWSINESS DETECTION - SIMULATION TEST")
print("="*80)
print(f"\nAlarm file: {alarm_file}")
print(f"File exists: {os.path.exists(alarm_file)}\n")

EYES_CLOSED_THRESHOLD = 150  # 5 seconds at 30fps
BLINK_THRESHOLD = 25
BLINK_WINDOW = 60

print("TEST 1: CONTINUOUS EYE CLOSURE (5 seconds)")
print("-" * 80)

eyes_closed_count = 0
last_alarm_time = 0

for frame in range(1, 200):
    # Simulate eyes closed for frames 50-200 (150 frames = 5 seconds)
    if frame >= 50:
        eyes_closed_count += 1
    else:
        eyes_closed_count = 0
    
    if frame % 30 == 0 or eyes_closed_count == EYES_CLOSED_THRESHOLD:
        status = f"Closed for {eyes_closed_count/30:.1f}s" if eyes_closed_count > 0 else "Open"
        print(f"Frame {frame:3d}: {status:20s} | THRESHOLD: {EYES_CLOSED_THRESHOLD/30:.1f}s")
    
    if eyes_closed_count >= EYES_CLOSED_THRESHOLD:
        current_time = time.time()
        if current_time - last_alarm_time > 1:
            last_alarm_time = current_time
            print(f"\n{'*'*80}")
            print(f"[FRAME {frame}] ALERT TRIGGERED: Continuous eye closure detected!")
            print(f"[FRAME {frame}] Eyes closed for {eyes_closed_count/30:.1f} seconds")
            print(f"{'*'*80}\n")
            t = Thread(target=sound_alarm, args=(alarm_file, 3), daemon=True)
            t.start()
            break
    
    time.sleep(0.02)  # Simulate ~50ms per frame

print("\n\nTEST 2: FREQUENT BLINKING (>25 blinks/minute)")
print("-" * 80)

eyes_were_open = True
blink_count = 0
blink_times = []
last_alarm_time = 0

# Simulate normal blinking pattern (open-close-open = 1 blink)
blink_pattern = (
    [True]*10 +   # Eyes open 10 frames
    [False]*3 +   # Eyes closed 3 frames (1 blink)
    [True]*8 +    # Eyes open 8 frames  
    [False]*3 +   # Eyes closed 3 frames (2nd blink)
    [True]*8 +    # Eyes open 8 frames
    [False]*3 +   # Eyes closed 3 frames (3rd blink)
    [True]*5 +    # Eyes open 5 frames
    # NOW SIMULATE EXCESSIVE BLINKING
    [False]*2 + [True]*2 +  # Blink 4
    [False]*2 + [True]*2 +  # Blink 5
    [False]*2 + [True]*2 +  # Blink 6
    [False]*2 + [True]*2 +  # Blink 7
    [False]*2 + [True]*2 +  # Blink 8
    [False]*2 + [True]*2 +  # Blink 9
    [False]*2 + [True]*2    # Blink 10 (>25/min detected in window)
)

for frame, eyes_closed_now in enumerate(blink_pattern, 1):
    # Detect blinks
    if not eyes_closed_now and eyes_were_open == False:
        blink_count += 1
        blink_times.append(frame)
        blink_times = [t for t in blink_times if frame - t < BLINK_WINDOW]
    
    eyes_were_open = not eyes_closed_now
    
    recent_blinks = len(blink_times)
    blink_rate = (recent_blinks / BLINK_WINDOW) * 1800
    
    eye_state = "Closed" if eyes_closed_now else "Open "
    if frame % 5 == 0 or recent_blinks > 3:
        print(f"Frame {frame:3d}: Eyes {eye_state} | Blinks detected: {recent_blinks:2d} | Rate: {blink_rate:6.1f}/min")
    
    if blink_rate > BLINK_THRESHOLD and recent_blinks >= 3:
        current_time = time.time()
        if current_time - last_alarm_time > 1:
            last_alarm_time = current_time
            print(f"\n{'*'*80}")
            print(f"[FRAME {frame}] ALERT TRIGGERED: Excessive blinking detected!")
            print(f"[FRAME {frame}] Blinking rate: {blink_rate:.1f} blinks/minute (>25 threshold)")
            print(f"{'*'*80}\n")
            t = Thread(target=sound_alarm, args=(alarm_file, 2), daemon=True)
            t.start()
            break
    
    time.sleep(0.02)

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
print("\nYou should have heard 2 different alert sequences:")
print("  • First test: 3 alarm sounds (continuous eye closure)")
print("  • Second test: 2 alarm sounds (frequent blinking)")
print("\nWhen camera works, these same triggers will work in real-time!")
print("="*80 + "\n")
