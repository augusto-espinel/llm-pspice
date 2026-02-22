# Updated UI - Model Dropdowns

## What's New

The app now shows **dropdown lists** of available models instead of plain text inputs!

## How to Use

### With Ollama Cloud ☁️

1. Check ☑️ **"Use Ollama Cloud"**

2. Enter your **Ollama Cloud API Key**

3. **Cloud models load automatically** - you'll see:
   - ✅ **☁️ Found X cloud models in your tier**

4. **Select from dropdown:**
   - Recommended models appear first (tested to work):
     - cogito-2.1:671b ⭐ (Best for circuit design)
     - qwen3-coder:480b (Excellent for code)
     - deepseek-v3.1:671b (Technical specialist)
     - kimi-k2:1t (1T params!)
     - nemotron-3-nano:30b
   - Other available models in your tier appear below

5. **Need a model not in the list?**
   - Check ☑️ **"🔧 Use custom model name"**
   - Type any model name (e.g., `glm-4.7`)

### With Local Ollama 💾

1. Uncheck ☐ **"Use Ollama Cloud"**

2. **Local models load automatically** - you'll see:
   - ✅ **💾 Found X local models**

3. **Select from dropdown:**
   - All downloaded local models (e.g., deepseek-r1:8b, llama3.2)

4. **Need a custom model?**
   - Check ☑️ **"🔧 Use custom model name"**
   - Type the model name

## Features

### ✅ Automatic Model Fetching

- **Cloud:** Fetches from Ollama Cloud API when API key is entered
- **Local:** Fetches from localhost:11434 when local Ollama is running

### ✅ Smart Ordering

**Cloud models:** Recommended working models appear first
- Models tested and confirmed working: cogito-2.1:671b, qwen3-coder:480b, etc.
- Other tier models follow alphabetically

**Local models:** In the order returned by Ollama

### ✅ Custom Model Override

Both cloud and local modes support:
- ☑️ **"🔧 Use custom model name"**
- **Custom Model Name** text input appears
- Type any model name (even if not in dropdown)

### ✅ Error Handling

**Cloud API issues:**
- ⚠️ Warning if can't fetch models
- Falls back to cogito-2.1:671b
- Suggests checking API key

**Local Ollama issues:**
- ⚠️ Warning if no models found
- Suggests checking if Ollama is running
- Falls back to deepseek-r1:8b

## Example Workflows

### Workflow 1: Start with Cloud Quick Test

```
1. Check ☑️ "Use Ollama Cloud"
2. Paste API key
3. Dropdown loads automatically
4. Select "cogito-2.1:671b"
5. Submit circuit request
```

### Workflow 2: Test Multiple Cloud Models

```
1. Enter API key → models load
2. Try "cogito-2.1:671b"
3. Submit request → check result
4. Try "qwen3-coder:480b"
5. Submit request → compare
6. Continue testing...
```

### Workflow 3: Use Specific Cloud Model

```
1. Enter API key → models load
2. Can't find model in dropdown?
3. Check ☑️ "🔧 Use custom model name"
4. Type: "gemma3:12b"
5. Submit request
```

### Workflow 4: Switch to Local Models

```
1. Uncheck ☐ "Use Ollama Cloud"
2. Local models load automatically
3. Select "deepseek-r1:8b"
4. Submit request

Or if need specific local model:
3. Check ☑️ "🔧 Use custom model name"
4. Type: "mistral:7b"
5. Submit request
```

## Technical Details

### Cloud Model Fetching

```python
def get_cloud_models(api_key):
    # Fetches from https://api.ollama.com/api/tags
    # Returns list of model names available in tier
    # Example: ["cogito-2.1:671b", "glm-4.7", ...]
```

### Local Model Fetching

```python
def get_local_models():
    # Fetches from http://localhost:11434/api/tags
    # Returns list of downloaded models
    # Example: ["deepseek-r1:8b", "llama3.2", ...]
```

### Session State

Models are cached in session state:
- `st.session_state.cloud_models` - Cloud model list
- `st.session_state.local_models` - Local model list
- `st.session_state.ollama_model` - Selected model
- `st.session_state.use_custom_model` - Custom model toggle

## Troubleshooting

### Cloud Models Don't Load

**Symptom:** ⚠️ Could not fetch cloud models

**Solutions:**
1. Check API key is correct
2. Verify Pro subscription is active: https://ollama.ai/cloud
3. Try regenerating API key
4. Check if Ollama Cloud is up: https://status.ollama.ai

### Local Models Don't Load

**Symptom:** ⚠️ No local models found

**Solutions:**
1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```
2. Download a model:
   ```bash
   ollama pull deepseek-r1:8b
   ```

### Custom Model Not Working

**Symptom:** Selected custom model but AI fails

**Solutions:**
1. Check model name spelling (no typos)
2. For cloud models: verify it's in your tier
3. For local models: verify it's downloaded
4. Check if model format is correct (e.g., "model:tag")

## Benefits

### Before (Text Input Only)

- ❌ Had to remember model names
- ❌ No visibility of tier availability
- ❌ Typos common
- ❌ No indication which models work

### After (Dropdown + Custom)

- ✅ See ALL available models
- ✅ Recommended models highlighted
- ✅ No typos possible (dropdown)
- ✅ Still supports custom names
- ✅ Better UX overall

---

**Enjoy the improved model selection! 🚀**