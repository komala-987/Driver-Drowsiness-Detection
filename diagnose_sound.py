"""
Diagnostic test to identify sound playback issues
"""

import os
import sys
import winsound
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
alert_file = os.path.join(script_dir, "Alert.wav")

print("🔍 SOUND DIAGNOSTIC TEST")
print("=" * 60)

# Check file exists
print(f"\n1. File Check:")
print(f"   Expected path: {alert_file}")
print(f"   File exists: {os.path.exists(alert_file)}")

if os.path.exists(alert_file):
    file_size = os.path.getsize(alert_file)
    print(f"   File size: {file_size} bytes")

# Test system beep
print(f"\n2. System Beep Test:")
try:
    print("   Playing 1 kHz beep for 500ms...")
    winsound.Beep(1000, 500)
    print("   ✓ System beep works!")
except Exception as e:
    print(f"   ✗ Error: {e}")

time.sleep(1)

# Test PlaySound with full path
print(f"\n3. PlaySound Test (Full Path):")
print(f"   File: {alert_file}")
try:
    print("   Playing sound file...")
    # Use winsound.SND_FILENAME | winsound.SND_NODEFAULT to avoid waiting
    result = winsound.PlaySound(alert_file, winsound.SND_FILENAME)
    print(f"   ✓ PlaySound returned: {result}")
except Exception as e:
    print(f"   ✗ Error: {e}")

time.sleep(2)

# Test multiple plays
print(f"\n4. Multiple Beeps Test:")
try:
    print("   Playing 3 beeps...")
    for i in range(3):
        print(f"     Beep {i+1}...", end=" ")
        winsound.Beep(1000, 300)
        time.sleep(0.2)
    print("\n   ✓ Multiple beeps work!")
except Exception as e:
    print(f"   ✗ Error: {e}")

time.sleep(1)

# Test async playback
print(f"\n5. Async PlaySound Test (Non-blocking):")
try:
    print("   Playing sound with SND_ASYNC flag...")
    winsound.PlaySound(alert_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    print("   ✓ Async playback initiated!")
    print("   (Sound should play in background)")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("Diagnostic complete!")
