# Hugging Face Spaces entry point
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname("app_main.py"))

# Import and run main app
from app_main import main

if __name__ == "__main__":
    main()