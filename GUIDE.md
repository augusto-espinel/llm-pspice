# Quick Start Guide - File Structure

## Root Directory (Clean & Organized)

### Python Files (12) - Core Application
```
app.py                             Main Streamlit UI
circuit_builder.py                Circuit building & simulation
llm_orchestrator.py               LLM API management
error_handler.py                  Error handling
issue_logger.py                   Issue tracking
ralph_fixer.py                    Ralph Fixer (automated analysis)
ralph_tester.py                   Ralph Tester
ralph_tester_streamlit_settings.py Ralph UI settings
sim_config.py                     Simulation config
unit_validator.py                 Unit validation
app_issue_reader.py               Issue log viewer
app_logger.py                     App logging
```

### Documentation (5) - Active
```
README.md                         Main app documentation
RALPH_README.md                   Ralph Fixer system docs
LLM_FIXES.md                      Recent fixes (2026-02-22)
FILE_STRUCTURE.md                 Complete file guide ⭐ NEW
REORGANIZATION_SUMMARY.md         What was reorganized ⭐ NEW
```

### Run Scripts (6)
```
run_app.ps1                        Launch Streamlit app
run_ralph.ps1                     Run Ralph Fixer
run_all_tests.bat                 Run all tests
start_tests.bat                   Start testing
run_ralph_test.bat                Test Ralph
run_test_models.bat               Test models
```

## Subdirectories

### `debug/` (24 files)
Debug and utility scripts for development/analysis
```
benchmark_rc_circuit.py          Benchmark tool
check_issues.py                  Issue analysis
find_working_models.py           Test models
verify_setup.py                  Verify setup
... and 20 more
```

### `docs/archive/` (46 files)
Historical documentation (archived, not actively maintained)

### `docs/guides/` (5 files)
API and Ollama guides
```
OLLAMA_CLOUD_GUIDE.md
OLLAMA_CLOUD_TROUBLESHOOTING.md
OLLAMA_GUIDE.md
OLLAMA_NATIVE_API.md
OLLAMA_UPDATE.md
```

### `test_outputs/` (16 files)
Organized test outputs, benchmark data, plots

### `logs/`
Issue logs (`issues.json`) and simulation data

---

## What's Required?

### To Run the App:
- `app.py`
- `circuit_builder.py`
- `llm_orchestrator.py`
- `error_handler.py`
- `issue_logger.py`
- `sim_config.py`
- `unit_validator.py`

### To Use Ralph Fixer:
- `ralph_fixer.py`
- `ralph_tester.py`
- `ralph_tester_streamlit_settings.py`

### Everything Else is Optional:
- Debug scripts
- Test output files
- Archived documentation

---

## Quick Launch

```bash
# Launch the app
streamlit run app.py

# Or use the PowerShell script
.\run_app.ps1

# Run Ralph Fixer (CLI)
python ralph_fixer.py
```

---

## Documentation Order

1. **START HERE:** `README.md` - Main documentation
2. **FILE GUIDE:** `FILE_STRUCTURE.md` - What each file does
3. **RALPH DOCS:** `RALPH_README.md` - Ralph Fixer system
4. **RECENT FIXES:** `LLM_FIXES.md` - Latest bug fixes
5. **HISTORY:** `REORGANIZATION_SUMMARY.md` - What changed

---

**Total Files:**
- Root: 29 files (12 py, 5 md, 6 scripts, 6 other)
- Debug: 24 files
- Docs: 51 files (46 archive + 5 guides)
- Test Outputs: 16 files
- **TOTAL: ~120 files** (organized and categorized)

**Last Updated:** 2026-02-22