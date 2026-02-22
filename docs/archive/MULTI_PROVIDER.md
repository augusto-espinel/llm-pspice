# Multi-Provider LLM Support

## Supported Providers

Your LLM Circuit Simulator now supports **5 LLM providers**:

### 1. OpenAI
- **API Key:** Get from https://platform.openai.com/api-keys
- **Models:** GPT-4, GPT-3.5-turbo
- **Usage:** Production-grade, high quality

### 2. Google Gemini
- **API Key:** Get from https://makersuite.google.com/app/apikey
- **Models:** Gemini Pro
- **Install:** `pip install google-generativeai` (already done)

### 3. Anthropic Claude
- **API Key:** Get from https://console.anthropic.com/settings/keys
- **Models:** Claude 3 Sonnet
- **Install:** `pip install anthropic` (already done)

### 4. DeepSeek
- **API Key:** Get from https://platform.deepseek.com/api_keys
- **Models:** DeepSeek-chat
- **Usage:** Cost-effective alternative to OpenAI

### 5. Ollama (Local)
- **API Key:** None needed (local inference)
- **Install:** Download from https://ollama.com
- **Models:** Any local model (default: llama3.2)
- **Setup:** Run `ollama serve` and `ollama pull llama3.2`

---

## Configuration

### Method 1: UI Configuration (Session)

1. Open the Streamlit app: http://localhost:8501
2. In the sidebar, select your LLM provider
3. Enter API key (not needed for Ollama)
4. Keys are saved for the current session only

### Method 2: Environment Variables (Persistent)

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your keys
OPENAI_API_KEY=sk-your-key-here
GEMINI_API_KEY=AIza-your-key-here
CLAUDE_API_KEY=sk-ant-your-key-here
DEEPSEEK_API_KEY=sk-your-key-here
```

---

## Using Ollama

1. Download Ollama: https://ollama.com
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```
3. Start the server:
   ```bash
   ollama serve
   ```
4. Select "Ollama" in the app's LLM Provider dropdown

**No API key needed** for Ollama - everything runs locally!

---

## Provider Comparison

| Provider | Cost | Quality | Speed | Privacy |
|----------|------|---------|-------|---------|
| OpenAI | High | Excellent | Fast | Cloud |
| Gemini | Medium | Good | Fast | Cloud |
| Claude | High | Excellent | Fast | Cloud |
| DeepSeek | Low | Good | Fast | Cloud |
| Ollama | **Free** | Varies by model | Slower | **Local** |

---

## Troubleshooting

### OpenAI API Error
- Check API key is valid
- Verify account has credits
- Check rate limits

### Gemini Error
- Ensure `google-generativeai` is installed
- Check API key format
- Verify billing is enabled in Google Cloud

### Claude Error
- Ensure `anthropic` is installed
- Claude 3 Sonnet is the fastest option
- Check quota limits

### DeepSeek Error
- API key format should start with `sk-`
- Check server status at https://status.deepseek.com

### Ollama Error
- Ensure `ollama serve` is running
- Check model is downloaded: `ollama list`
- Test with: `ollama run llama3.2 "test"`

---

## Quick Test

1. Select your provider in the sidebar
2. Enter API key (if needed)
3. Type in chat: *"Create a simple RC circuit"*
4. View results!

---

**Note:** You can switch between providers anytime in the UI. Each provider will generate the same PySpice code format, so switching doesn't break your simulations.