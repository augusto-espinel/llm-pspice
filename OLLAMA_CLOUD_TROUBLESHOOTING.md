# Ollama Cloud Troubleshooting

## Connection Errors

### Error: "Connection error" when using Ollama Cloud models

This typically means the app cannot reach the Ollama Cloud API endpoint.

## Quick Fixes

### 1. Verify Your API Key

Your Ollama Cloud API key might be invalid or expired:

```bash
# In PowerShell, check if your key works:
curl https://api.ollama.ai/v1/models `
  -H "Authorization: Bearer YOUR_API_KEY"
```

If this fails, get a new key from: https://ollama.ai

### 2. Try Different Endpoint URLs

The Ollama Cloud API base URL might have changed. The app tries these in order:

1. `https://api.ollama.ai/v1` (primary)
2. `https://api.ollama.com/v1` (alternative)
3. `https://ollama.ai/api/v1` (another alternative)

**Test each URL manually:**

```bash
# Test URL 1
curl https://api.ollama.ai/v1/models `
  -H "Authorization: Bearer YOUR_API_KEY"

# Test URL 2
curl https://api.ollama.com/v1/models `
  -H "Authorization: Bearer YOUR_API_KEY"

# Test URL 3
curl https://ollama.ai/api/v1/models `
  -H "Authorization: Bearer YOUR_API_KEY"
```

If one works, set it via environment variable:

```bash
# This file: .env
OLLAMA_CLOUD_URL=https://api.ollama.com/v1
```

### 3. Check Ollama Cloud Service Status

Visit the Ollama status page:
- https://status.ollama.ai

If there's an outage, you'll need to wait or use local models.

### 4. Verify the Model Exists

Make sure the cloud model you're trying to use exists in your plan:

```bash
curl https://api.ollama.ai/v1/tags `
  -H "Authorization: Bearer YOUR_API_KEY" `
  | jq
```

Look for models like:
- `glm-4.7:cloud`
- `minimax-m2.1:cloud`

## Network Issues

### Firewall Blocking Port 443?

Make sure outbound HTTPS (port 443) is allowed:

```powershell
# Test connectivity
Test-NetConnection -ComputerName api.ollama.ai -Port 443
Test-NetConnection -ComputerName api.ollama.com -Port 443
```

### Corporate Proxy?

If you're behind a corporate proxy, you may need to configure it:

```bash
# Set proxy environment variables
$env:HTTP_PROXY = "http://proxy.company.com:8080"
$env:HTTPS_PROXY = "http://proxy.company.com:8080"

# Then restart Streamlit
streamlit run app.py --server.headless true
```

## Alternative: Use Local Ollama

If cloud keeps failing, use local models instead:

1. **Stop using cloud:**
   - In sidebar, uncheck "Use Ollama Cloud" ☐

2. **Install a local model:**
   ```bash
   ollama pull deepseek-r1:8b
   ```

3. **Set model name in sidebar:**
   - Change from `glm-4.7:cloud` to `deepseek-r1:8b`

4. **Submit your circuit request**

Local models are slower but don't require API keys and won't have connection errors.

## Debug Mode

To see what's happening, check the Streamlit logs:

```bash
# The logs show:
# - Which base URL is being used
# - The exact error message
# - Timeout settings

# Look for lines like:
# Ollama Cloud client initialized with base URL: https://api.ollama.ai/v1
# API call failed: Connection error...
```

## Testing Your API Key Manually

Create a test script `test_ollama_cloud.py`:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.ollama.ai/v1",
    api_key="YOUR_API_KEY_HERE"
)

# Test by listing models
try:
    models = client.models.list()
    print("✅ API key works!")
    print("Available models:")
    for model in models.data:
        print(f"  - {model.id}")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run it:

```bash
python test_ollama_cloud.py
```

## Known Issues

### Issue: Ollama Cloud endpoint changed

**Status:** Happens occasionally as Ollama evolves their API.

**Solution:** Try the alternative URLs listed above. Check the [official docs](https://github.com/ollama/ollama) for updates.

### Issue: Model not found

**Error:** `The model 'glm-4.7:cloud' does not exist or you do not have access`

**Cause:** Your subscription plan might not include this model.

**Solution:**
- Check your account at https://ollama.ai
- Verify which cloud models are included
- Try `deepseek-r1:cloud` if available, or use local models

### Issue: Rate limiting

**Error:** `429 Too Many Requests`

**Cause:** You've hit the rate limit for your account.

**Solution:**
- Wait a bit before trying again
- Upgrade your subscription for higher limits
- Use local models instead

## Getting Help

Still stuck?

1. **Check the logs** - They often contain useful error details
2. **Try local mode** - Verify the rest of the app works
3. **Test API key** - Use the test script above
4. **Check Ollama status** - https://status.ollama.ai
5. **Ask in Ollama community** - https://github.com/ollama/ollama/discussions

---

**Summary:** Connection errors usually point to URL issues, invalid API keys, or service outages. Try local models as a fallback! 🔧