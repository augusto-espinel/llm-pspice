# Conversation History Feature

## Overview
The LLM Circuit Simulator now supports multi-turn conversations where the LLM remembers previous context and the **actual simulated circuit code** (after fixes).

## Key Features

### 1. Context Tracking
- **Chat history**: Display-only history shown in the chat interface
- **Chat messages**: Context sent to LLM API (last 10 turns to manage token usage)
- **Last simulated code**: The successfully executed PySpice code (after automatic fixes)

### 2. How It Works

When you send a query:
1. App checks if there's a previously simulated circuit (`st.session_state.last_simulated_code`)
2. If yes, it includes the **fixed** code as context:
   ```python
   Current working circuit code (successfully simulated):
   ```python
   [The actual PySpice code that ran]
   ```
   For modifications, update this code appropriately.
   ```
3. App sends last 10 conversation turns to the LLM
4. LLM responds with modifications to the working circuit

### 3. Example Workflow

**Query 1:** "Create an RC low-pass filter with 1kHz cutoff"
- LLM generates code
- App fixes issues (e.g., `Sinusoidal()` → `SinusoidalVoltageSource()`)
- Simulation succeeds
- **Result**: `last_simulated_code` contains the FIXED code

**Query 2:** "Change R to 2kΩ"
- LLM receives the FIXED code from Query 1
- Modifies the resistor value
- App runs simulation with updated code
- **Success!** Modification based on real code, not LLM hallucination

**Query 3:** "Add a second capacitor in parallel"
- LLM receives the code from Query 2 (already with 2kΩ resistor)
- Adds capacitor to the working circuit
- Simulation runs successfully
- **Accumulated improvements** build on each other

### 4. Technical Implementation

#### Session State Variables
```python
st.session_state.chat_history = []           # For display (role, message)
st.session_state.chat_messages = []          # For LLM API (role, message)
st.session_state.last_simulated_code = None  # Successfully simulated code
st.session_state.circuit_code = None         # Latest generated code (LLM proposal)
```

#### API Request Format
```python
messages = [
    {"role": "system", "content": system_prompt},
    # Last 10 conversation turns
    {"role": "user", "content": "Create RC filter"},
    {"role": "assistant", "content": "Here's the code..."},
    # ...
    # Current working circuit (after fixes)
    {"role": "system", "content": "Current working circuit code..."},
    # Current request
    {"role": "user", "content": "Change R to 2kΩ"}
]
```

### 5. Provider Support

All providers support conversation history:
- ✅ OpenAI (GPT-3.5-Turbo)
- ✅ DeepSeek
- ✅ Ollama (native and cloud)
- ✅ Google Gemini
- ✅ Anthropic Claude

Each provider formats messages according to their specific API requirements.

### 6. Token Management

- **MAX_CHAT_HISTORY = 10**: Only the last 10 turns are sent to LLM
- Prevents token limit errors
- Older context is dropped automatically
- System prompt and current circuit context are always included

### 7. Error Handling

- **Empty LLM response**: Not added to chat context (avoids pollution)
- **Simulation failure**: `last_simulated_code` NOT updated (keeps previous working code)
- **API errors**: Graceful fallback with error messages
- **Provider-specific validation**: Each provider validates message format

### 8. Testing Plan

#### Manual Test (Streamlit UI)
1. Start fresh session: "Create RC low-pass filter"
2. Verify simulation runs successfully
3. Query: "Change R to 2kΩ"
4. Verify modification is based on the first circuit
5. Query: "Run AC analysis instead of transient"
6. Verify analysis type changes
7. Query: "Add second pole with another RC stage"
8. Verify circuit complexity increases

#### Browser Automation Test
```python
# Navigate to app
browser(action="open", profile="openclaw", targetUrl="http://localhost:8501")

# Take snapshot
browser(action="snapshot", profile="openclaw")

# Send first query
browser(action="act", profile="openclaw", ref="[textbox]", request={
    "kind": "click",
    "ref": "[textbox]"
})
# Type query
browser(action="act", profile="openclaw", ref="[textbox]", request={
    "kind": "type",
    "text": "RC low-pass filter 1kHz"
})
# Submit
browser(action="act", profile="openclaw", ref="[send button]", request={
    "kind": "press",
    "key": "Enter"
})

# Wait for simulation to complete
time.sleep(15)

# Take snapshot of results
browser(action="snapshot", profile="openclaw")

# Send follow-up query
# ... (repeat for modification tests)
```

### 9. Known Limitations

1. **Token limits**: Very long circuits may hit context limits
2. **Memory**: Session persists until page refresh
3. **Provider differences**: Each provider handles context slightly differently
4. **No persistence**: Context lost on browser refresh (Streamlit limitation)

### 10. Future Improvements

- [ ] Persistent conversation storage (database)
- [ ] Circuit comparison/diff viewer
- [ ] Undo/redo functionality
- [ ] Circuit versioning
- [ ] Export conversation with code
- [ ] Context summary for long conversations

## Developer Notes

### Files Modified
1. **app.py**: Added `chat_messages`, `last_simulated_code`, and context building logic
2. **llm_orchestrator.py**: Updated all provider methods to accept `chat_history` and `circuit_context`

### Adding Support for New Provider
When adding a new provider, ensure:
```python
def _new_provider_request(self, user_request, system_prompt, chat_history=None, circuit_context=None):
    # Build messages with context
    messages = [{"role": "system", "content": system_prompt}]

    if chat_history:
        messages.extend([{"role": role, "content": msg} for role, msg in chat_history])

    if circuit_context:
        messages.append({"role": "system", "content": circuit_context})

    messages.append({"role": "user", "content": user_request})

    # Make API call with messages...
```

## Troubleshooting

**Problem**: LLM ignores previous queries
- Check that `st.session_state.chat_messages` is populated
- Verify `last_simulated_code` is set after successful simulation
- Check browser console for API errors

**Problem**: Too many tokens
- Reduce `MAX_CHAT_HISTORY` value in app.py
- Simplify queries
- Use provider with higher token limits (GPT-4, Claude)

**Problem**: Modifications not accumulated
- Verify simulation succeeded before modification
- Check console logs for "last_simulated_code" updates
- Ensure LLM receives the fixed code, not the original LLM proposal