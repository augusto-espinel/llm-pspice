# Project Structure and File Guide

## Overview
This document explains the purpose of each Python file in the `llm-sim-poc` project.

## Directory Structure

```
llm-sim-poc/
├── app.py                          # Main Streamlit application
├── circuit_builder.py              # Core circuit building & simulation
├── llm_orchestrator.py             # LLM API management (multi-provider)
├── error_handler.py                # Error handling & categorization
├── issue_logger.py                 # Issue tracking system
├── sim_config.py                   # Simulation configuration
├── unit_validator.py               # PySpice unit validation
├── app_issue_reader.py             # Issue log viewer utility
├── app_logger.py                   # App-level logging
├── ralph_fixer.py                  # Ralph Fixer: automated issue analysis
├── ralph_tester.py                 # Ralph Tester: testing fixes
├── ralph_tester_streamlit_settings.py  # Ralph UI settings
│
├── docs/                           # Documentation
│   ├── archive/                    # Historical docs (archived)
│   └── guides/                     # API/Ollama guides
│
├── debug/                          # Debug & utility scripts
│   ├── benchmark_rc_circuit.py     # Benchmark tool
│   ├── check_issues.py             # Issue analysis
│   └── (21 more debug tools)       # For development/analysis
│
└── logs/                           # Log files
    └── issues.json                 # Tracked simulation issues
```

---

## Core Application Files (REQUIRED)

These files are **essential** for the LLM-PSPICE application to function:

| File | Size (KB) | Purpose | Required? |
|------|-----------|---------|-----------|
| **app.py** | 30.5 | Main Streamlit UI application | ✅ Yes |
| **circuit_builder.py** | 29.2 | Circuit construction, simulation execution, LLM code fixes | ✅ Yes |
| **llm_orchestrator.py** | 21.2 | LLM API wrapper for OpenAI, Ollama, DeepSeek, etc. | ✅ Yes |
| **error_handler.py** | 12.4 | Error categorization, timeout handling, exception management | ✅ Yes |
| **issue_logger.py** | 11.9 | Logging failed prompts, simulation errors, status tracking | ✅ Yes |
| **sim_config.py** | 1.9 | Simulation configuration constants and settings | ✅ Yes |
| **unit_validator.py** | 1.0 | PySpice unit validation (detects u_uF, u_MOhm typos) | ✅ Yes |

### Optional Application Enhancements

| File | Size (KB) | Purpose | Required? |
|------|-----------|---------|-----------|
| **app_issue_reader.py** | 4.1 | Streamlit page for viewing issue logs | ⚪ Optional |
| **app_logger.py** | 5.0 | App-level logging utilities | ⚪ Optional |

---

## Ralph Fixer System (REQUIRED for Ralph)

These files are **required** if you're using the Ralph Fixer automated issue analysis system:

| File | Size (KB) | Purpose | Required? |
|------|-----------|---------|-----------|
| **ralph_fixer.py** | 26.5 | Ralph Fixer: analyzes issues and generates fix strategies | ✅ Yes (for Ralph) |
| **ralph_tester.py** | 16.9 | Ralph Tester: tests Ralph fixer output | ✅ Yes (for Ralph) |
| **ralph_tester_streamlit_settings.py** | 16.8 | Ralph UI settings and preferences | ✅ Yes (for Ralph) |

**Documentation:** See `RALPH_README.md` for complete Ralph Fixer documentation.

---

## Commonly Used Debug Scripts

While all debug scripts are optional, these are particularly useful:

| File | Purpose |
|------|---------|
| `benchmark_rc_circuit.py` | Benchmark RC circuit performance |
| `check_issues.py` | Analyze issue logs (useful with Ralph) |
| `check_version.py` | Check library versions (troubleshooting) |
| `verify_setup.py` | Verify setup is correct |
| `find_working_models.py` | Test which LLM models work well |

---

## All Debug & Utility Scripts (optional)

These files are in the `debug/` directory and are **only needed for development, analysis, or troubleshooting**:

