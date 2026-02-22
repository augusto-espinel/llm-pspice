"""
Debug actual API response to see what Ollama Cloud returns
"""

import requests
import json

API_KEY = "eea0dd8d82c144debbc9bbcfd367b212"
BASE_URL = "https://api.ollama.com"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Test exactly what the app is sending
print("Testing exact request format from app.py...")
print("=" * 70)

payload = {
    "model": "glm-4.7",
    "messages": [
        {"role": "system", "content": "You are a circuit design assistant."},
        {"role": "user", "content": "Say hello"}
    ],
    "stream": False,
    "options": {
        "num_predict": 1000,
        "temperature": 0.7
    }
}

url = f"{BASE_URL}/api/chat"

print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\nSending request...")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=120)

    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body (raw):")
    print(repr(response.text))
    print(f"\nResponse Body (decoded if possible):")
    print(response.text)

    # Try to parse JSON if possible
    try:
        result = response.json()
        print(f"\nParsed JSON result:")
        print(json.dumps(result, indent=2))
    except:
        print("\nCannot parse as JSON - response body is empty or invalid")

except Exception as e:
    print(f"Exception: {e}")

# Try alternative: Minimal payload
print("\n" + "=" * 70)
print("Testing with MINIMAL payload...")
print("=" * 70)

payload_minimal = {
    "model": "glm-4.7",
    "messages": [
        {"role": "user", "content": "Hi"}
    ]
}

print(f"Minimal Payload: {json.dumps(payload_minimal)}")

try:
    response = requests.post(url, json=payload_minimal, headers=headers, timeout=60)

    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body (raw): {repr(response.text)}")

    if response.text:
        result = response.json()
        content = result.get("message", {}).get("content", "")
        print(f"Content: '{content}'")
        print(f"Length: {len(content)}")

except Exception as e:
    print(f"Exception: {e}")

# Try the /api/generate endpoint
print("\n" + "=" * 70)
print("Testing /api/generate endpoint...")
print("=" * 70)

url_generate = f"{BASE_URL}/api/generate"
payload_generate = {
    "model": "glm-4.7",
    "prompt": "Say hello",
    "stream": False
}

print(f"URL: {url_generate}")
print(f"Payload: {json.dumps(payload_generate)}")

try:
    response = requests.post(url_generate, json=payload_generate, headers=headers, timeout=60)

    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body (raw): {repr(response.text)}")

    if response.text:
        result = response.json()
        content = result.get("response", "")
        print(f"Content: '{content}'")
        print(f"Length: {len(content)}")

except Exception as e:
    print(f"Exception: {e}")