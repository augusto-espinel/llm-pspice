"""
Test OpenRouter integration
Run this to verify OpenRouter works with llm_orchestrator
"""

from llm_orchestrator import LLMOrchestrator

def test_openrouter_init():
    """Test that OpenRouter initializes correctly"""
    print("Testing OpenRouter initialization...")
    
    # Test with default model
    try:
        orchestrator = LLMOrchestrator(
            provider="openrouter",
            api_key="test-key-123",  # Won't make actual API call
            model_name=None  # Should use default
        )
        print("✅ OpenRouter initialized with default model")
        print(f"   Provider: {orchestrator.provider}")
        print(f"   Model: {orchestrator.model_name}")
        print(f"   Client: {type(orchestrator.client).__name__}")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Test with custom model
    try:
        orchestrator = LLMOrchestrator(
            provider="openrouter",
            api_key="test-key-123",
            model_name="anthropic/claude-3.5-sonnet"
        )
        print("\n✅ OpenRouter initialized with custom model")
        print(f"   Provider: {orchestrator.provider}")
        print(f"   Model: {orchestrator.model_name}")
        print(f"   Client: {type(orchestrator.client).__name__}")
    except Exception as e:
        print(f"❌ Failed to initialize with custom model: {e}")
        return False
    
    return True

def test_provider_routing():
    """Test that OpenRouter is routed to the correct request method"""
    print("\n\nTesting provider routing...")
    
    orchestrator = LLMOrchestrator(
        provider="openrouter",
        api_key="test-key-123",
        model_name="openai/gpt-3.5-turbo"
    )
    
    # Check that client was initialized
    if orchestrator.client is None:
        print("❌ Client was not initialized")
        return False
    
    # Check that base_url is correct
    if hasattr(orchestrator.client, 'base_url'):
        base_url = str(orchestrator.client.base_url)
        if 'openrouter.ai' in base_url:
            print(f"✅ Correct base URL: {base_url}")
        else:
            print(f"❌ Wrong base URL: {base_url}")
            return False
    
    print("✅ Provider routing configured correctly")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("OpenRouter Integration Test")
    print("=" * 60)
    
    success = True
    
    # Run tests
    if not test_openrouter_init():
        success = False
    
    if not test_provider_routing():
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
        print("\nNext steps:")
        print("1. Get an OpenRouter API key from https://openrouter.ai")
        print("2. Start the app: python run_app.ps1")
        print("3. Select 'OpenRouter' from the provider dropdown")
        print("4. Enter your API key")
        print("5. Choose a model (e.g., 'anthropic/claude-3.5-sonnet')")
        print("6. Generate a circuit!")
    else:
        print("❌ Some tests failed")
        print("Check the errors above")
    print("=" * 60)
