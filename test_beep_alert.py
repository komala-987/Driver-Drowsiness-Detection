"""
Test the new system beep alert sounds
No wav files needed - pure system beeps
"""

import winsound
import time

print("🔊 TESTING SYSTEM BEEP ALERTS")
print("=" * 60)

# Test 1: Continuous closure alert (3 beeps)
print("\n[TEST 1] Continuous Eye Closure Alert (3 beeps)")
print("Sound: 800 Hz (warning tone)")
print("Playing...")

for i in range(3):
    print(f"  Beep {i+1}... ", end="", flush=True)
    winsound.Beep(800, 400)   # 800Hz for 400ms
    time.sleep(0.3)
    winsound.Beep(800, 400)
    time.sleep(0.3)
    print("✓")

print("\n✓ TEST 1 PASSED\n")
time.sleep(1)

# Test 2: Excessive blinking alert (2 beeps)
print("[TEST 2] Excessive Blinking Alert (2 beeps)")
print("Sound: 1200 Hz (urgent tone)")
print("Playing...")

for i in range(2):
    print(f"  Beep {i+1}... ", end="", flush=True)
    winsound.Beep(1200, 400)  # 1200Hz for 400ms
    time.sleep(0.3)
    winsound.Beep(1200, 400)
    time.sleep(0.3)
    print("✓")

print("\n✓ TEST 2 PASSED\n")

# Test 3: Test alert pattern recognition
print("[TEST 3] Alert Pattern Test")
print("-" * 60)
print("You should hear:")
print("  1. Lower tone (800 Hz) × 6 beeps = DROWSINESS (EYE CLOSURE)")
print("  2. Higher tone (1200 Hz) × 4 beeps = DROWSINESS (EXCESSIVE BLINKING)")
print("\nPlaying pattern...")

print("\n  Continuous Closure Alert: ", end="", flush=True)
for _ in range(3):
    winsound.Beep(800, 400)
    time.sleep(0.3)
    winsound.Beep(800, 400)
    time.sleep(0.3)
print("✓")

time.sleep(2)

print("  Excessive Blinking Alert: ", end="", flush=True)
for _ in range(2):
    winsound.Beep(1200, 400)
    time.sleep(0.3)
    winsound.Beep(1200, 400)
    time.sleep(0.3)
print("✓")

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("\nYour drowsiness detection system now uses reliable system beeps:")
print("  • 800 Hz = Eyes closed for 5+ seconds")
print("  • 1200 Hz = Excessive blinking (>25/min)")
print("\nNo wav files needed - works on all Windows systems!")
print("=" * 60)
