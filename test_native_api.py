"""
Test with native Ollama library format
"""

import requests
import json

api_key = "eea0dd8d82c144debbc9bbcfd367b212.ULktML3z6tsOissLTRKGYZT9"

print("=" * 60)
print("Testing Native Ollama Cloud API format")
print("=" * 60)

# Test direct HTTP request to Ollama Cloud
print("\nTest 1: Direct HTTP request to /api/chat")
url = "https://api.ollama.com/api/chat"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "glm-4.7",
    "messages": [
        {"role": "user", "content": "Say 'hello' in one word"}
    ]
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test with /v1/chat/completions format
print("\n" + "=" * 60)
print("Test 2: /v1/chat/completions format")
url = "https://api.ollama.com/v1/chat/completions"

payload = {
    "model": "glm-4.7",
    "messages": [
        {"role": "user", "content": "Say 'hello' in one word"}
    ]
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test with /api/generate format (for completion, not chat)
print("\n" + "=" * 60)
print("Test 3: /api/generate format")
url = "https://api.ollama.com/api/generate"

payload = {
    "model": "glm-4.7",
    "prompt": "Say 'hello' in one word",
    "stream": False
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("If all tests fail with unauthorized, the API key might:")
print("1. Need to be regenerated (run: ollama cloud key)")
print("2. Be for a different service/endpoint")
print("3. Require additional headers or authentication")
print("\nCheck: https://github.com/ollama/ollama for documentation")