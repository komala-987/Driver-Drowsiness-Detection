import playsound
import os

script_dir = r"c:\Users\komal\Downloads\Real-Time-Drowsiness-Detection-System-main (1)\Real-Time-Drowsiness-Detection-System-main"
alarm_file = os.path.join(script_dir, "Alert.wav")

print(f"Testing alarm file: {alarm_file}")
print(f"File exists: {os.path.exists(alarm_file)}")
print(f"File size: {os.path.getsize(alarm_file) if os.path.exists(alarm_file) else 'N/A'} bytes")

if os.path.exists(alarm_file):
    print("\nPlaying sound... (you should hear a beep)")
    try:
        playsound.playsound(alarm_file)
        print("Sound played successfully!")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Alert.wav not found!")
