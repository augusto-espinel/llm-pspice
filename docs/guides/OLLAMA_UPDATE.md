# OLLAMA CLOUD - IMPORTANT UPDATE

## ⚡ Breaking Change: Model Names

As of February 2026, Ollama Cloud **no longer requires** the `:cloud` suffix.

### Old Way (Deprecated)
```python
model = "glm-4.7:cloud"  # ❌ No longer works
```

### New Way (Current)
```python
model = "glm-4.7"  # ✅ Correct
model = "glm-5"    # ✅ Correct
model = "deepseek-v3.2"  # ✅ Correct
```

## Endpoint Update

The working Ollama Cloud endpoint is:

```
https://api.ollama.com/v1
```

Note: `api.ollama.ai` does not resolve (DNS error) and should not be used.

## Available Cloud Models (as of Feb 2026)

Based on API response, here are available models:

```json
{
  "glm-5": "Latest GLM model",
  "glm-4.7": "High performance",
  "glm-4.6": "Previous generation",
  "deepseek-v3.2": "DeepSeek's latest",
  "deepseek-v3.1": "DeepSeek V3.1",
  "minimax-m2.1": "MiniMax M2.1",
  "minimax-m2": "MiniMax M2",
  "gpt-oss:120b": "Open-source GPT 120B",
  "gpt-oss:20b": "Open-source GPT 20B",
  "ministral-3:8b": "Mistral 3 8B",
  "ministral-3:14b": "Mistral 3 14B",
  "mistral-large-3:675b": "Large model",
  "gemma3:12b": "Gemma 3 12B",
  "gemma3:27b": "Gemma 3 27B",
  "qwen3-coder:480b": "Qwen 3 Coder",
  "qwen3-next:80b": "Qwen 3 Next",
  "kimi-k2.5": "Kimi K2.5",
  "gemini-3-flash-preview": "Gemini 3 Flash",
  "devstral-2:123b": "Devstral 2 123B"
}
```

## Quick Test

To verify your API key works:

```powershell
$headers = @{"Authorization" = "Bearer YOUR_KEY"}
Invoke-WebRequest -Uri "https://api.ollama.com/v1/models" -Headers $headers | Select-Object -ExpandProperty Content
```

## Usage in the App

1. Select **Ollama** provider in sidebar
2. Check ☑️ **"Use Ollama Cloud"**
3. Enter your API key (from `ollama cloud key`)
4. Enter model name (e.g., `glm-4.7`, `deepseek-v3.2`)
5. Submit your request!

## Migration Guide

If you have old code/config using `:cloud` suffix:

1. Remove `:cloud` suffix from model names
2. Update endpoint to `https://api.ollama.com/v1`
3. Test your API key with the curl command above
4. All else should work the same!

## Documentation

- Full guide: `OLLAMA_CLOUD_GUIDE.md`
- Troubleshooting: `OLLAMA_CLOUD_TROUBLESHOOTING.md`

---

**Questions?** Check the documentation files above for detailed help! 🚀