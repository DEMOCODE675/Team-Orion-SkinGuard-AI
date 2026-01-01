#!/usr/bin/env python
"""Test backend startup."""
import sys
import os

# Change to backend dir
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("Testing backend imports...")
print("=" * 60)

try:
    print("1. Loading .env...")
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"   ✓ GEMINI_API_KEY: {'SET' if api_key else 'NOT SET'}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

try:
    print("2. Importing FastAPI...")
    from fastapi import FastAPI
    print("   ✓ FastAPI OK")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

try:
    print("3. Importing TensorFlow...")
    import tensorflow as tf
    print("   ✓ TensorFlow OK")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

try:
    print("4. Importing Google Generative AI...")
    import google.generativeai as genai
    print("   ✓ Google Generative AI OK")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

try:
    print("5. Loading app module...")
    import app
    print("   ✓ App module imported successfully")
except Exception as e:
    print(f"   ✗ Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("All imports successful! Starting Uvicorn...")
print("=" * 60 + "\n")

import uvicorn
uvicorn.run(app.app, host="127.0.0.1", port=8000, reload=False)
