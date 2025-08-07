#!/usr/bin/env python3
"""Simple wrapper to run the app with explicit imports"""

import uvicorn
import sys
import os

# Ensure we're using the current directory's modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)