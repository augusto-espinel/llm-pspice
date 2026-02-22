# Test script to verify ngspice 38 is used
$CONDA_NGSPICE = "C:\Users\augus\anaconda3\envs\pyspice\Library\bin"
$env:PATH = "$CONDA_NGSPICE;$env:PATH"

$ngspicePath = Get-Command ngspice | Select-Object -ExpandProperty Source
Write-Host "ngspice.exe location: $ngspicePath"

# Now run Python to verify PySpice detects the right version
conda run -n pyspice python -c "from PySpice.Spice.Netlist import Circuit; c = Circuit('test'); c.V('v', '1', '0', 1); sim = c.simulator(); print('Success! ngspice working')"