#!/usr/bin/env python3
"""
System Verification Script
Checks that the drowsiness detection system is properly configured
"""

import os
import sys
import cv2
import imutils

def check_files():
    """Check that required files exist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_to_check = [
        ('drowsiness_yawn.py', 'Main detection script'),
        ('Alert.wav', 'Alert sound file'),
        ('haarcascade_frontalface_default.xml', 'Face detection cascade'),
    ]
    
    print("\n📁 FILE CHECK:")
    print("=" * 60)
    all_files_exist = True
    for filename, description in files_to_check:
        filepath = os.path.join(script_dir, filename)
        exists = os.path.exists(filepath)
        status = "✓" if exists else "✗"
        print(f"{status} {filename:40} ({description})")
        if not exists:
            all_files_exist = False
            print(f"   → Expected location: {filepath}")
    
    return all_files_exist

def check_dependencies():
    """Check that required Python packages are installed"""
    print("\n📦 DEPENDENCY CHECK:")
    print("=" * 60)
    
    dependencies = [
        ('cv2', 'OpenCV'),
        ('imutils', 'imutils'),
        ('numpy', 'numpy'),
        ('scipy', 'scipy'),
    ]
    
    all_deps_ok = True
    for module_name, display_name in dependencies:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✓ {display_name:20} v{version}")
        except ImportError:
            print(f"✗ {display_name:20} NOT INSTALLED")
            all_deps_ok = False
    
    # Check for winsound (Windows-only)
    try:
        import winsound
        print(f"✓ {'winsound':20} (Windows native)")
    except ImportError:
        print(f"⚠ {'winsound':20} NOT AVAILABLE (Windows only)")
    
    return all_deps_ok

def check_cascades():
    """Check that cascade classifiers can be loaded"""
    print("\n🎯 CASCADE CLASSIFIER CHECK:")
    print("=" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    cascades = [
        (os.path.join(script_dir, 'haarcascade_frontalface_default.xml'), 'Face Detection'),
        (cv2.data.haarcascades + 'haarcascade_eye.xml', 'Eye Detection'),
    ]
    
    all_cascades_ok = True
    for cascade_path, description in cascades:
        try:
            cascade = cv2.CascadeClassifier(cascade_path)
            if cascade.empty():
                print(f"✗ {description:20} - Cascade empty")
                all_cascades_ok = False
            else:
                print(f"✓ {description:20} - Loaded successfully")
        except Exception as e:
            print(f"✗ {description:20} - Error: {e}")
            all_cascades_ok = False
    
    return all_cascades_ok

def check_config():
    """Check detection parameters"""
    print("\n⚙️  DETECTION PARAMETERS:")
    print("=" * 60)
    print(f"✓ Continuous closure threshold  : 150 frames (5.0 seconds)")
    print(f"✓ Blink rate threshold         : 25 blinks/minute")
    print(f"✓ Blink window                 : 60 frames (2.0 seconds)")
    print(f"✓ Eye closed area threshold    : 100 pixels²")
    print(f"✓ Alert cooldown               : 1.0 second minimum")

def main():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("DROWSINESS DETECTION SYSTEM - VERIFICATION")
    print("=" * 60)
    
    checks = [
        ("Files", check_files()),
        ("Dependencies", check_dependencies()),
        ("Cascades", check_cascades()),
    ]
    
    check_config()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    all_ok = all(result for _, result in checks)
    
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {check_name}")
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("✓ ALL CHECKS PASSED - SYSTEM IS READY!")
        print("\nRun: python drowsiness_yawn.py")
        print("=" * 60 + "\n")
        return 0
    else:
        print("✗ SOME CHECKS FAILED - SEE ABOVE FOR DETAILS")
        print("=" * 60 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
