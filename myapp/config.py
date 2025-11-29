# myapp/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")   # only works locally, harmless on Render

# Everything will come from Render Environment Variables
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Groq is required (since you use it)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing! Add it in Render → Environment Variables")

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

# Other platforms (add later if needed)
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
YOUTUBE_CLIENT_ID      = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
FB_PAGE_ID            = os.getenv("FB_PAGE_ID", "")
FB_ACCESS_TOKEN       = os.getenv("FB_ACCESS_TOKEN", "")
X_CONSUMER_KEY        = os.getenv("X_CONSUMER_KEY", "")
X_CONSUMER_SECRET     = os.getenv("X_CONSUMER_SECRET", "")
X_ACCESS_TOKEN        = os.getenv("X_ACCESS_TOKEN", "")
X_ACCESS_SECRET       = os.getenv("X_ACCESS_SECRET", "")