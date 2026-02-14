"""
Test Ollama Cloud API connection
"""

from openai import OpenAI

# Test with the API key provided by the user
api_key = "eea0dd8d82c144debbc9bbcfd367b212.ULktML3z6tsOissLTRKGYZT9"

def test_api():
    """Test Ollama Cloud API connection"""

    print("=" * 60)
    print("Testing Ollama Cloud API Connection")
    print("=" * 60)

    print(f"\nAPI Key: {api_key[:20]}... (length: {len(api_key)})")

    # Test with OpenAI client
    try:
        client = OpenAI(
            base_url="https://api.ollama.com/v1",
            api_key=api_key,
            timeout=30.0
        )

        print("\nClient initialized successfully")

        # Try to list models
        print("\nFetching models...")
        models = client.models.list()

        print(f"\nSuccess! Found {len(models.data)} models")

        # Show first few models
        print("\nFirst 5 models:")
        for i, model in enumerate(models.data[:5], 1):
            print(f"  {i}. {model.id}")

        # Try a simple chat completion
        print("\nTesting chat completion...")
        response = client.chat.completions.create(
            model="glm-4.7",
            messages=[
                {"role": "user", "content": "Say 'hello' in one word"}
            ],
            max_tokens=10
        )

        print(f"Chat successful! Response: {response.choices[0].message.content}")

        return True

    except Exception as e:
        print(f"\nError: {e}")
        print(f"\nError type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    test_api()