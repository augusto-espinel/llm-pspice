# 🚀 Quick Start Guide

## 5-Minute Setup

### 1. Install Ngspice (System Dependency)

**Windows:**
- Download: https://ngspice.sourceforge.io/downloads.html
- Install and add to PATH (or keep in default location)

**Mac:**
```bash
brew install ngspice
```

**Linux:**
```bash
sudo apt install ngspice
```

### 2. Install Python Dependencies

```bash
cd llm-sim-poc
pip install -r requirements.txt
```

### 3. (Optional) Add OpenAI API Key

```bash
cp .env.example .env
# Edit .env and add your API key
```

### 4. Run Tests

```bash
python test_setup.py
```

### 5. Launch App

```bash
streamlit run app.py
```

Open: http://localhost:8501

**That's it!** 🎉

---

## 💡 First Things to Try

1. Type: *"Create a simple RC circuit with R=1kΩ, C=10µF"*
2. Watch LLM generate code
3. See simulation plot appear on the right
4. Download CSV with numerical data

---

## 🆘 Troubleshooting

### Ngspice not found
**Error:** `spice not found` or `ngspice not in PATH`

**Fix:** Install Ngspice (see step 1 above) and ensure it's in your system PATH

### PySpice import error
**Error:** `ModuleNotFoundError: No module named 'PySpice'`

**Fix:** Run `pip install -r requirements.txt` again

### LLM not generating circuits
**Symptoms:** Generic fallback responses only

**Fix:** Add OpenAI API key to `.env` file

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit UI |
| `circuit_builder.py` | PySpice integration |
| `llm_orchestrator.py` | LLM interface |
| `test_setup.py` | Verify installation |

---

## 🎯 Pro Tips

- Start with **fallback mode** (no API key) to test basics
- Gradually add complex circuits as you learn
- Export CSV for analysis in Excel/Matlab
- Modify `llm_orchestrator.py` to customize prompts

---

**Need more?** See `README.md` for full documentation