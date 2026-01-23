#!/usr/bin/env python
"""Quick test script to verify imports work"""

import sys
import traceback

print("Python version:", sys.version)
print("Current directory:", sys.path[0] if sys.path else "unknown")

try:
    print("\n1. Testing bot package import...")
    import bot
    print("   ✓ bot package imported successfully")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n2. Testing bot.app import...")
    from bot.app import app
    print("   ✓ bot.app imported successfully")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n3. Testing FastAPI app creation...")
    print(f"   App title: {app.title}")
    print("   ✓ FastAPI app instance is valid")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All imports successful! App is ready to run.")
print("\nRun with: uvicorn bot.app:app --host 0.0.0.0 --port 8000")
