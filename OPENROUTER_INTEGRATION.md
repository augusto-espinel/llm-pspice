# OpenRouter Integration for LLM-Sim-POC

## Overview
OpenRouter has been added as a new LLM provider for the circuit simulator. OpenRouter provides unified access to hundreds of models from multiple providers through a single API.

## Changes Made

### 1. `llm_orchestrator.py`
- Updated module docstring to include OpenRouter
- Added OpenRouter initialization in `_init_client()`:
  - Uses OpenAI-compatible API endpoint: `https://openrouter.ai/api/v1`
  - Reads API key from `OPENROUTER_API_KEY` environment variable
- Added "openrouter" to the OpenAI-compatible providers list in `process_request()`
- Added model mapping for OpenRouter with default: `"openai/gpt-3.5-turbo"`
- Model names use OpenRouter's `provider/model-name` format (e.g., `anthropic/claude-3.5-sonnet`)

### 2. `app.py`
- Added "OpenRouter" to the provider dropdown in Settings
- Initialize OpenRouter model session state: `st.session_state.openrouter_model = "openai/gpt-3.5-turbo"`
- Added UI section for OpenRouter model selection:
  - Text input for model name (supports OpenRouter's `provider/model-name` format)
  - Help text with common model examples
  - Link to OpenRouter documentation
- Pass model name to LLMOrchestrator when initializing for OpenRouter

## Usage

### 1. Get an API Key
1. Visit [openrouter.ai](https://openrouter.ai)
2. Sign up and create an API key
3. Fund your account or enable free tier (if available)

### 2. Configure in App
1. Select "OpenRouter" from the LLM Provider dropdown
2. Enter your OpenRouter API key
3. Enter a model name in `provider/model-name` format, e.g.:
   - `openai/gpt-4`
   - `anthropic/claude-3.5-sonnet`
   - `google/gemini-2.0-flash-exp`
   - `meta-llama/llama-3-70b-instruct`
   - `deepseek/deepseek-r1`

### 3. Available Models
OpenRouter supports models from:
- **OpenAI**: GPT-4, GPT-3.5-Turbo, etc.
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus, etc.
- **Google**: Gemini 2.0 Flash, Gemini Pro, etc.
- **Meta**: Llama 2, Llama 3, etc.
- **DeepSeek**: DeepSeek R1, DeepSeek Chat, etc.
- **xAI**: Grok 2, Grok 3, etc.
- **Mistral**: Mistral Large, Mixtral, etc.
- And many more...

See the full model list at: https://openrouter.ai/docs#models

## Advantages

1. **Unified API**: Single integration for dozens of model providers
2. **Easy Model Switching**: Change models without changing API clients
3. **Cost Optimization**: Compare pricing across providers in one place
4. **Conversation Support**: Full conversation history support (like all other providers)
5. **Fallback Options**: If one model is down, try another through the same API

## Implementation Notes

- OpenRouter uses the OpenAI-compatible API format, so it integrates seamlessly with the existing `_openai_compatible_request()` method
- No new dependencies required (uses existing `openai` library)
- Model names follow OpenRouter's naming convention: `provider/model-name`
- API endpoint automatically handles routing to the specified model provider

## Troubleshooting

**"Invalid API key" error:**
- Check your API key is correct at openrouter.ai
- Verify your account is funded or free tier is enabled

**"Model not found" error:**
- Check model name format: should be `provider/model-name`
- Verify the model exists on OpenRouter (check https://openrouter.ai/docs#models)

**Rate limit errors:**
- Check your OpenRouter usage limits
- Consider using a different model with better rate limits

## Future Enhancements

Potential additions:
- Model dropdown with real-time fetching of available models from OpenRouter API
- Pricing display per model
- Token usage tracking
- Response time statistics for different models
