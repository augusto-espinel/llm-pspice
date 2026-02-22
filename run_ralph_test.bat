@echo off
cd llm-sim-poc
call conda activate pyspice
python test_ralph_cloud.py > ralph_test_output.txt 2>&1
type ralph_test_output.txt