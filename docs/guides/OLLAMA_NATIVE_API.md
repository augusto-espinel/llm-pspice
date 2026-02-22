# OLLAMA CLOUD API FIX - CRITICAL UPDATE

## Problem Identified

The OpenAI-compatible API format `/v1/chat/completions` **does NOT work** with Ollama Cloud. It returns "unauthorized" errors even with a valid API key.

## Solution

Use the **native Ollama API format** instead:

- ✅ Working: `https://api.ollama.com/api/chat`
- ✅ Working: `https://api.ollama.com/api/generate`
- ❌ Broken: `https://api.ollama.com/v1/chat/completions`

## API Endpoints

### /api/chat (Chat Completions)

```bash
curl https://api.ollama.com/api/chat \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.7",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant"},
      {"role": "user", "content": "Say hello"}
    ],
    "stream": false
  }'
```

### /api/generate (Text Completion)

```bash
curl https://api.ollama.com/api/generate \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.7",
    "prompt": "Say hello",
    "stream": false
  }'
```

## Code Implementation

### Python (requests library)

```python
import requests

api_key = "your_api_key"
base_url = "https://api.ollama.com"

# Chat completion
response = requests.post(
    f"{base_url}/api/chat",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "glm-4.7",
        "messages": [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Say hello"}
        ],
        "stream": False
    }
)

result = response.json()
content = result["message"]["content"]
print(content)
```

## Testing Results

### Test 1: /api/chat
- ✅ Status: 200
- ✅ Response: Works correctly
- ✅ Streaming: Supported

### Test 2: /api/generate
- ✅ Status: 200
- ✅ Response: Works correctly
- ✅ Simpler: Good for single-turn prompts

### Test 3: /v1/chat/completions (OpenAI-compatible)
- ❌ Status: 401 Unauthorized
- ❌ Does NOT work with API keys
- ❌ Only works for local Ollama

## Updated Documentation

The app now correctly uses:
- **Local Ollama:** `/v1/chat/completions` (OpenAI-compatible at `localhost:11434/v1/`)
- **Ollama Cloud:** `/api/chat` (native API at `api.ollama.com/api/`)

## Troubleshooting

### Error: "unauthorized"

Check:
1. API key is correct: run `ollama cloud key`
2. Using correct endpoint (`/api/chat` not `/v1/chat/completions`)
3. Bearer token format: `Authorization: Bearer key`
4. Subscription is active: https://ollama.ai/cloud

### Error: "model not found"

Check available models:
```bash
curl https://api.ollama.com/api/tags \
  -H "Authorization: Bearer YOUR_KEY"
```

Or in PowerShell:
```powershell
$headers = @{"Authorization" = "Bearer YOUR_KEY"}
Invoke-WebRequest -Uri "https://api.ollama.com/api/tags" -Headers $headers
```

## Available Cloud Models

As of February 2026:

- `glm-5` - Latest GLM
- `glm-4.7` - High performance (recommended)
- `glm-4.6` - Previous generation
- `deepseek-v3.2` - Coding specialist
- `deepseek-v3.1` - DeepSeek V3.1
- `minimax-m2.1` - Efficient
- `gpt-oss:120b` - Open-source GPT
- `mistral-large-3:675b` - Largest model
- `gemma3:12b` - Google Gemma
- And many more...

**Note:** No `:cloud` suffix needed for model names!

---

## Test Script

Use `test_native_api.py` to verify your setup works:

```bash
python test_native_api.py
```

This tests all three endpoints and shows which ones work with your API key.

---

**Updated:** Ollama Cloud now uses native API format for authentication. 🚀