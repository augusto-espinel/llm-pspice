# Quick Fix: Ollama Model Not Found

## Your Available Models

Based on your Ollama installation, you have these models:

### ✅ Recommended for Circuit Design:
- `deepseek-r1:8b` - Good balance (4.9GB)
- `mannix/gemma2-9b-sppo-iter3:latest` - High quality (5.8GB)

### ☁️ Cloud Models (may need special config):
- `glm-4.7:cloud`
- `minimax-m2.1:cloud`

### Other DeepSeek Models:
- `erwan2/DeepSeek-R1-Distill-Qwen-7B:latest` (4.7GB)
- `erwan2/DeepSeek-R1-Distill-Qwen-14B:latest` (9.0GB) - Larger, slower
- `hf.co/unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF:Q8_0` (8.5GB)

---

## Quick Fix

1. In the Streamlit app sidebar (under LLM Provider "Ollama")
2. Find "Ollama Model" field
3. Change from `deepseek-r1:8b` to your preferred model (I've already updated the default)
4. Try again with a circuit request

---

## What I Fixed

✅ Changed default model from `llama3` (which you don't have) to `deepseek-r1:8b` (which you do have)

✅ Added "Ollama Model" text input so you can switch between any of your installed models

✅ You can use any model from your `ollama list` output by copying the NAME column

---

The app should now work with `deepseek-r1:8b` as the default! Try it again.