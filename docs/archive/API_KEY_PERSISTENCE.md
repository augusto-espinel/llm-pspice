# API Key Persistence

## Overview

The app now **persists your API keys** between sessions! ✅

## How It Works

When you enter an API key in the sidebar, it's saved to `saved_api_keys.json` in the project directory. The next time you open the app, your keys will automatically load.

## What Gets Saved

- ✅ **OpenAI API Key** - saved under "openai"
- ✅ **Google Gemini API Key** - saved under "gemini"
- ✅ **Anthropic Claude API Key** - saved under "claude"
- ✅ **DeepSeek API Key** - saved under "deepseek"
- ✅ **Ollama Cloud API Key** - saved under "ollama_cloud"

**Note:** API keys are stored locally on your machine in plain text. Keep your project directory secure!

## File Location

```
llm-sim-poc/
├── saved_api_keys.json      ← API keys stored here
├── .gitignore                ← Excludes saved_api_keys.json
└── app.py                    ← Loading/saving logic
```

## Security

### ⚠️ Important Considerations

1. **Local Storage Only:** Keys are stored locally on your machine
2. **Not Encrypted:** Keys are saved in plain text in JSON format
3. **Do Not Commit:** `saved_api_keys.json` is in `.gitignore`
4. **Protect Your Files:** Keep your project directory secure

### Recommended Practices

- ✅ Use `.env` for production (not tracked by git)
- ✅ Limit file permissions on saved_api_keys.json
- ⚠️ Don't share the saved_api_keys.json file
- ⚠️ Don't commit API keys to version control

## Using .env Instead (Optional)

If you prefer environment variables over the JSON file:

1. Create a `.env` file in the project root
2. Add your keys:
   ```bash
   OPENAI_API_KEY=sk-your-key
   OLLAMA_API_KEY=your-ollama-cloud-key
   GEMINI_API_KEY=your-gemini-key
   CLAUDE_API_KEY=your-claude-key
   DEEPSEEK_API_KEY=your-deepseek-key
   ```
3. The app will automatically load from `.env` if available
4. Keys loaded from `.env` are NOT saved to `saved_api_keys.json`

## Clearing Saved Keys

To remove saved keys:

**Option 1: Delete the file**
```bash
rm saved_api_keys.json
```

**Option 2: Clear individual keys in the app**
1. Open the app
2. Select the provider
3. Delete the text in the API key field
4. Press Enter or move to another field (empty keys are not saved)

## Troubleshooting

### API key not loading?
- Check that `saved_api_keys.json` exists
- Verify the JSON format is correct
- Try restarting the app

### Key not saving?
- Make sure you're not in read-only mode
- Check file permissions on `saved_api_keys.json`
- Ensure the key is not empty (empty keys are not saved)

### Want to use .env instead?
- Create `.env` file with your keys
- The app prioritizes `.env` over saved keys
- Delete `saved_api_keys.json` if switching completely

---

**Happy circuit simulating! 🚀**