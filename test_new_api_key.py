"""
Test your new Ollama Cloud API key after upgrading
"""

import requests
import sys

def test_ollama_key(api_key):
    """Test if the API key works for inference"""

    BASE_URL = "https://api.ollama.com"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print("=" * 70)
    print("OLLAMA CLOUD API KEY TEST")
    print("=" * 70)

    # Test 1: List models
    print("\n[Test 1] Checking model access...")
    try:
        response = requests.get(f"{BASE_URL}/api/tags", headers=headers, timeout=30)

        if response.status_code == 200:
            models = response.json()
            count = len(models.get("models", []))
            print(f"[OK] Can list {count} models")
        else:
            print(f"[FAIL] Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        return False

    # Test 2: Run inference
    print("\n[Test 2] Testing model inference...")
    test_models = ["glm-4.7", "glm-5", "deepseek-v3.2"]

    for model in test_models:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "Hi"}],
                "stream": False,
                "options": {"num_predict": 10}
            }

            response = requests.post(
                f"{BASE_URL}/api/chat",
                json=payload,
                headers=headers,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("message", {}).get("content", "")

                if content:
                    print(f"[OK] {model}: Works! Response: '{content}'")
                    print(f"\n==> Your API key is WORKING for Ollama Cloud!")
                    print(f"==> You can now use '{model}' in the Streamlit app.")
                    return True
                else:
                    print(f"[WARN] {model}: Empty response")
            else:
                print(f"[FAIL] {model}: Status {response.status_code} - {response.text[:100]}")

        except Exception as e:
            print(f"[FAIL] {model}: Exception - {str(e)[:100]}")

    print("\n[FAIL] Your API key cannot run model inference.")
    print("Upgrade your tier at: https://ollama.ai/cloud")
    return False

if __name__ == "__main__":
    # Get API key from user
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        print("\nEnter your Ollama Cloud API key:")
        api_key = input("> ").strip()

    test_ollama_key(api_key)