"""Quick test with your saved API key"""

import requests
import json

# Your saved API key
API_KEY = "eea0dd8d82c144debbc9bbcfd367b212.ULktML3z6tsOissLTRKGYZT9"

print("=" * 70)
print("Testing your Ollama Cloud API key...")
print("=" * 70)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Test with simple request
payload = {
    "model": "glm-4.7",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": False,
    "options": {"num_predict": 50}
}

print("\nTesting with model: glm-4.7")

try:
    response = requests.post(
        "https://api.ollama.com/api/chat",
        json=payload,
        headers=headers,
        timeout=60
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response body: {response.text[:200]}")

    if response.status_code == 200:
        result = response.json()
        content = result.get("message", {}).get("content", "")
        print(f"\n[SUCCESS] Your key works!")
        print(f"Model response: '{content}'")
        print(f"\nYou can use this key in Streamlit app.")
    else:
        print(f"\n[FAILED] Status {response.status_code}")
        if response.status_code == 401:
            print("This means: Unauthorized")
            print("\nSolutions:")
            print("1. Check your Pro subscription is active at: https://ollama.ai/cloud")
            print("2. Generate a new API key from the website")
            print("3. Make sure you're logged into the correct account")
        else:
            print(f"Error: {response.text}")

except Exception as e:
    print(f"\n[ERROR] {e}")