# Script to launch Streamlit with conda environment (PySpice + ngspice 38)

# Python path - using conda environment with working PySpice setup
$CONDA_PYTHON = "C:\Users\augus\anaconda3\envs\pyspice\python.exe"

Write-Host "================================================================="
Write-Host " LLM Circuit Simulator - PySpice Environment"
Write-Host "================================================================="
Write-Host ""
Write-Host "Conda Python: $CONDA_PYTHON"
Write-Host "PySpice version: 1.5"
Write-Host "ngspice version: 38 (via conda)"
Write-Host "Python version: 3.10"
Write-Host ""
Write-Host "This environment provides:"
Write-Host "  - Accurate transient analysis (DC-to-pulse auto-conversion)"
Write-Host "  - < 1% simulation error (validated with RC circuit)"
Write-Host "  - Proper ngspice DLL support"
Write-Host ""
Write-Host "================================================================="
Write-Host ""

# Launch Streamlit with conda Python
Set-Location "C:\Users\augus\.openclaw\workspace\llm-sim-poc"
& $CONDA_PYTHON -m streamlit run app.py