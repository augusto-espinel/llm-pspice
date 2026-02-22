# Ralph Category: Response Duplication

## Issue Type: `response_duplication`

Categorization for Ralph Fixer:

```python
elif issue_type == 'response_duplication':
    analysis['root_cause'] = 'UI display logic or LLM generating duplicate content'
    analysis['recommendation'] = 'Parse response to separate text and code, display each once'
    analysis['fix_strategy'] = 'code_review'  # Manual fix required
    analysis['category'] = 'likely_code_bug'  # Display logic issue, not prompt
```

## Categorization Logic

**Likely Code Bug:**
- Duplication caused by app display logic (st.write + st.code)
- Requires code review and manual fix

**Likely Prompt Issue:**
- LLM itself generating duplicate content in response
- Could be fixed by enhanced prompt instructions

**Mixed:**
- Combination of both - display logic + LLM generation
- Needs full review

## Logging

**App Side:**
- `log_response_duplication()` in `app_logger.py`
- Called when duplication detected
- Logs to `logs/issues.json`

**Ralph Side:**
- Analyzes via `app_issue_reader.py`
- Categorizes as `likely_code_bug` (default)
- Recommends code review

## Files

- `app_logger.py` - Logger function
- `app.py` - Fixed duplication bug (2026-02-16)
- `BUGFIX_RESPONSE_DUPLICATION.md` - Full fix documentation

---

**Integration Date:** 2026-02-16
**For:** Ralph Fixer categorization enhancement