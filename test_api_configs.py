"""
Test different Ollama Cloud endpoints and configurations
"""

from openai import OpenAI

api_key = "eea0dd8d82c144debbc9bbcfd367b212.ULktML3z6tsOissLTRKGYZT9"

def test_configuration(base_url, model):
    """Test a specific configuration"""

    print(f"\n{'=' * 60}")
    print(f"Testing: {base_url}")
    print(f"Model: {model}")
    print(f"{'=' * 60}")

    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=30.0
        )

        print("Client initialized")

        # Try chat completion
        print("\nAttempting chat completion...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say 'hello' in one word"}
            ],
            max_tokens=10
        )

        print(f"SUCCESS! Response: {response.choices[0].message.content}")
        return True, response.choices[0].message.content

    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")
        return False, str(e)

# Test different configurations
configs = [
    ("https://api.ollama.com/v1", "glm-4.7"),
    ("https://api.ollama.com/v1", "glm-5"),
    ("https://api.ollama.com/v1", "deepseek-v3.2"),
    ("https://api.ollama.com/v1/chat", "glm-4.7"),
    ("https://ollama.ai/api/chat", "glm-4.7"),
]

print("=" * 60)
print("Ollama Cloud API Configuration Test")
print("=" * 60)
print(f"\nAPI Key: {api_key[:20]}... (length: {len(api_key)})")

results = []

for base_url, model in configs:
    success, result = test_configuration(base_url, model)
    results.append({
        "base_url": base_url,
        "model": model,
        "success": success,
        "result": result
    })

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

for r in results:
    status = "✓ WORKS" if r["success"] else "✗ FAILED"
    print(f"{status}: {r['base_url']} - {r['model']}")
    if not r["success"]:
        print(f"         Error: {r['result'][:100] if len(r['result']) > 100 else r['result']}")