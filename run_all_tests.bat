@echo off
echo ========================================
echo Test Suite - llm-pspice
echo ========================================
echo.

echo Test 1: Direct LLM Test
echo ------------------------
echo Checking: Does LLM generate correct pulse syntax?
echo.
cd llm-sim-poc
call conda activate pyspice
python test_llm_direct.py > test_1_output.txt 2>&1
type test_1_output.txt
if errorlevel 1 (
    echo [ERROR] Test 1 failed
) else (
    echo [OK] Test 1 completed
)
echo.
echo.

echo Test 2: Complete Simulation Test
echo --------------------------------
echo Checking: Full Streamlit workflow with ACTUAL simulation
echo This test:
echo   1. Generates circuit code
echo   2. Builds circuit
echo   3. RUNS simulation (ngspice)
echo   4. Verifies data produced
echo   5. Stores data OUTSIDE workspace
echo.
python test_like_streamlit_simulation.py > test_2_simulation_output.txt 2>&1
type test_2_simulation_output.txt
if errorlevel 1 (
    echo [ERROR] Test 2 failed
) else (
    echo [OK] Test 2 completed
)
echo.
echo.

echo ========================================
echo ALL TESTS COMPLETE
echo ========================================
echo.
echo Output files:
echo   - test_1_response.txt (test 1 LLM response)
echo   - test_2_simulation_summary.json (test 2 summary)
echo   - Raw data: ~/.openclaw/simulation_data/llm-pspice/
echo.
echo Check test_1_output.txt and test_2_simulation_output.txt for detailed results
echo.
pause