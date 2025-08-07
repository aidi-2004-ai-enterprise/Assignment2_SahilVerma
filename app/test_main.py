#!/usr/bin/env python3
"""Test the main.py load_model_and_metadata function directly"""

import sys
sys.path.insert(0, '.')

from main import load_model_and_metadata

print("Testing load_model_and_metadata function...")
try:
    load_model_and_metadata()
    print("✅ Success!")
except Exception as e:
    print(f"❌ Error: {e}")