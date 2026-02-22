# App Refactor - Complete Decoupling from Ralph

## Executive Summary

The app has been refactored to eliminate all dependencies on Ralph, making the production version standalone and secure. Ralph is now an **independent CLI analysis tool** that reads app logs and generates improvement suggestions.

## Architecture Changes

### Before (Coupled - Security Risk)
```
┌─────────────────┐
│   app.py        │
│   + imports     │◄── Depends on Ralph
│   + Ralph Fixer │
│   + Ralph Tester│
└────────┬────────┘
         │ writes
    logs/issues.json
         │ (Ralph modifies app's log)
```

### After (Decoupled - Secure)
```
┌─────────────────┐                  ┌─────────────────┐
│   app.py        │ read-only       │ Ralph Fixer     │
│   + app_logger  │────────────────▶│ (CLI Tool)      │
│   (standalone)  │                  │   + reader.py   │
└────────┬────────┘                  │   + tester.py   │
         │ writes                   └────────┬────────┘
    logs/issues.json                         │ generator
         │ (write-only)                      │
                                          generated files:
                                          - improved_system_prompt.txt
                                          - template_issue_*.py
                                          - logs/ralph_resolution.json
```

## Key Changes

### 1. App (`app.py`) - Production

**Removed:**
- ❌ All Ralph imports
- ❌ Ralph Fixer integration
- ❌ Ralph Tester integration
- ❌ "Run Ralph Analysis" button
- ❌ Ralph UI section in sidebar

**Added:**
- ✅ `app_logger.py` - Simple file logger (no Ralph deps)
- ✅ Minimal issue logging only
- ✅ Zero Ralph/Fixer/Tester imports

**App Logger (`app_logger.py`):**
```python
# Simple production logger
class AppLogger:
    def log_issue(self, prompt, issue_type, error_message="", **metadata):
        # Logs to logs/issues.json (append-only)
        # No status tracking, no Ralph dependencies
        # Pure production logging
```

### 2. Ralph Fixer (`ralph_fixer.py`) - CLI Tool

**Now:** Standalone CLI tool that:
- ✅ Reads app logs (read-only)
- ✅ Analyzes patterns
- ✅ Generates suggestions:
  * `improved_system_prompt.txt`
  * `template_issue_*.py`
- ✅ Maintains own resolution log: `logs/ralph_resolution.json`
- ❌ NEVER modifies app logs
- ❌ NEVER modifies app source code

**Resolution Log:** `logs/ralph_resolution.json`
```json
[
  {
    "issue_id": 7,
    "timestamp": "2026-02-16T01:35:00Z",
    "strategy": "enhanced_system_prompt",
    "test_evidence": "Tested 3 prompts, 2 work (66.7% success)",
    "resolution_note": "Applied fix: enhanced_system_prompt | Evidence: ..."
  }
]
```

### 3. New Components

**`app_logger.py` (4.6KB)**
- Production-only issue logger
- No Ralph dependencies
- Simple JSON file logging

**`app_issue_reader.py` (3.4KB)**
- Ralph's read-only interface to app logs
- NEVER writes to app logs
- Backward compatible with old log format

**`ralph_fixer.py` (updated)**
- Now uses `app_issue_reader` instead of modifying app logs
- Saves resolution to separate `logs/ralph_resolution.json`
- No longer calls `logger.mark_resolved()` on app logs

**`ralph_tester.py` (updated)**
- Uses `app_issue_reader` to read app logs
- No imports from app or Ralph's logger

### 4. Log Format Separation

**App Log (`logs/issues.json`):**
```json
{
  "timestamp": "2026-02-16T01:35:00Z",
  "prompt": "Create a simple circuit",
  "issue_type": "simulation_error",
  "error_message": "singular matrix",
  "metadata": {
    "llm_model": "deepseek-r1:8b",
    "provider": "ollama"
  }
}
```
- Write-only from app
- Read-only for Ralph
- No status tracking

**Ralph Resolution Log (`logs/ralph_resolution.json`):**
```json
{
  "issue_id": 3,
  "timestamp": "2026-02-16T01:35:00Z",
  "strategy": "enhanced_system_prompt",
  "test_evidence": "Tested 3 prompts, 2 work (66.7% success)",
  "resolution_note": "..."
}
```
- Write-only from Ralph
- Invisible to app
- Ralph's private resolution tracking

## Security Benefits

1. ✅ **App cannot modify itself** - No Ralph → app code path
2. ✅ **App logs append-only** - App writes, Ralph reads
3. ✅ **Ralph isolated** - Separate CLI tool, no app dependencies
4. ✅ **Clear separation** - Deploy app, run Ralph separately (if needed)
5. ✅ **Production safe** - App has zero external analysis tool dependencies

## Usage

### App (Production)
```bash
# Just run the app - no Ralph involved
cd llm-sim-poc
streamlit run app.py

# App will log failures to logs/issues.json automatically
# No Ralph button, no Ralph UI
```

### Ralph (Developer Tool)
```bash
# Run Ralph separately
cd llm-sim-poc
python test_ralph.py

# Output:
# - improved_system_prompt.txt
# - template_issue_*.py
# - logs/ralph_resolution.json (Ralph's private log)
```

## Backward Compatibility

**Existing logs:** Old `logs/issues.json` with status field still work
- Ralph treats `status: resolved` as addressed
- Ralph treats no status field as open
- Smooth transition from old to new logger format

## Files

### App (Production)
- `app.py` - Standalone, no Ralph deps
- `app_logger.py` - Simple production logger

### Ralph (CLI Tool)
- `ralph_fixer.py` - Analysis and fix generation
- `ralph_tester.py` - Automated verification
- `app_issue_reader.py` - Read-only app log reader
- `test_ralph.py` - CLI interface

### Logs
- `logs/issues.json` - App's issue log (app writes, Ralph reads)
- `logs/ralph_resolution.json` - Ralph's resolution log (Ralph only)
- `logs/ralph_test_results.json` - Test results (Tester only)

## Developer Workflow

1. **Deploy app** (production)
   - No Ralph, just Streamlit app
   - Logs failures automatically

2. **User uses app**
   - Generates circuits
   - Failures logged to `logs/issues.json`

3. **Developer runs Ralph** (optional)
   ```bash
   python test_ralph.py
   ```
   - Analyzes app logs
   - Generates improvements
   - Tests improvements automatically

4. **Developer reviews**
   - Check `improved_system_prompt.txt`
   - Check `logs/ralph_resolution.json`
   - Decide to apply or not

5. **If approved**
   - Manually update `llm_orchestrator.py` with improved prompt
   - Redeploy app

## Summary

✅ **App is completely standalone**
✅ **No self-modification capability**
✅ **Ralph is separate analysis tool**
✅ **Clear separation of concerns**
✅ **Security maintained**
✅ **Production ready**

---

**Status:** ✅ Complete decoupling implemented
**Security:** ✅ App cannot modify itself
**Architecture:** ✅ Clean separation: App (runtime) | Ralph (analysis tool)