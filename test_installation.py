"""
Test script to verify the Jetson Assistant installation.
"""

import sys
import logging
from utils.config_manager import ConfigManager
from utils.logger import setup_logger

def test_config_loading():
    """Test if the configuration loads correctly."""
    print("Testing configuration loading...")
    try:
        config = ConfigManager("config.yml")
        print("[OK] Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to load configuration: {e}")
        return False

def test_logging():
    """Test if logging is working."""
    print("\nTesting logging...")
    try:
        setup_logger(level="DEBUG", log_file="test.log")
        logger = logging.getLogger(__name__)
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        print("[OK] Logging test completed. Check test.log for output")
        return True
    except Exception as e:
        print(f"[ERROR] Logging test failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported."""
    print("\nTesting imports...")
    modules = [
        "PyQt5.QtWidgets",
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "yaml",
        "numpy",
        "pyaudio",
        "speech_recognition",
        "gtts",
        "pytz",
        "python_dateutil",
        "core.engine",
        "core.skills.time_date",
        "core.skills.base_skill",
        "ui.main_window",
        "utils.config_manager",
        "utils.event_bus",
        "utils.logger"
    ]
    
    success = True
    for module in modules:
        try:
            __import__(module)
            print(f"[OK] Imported {module}")
        except ImportError as e:
            print(f"[ERROR] Failed to import {module}: {e}")
            success = False
    
    return success

def main():
    """Run all tests."""
    print("=" * 50)
    print("Jetson Assistant Installation Test")
    print("=" * 50)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Logging", test_logging),
        ("Module Imports", test_imports)
    ]
    
    results = []
    for name, test in tests:
        print(f"\n{' ' + name + ' ':-^50}")
        result = test()
        results.append((name, result))
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("-" * 50)
    
    all_passed = True
    for name, result in results:
        status = "[PASSED]" if result else "[FAILED]"
        print(f"{name:.<40} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] All tests passed! Your installation appears to be working correctly.")
    else:
        print("[ERROR] Some tests failed. Please check the error messages above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
