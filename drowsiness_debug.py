"""
Drowsiness Detection - Static Image Test
Simulates eye closure detection for testing without webcam
"""

import cv2
import numpy as np
import os
from threading import Thread
import playsound
import time

script_dir = os.path.dirname(os.path.abspath(__file__))

def sound_alarm(path):
    try:
        if os.path.exists(path):
            playsound.playsound(path)
            print("ALARM SOUND PLAYED!")
        else:
            print(f"Alert file not found: {path}")
    except Exception as e:
        print(f"Error playing sound: {e}")

def is_eye_closed(eye_region):
    """Detect if eye is closed based on contours and area"""
    if eye_region is None or eye_region.size == 0:
        return True
    
    # Apply threshold
    _, thresh = cv2.threshold(eye_region, 70, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return True
    
    max_area = max(cv2.contourArea(c) for c in contours) if contours else 0
    print(f"  Eye area: {max_area:.0f} (closed if < 100)")
    return max_area < 100

# Load classifiers
detector = cv2.CascadeClassifier(os.path.join(script_dir, "haarcascade_frontalface_default.xml"))
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

EYE_AR_CONSEC_FRAMES = 5  # Lower threshold for testing
alarm_file = os.path.join(script_dir, "Alert.wav")

print("=== DROWSINESS DETECTION - WEBCAM TEST ===")
print(f"Alarm file: {alarm_file}")
print("Close eyes for ~5 frames to trigger alarm")
print("Quit with 'q'\n")

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Try V4L2 backend
if not cap.isOpened():
    cap = cv2.VideoCapture(0)  # Fallback

cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

time.sleep(1)

EYES_CLOSED_COUNT = 0
alarm_status = False
frame_count = 0

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
    
    for (x, y, w, h) in faces:
        face_found = True
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.05, 3, 0, (15, 15))
        
        eyes_closed_this_frame = 0
        
        if len(eyes) >= 2:
            print(f"[Frame {frame_count}] Eyes detected: {len(eyes)}")
            eye_list = sorted(eyes, key=lambda e: e[0])[:2]
            
            for i, (ex, ey, ew, eh) in enumerate(eye_list):
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                
                eye_region = roi_gray[ey:ey+eh, ex:ex+ew]
                closed = is_eye_closed(eye_region)
                
                print(f"  Eye {i+1}: {'CLOSED' if closed else 'OPEN'}")
                if closed:
                    eyes_closed_this_frame += 1
            
            if eyes_closed_this_frame >= 2:
                EYES_CLOSED_COUNT += 1
                print(f"  -> Both eyes CLOSED! Count: {EYES_CLOSED_COUNT}/{EYE_AR_CONSEC_FRAMES}\n")
            else:
                EYES_CLOSED_COUNT = 0
                print(f"  -> Eyes OPEN. Count reset.\n")
        else:
            print(f"[Frame {frame_count}] Eyes NOT detected!")
            EYES_CLOSED_COUNT += 1
        
        # Trigger alarm
        if EYES_CLOSED_COUNT >= EYE_AR_CONSEC_FRAMES:
            if not alarm_status:
                alarm_status = True
                print("***" * 20)
                print("DROWSINESS ALERT TRIGGERED!")
                print("***" * 20)
                if os.path.exists(alarm_file):
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
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
