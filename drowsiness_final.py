"""
Drowsiness Detection - Testing with Sound
Simulates eye closure and tests alarm functionality
"""

import cv2
import numpy as np
import os
from threading import Thread
import time
import winsound

script_dir = os.path.dirname(os.path.abspath(__file__))

def sound_alarm(path):
    try:
        if not os.path.exists(path):
            print(f"Alert file not found: {path}")
            # Fallback beep
            winsound.Beep(1000, 500)
            return
        
        print(f"Playing alarm: {path}")
        winsound.PlaySound(path, winsound.SND_FILENAME)
        print("ALARM SOUND PLAYED!")
    except Exception as e:
        print(f"Error: {e}")

def is_eye_closed(eye_region):
    if eye_region is None or eye_region.size == 0:
        return True
    
    _, thresh = cv2.threshold(eye_region, 70, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return True
    
    max_area = max(cv2.contourArea(c) for c in contours) if contours else 0
    return max_area < 100

# Load classifiers
detector = cv2.CascadeClassifier(os.path.join(script_dir, "haarcascade_frontalface_default.xml"))
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

EYE_AR_CONSEC_FRAMES = 8  # Very sensitive
alarm_file = os.path.join(script_dir, "Alert.wav")

print("="*70)
print("DROWSINESS DETECTION - ACCURATE TEST VERSION")
print("="*70)
print(f"\nAlarm file: {alarm_file}")
print(f"File exists: {os.path.exists(alarm_file)}")
print("\nInstructions:")
print("  1. Close both eyes completely for ~8 frames (~0.27 seconds)")
print("  2. You should see 'DROWSINESS ALERT!' and hear the alarm")
print("  3. Open your eyes to reset")
print("  4. Press 'q' to quit\n")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

EYES_CLOSED_COUNT = 0
alarm_status = False
last_alarm_time = 0
frame_count = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Camera error")
        time.sleep(0.1)
        continue
    
    frame_count += 1
    frame = cv2.resize(frame, (450, 350))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    
    faces = detector.detectMultiScale(gray, 1.05, 4, 0, (30, 30))
    
    face_found = False
    
    for (x, y, w, h) in faces:
        face_found = True
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.05, 3, 0, (15, 15))
        
        eyes_closed_this_frame = 0
        
        if len(eyes) >= 2:
            eye_list = sorted(eyes, key=lambda e: e[0])[:2]
            
            for (ex, ey, ew, eh) in eye_list:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                
                eye_region = roi_gray[ey:ey+eh, ex:ex+ew]
                if is_eye_closed(eye_region):
                    eyes_closed_this_frame += 1
            
            if eyes_closed_this_frame >= 2:
                EYES_CLOSED_COUNT += 1
            else:
                EYES_CLOSED_COUNT = 0
        else:
            EYES_CLOSED_COUNT += 1
        
        # Trigger alarm
        if EYES_CLOSED_COUNT >= EYE_AR_CONSEC_FRAMES:
            current_time = time.time()
            if current_time - last_alarm_time > 2:
                last_alarm_time = current_time
                alarm_status = True
                print(f"\n{'*'*70}")
                print(f"[FRAME {frame_count}] DROWSINESS ALERT! Eyes closed for {EYES_CLOSED_COUNT} frames")
                print(f"{'*'*70}")
                t = Thread(target=sound_alarm, args=(alarm_file,), daemon=True)
                t.start()
            
            cv2.putText(frame, "DROWSINESS ALERT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.putText(frame, f"Closed: {EYES_CLOSED_COUNT}/{EYE_AR_CONSEC_FRAMES}", (270, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    if not face_found:
        EYES_CLOSED_COUNT = 0
        alarm_status = False
        cv2.putText(frame, "NO FACE DETECTED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    cv2.imshow("Drowsiness Detection", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("\nExiting...")
        break

cap.release()
cv2.destroyAllWindows()
