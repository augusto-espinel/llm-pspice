# Getting Your Ollama Cloud API Key

## Method: Get from Website (Currently Works)

Since your Ollama CLI doesn't have the `cloud key` command (version 0.16.0):

### Step 1: Get API Key from Website

1. Go to: https://ollama.ai/cloud
2. Log in with your account
3. Look for "API Keys" or "Manage Keys" section
4. Generate or copy your API key

### Step 2: Test the Key

Run the test script:

```bash
python test_new_api_key.py
```

Paste your API key when prompted.

### Step 3: Update Streamlit App

If the test passes, update the key in the Streamlit sidebar:
→ Paste into "Ollama Cloud API Key"

---

## Alternative: Check Existing Key

If you already have an API key saved somewhere:

Look in:
1. `saved_api_keys.json` (in this directory)
2. Your password manager
3. Ollama website account settings

---

## What to Look For

Your API key should:
- Be a long string of characters
- Start with something like: `eea0dd8d82c144debbc9...`
- Be copied exactly (no extra spaces)

---

**Quick Start:**
1. Get API Key from https://ollama.ai/cloud
2. Test with: `python test_new_api_key.py`
3. If OK, paste into Streamlit sidebar