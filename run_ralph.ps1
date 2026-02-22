# Ralph Test Runner Script
$ErrorActionPreference = "Continue"

cd "C:\Users\augus\.openclaw\workspace\llm-sim-poc"

& "C:\Users\augus\anaconda3\envs\pyspice\python.exe" "test_ralph.py" "--test-fixes"