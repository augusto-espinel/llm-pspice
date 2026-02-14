# Ollama Cloud Support

## Overview

This app supports **Ollama Cloud API** for accessing high-end models that may not be available or practical to run locally on your machine.

## Quick Start

### 1. Get Your Ollama Cloud API Key

```bash
ollama cloud key
```

Copy the key (starts with something like `eea0dd8d82c144debbc9bbcfd367b212...`)

### 2. Enable Ollama Cloud in the App

1. Open the Streamlit sidebar
2. Make sure **Ollama** is selected as the LLM Provider
3. Check ☑️ **"Use Ollama Cloud"**
4. Paste your API key in **"Ollama Cloud API Key"**
5. Set model name (e.g., `glm-4.7`, `deepseek-v3.2`)
6. Submit a circuit request!

## Available Cloud Models

Based on Ollama's latest API, these cloud models are available:

### Recommended Models

**Tested and Working (Recommended):**

| Model | Description | Use Case |
|-------|-------------|----------|
| `cogito-2.1:671b` | Cogito 2.1 | Balanced, reliable, recommended |
| `qwen3-coder:480b` | Qwen 3 Coder | Coding specialist |
| `deepseek-v3.1:671b` | DeepSeek V3.1 | Coding, math, reasoning |
| `kimi-k2:1t` | Kimi K2 1T参数 | High quality, technical tasks |

**Available but Untested (try at your own risk):**

| Model | Description | Use Case |
|-------|-------------|----------|
| `glm-4.6` | Previous generation GLM | Good performance, lower cost |
| `deepseek-v3.2` | DeepSeek's latest | Coding, math, reasoning |
| `gpt-oss:120b` | Open-source GPT | High quality generation |
| `minimax-m2.1` | MiniMax 2.1 | Efficient, good quality |
| `gemini-3-flash-preview` | Flash preview | Fast responses |

**Known Issues:**

| Model | Status | Issue |
|-------|--------|-------|
| `glm-4.7` | ⚠️ Works but empty responses | Model returns 200 status with no content |
| `glm-5` | ⚠️ Works but empty responses | Model returns 200 status with no content |

> **Note:** GLM-4.7 and GLM-5 appear in your catalog but currently return empty responses. This may be due to model configuration or API limitations. Use the recommended models above instead.

### Specialized Models

| Model | Description |
|-------|-------------|
| `qwen3-next:80b` | Next-generation Qwen |
| `ministral-3:8b` | Lightweight Mistral |
| `ministral-3:14b` | Balanced Mistral |
| `mistral-large-3:675b` | Large model, highest quality |
| `gemma3:12b` | Google Gemma 3 12B |
| `gemma3:27b` | Google Gemma 3 27B |

### For full list:

```powershell
$headers = @{"Authorization" = "Bearer YOUR_KEY"}
Invoke-WebRequest -Uri "https://api.ollama.com/v1/models" -Headers $headers
```

## Important Notes

### Model Names

**Cloud models do NOT use the `:cloud` suffix anymore.**
- ❌ Wrong: `glm-4.7:cloud`
- ✅ Correct: `glm-4.7`

Just use the model name directly from the API response!

### API Endpoint

The app now uses the correct Ollama Cloud endpoint:
- **Base URL:** `https://api.ollama.com/v1`

## Configuration

### Using .env file

Create a `.env` file in the project root:

```bash
# .env
OLLAMA_API_KEY=your_api_key_here
OLLAMA_CLOUD_URL=https://api.ollama.com/v1
```

### Using app sidebar

Enter the API key directly in the sidebar under **"Ollama Cloud API Key"**. The app will save it to `saved_api_keys.json` for future sessions.

## Local vs Cloud

| Feature | Local Ollama | Ollama Cloud |
|---------|--------------|--------------|
| Requires API key | No | Yes |
| Model selection | Models you pull | Full catalog |
| CPU/GPU usage | Yes (your hardware) | No (offloaded) |
| Latency | Lower | Higher (networked) |
| Cost | Free | Subscription-based |
| Reliability | High | Depends on internet |

## Testing Your Connection

### PowerShell

```powershell
$headers = @{"Authorization" = "Bearer YOUR_KEY"}
Invoke-WebRequest -Uri "https://api.ollama.com/v1/models" -Headers $headers | Select-Object -ExpandProperty Content
```

### Bash/Curl

```bash
curl https://api.ollama.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

### Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.ollama.com/v1",
    api_key="YOUR_KEY"
)

models = client.models.list()
for model in models.data:
    print(model.id)
```

## Troubleshooting

### Error: "Connection error"

1. Make sure you're using the correct endpoint: `https://api.ollama.com/v1`
2. Verify your API key is valid: run the test commands above
3. Check internet connectivity
4. See `OLLAMA_CLOUD_TROUBLESHOOTING.md` for detailed help

### Error: "Model not found"

1. Check available models via the API
2. Make sure you're using the correct model name (no `:cloud` suffix)
3. Verify your subscription includes that model

### Error: "Unauthorized" or 401

1. Your API key is invalid or expired
2. Get a new key: `ollama cloud key`
3. Update in app sidebar

### Still having issues?

See `OLLAMA_CLOUD_TROUBLESHOOTING.md` for detailed troubleshooting steps.

## Pricing

Ollama Cloud offers different tiers with varying model access. Check:

- https://ollama.ai/cloud
- https://ollama.ai/pricing

for current pricing and model availability.

## Example Models to Try

```python
# High quality (more expensive)
model = "glm-5"
model = "deepseek-v3.2"
model = "mistral-large-3:675b"

# Balanced (good value)
model = "glm-4.7"
model = "minimax-m2.1"
model = "qwen3-next:80b"

# Faster/lighter
model = "ministral-3:8b"
model = "gemma3:12b"
```

## Support

- **Official docs:** https://github.com/ollama/ollama
- **Cloud status:** https://status.ollama.ai
- **Community:** https://github.com/ollama/ollama/discussions

---

**Enjoy the power of cloud-based LLMs for circuit simulation! 🚀**