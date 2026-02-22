# Model Selection Fix - Version 2

## Problem
The model selection in llm-pspice was resetting to "cogito-2.1:671b" (cloud) or "deepseek-r1:8b" (local) on every app rerun, regardless of user selection.

## Root Causes
1. Cloud/local models were being re-fetched on every rerun
2. Model was being reset when fetch failed or returned empty
3. No tracking of user's explicit selections
4. Streamlit selectbox state conflicts

## Solution

### 1. Add Selection Tracking
Added `user_has_selected_model` flag to session state to prevent auto-reset:
```python
if 'user_has_selected_model' not in st.session_state:
    st.session_state.user_has_selected_model = False
```

### 2. Cache Model Lists
Only fetch cloud/local models once, not on every rerun:
```python
if not st.session_state.cloud_models:
    st.session_state.cloud_models = get_cloud_models(cloud_key)
```

### 3. Respect User Selection
Only set default models when user hasn't selected anything yet:
```python
if not st.session_state.user_has_selected_model:
    # Set default
else:
    # Keep user's selection
```

### 4. Track User Interactions
Mark model as user-selected when they explicitly change it:
```python
if ollama_model != st.session_state.ollama_model:
    st.session_state.ollama_model = ollama_model
    st.session_state.user_has_selected_model = True
```

### 5. Mode Switching
Clear selection flag when switching between cloud/local modes:
```python
if use_cloud != st.session_state.ollama_use_cloud:
    st.session_state.ollama_use_cloud = use_cloud
    st.session_state.user_has_selected_model = False
```

### 6. Unique Keys for Selectboxes
Added unique keys to prevent Streamlit state conflicts:
```python
st.selectbox("...", ..., key="cloud_model_select")
st.selectbox("...", ..., key="local_model_select")
```

## Testing
1. Start the app
2. Select a cloud model from the dropdown
3. Send a chat message (triggers rerun)
4. Verify the selected model is preserved
5. Switch to local mode
6. Local default is applied (not cloud selection)
7. Select a local model
8. Verify it's preserved on rerun

## Expected Behavior
- ✅ Initial load: Default cloud/local model
- ✅ User selects model: Selection preserved across reruns
- ✅ Fetch fails: Keeps existing selection (doesn't reset)
- ✅ Switch cloud/local: New mode's default is applied
- ✅ Custom model: Stored in "Custom Model" text input

## Files Modified
- `llm-sim-poc/app.py` lines 155-177 (session state initialization)
- `llm-sim-poc/app.py` lines 465-547 (cloud models section)
- `llm-sim-poc/app.py` lines 549-597 (local models section)
- `llm-sim-poc/app.py` lines 467-476 (mode switch toggle)