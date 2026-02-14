"""Find all working models for your Ollama Pro tier"""

import requests
import json

API_KEY = "eea0dd8d82c144debbc9bbcfd367b212.ULktML3z6tsOissLTRKGYZT9"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Get all available models
print("Fetching available models...")
response = requests.get("https://api.ollama.com/api/tags", headers=headers, timeout=30)

if response.status_code == 200:
    result = response.json()
    models = [m["name"] for m in result.get("models", [])]

    print(f"\nFound {len(models)} models. Testing which ones work...\n")
    print("=" * 70)

    # Test each model
    working_models = []
    empty_models = []
    failed_models = []

    for model in models[:20]:  # Test first 20 for speed
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "stream": False,
            "options": {"num_predict": 10}
        }

        try:
            response = requests.post(
                "https://api.ollama.com/api/chat",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("message", {}).get("content", "")

                if content:
                    working_models.append((model, content))
                    print(f"[OK] {model}: '{content}'")
                else:
                    empty_models.append(model)
                    print(f"[ ] {model}: Empty (tier limit)")
            else:
                failed_models.append((model, response.status_code))
                print(f"[X] {model}: {response.status_code}")

        except Exception as e:
            failed_models.append((model, str(e)))
            print(f"[?] {model}: Error")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n[WORKING] {len(working_models)} models:")
    for model, response in working_models:
        print(f"  - {model}")

    print(f"\n[EMPTY/TIER LIMIT] {len(empty_models)} models:")
    for model in empty_models[:10]:  # Show first 10
        print(f"  - {model}")

    print(f"\n[FAILED] {len(failed_models)} models")

    print("\n" + "=" * 70)
    print("RECOMMENDED FOR CIRCUIT DESIGN")
    print("=" * 70)
    if working_models:
        print(f"\nBest available model: {working_models[0][0]}")
        print("\nOther working models:")
        for model, _ in working_models[1:5]:
            print(f"  - {model}")

else:
    print(f"Failed to get models: {response.text}")