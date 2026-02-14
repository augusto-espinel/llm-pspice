"""
Test Ollama Cloud with different models and settings to find the fastest/configured one
"""

import requests
import time

api_key = "eea0dd8d82c144debbc9bbcfd367b212.ULktML3z6tsOissLTRKGYZT9"
base_url = "https://api.ollama.com"

# Test configurations
configs = [
    ("glm-4.7", 1000),
    ("glm-4.7", 500),
    ("glm-5", 1000),
    ("glm-5", 500),
    ("deepseek-v3.2", 1000),
    ("deepseek-v3.2", 500),
    ("minimax-m2.1", 1000),
    ("minimax-m2.1", 500),
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

system_prompt = "You are a circuit design expert. Write Python code using PySpice."
user_request = "Create a simple RC circuit with R=10k and C=10uF"

print("=" * 70)
print("Ollama Cloud Performance Test")
print("=" * 70)
print(f"\nTesting with: {len(configs)} different configurations")
print(f"Request: {user_request}\n")

results = []

for model, num_tokens in configs:
    url = f"{base_url}/api/chat"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request}
        ],
        "stream": False,
        "options": {
            "num_predict": num_tokens,
            "temperature": 0.7
        }
    }

    try:
        print(f"Testing {model} (max_tokens={num_tokens})...", end=" ")
        start = time.time()

        response = requests.post(url, json=payload, headers=headers, timeout=120)

        elapsed = time.time() - start

        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            token_count = len(content.split())

            print(f"✓ {elapsed:.1f}s | {token_count} tokens")
            results.append({
                "model": model,
                "tokens": num_tokens,
                "response_tokens": token_count,
                "time": elapsed,
                "tokens_per_sec": token_count / elapsed if elapsed > 0 else 0
            })
        else:
            print(f"✗ Status {response.status_code}")
            results.append({
                "model": model,
                "tokens": num_tokens,
                "time": None,
                "error": f"Status {response.status_code}"
            })

    except Exception as e:
        print(f"✗ {str(e)[:50]}")
        results.append({
            "model": model,
            "tokens": num_tokens,
            "time": None,
            "error": str(e)[:100]
        })

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Sort by time
successful = [r for r in results if r.get("time") is not None]
if successful:
    successful.sort(key=lambda x: x["time"])

    print("\nFastest to slowest:")
    for i, r in enumerate(successful, 1):
        print(f"{i}. {r['model']} (tokens={r['tokens']}): {r['time']:.1f}s "
              f"({r['tokens_per_sec']:.1f} tokens/s)")

# Failed
failed = [r for r in results if r.get("error") is not None]
if failed:
    print("\nFailed:")
    for r in failed:
        print(f"✗ {r['model']}: {r.get('error', 'Unknown error')}")

print("\n" + "=" * 70)
print("RECOMMENDATIONS:")
print("=" * 70)

if successful:
    fastest = successful[0]
    print(f"\n✓ Fastest model: {fastest['model']} (limit={fastest['tokens']})")
    print(f"  Time: {fastest['time']:.1f}s")
    print(f"  Speed: {fastest['tokens_per_sec']:.1f} tokens/s")

    print("\nFor this app, I recommend:")
    print(f"• Use {fastest['model']} for speed")
    print(f"• Set num_predict to {fastest['tokens']} for reasonable responses")
    print(f"• If it still times out, reduce to 300-500 tokens")
else:
    print("\n✗ All requests failed!")
    print("This could mean:")
    print("• Ollama Cloud service is down")
    print("• Network connectivity issues")
    print("• API key limitations")
    print("\nTry using local models instead.")