# 🚀 Quick Start Guide - Drowsiness Detection System

## What Was Updated?

Your drowsiness detection system now has **TWO independent alert triggers**:

1. **5-Second Eye Closure** 
   - Detects when your eyes are continuously closed for 5 seconds
   - Alarm: 3 beeps
   
2. **Frequent Blinking** 
   - Detects when you blink more than 25 times per minute
   - Alarm: 2 beeps (distinct from closure alert)

## ✅ Current Status

- **Code**: ✓ Fully updated and syntax-checked
- **Testing**: ✓ Detection logic validated with simulations
- **Audio**: ✓ Alert system functional
- **Ready**: ✓ Ready to run with webcam

## 🎯 How to Run

### Step 1: Start the Program
Open PowerShell/Command Prompt in the project folder:
```bash
python drowsiness_yawn.py
```

### Step 2: Camera Feed
- A window will open showing your face
- System detects face and both eyes in real-time
- Displays: Closure duration (seconds) and Blink rate (per minute)

### Step 3: Triggers
**Alert triggers automatically when:**
- Your eyes stay closed for 5 seconds continuously, OR
- You blink more than 25 times in a minute

### Step 4: Exit
Press `Q` key to close the program

## 📊 What You'll See

### Normal Mode (No Alert):
```
Face: Detected ✓
Closed: 0.0s | Blinks: 12/min
```

### Alert Mode (Eye Closure):
```
DROWSINESS ALERT!
Closed: 5.0s | Blinks: 8/min
[ALARM] Playing alert (3 sound(s))...
```

### Alert Mode (Excessive Blinking):
```
EXCESSIVE BLINKING ALERT!
Closed: 0.1s | Blinks: 45/min
[ALARM] Playing alert (2 sound(s))...
```

## 🔧 Files Modified

1. **drowsiness_yawn.py** ← Main detection script (updated)
   - Added blink detection algorithm
   - Implemented dual-trigger system
   - Uses Windows native audio (winsound)

2. **IMPLEMENTATION_GUIDE.md** ← Detailed technical documentation
   - Full algorithm explanation
   - Configuration parameters
   - Troubleshooting guide

## ⚠️ Important Notes

1. **Camera Required**: Must have working webcam
2. **Lighting**: Good lighting improves face/eye detection
3. **Distance**: Sit 1-2 feet from camera
4. **Full Face**: Keep entire face visible in camera frame

## 🔊 Alert Sounds

- **3 Beeps** = Eyes closed for 5+ seconds (drowsy)
- **2 Beeps** = Blinking too much (also drowsy)
- Alert file used: `Alert.wav` (776204 bytes)

## 🎚️ Customizing Sensitivity

Edit these values in `drowsiness_yawn.py` (line ~100):

```python
EYE_AR_CONSEC_FRAMES = 150      # Default: 5 seconds
BLINK_THRESHOLD = 25            # Default: 25 blinks/min
```

### To Make More Sensitive (Alert Faster):
```python
EYE_AR_CONSEC_FRAMES = 100      # 3.3 seconds instead
BLINK_THRESHOLD = 15            # 15 blinks/min instead
```

### To Make Less Sensitive (Alert Only if Very Drowsy):
```python
EYE_AR_CONSEC_FRAMES = 200      # 6.7 seconds instead
BLINK_THRESHOLD = 35            # 35 blinks/min instead
```

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| "NO FACE DETECTED" | Check lighting, position face toward camera |
| No alert even when eyes closed | Try increasing eye region in frame, ensure both eyes visible |
| Sound not playing | Check Alert.wav exists, volume is on, winsound module available |
| Camera error | Try different webcam index: `python drowsiness_yawn.py --webcam 1` |

## 📝 Testing Checklist

- [ ] Camera feed appears in window
- [ ] Face is detected and highlighted
- [ ] Eyes are detected and highlighted
- [ ] Closure timer increases when eyes closed
- [ ] Blink count increases when you blink
- [ ] Alert triggers when eyes closed for 5+ seconds
- [ ] Alert triggers when blinking frequently
- [ ] You can hear the alarm sounds
- [ ] Pressing Q closes the program

## 🎓 Technical Summary

**Detection Method**: OpenCV Cascade Classifiers (no dlib needed)
**Blink Detection**: State-transition based (efficient)
**Alert System**: Multi-threaded (non-blocking)
**Audio**: Windows native (winsound) - reliable

---

**Questions?** Check IMPLEMENTATION_GUIDE.md for detailed technical information.
