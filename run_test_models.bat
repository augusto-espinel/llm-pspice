@echo off
cd llm-sim-poc
call conda activate pyspice
python test_both_models.py > test_models_output.txt 2>&1
type test_models_output.txt