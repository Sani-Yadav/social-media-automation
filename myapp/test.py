import os
import sys
import requests

# Add project root to path to ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from myapp.config import GROQ_API_KEY
except ImportError:
    print("❌ Config import failed. Make sure you run this from the project root.")
    GROQ_API_KEY = None

def test_groq_connection():
    print("\n🔍 Testing Groq API Connection...")
    
    if not GROQ_API_KEY:
        print("❌ Error: GROQ_API_KEY is missing in config.py or .env file!")
        return

    print(f"🔑 API Key loaded: {GROQ_API_KEY[:5]}...{GROQ_API_KEY[-4:]}")
    
    # Try a simple request
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": "Say 'Hello' in Hindi"}],
                "max_tokens": 10
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API Success! Response:", response.json()['choices'][0]['message']['content'])
        else:
            print(f"❌ API Failed with Status Code: {response.status_code}")
            print(f"⚠️ Error Message: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_groq_connection()
