# Ollama Configuration Guide

## Setting Up Ollama

### 1. Install Ollama
Download from: https://ollama.com

### 2. Pull a Model
```bash
# Basic model (good for circuit design)
ollama pull llama3

# List all available models
ollama pull llama2
ollama pull mistral
ollama pull codellama
```

### 3. Start the Server
```bash
ollama serve
```

### 4. Test Your Setup
```bash
# List installed models
ollama list

# Test a model
ollama run llama3 "test"
```

---

## Common Ollama Models for Circuit Design

### Recommended
- **llama3** - Best balance of speed and quality (recommended!)
- **llama2** - Slightly older but still good
- **mistral** - Fast and capable

### Code Specialized
- **codellama** - Good for code generation but slower

---

## Troubleshooting

### Error: "model not found"
1. Check installed models: `ollama list`
2. Pull the model: `ollama pull <model-name>`
3. Update the "Ollama Model" field in the app sidebar

### Connection Refused
1. Make sure Ollama is running: `ollama serve`
2. Check firewall settings
3. Restart the application

### Slow Response
Ollama runs on CPU by default:
- Consider a GPU-accelerated machine
- Use smaller models (llama2 instead of llama3)
- Close other applications

---

## Using Custom Models

If you have custom models trained with your Ollama subscription:

1. List your models: `ollama list`
2. Copy your desired model name (e.g., `my-custom-circuit-v1`)
3. Enter it in the "Ollama Model" field in the app sidebar
4. No API key needed!

---

## Model Comparison

| Model | Speed | Quality | Size | Recommended |
|-------|-------|---------|------|-------------|
| llama3 | Fast | High | 4.7GB | ✅ Yes |
| llama2 | Very Fast | Good | 3.8GB | ✅ Yes |
| mistral | Very Fast | Good | 4.1GB | ✅ Yes |
| codellama | Medium | High | 3.8GB | Maybe |

---

**Note:** The app default is `llama3`. Change this in the sidebar if you prefer another model!