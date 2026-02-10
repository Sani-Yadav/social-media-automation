import os
import sys
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instagrapi import Client
from myapp.config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

def test_login():
    print("\n🔍 Testing Instagram Login...")
    
    # Always start with a fresh session for testing to avoid "Unknown" errors
    if os.path.exists("session.json"):
        print("🗑️ Removing old session.json for fresh login...")
        os.remove("session.json")
    
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        print("❌ Error: Username or Password missing in config.py")
        return

    print(f"👤 User: {INSTAGRAM_USERNAME}")
    
    cl = Client()
    try:
        # Try to login
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        print("✅ Login Successful!")
        
        # Get user info to confirm
        info = cl.user_info(cl.user_id)
        print(f"✅ Authenticated as: {info.username} ({info.full_name})")
        
    except Exception as e:
        print(f"❌ Login Failed: {str(e)}")
        if "challenge_required" in str(e).lower():
            print("\n🚨 CHALLENGE REQUIRED DETECTED! 🚨")
            print("1. Open Instagram App on your phone.")
            print("2. Go to Settings > Security > Login Activity.")
            print("3. You should see a login attempt from a new device/location.")
            print("4. Tap 'This was me'.")
            print("5. Run this script again.")
        else:
            print("💡 Tip: Agar 'ChallengeRequired' error hai, to Instagram app open karke 'This was me' click karein.")
        
        # Delete session file if exists
        if os.path.exists("session.json"):
            print("🗑️ Deleting old session.json and retrying...")
            os.remove("session.json")

if __name__ == "__main__":
    test_login()