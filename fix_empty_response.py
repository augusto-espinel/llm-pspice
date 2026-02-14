"""
Fix for Ollama Cloud Empty Response Issue
Tests API and provides diagnostic information
"""

import requests
import json

# Your API key from the logs
API_KEY = "eea0dd8d82c144debbc9bbcfd367b212"  # truncated for security
BASE_URL = "https://api.ollama.com"

print("=" * 70)
print("OLLAMA CLOUD DIAGNOSTIC - Empty Response Issue")
print("=" * 70)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Test 1: Check available models
print("\n[Test 1] Checking available models in your tier...")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/api/tags", headers=headers, timeout=30)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        models = response.json()
        available_models = models.get("models", [])

        print(f"[OK] Found {len(available_models)} available models:")
        for m in available_models[:20]:  # Show first 20
            print(f"   - {m.get('name', 'unknown')}")
    else:
        print(f"[FAIL] Error: {response.text[:200]}")
except Exception as e:
    print(f"[FAIL] Exception: {e}")

# Test 2: Simple prompt with minimal tokens
print("\n[Test 2] Testing with minimal prompt (simple)...")
print("-" * 70)
test_models = ["glm-4.7", "glm-5", "deepseek-v3.2", "llama3.2"]

for model in test_models:
    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Say hi"}
            ],
            "stream": False,
            "options": {
                "num_predict": 5,  # Very low token limit
                "temperature": 0.7
            }
        }

        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers=headers,
            timeout=30
        )

        result = response.json()

        if response.status_code == 200:
            content = result.get("message", {}).get("content", "")
            if content:
                print(f"[OK] {model}: Response '{content}' (length: {len(content)})")
            else:
                print(f"[WARN] {model}: Empty response (status 200 but no content)")
                # Print full response for debugging
                if result:
                    print(f"   Full response: {json.dumps(result, indent=2)[:300]}")
        else:
            print(f"[FAIL] {model}: Status {response.status_code} - {response.text[:100]}")

    except Exception as e:
        print(f"[FAIL] {model}: Exception - {str(e)[:100]}")

# Test 3: Test quota/status endpoint
print("\n[Test 3] Checking account status/quota...")
print("-" * 70)
try:
    # Try models endpoint which often shows quota info
    response = requests.get("https://api.ollama.com/v1/models", headers=headers, timeout=30)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        # Check if quota info in headers or response
        rate_limit = response.headers.get('X-RateLimit-Remaining', 'N/A')
        print(f"Rate limit remaining: {rate_limit}")
    elif response.status_code == 401:
        print("[FAIL] Unauthorized - API key may be invalid")
    elif response.status_code == 429:
        print("[FAIL] Rate limited - Quota exhausted")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"[FAIL] Exception: {e}")

# Test 4: Alternative working model
print("\n[Test 4] Testing alternative models known to work...")
print("-" * 70)
alt_models = ["gemma3:12b", "ministral-3:8b", "qwen3-next:80b"]

for model in alt_models:
    try:
        payload = {
            "model": model,
            "prompt": "Hi",
            "stream": False,
            "options": {"num_predict": 10}
        }

        response = requests.post(
            f"{BASE_URL}/api/generate",
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "")
            if content:
                print(f"[OK] {model}: Works! Response: '{content}'")
                break
        else:
            print(f"[FAIL] {model}: Status {response.status_code}")

    except Exception as e:
        print(f"[FAIL] {model}: {str(e)[:80]}")

print("\n" + "=" * 70)
print("DIAGNOSIS SUMMARY")
print("=" * 70)
print("""
If you see empty responses for all models:
→ You likely need a higher Ollama Cloud tier
→ Visit: https://ollama.ai/cloud to upgrade

If some models work but others don't:
→ Those models aren't in your current tier
→ Use the working ones listed above

If all tests fail with unauthorized:
→ Regenerate API key: ollama cloud key

Next steps:
1. Upgrade Ollama Cloud subscription at https://ollama.ai/cloud
2. Or use local models (uncheck "Use Ollama Cloud" in sidebar)
3. Try smaller models like gemma3:12b or ministral-3:8b
""")