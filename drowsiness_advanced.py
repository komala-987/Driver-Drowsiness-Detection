"""
Advanced Drowsiness Detection System
- Detects 5 seconds of continuous eye closure
- Detects frequent blinking (too many blinks per minute = drowsiness indicator)
"""

import cv2
import numpy as np
import os
from threading import Thread
import time
import winsound

script_dir = os.path.dirname(os.path.abspath(__file__))

def sound_alarm(path, beep_count=3):
    """Play alarm multiple times"""
    try:
        if not os.path.exists(path):
            print(f"[ERROR] Alert file not found: {path}")
            for _ in range(beep_count):
                winsound.Beep(1000, 500)
                time.sleep(0.2)
            return
        
        print(f"\n[ALARM] Playing alert sound...")
        for i in range(beep_count):
            winsound.PlaySound(path, winsound.SND_FILENAME)
            if i < beep_count - 1:
                time.sleep(0.3)
        print("[ALARM] Alert complete!\n")
    except Exception as e:
        print(f"[ERROR] Sound playback failed: {e}")
        try:
            for _ in range(beep_count):
                winsound.Beep(1000, 500)
                time.sleep(0.2)
        except:
            pass

def is_eye_closed(eye_region, threshold=100):
    """Detect if eye is closed based on contour area"""
    if eye_region is None or eye_region.size == 0:
        return True
    
    _, thresh = cv2.threshold(eye_region, 70, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return True
    
    max_area = max(cv2.contourArea(c) for c in contours) if contours else 0
    return max_area < threshold

# Load classifiers
detector = cv2.CascadeClassifier(os.path.join(script_dir, "haarcascade_frontalface_default.xml"))
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

alarm_file = os.path.join(script_dir, "Alert.wav")

# Detection parameters
EYES_CLOSED_THRESHOLD = 150  # 5 seconds at 30fps
BLINK_THRESHOLD = 25  # More than 25 blinks per minute = drowsy
BLINK_WINDOW = 60  # Window for counting blinks (frames, ~2 seconds at 30fps)

# State tracking
eyes_closed_count = 0
eyes_were_open = True
blink_count = 0
blink_times = []
last_alarm_time = 0
frame_count = 0
alarm_triggered_continuous = False
alarm_triggered_blink = False

print("\n" + "="*80)
print("ADVANCED DROWSINESS DETECTION SYSTEM")
print("="*80)
print(f"\nAlarm file: {alarm_file}")
print(f"File exists: {os.path.exists(alarm_file)}")
print("\nDetection Parameters:")
print(f"  • Continuous eye closure alert: {EYES_CLOSED_THRESHOLD} frames (~{EYES_CLOSED_THRESHOLD/30:.1f} seconds)")
print(f"  • Frequent blinking alert: >{BLINK_THRESHOLD} blinks/minute")
print(f"\nInstructions:")
print("  1. Keep eyes open for normal driving")
print("  2. Close eyes for 5 seconds continuously → ALERT")
print("  3. Blink very frequently (>25 times/min) → ALERT")
print("  4. Press 'q' to quit\n")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

try:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Camera error - retrying...")
            time.sleep(0.1)
            continue
        
        frame_count += 1
        frame = cv2.resize(frame, (450, 350))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        faces = detector.detectMultiScale(gray, 1.05, 4, 0, (30, 30))
        
        face_found = False
        eyes_closed_this_frame = 0
        total_eyes_detected = 0
        
        for (x, y, w, h) in faces:
            face_found = True
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.05, 3, 0, (15, 15))
            
            if len(eyes) >= 2:
                total_eyes_detected = 2
                eye_list = sorted(eyes, key=lambda e: e[0])[:2]
                
                for (ex, ey, ew, eh) in eye_list:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                    
                    eye_region = roi_gray[ey:ey+eh, ex:ex+ew]
                    if is_eye_closed(eye_region):
                        eyes_closed_this_frame += 1
        
        # DETECT BLINKS
        # A blink is when both eyes transition from open → closed → open
        eyes_closed_now = (eyes_closed_this_frame >= 2 and total_eyes_detected == 2)
        
        if not eyes_closed_now and eyes_were_open == False:
            # Eyes just opened - this was a blink
            blink_count += 1
            blink_times.append(frame_count)
            # Keep only recent blink times (within BLINK_WINDOW frames)
            blink_times = [t for t in blink_times if frame_count - t < BLINK_WINDOW]
        
        eyes_were_open = not eyes_closed_now
        
        # DETECT CONTINUOUS EYE CLOSURE
        if eyes_closed_now:
            eyes_closed_count += 1
        else:
            eyes_closed_count = 0
            alarm_triggered_continuous = False
        
        # Check for continuous eye closure alert
        if eyes_closed_count >= EYES_CLOSED_THRESHOLD and not alarm_triggered_continuous:
            alarm_triggered_continuous = True
            current_time = time.time()
            if current_time - last_alarm_time > 1:
                last_alarm_time = current_time
                print(f"\n[FRAME {frame_count}] ALERT: Continuous eye closure detected! ({eyes_closed_count} frames = {eyes_closed_count/30:.1f} seconds)")
                t = Thread(target=sound_alarm, args=(alarm_file, 3), daemon=True)
                t.start()
        
        # Check for frequent blinking alert
        # Calculate blinks per minute
        recent_blinks = len(blink_times)
        blink_rate = (recent_blinks / BLINK_WINDOW) * 1800  # Convert to per minute (30fps, 60 frames/sec)
        
        if blink_rate > BLINK_THRESHOLD and not alarm_triggered_blink:
            if recent_blinks >= 3:  # Need at least 3 blinks to be sure
                alarm_triggered_blink = True
                current_time = time.time()
                if current_time - last_alarm_time > 1:
                    last_alarm_time = current_time
                    print(f"\n[FRAME {frame_count}] ALERT: Excessive blinking detected! ({blink_rate:.1f} blinks/min)")
                    t = Thread(target=sound_alarm, args=(alarm_file, 2), daemon=True)
                    t.start()
        elif blink_rate <= BLINK_THRESHOLD:
            alarm_triggered_blink = False
        
        # Draw status on frame
        h, w = frame.shape[:2]
        
        # Status box
        if eyes_closed_count >= EYES_CLOSED_THRESHOLD:
            cv2.rectangle(frame, (5, 5), (450, 85), (0, 0, 255), -1)
            cv2.putText(frame, "DROWSINESS ALERT!", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(frame, f"Eyes Closed: {eyes_closed_count/30:.1f}s", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        elif blink_rate > BLINK_THRESHOLD and recent_blinks >= 3:
            cv2.rectangle(frame, (5, 5), (450, 85), (0, 0, 255), -1)
            cv2.putText(frame, "EXCESSIVE BLINKING!", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(frame, f"Blinks: {blink_rate:.0f}/min", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        else:
            cv2.rectangle(frame, (5, 5), (450, 85), (0, 100, 0), -1)
            cv2.putText(frame, "ALERT MONITORING", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Eyes Closed: {eyes_closed_count/30:.1f}s | Blinks: {blink_rate:.0f}/min", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        # Counter display
        cv2.putText(frame, f"Frame: {frame_count}", (10, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        if not face_found:
            cv2.putText(frame, "NO FACE DETECTED", (150, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        
        cv2.imshow("Drowsiness Detection", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nExiting...")
            break

except KeyboardInterrupt:
    print("\nInterrupted by user")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Program ended\n")
