@echo off
REM ========================================
REM Show Test Summary Then Run Tests
REM ========================================

call conda activate pyspice
python test_summary.py

echo.
echo ========================================
echo Ready to run tests?
echo ========================================
echo.
echo Press any key to run both tests...
pause > nul

.\run_all_tests.bat

echo.
echo ========================================
echo Tests complete!
echo ========================================
echo.
echo Check these files:
echo   - TEST_SUITE_README.md (Detailed guide)
echo   - test_1_response.txt (LLM response test 1)
echo   - streamlit_response.txt (LLM response test 2)
echo.
pause