# Ollama Pro Subscription Fix

If you have Ollama Pro but getting 401 errors, fix it in 2 minutes:

## Step 1: Regenerate Your API Key

Run this command to get a fresh key:

```bash
ollama cloud key
```

This will display a new API key. Copy it.

## Step 2: Test the New Key

Use the test script I created:

```bash
python test_new_api_key.py
```

When prompted, paste your new API key.

If it says `[OK]`, your key works!

## Step 3: Update in Streamlit App

1. Open the Streamlit sidebar
2. Find "Ollama Cloud API Key"
3. Replace the old key with your new one
4. Try submitting a circuit request

---

## If It Still Doesn't Work

### Check Subscription Status

1. Go to https://ollama.ai/cloud
2. Log in
3. Verify your Pro subscription is **Active**
4. Make sure you're logged into the right account

### Try Direct Key Test

Replace the key in this script with yours:

```python
import requests

api_key = "YOUR_NEW_KEY_HERE"
url = "https://api.ollama.com/api/chat"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "glm-4.7",
    "messages": [{"role": "user", "content": "Say hello"}],
    "stream": False
}

response = requests.post(url, json=payload, headers=headers, timeout=60)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

### Common Issues

**Issue 1: Old/cached key**
- Solution: Run `ollama cloud key` again to get fresh key

**Issue 2: Wrong account**
- Solution: Log in to https://ollama.ai/cloud and verify it matches your Ollama CLI login

**Issue 3: Subscription not activated**
- Solution: Check billing page at https://ollama.ai/cloud

**Issue 4: API endpoint changed**
- The app uses the correct endpoint: `https://api.ollama.com/api/chat`
- If Ollama changes it, check their docs

---

## Quick Fix Command

```bash
# 1. Get new key
ollama cloud key | Select-String -Pattern "ollama" | ForEach-Object {
    # Copy the API key (select the output)
}

# 2. Test it
python test_new_api_key.py

# 3. If OK, paste into Streamlit sidebar
```

---

**Next:** Run `ollama cloud key` and paste the new key into the Streamlit app. It should work immediately with Pro!