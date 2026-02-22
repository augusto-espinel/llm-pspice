# VS Code Debugging - Quick Reference

## Keyboard Shortcuts

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Start Debugging | `F5` | `F5` |
| Step Over | `F10` | `F10` |
| Step Into | `F11` | `F11` |
| Step Out | `Shift+F11` | `Shift+F11` |
| Stop Debugging | `Shift+F5` | `Shift+F5` |
| Toggle Breakpoint | `F9` | `F9` |
| Continue | `F5` | `F5` |
| Debug View | `Ctrl+Shift+D` | `Cmd+Shift+D` |
| Debug Console | `Ctrl+Shift+Y` | `Cmd+Shift+Y` |

---

## Common Debug Locations

### Circuit Builder (`circuit_builder.py`)
- Line 227: `run_simulation()` entry
- Line 254: DC→Pulse conversion
- Line 278: LLM fixes applied
- Line 288: Before code execution

### LLM Orchestrator (`llm_orchestrator.py`)
- Line 120: Before API call
- Line 125: After response

### Error Handler (`error_handler.py`)
- Line 45: Error categorization
- Line 65: Error logging

---

## Quick Debug Commands

### In Debug Console

```python
# Inspect variables
filtered_code
namespace.keys()
results['error']
analysis.frequency

# Test functions
len(circuit_code)
type(results['error'])
'SinusoidalVoltageSource' in filtered_code

# Print formatted
print(f"Data points: {len(analysis.frequency)}")
```

---

## Debug All Commands (VS Code)

### View: Toggle (Open Debug View)
`Ctrl+Shift+D`

### Views: Debug: Show Variables (Left panel)
Open automatically during debug

### Views: Debug: Show Watch (Add expressions)
`Ctrl+Shift+D` → Watch section

### Debug: Run and Debug
`F5`

### Debug: Stop
`Shift+F5`

### Debug: Restart
`Ctrl+Shift+F5`

### Debug: Step Over
`F10`

### Debug: Step Into
`F11`

### Debug: Step Out
`Shift+F11`

---

## Breakpoints Types

### Simple Breakpoint
Click gutter → Red dot appears

### Conditional Breakpoint
Right-click gutter → "Edit Breakpoint" → Add condition:

```python
len(circuit_code) > 5000
results.get('error') is not None
i == 10
```

### Log Point (New!)
Right-click gutter → "Add Log Point" → Add message:

```python
"Circuit code length: {len(circuit_code)}"
"Error: {results.get('error')}"
```

---

## 30-Second Debug Setup

1. Open VS Code in project directory
   ```powershell
   cd C:\Users\augus\.openclaw\workspace\llm-sim-poc
   code .
   ```

2. Select Python interpreter
   `Ctrl+Shift+P` → "Python: Select Interpreter"
   Choose: `pyspice` environment

3. Open `circuit_builder.py`
4. Click line 227 (left margin) → Red dot appears
5. `Ctrl+Shift+D` (Debug view)
6. Select "Streamlit: Run App"
7. `F5` (Start debugging)

**Done!** App runs with breakpoint active.

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Breakpoint not hit | Check file path, restart VS Code |
| ModuleNotFoundError | Select correct interpreter (pyspice) |
| Can't add watch | Ensure debug session is active |
| Variables not showing | Check DEBUG CONSOLE tab |

---

## Debug Panels

**Left Side (during debug):**
- Variables - See all variables in scope
- Watch - Monitor specific expressions
- Call Stack - See function call hierarchy

**Bottom:**
- Debug Console - Execute Python code
- Terminal - Streamlit output

---

## Tip: Debug Streamlit Reruns

Streamlit reruns on every interaction. To debug:

```python
# In app.py, add this:
if st.session_state.get('debug_count', 0) > 10:
    st.warning(f"Reran {st.session_state.get('debug_count', 0)} times")
st.session_state['debug_count'] = st.session_state.get('debug_count', 0) + 1
```

---

## Next Steps

**Full Guide:** See `docs/VS_CODE_DEBUGGING.md`

**Practice:**
1. Set breakpoint in `circuit_builder.py` line 227
2. Debug the app with F5
3. Submit a circuit request
4. Inspect `filtered_code` variable
5. Step through with F10
6. See what happens under the hood!

---

**Happy Coding! 🚀**