#Simple drowsiness detection without video stream - for testing

from threading import Thread
import numpy as np
import cv2
import playsound
import os
import time

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

def sound_alarm(path):
    try:
        if os.path.exists(path):
            playsound.playsound(path)
        else:
            print(f"Alert file not found: {path}")
    except Exception as e:
        print(f"Error playing sound: {e}")

def is_eye_closed(eye_region):
    """Detect if eye is closed based on contours and area"""
    if eye_region is None or eye_region.size == 0:
        return True
    
    # Apply threshold to get binary image
    _, thresh = cv2.threshold(eye_region, 70, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return True
    
    # Get the largest contour area
    max_area = max(cv2.contourArea(c) for c in contours) if contours else 0
    
    # If area is very small, eye is likely closed
    return max_area < 100

# Load cascade classifiers
detector = cv2.CascadeClassifier(os.path.join(script_dir, "haarcascade_frontalface_default.xml"))
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

EYE_AR_CONSEC_FRAMES = 10  # ~0.3 seconds at 30fps
alarm_status = False
COUNTER = 0
EYES_CLOSED_COUNT = 0
alarm_file = os.path.join(script_dir, "Alert.wav")

print("-> Starting with Webcam 0")
print(f"-> Alarm file: {alarm_file}")
print("Close your eyes for ~10 frames to trigger alarm")
print("Press 'q' to quit\n")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer
time.sleep(2)

frame_count = 0
last_alarm_time = 0

try:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame, retrying...")
            time.sleep(0.1)
            continue
        
        frame_count += 1
        frame = cv2.resize(frame, (450, 350))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        faces = detector.detectMultiScale(gray, scaleFactor=1.05,
                                         minNeighbors=4, minSize=(30, 30),
                                         flags=cv2.CASCADE_SCALE_IMAGE)
        
        face_detected = False
        
        for (x, y, w, h) in faces:
            face_detected = True
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.05, 
                                               minNeighbors=3, minSize=(15, 15))
            
            eye_closed_count_frame = 0
            
            if len(eyes) >= 2:
                eye_list = sorted(eyes, key=lambda e: e[0])[:2]
                for (ex, ey, ew, eh) in eye_list:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                    
                    eye_region = roi_gray[ey:ey+eh, ex:ex+ew]
                    if is_eye_closed(eye_region):
                        eye_closed_count_frame += 1
                
                # If both eyes are closed
                if eye_closed_count_frame >= 2:
                    EYES_CLOSED_COUNT += 1
                    COUNTER = 0
                else:
                    EYES_CLOSED_COUNT = 0
                    COUNTER += 1
                    alarm_status = False
            else:
                # Eyes not detected - treat as closed
                EYES_CLOSED_COUNT += 1
                COUNTER = 0
            
            # Check if drowsiness threshold reached
            if EYES_CLOSED_COUNT >= EYE_AR_CONSEC_FRAMES:
                if not alarm_status:
                    alarm_status = True
                    current_time = time.time()
                    if current_time - last_alarm_time > 2:  # Prevent too frequent alarms
                        last_alarm_time = current_time
                        print(f"[FRAME {frame_count}] DROWSINESS ALERT! Eyes closed for {EYES_CLOSED_COUNT} frames")
                        if os.path.exists(alarm_file):
                            t = Thread(target=sound_alarm, args=(alarm_file,), daemon=True)
                            t.start()
                
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            
            # Display counters
            cv2.putText(frame, f"Eyes Closed: {EYES_CLOSED_COUNT}/{EYE_AR_CONSEC_FRAMES}", (300, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Open: {COUNTER}", (300, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # If no face detected, reset
        if not face_detected:
            COUNTER = 0
            EYES_CLOSED_COUNT = 0
            alarm_status = False
            cv2.putText(frame, "NO FACE DETECTED", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        
        cv2.imshow("Drowsiness Detection", frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord("q"):
            print("Exiting...")
            break

except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Program ended")
