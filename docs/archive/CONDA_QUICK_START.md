# Conda Quick Start Guide

## Recommended Setup: Conda Environment (Most Reliable)

The conda environment provides the most stable PySpice installation with all required dependencies.

---

## 1. Create Conda Environment

```bash
# Create environment with Python 3.10
conda create -n pyspice python=3.10 -y

# Activate environment
conda activate pyspice
```

**Why Python 3.10?**
- PySpice 1.5 requires Python 3.10 (not 3.11 or 3.12)
- Provides stable ngspice integration
- Best compatibility

---

## 2. Install PySpice

```bash
# Install PySpice with ngspice (includes SPICE engine)
conda install -c conda-forge pyspice -y
```

This installs:
- **PySpice 1.5** - Python SPICE interface
- **ngspice 38** - SPICE simulation engine
- **All dependencies** (numpy, matplotlib, etc.)

---

## 3. Install Project Dependencies

```bash
# Navigate to project directory
cd C:\Users\augus\.openclaw\workspace\llm-sim-poc

# Install Python packages
pip install -r requirements.txt
```

---

## 4. Verify Installation

```bash
# Test PySpice installation
C:\Users\augus\anaconda3\envs\pyspice\python.exe -c "import PySpice; print('PySpice:', PySpice.__version__)"

# Run validation test
C:\Users\augus\anaconda3\envs\pyspice\python.exe test_rc_pulse_final.py
```

Expected output:
```
PySpice: 1.5
[SUCCESS] Pulse source approach works!
PySpice + ngspice 38: SIMULATIONS ARE ACCURATE
```

---

## 5. Run the App

### Option A: Using Conda Python Directly (Recommended)

```bash
# Activate environment
conda activate pyspice

# Run app
streamlit run app.py
```

### Option B: Using Full Python Path

```powershell
# Windows PowerShell
C:\Users\augus\anaconda3\envs\pyspice\python.exe -m streamlit run app.py
```

### Option C: Create Batch File

Create `run_app.cmd`:

```batch
@echo off
call C:\Users\augus\anaconda3\Scripts\activate.bat pyspice
streamlit run app.py
pause
```

Then double-click to run.

---

## 6. Open in Browser

The app launches at: **http://localhost:8501**

---

## Environment Location

Your conda environment is installed at:
```
C:\Users\augus\anaconda3\envs\pyspice\
```

Python executable:
```
C:\Users\augus\anaconda3\envs\pyspice\python.exe
```

---

## Common Commands

```bash
# Activate environment
conda activate pyspice

# Deactivate environment
conda deactivate

# View installed packages
conda list

# Update PySpice
conda update -c conda-forge pyspice

# Reinstall PySpice (if needed)
conda install -n pyspice -c conda-forge pyspice --force-reinstall
```

---

## Troubleshooting

### "Python 3.11 not supported"

**Problem:** Using wrong Python version

**Solution:**
```bash
# Recreate with Python 3.10
conda remove -n pyspice --all
conda create -n pyspice python=3.10 -y
conda activate pyspice
conda install -c conda-forge pyspice -y
```

### "ngspice.dll not found"

**Problem:** ngspice not on PATH

**Solution:** Using conda should fix this. Verify:
```bash
where ngspice
# Should show: C:\Users\augus\anaconda3\envs\pyspice\Library\bin\ngspice.exe
```

If not found:
```bash
conda install -n pyspice -c conda-forge ngspice -y
```

### Streamlit not found

**Problem:** Dependencies not installed

**Solution:**
```bash
conda activate pyspice
pip install -r requirements.txt
```

### Activation not working

**Problem:** conda not initialized

**Solution (add to PATH):**
```powershell
# Add conda to system PATH
# C:\Users\augus\anaconda3
# C:\Users\augus\anaconda3\Scripts
# C:\Users\augus\anaconda3\Library\bin

# Then restart terminal
```

---

## Alternative: Virtual Environment

If you prefer virtual environment without conda (less reliable):

```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install ngspice manually first!
# Download: https://ngspice.sourceforge.io/downloads.html

# Install Python packages
pip install -r requirements.txt

# Run
streamlit run app.py
```

**Warning:** Virtual environment requires manual ngspice installation and PATH configuration.

---

## Success Criteria

✅ All tests pass:
- PySpice imports without errors
- `test_rc_pulse_final.py` shows 0.01% accuracy
- App launches at http://localhost:8501
- Simulations run without errors

---

## Next Steps

1. **Install LLM API Key** (see README.md)
2. **Run your first circuit simulation**
3. **Read DC_TO_PULSE_FIX.md** (important!)

---

**Need Help?** Check:
- `README.md` - Full documentation
- `DC_TO_PULSE_FIX.md` - Circuit simulation details
- `PYSPICE_SETUP_SUCCESS.md` - Architecture guide
- `OLLAMA_CLOUD_GUIDE.md` - Free LLM option

---

**Author:** Conda Quick Start Guide
**Date:** 2026-02-14
**Status:** ✅ Tested and Validated