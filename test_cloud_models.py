"""
Test script to verify Ollama Cloud API and identify working models
"""

import requests
import json
import time
import sys
import io

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# API key from the user
API_KEY = "eea0dd8d82c144debbc9bbcfd367b212.ULktML3z6tsOissLTRKGYZT9"

# Test different base URLs
BASE_URLS = [
    "https://api.ollama.com",
    "https://api.ollama.ai"
]

print("="*60)
print("OLLAMA CLOUD API MODEL TESTER")
print("="*60)
print(f"API Key: {API_KEY[:30]}...")
print()

def test_tags_endpoint(base_url):
    """Test the /api/tags endpoint to list available models"""
    url = f"{base_url}/api/tags"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print(f"Testing: {url}")
        response = requests.get(url, headers=headers, timeout=30)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            models = result.get("models", [])
            print(f"✅ Found {len(models)} models")
            return models
        else:
            print(f"❌ Error: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_model_request(base_url, model_name):
    """Test a specific model with a simple request"""
    url = f"{base_url}/api/chat"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say just 'Hello'"}
        ],
        "stream": False,
        "options": {
            "num_predict": 5,
            "temperature": 0.5
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            print(f"  ✅ {model_name}: {content[:50]}")
            return True
        else:
            print(f"  ❌ {model_name}: Status {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  ❌ {model_name}: {str(e)[:100]}")
        return False

# Step 1: Find working base URL and get model list
print("STEP 1: Testing base URLs and fetching model list")
print("-"*60)

working_models = []
working_base_url = None

for base_url in BASE_URLS:
    models = test_tags_endpoint(base_url)
    if models:
        working_base_url = base_url
        working_models = models
        print()
        print(f"✅ Working base URL: {base_url}")
        break
    print()

if not working_base_url:
    print("\n❌ No working base URL found!")
    print("Please check your API key or try again later.")
    exit(1)

# Step 2: Display all available models
print()
print("STEP 2: Available models")
print("-"*60)
model_names = [m["name"] for m in working_models]
for i, name in enumerate(model_names[:20], 1):  # Show first 20
    print(f"{i:2}. {name}")

if len(model_names) > 20:
    print(f"    ... and {len(model_names) - 20} more")

# Step 3: Test a few representative models
print()
print("STEP 3: Testing individual models")
print("-"*60)

# Models mentioned in documentation to test
models_to_test = [
    "cogito-2.1:671b",
    "qwen3-coder:480b", 
    "deepseek-v3.1:671b",
    "kimi-k2:1t",
    "glm-4.7",
    "glm-5"
]

working = []
failing = []

for model in models_to_test:
    if model in model_names:
        is_working = test_model_request(working_base_url, model)
        if is_working:
            working.append(model)
        else:
            failing.append(model)
        time.sleep(1)  # Rate limiting
    else:
        print(f"  ⏭️  {model}: Not available in your tier")

# Step 4: Summary
print()
print("="*60)
print("SUMMARY")
print("="*60)
print(f"Working base URL: {working_base_url}")
print(f"Total available models: {len(model_names)}")
print()

if working:
    print(f"✅ Working models ({len(working)}):")
    for m in working:
        print(f"   • {m}")

if failing:
    print()
    print(f"❌ Failing models ({len(failing)}):")
    for m in failing:
        print(f"   • {m}")

print()
print("Recommendation: Use the working models listed above in the app.")