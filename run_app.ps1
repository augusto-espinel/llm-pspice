# Script to set ngspice path and launch Streamlit

# Set ngspice path for this session
$env:PATH += ";C:\Users\augus\Tools\ngspice\Spice64\bin"
Set-Item -Path "Env:NGSPICE_HOME" -Value "C:\Users\augus\Tools\ngspice\Spice64\bin"

Write-Host "NGSPICE_HOME: $env:NGSPICE_HOME"
Write-Host "ngspice in PATH: $(Get-Command ngspice -ErrorAction SilentlyContinue)"

# Launch Streamlit
Set-Location "C:\Users\augus\.openclaw\workspace\llm-sim-poc"
streamlit run app.py