#python drowsiness_yawn.py --Advanced Detection Mode
# Detects:
# 1. Continuous eye closure for 5 seconds
# 2. Excessive blinking (>25 blinks per minute)

from scipy.spatial import distance as dist
from imutils.video import VideoStream
from threading import Thread
import numpy as np
import argparse
import imutils
import time
import cv2
import os
import sys

# Try both playsound and winsound for alarm
try:
    import winsound
    USE_WINSOUND = True
except ImportError:
    USE_WINSOUND = False
    try:
        import playsound
    except ImportError:
        print("Warning: Neither winsound nor playsound available")

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))


def sound_alarm(path, beep_count=3):
    """Play alarm using system beeps - guaranteed to work on all Windows systems"""
    try:
        if beep_count == 3:
            # Continuous eye closure alert - lower frequency (warning)
            print(f"[ALARM] 🔴 CONTINUOUS CLOSURE ALERT - Playing {beep_count} beeps...")
            for i in range(beep_count):
                winsound.Beep(800, 400)   # 800Hz for 400ms
                time.sleep(0.3)
                winsound.Beep(800, 400)
                time.sleep(0.3)
        elif beep_count == 2:
            # Excessive blinking alert - higher frequency (urgent)
            print(f"[ALARM] 🟡 EXCESSIVE BLINKING ALERT - Playing {beep_count} beeps...")
            for i in range(beep_count):
                winsound.Beep(1200, 400)  # 1200Hz for 400ms
                time.sleep(0.3)
                winsound.Beep(1200, 400)
                time.sleep(0.3)
        
        print("[ALARM] ✓ Alert sound played!")
    except Exception as e:
        print(f"Error playing sound: {e}")
        # Fallback: at least beep something
        try:
            for _ in range(beep_count * 2):
                winsound.Beep(1000, 200)
                time.sleep(0.2)
        except:
            print("[ALARM] Could not play sound")

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


ap = argparse.ArgumentParser()
ap.add_argument("-w", "--webcam", type=int, default=0,
                help="index of webcam on system")
ap.add_argument("-a", "--alarm", type=str, default=os.path.join(script_dir, "Alert.wav"), help="path alarm .WAV file")
ap.add_argument("-p", "--predictor", type=str, default=os.path.join(script_dir, "shape_predictor_68_face_landmarks.dat"), help="path to dlib face landmarks predictor")
args = vars(ap.parse_args())

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 150  # 5 seconds at 30fps for continuous closure
BLINK_THRESHOLD = 25  # Blinks per minute
BLINK_WINDOW = 60  # Frames for blink counting (~2 seconds)
YAWN_THRESH = 20
alarm_status = False
alarm_status2 = False
saying = False
COUNTER = 0
EYES_CLOSED_COUNT = 0
eyes_were_open = True
blink_count = 0
blink_times = []
last_alarm_time = 0
alarm_triggered_continuous = False
alarm_triggered_blink = False

print("-> Loading the detector...")
detector = cv2.CascadeClassifier(os.path.join(script_dir, "haarcascade_frontalface_default.xml"))
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

print("-> Starting Video Stream")
print(f"-> Alert Threshold: 5 seconds continuous closure OR >25 blinks/minute\n")

vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)

frame_count = 0

while True:
    try:
        frame = vs.read()
        frame_count += 1
        
        # Check if frame is None (camera error)
        if frame is None:
            time.sleep(0.1)
            continue
        
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = detector.detectMultiScale(gray, scaleFactor=1.05,
            minNeighbors=4, minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE)

        face_detected = False
        eyes_closed_this_frame = 0
        total_eyes_detected = 0
        
        for (x, y, w, h) in faces:
            face_detected = True
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # Eye detection
            eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.05, 
                                               minNeighbors=3, minSize=(15, 15))
            
            if len(eyes) >= 2:
                total_eyes_detected = 2
                eye_list = sorted(eyes, key=lambda e: e[0])[:2]
                for (ex, ey, ew, eh) in eye_list:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                    
                    eye_region = roi_gray[ey:ey+eh, ex:ex+ew]
                    if is_eye_closed(eye_region):
                        eyes_closed_this_frame += 1
        
        # DETECT BLINKS
        eyes_closed_now = (eyes_closed_this_frame >= 2 and total_eyes_detected == 2)
        
        if not eyes_closed_now and eyes_were_open == False:
            # Eyes just opened - this was a blink
            blink_count += 1
            blink_times.append(frame_count)
            # Keep only recent blink times
            blink_times = [t for t in blink_times if frame_count - t < BLINK_WINDOW]
        
        eyes_were_open = not eyes_closed_now
        
        # DETECT CONTINUOUS EYE CLOSURE
        if eyes_closed_now:
            EYES_CLOSED_COUNT += 1
        else:
            EYES_CLOSED_COUNT = 0
            alarm_triggered_continuous = False
        
        # Check for continuous eye closure alert (5 seconds)
        if EYES_CLOSED_COUNT >= EYE_AR_CONSEC_FRAMES and not alarm_triggered_continuous:
            alarm_triggered_continuous = True
            current_time = time.time()
            if current_time - last_alarm_time > 1:
                last_alarm_time = current_time
                print(f"\n{'*'*80}")
                print(f"[FRAME {frame_count}] DROWSINESS ALERT: Continuous eye closure! ({EYES_CLOSED_COUNT/30:.1f}s)")
                print(f"{'*'*80}\n")
                if os.path.exists(args["alarm"]):
                    t = Thread(target=sound_alarm, args=(args["alarm"], 3), daemon=True)
                    t.start()
            
            # Draw alert box
            cv2.rectangle(frame, (5, 5), (450, 100), (0, 0, 255), -1)
            cv2.putText(frame, "!!DROWSINESS ALERT!!", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
            cv2.putText(frame, f"Eyes closed: {EYES_CLOSED_COUNT/30:.1f}s", (10, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Check for frequent blinking alert
        recent_blinks = len(blink_times)
        blink_rate = (recent_blinks / BLINK_WINDOW) * 1800  # Convert to per minute
        
        if blink_rate > BLINK_THRESHOLD and recent_blinks >= 3 and not alarm_triggered_blink:
            alarm_triggered_blink = True
            current_time = time.time()
            if current_time - last_alarm_time > 1:
                last_alarm_time = current_time
                print(f"\n{'*'*80}")
                print(f"[FRAME {frame_count}] DROWSINESS ALERT: Excessive blinking! ({blink_rate:.0f} blinks/min)")
                print(f"{'*'*80}\n")
                if os.path.exists(args["alarm"]):
                    t = Thread(target=sound_alarm, args=(args["alarm"], 2), daemon=True)
                    t.start()
            
            # Draw alert box
            cv2.rectangle(frame, (5, 5), (450, 100), (0, 0, 255), -1)
            cv2.putText(frame, "!!EXCESSIVE BLINKING!!", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
            cv2.putText(frame, f"Blinks: {blink_rate:.0f}/min (>25)", (10, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        elif blink_rate <= BLINK_THRESHOLD:
            alarm_triggered_blink = False
        
        # Display status
        cv2.putText(frame, f"Closed: {EYES_CLOSED_COUNT/30:.1f}s | Blinks: {blink_rate:.0f}/min", (270, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # If no face detected, reset
        if not face_detected:
            COUNTER = 0
            EYES_CLOSED_COUNT = 0
            alarm_status = False
            alarm_triggered_continuous = False
            alarm_triggered_blink = False
            cv2.putText(frame, "NO FACE DETECTED", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        
    except Exception as e:
        print(f"Frame processing error: {e}")
        continue

cv2.destroyAllWindows()
vs.stop()
