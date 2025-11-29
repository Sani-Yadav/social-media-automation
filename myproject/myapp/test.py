import requests
from myapp.config import GROQ_API_KEY
prompt = "Python programming ke basic concepts Hindi me explain karo in 2-3 lines"

try:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",  # ✅ Updated model
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 1.0,
            "max_tokens": 150
        },
        timeout=30
    )

    data = response.json()

    choices = data.get("choices", [])
    if choices:
        content = choices[0].get("message", {}).get("content")
        if not content:
            content = choices[0].get("text")
        print("\n📝 Groq API Response Content:\n", content)
    else:
        print("⚠️ No choices returned by API!")

except Exception as e:
    print("⚠️ API call failed:", e)
