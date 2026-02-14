"""Test different models to find one that works"""

import requests
import json

API_KEY = "eea0dd8d82c144debbc9bbcfd367b212.ULktML3z6tsOissLTRKGYZT9"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Test multiple models
models_to_test = [
    ("glm-4.7", "GLM 4.7"),
    ("glm-5", "GLM 5 (latest)"),
    ("deepseek-v3.2", "DeepSeek V3.2"),
    ("gemma3:12b", "Gemma 3 12B"),
    ("llama3.2", "LLaMA 3.2")
]

payload_base = {
    "messages": [{"role": "user", "content": "Say hello in exactly one word"}],
    "stream": False,
    "options": {"num_predict": 20, "temperature": 0.7}
}

print("=" * 70)
print("Testing Multiple Models")
print("=" * 70)

for model, description in models_to_test:
    print(f"\nTesting: {model} ({description})")
    print("-" * 70)

    payload = {**payload_base, "model": model}

    try:
        response = requests.post(
            "https://api.ollama.com/api/chat",
            json=payload,
            headers=headers,
            timeout=60
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            # Check different response formats
            content = result.get("message", {}).get("content", "")
            thinking = result.get("thinking", "")

            if content:
                print(f"[OK] Response: '{content}'")
            elif thinking:
                print(f"[WARN] Has 'thinking' but no 'content'")
                print(f"    Thinking field: {thinking[:100]}...")
                print(f"    Trying /api/generate endpoint...")

                # Try generate endpoint
                payload_gen = {
                    "model": model,
                    "prompt": "Say hello",
                    "stream": False
                }
                response2 = requests.post(
                    "https://api.ollama.com/api/generate",
                    json=payload_gen,
                    headers=headers,
                    timeout=60
                )
                if response2.status_code == 200:
                    result2 = response2.json()
                    gen_content = result2.get("response", "")
                    if gen_content:
                        print(f"[OK] /api/generate works: '{gen_content}'")
                    else:
                        print(f"[FAIL] /api/generate also empty")
            else:
                print(f"[FAIL] Empty response")
                print(f"    Full response keys: {list(result.keys())}")

        else:
            print(f"[FAIL] {response.text[:100]}")

    except Exception as e:
        print(f"[ERROR] {e}")

print("\n" + "=" * 70)
print("Done!")