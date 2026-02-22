# QUICK FIX - Duplicate Declaration Error

## The Error

```
❌ Simulation error: <cdef source string>:7: duplicate declaration of struct ngcomplex
```

## What Happened

Your circuit simulation failed because PySpice tried to initialize twice in the same session. This happens when:
- The LLM generates code with `from PySpice.Spice.Netlist import Circuit`
- Multiple simulations run in the same Streamlit session
- Ngspice doesn't allow re-initialization

## The Fix ✅

**We've updated `circuit_builder.py` to:**

1. **Automatically filter out PySpice import statements** from LLM code
2. **Use a pre-loaded namespace** with Circuit() and units
3. **Show clear error messages** if it still happens

## What You Need to Do

### Option 1: Just Restart (Quickest)

1. In Streamlit, click **"Stop"**
2. Then click **"Run"** again
3. Or refresh your browser page

This restarts the Python process and clears Ngspice's state.

### Option 2: Already Fixed (If You Restart)

The fix is now in place. After restarting:
1. Try your circuit request again
2. The imports will be filtered automatically
3. Simulation should work

## Test It

Try a simple circuit:

```
Create an RC circuit with R=1kΩ, C=10µF, and 5V input
```

You should now see:
```
[FILTER] Removed PySpice import: from PySpice.Spice.Netlist import Circuit
[FILTER] Removed PySpice import: from PySpice.Unit import *

=== DEBUG INFO ===
Analysis type: <class 'PySpice.RawFile'>
Time length: 51

✅ Simulation completed! Found X data points.
```

## If It Still Happens Then

1. Refresh the page (F5 / Cmd+R)
2. Click "Clear Chat" in sidebar
3. Try again with a simpler circuit

---

**The fix is automatic - just restart the app and you're good!** 🚀