| File | Purpose |
|------|---------|
| `check_issues.py` | Analyze issue logs |
| `check_last_issue.py` | View most recent issue |
| `check_recent_issues.py` | View recent issues |
| `check_transient.py` | Debug transient analysis issues |
| `check_units.py` | Debug PySpice unit validation |
| `cleanup_issues.py` | Clean up old issue entries |
| `compress_issues.py` | Compress issue log file |
| `debug_api_response.py` | Debug LLM API responses |
| `find_and_save_examples.py` | Find working circuit examples |
| `find_examples.py` | Find circuit examples |
| `find_pulse_source.py` | Find pulse source patterns |
| `find_working_models.py` | Test which LLM models work |
| `fix_duplicate_declaration.py` | Fix duplicate declaration errors |
| `fix_empty_response.py` | Fix empty LLM responses |
| `fix_issues_status.py` | Update issue statuses |
| `fix_manual_issues.py` | Apply manual fixes |
| `group_issues.py` | Group issues by category |
| `mark_resolved.py` | Mark issues as resolved |
| `quick_test.py` | Quick circuit test |
| `standalone_test.py` | Standalone circuit simulation test |

**Note:** Some debug files are still in the root:
- `benchmark_rc_circuit.py` - Benchmark RC circuit performance
- `check_version.py` - Check library versions
- `verify_setup.py` - Verify setup is correct

---

## Test Files (DELETED)

All `test_*.py` files have been removed as they were temporary/one-time tests. If you need to re-create tests, see the archived documentation in `docs/archive/`.

---

## Documentation Files

### Root Documentation (Active)

| File | Purpose |
|------|---------|
| **README.md** | Main application documentation |
| **RALPH_README.md** | Ralph Fixer system documentation |
| **LLM_FIXES.md** | Recent LLM code fixes (2026-02-22) |
| **FILE_STRUCTURE.md** | This file |
| **DEBUGGING_SETUP.md** | VS Code debugging setup guide (NEW) |
| **DEBUG_REFERENCE.md** | VS Code debugging quick reference |

### Archived Documentation

All historical documentation is in `docs/archive/`:
- Fix progress reports
- Testing guides
- API configuration guides
- Troubleshooting guides
- Implementation notes

### API/Ollama Guides

API and Ollama-specific guides are in `docs/guides/`:
- OLLAMA_CLOUD_GUIDE.md
- OLLAMA_CLOUD_TROUBLESHOOTING.md
- OLLAMA_GUIDE.md
- OLLAMA_NATIVE_API.md
- OLLAMA_UPDATE.md

---

## Running the Application

### Minimal Setup (Streamlit app only)
```bash
cd C:\Users\augus\.openclaw\workspace\llm-sim-poc
conda activate pyspice
streamlit run app.py
```

### With Ralph Fixer
```bash
cd C:\Users\augus\.openclaw\workspace\llm-sim-poc
conda activate pyspice
streamlit run app.py
# Ralph Fixer available in app sidebar
```

### Using Debug Scripts
```bash
cd C:\Users\augus\.openclaw\workspace\llm-sim-poc\debug
conda activate pyspice
python debug\check_issues.py
```

---

## Dependencies

Required files import from each other in this order:

```
sim_config.py
    ↓
unit_validator.py
    ↓
circuit_builder.py ← imports both
    ↓
llm_orchestrator.py
    ↓
error_handler.py
    ↓
issue_logger.py
    ↓
app.py ← imports all above
    ↓
ralph_fixer.py ← uses circuit_builder, error_handler, issue_logger
    ↓
ralph_tester.py ← uses ralph_fixer
```

---

## File Sizes Summary

| Category | Files | Total Size |
|----------|-------|------------|
| Core App | 7 files | ~84 KB |
| Ralph System | 3 files | ~60 KB |
| Debug Scripts | 24 files | ~88 KB |
| Total Python | 34 files | ~232 KB |

---

## Maintenance Notes

- **Core files** should only be modified with careful testing
- **Debug scripts** can be freely modified or deleted
- **Test files** can be created as needed and deleted after use
- **Documentation** should be kept up-to-date with code changes

---

**Last Updated:** 2026-02-22
**Project:** LLM-PSPICE (Circuit Simulator with LLM Integration)
**Location:** `C:\Users\augus\.openclaw\workspace\llm-sim-poc`