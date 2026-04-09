"""
Test the updated drowsiness_yawn.py detection logic
Simulates continuous eye closure and excessive blinking
"""

import time
import os

# Simulate the detection logic from updated drowsiness_yawn.py

def test_continuous_closure_detection():
    """Test that continuous closure triggers at 150 frames"""
    print("=" * 80)
    print("TEST 1: Continuous Eye Closure Detection (5 seconds)")
    print("=" * 80)
    
    # Simulation variables (from drowsiness_yawn.py)
    EYES_CLOSED_COUNT = 0
    EYE_AR_CONSEC_FRAMES = 150
    alarm_triggered_continuous = False
    frame_count = 0
    
    # Simulate 200 frames with eyes closed
    for frame in range(200):
        frame_count = frame
        eyes_closed_now = True
        
        if eyes_closed_now:
            EYES_CLOSED_COUNT += 1
        else:
            EYES_CLOSED_COUNT = 0
            alarm_triggered_continuous = False
        
        # Check for continuous eye closure alert (5 seconds)
        if EYES_CLOSED_COUNT >= EYE_AR_CONSEC_FRAMES and not alarm_triggered_continuous:
            alarm_triggered_continuous = True
            print(f"\n✓ FRAME {frame_count}: DROWSINESS ALERT TRIGGERED!")
            print(f"  Continuous eye closure detected after {EYES_CLOSED_COUNT/30:.1f} seconds")
            print(f"  Threshold: {EYE_AR_CONSEC_FRAMES/30:.1f} seconds\n")
            return True
        
        if frame % 30 == 0:
            print(f"Frame {frame_count}: Eyes closed for {EYES_CLOSED_COUNT/30:.2f}s", end="\r")
    
    print("\n✗ FAILED: Alert not triggered\n")
    return False


def test_excessive_blinking_detection():
    """Test that excessive blinking triggers at >25 blinks/min"""
    print("=" * 80)
    print("TEST 2: Excessive Blinking Detection (>25 blinks/minute)")
    print("=" * 80)
    
    # Simulation variables (from drowsiness_yawn.py)
    eyes_were_open = True
    blink_count = 0
    blink_times = []
    BLINK_WINDOW = 60
    BLINK_THRESHOLD = 25
    alarm_triggered_blink = False
    frame_count = 0
    
    # Simulate blink pattern: rapid open/close cycles
    # Create 10 blinks in 60 frames = 300 blinks per minute (extreme drowsiness)
    blink_sequence = [
        False,  # closed
        True,   # open (blink 1)
        False,  # closed
        True,   # open (blink 2)
        False,  # closed
        True,   # open (blink 3)
        False,  # closed
        True,   # open (blink 4)
        False,  # closed
        True,   # open (blink 5)
        False,  # closed
        True,   # open (blink 6)
        False,  # closed
        True,   # open (blink 7)
        False,  # closed
        True,   # open (blink 8)
        False,  # closed
        True,   # open (blink 9)
        False,  # closed
        True,   # open (blink 10)
    ]
    
    # Repeat pattern and extend to 100 frames
    full_sequence = (blink_sequence * 6)[:100]
    
    for frame_idx in range(len(full_sequence)):
        frame_count = frame_idx
        eyes_closed_now = not full_sequence[frame_idx]
        
        # DETECT BLINKS (from drowsiness_yawn.py)
        if not eyes_closed_now and eyes_were_open == False:
            blink_count += 1
            blink_times.append(frame_count)
            print(f"Frame {frame_count}: Blink #{blink_count}")
        
        eyes_were_open = not eyes_closed_now
        
        # Check for frequent blinking alert
        recent_blinks = len([t for t in blink_times if frame_count - t < BLINK_WINDOW])
        blink_rate = (recent_blinks / BLINK_WINDOW) * 1800  # Convert to per minute
        
        if blink_rate > BLINK_THRESHOLD and recent_blinks >= 3 and not alarm_triggered_blink:
            alarm_triggered_blink = True
            print(f"\n✓ FRAME {frame_count}: DROWSINESS ALERT TRIGGERED!")
            print(f"  Excessive blinking detected: {blink_rate:.1f} blinks/minute")
            print(f"  Recent blinks: {recent_blinks} in {BLINK_WINDOW} frames")
            print(f"  Threshold: {BLINK_THRESHOLD} blinks/minute\n")
            return True
        
        if frame_idx % 10 == 0 and recent_blinks > 0:
            print(f"Frame {frame_count}: {recent_blinks} blinks, Rate: {blink_rate:.1f}/min", end="\r")
    
    print("\n✗ FAILED: Alert not triggered\n")
    return False


def test_alert_cooldown():
    """Test that alerts have proper cooldown"""
    print("=" * 80)
    print("TEST 3: Alert Cooldown (1 second minimum between alerts)")
    print("=" * 80)
    
    EYES_CLOSED_COUNT = 0
    EYE_AR_CONSEC_FRAMES = 150
    alarm_triggered_continuous = False
    last_alarm_time = 0
    frame_count = 0
    
    alert_count = 0
    
    # Simulate 500 frames with continuous closure
    for frame in range(500):
        frame_count = frame
        eyes_closed_now = True
        
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
                alert_count += 1
                print(f"Frame {frame_count}: Alert #{alert_count} (after {EYES_CLOSED_COUNT/30:.1f}s closure)")
        
        if frame_count > 400:
            break
    
    print(f"\n✓ Alerts triggered: {alert_count}")
    print(f"  Expected behavior: Alert every 1+ second while eyes closed\n")
    return alert_count >= 2  # Should have at least 2 alerts in 400 frames


if __name__ == "__main__":
    print("\nTesting updated drowsiness_yawn.py detection logic\n")
    
    results = []
    
    # Test 1: Continuous closure
    results.append(("Continuous Eye Closure (5s)", test_continuous_closure_detection()))
    
    # Test 2: Excessive blinking
    results.append(("Excessive Blinking (>25/min)", test_excessive_blinking_detection()))
    
    # Test 3: Alert cooldown
    results.append(("Alert Cooldown (1s)", test_alert_cooldown()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed\n")
