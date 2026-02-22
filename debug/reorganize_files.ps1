# File Reorganization Script for llm-sim-poc
# Run this script to organize the project files

$ErrorActionPreference = "Continue"

# Function to move file with suppression
function MoveFile {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (Test-Path $Source) {
        Move-Item -Path $Source -Destination $Destination -Force
        Write-Host "Moved: $Source -> $Destination"
    } else {
        Write-Host "Not found: $Source"
    }
}

write-host "================================" -ForegroundColor Cyan
write-host "ORGANIZING MD FILES" -ForegroundColor Cyan
write-host "================================" -ForegroundColor Cyan
write-host ""

# === MOVE TO DOCS/ARCHIVE/ ===
write-host "Moving historical documentation to docs/archive/..." -ForegroundColor Yellow
write-host ""

$archiveFiles = @(
    "AC_ANALYSIS_FIX_COMPLETE.md",
    "API_KEY_PERSISTENCE.md",
    "BENCHMARK_README.md",
    "BUGFIX_RESPONSE_DUPLICATION.md",
    "CONDA_QUICK_START.md",
    "COORDINATION_MESSAGE.md",
    "DATA_STORAGE_CONFIGURATION.md",
    "DC_TO_PULSE_FIX.md",
    "DUPLICATE_DECLARATION_FIX.md",
    "DUPLICATE_FIX.md",
    "EMPTY_RESPONSE_FIX.md",
    "FINAL_STATUS.md",
    "FINAL_TEST_RESULTS.md",
    "FIX_INSTRUCTIONS.md",
    "get_api_key_website.md",
    "HOW_TO_RUN_TESTS.md",
    "IMPLEMENTATION_SUMMARY.md",
    "ISSUE_CATEGORIZATION.md",
    "LLM_PSPICE_PASPICE_COMPLETE.md",
    "MANUAL_TESTING_README.md",
    "MODEL_SELECTION_FIX_V2.md",
    "MULTI_PROVIDER.md",
    "NEW_UI_GUIDE.md",
    "PRO_FIX_GUIDE.md",
    "PULSE_SOURCE_FIX.md",
    "PYSPICE_SETUP_SUCCESS.md",
    "QUICK_FIX_DUPLICATE.md",
    "QUICK_FIX_OLLAMA.md",
    "QUICKSTART.md",
    "RALPH_CATEGORY_RESPONSE_DUPLICATION.md",
    "RALPH_MANUAL_FIXES_SUMMARY.md",
    "RALPH_TESTER_IMPLEMENTATION.md",
    "RALPH_TESTER_README.md",
    "RALPH_TESTER_UPDATE.md",
    "RALPH_TESTING_HONEST_TRUTH.md",
    "REFACTOR_DECOUPLING.md",
    "REPO_STATUS.md",
    "SIMULATION_ERROR_QUICK_REFERENCE.md",
    "SOLUTION_FOUND.md",
    "TEST_RESULTS_2026-02-19.md",
    "TEST_SUITE_README.md",
    "TODAYS_WORK.md",
    "VSCODE_QUICK_REFERENCE.md",
    "VSCODE_TESTING_GUIDE.md",
    "WORKING_EXAMPLE_EXPLANATION.md"
)

foreach ($file in $archiveFiles) {
    MoveFile -Source $file -Destination "docs\archive\$file"
}

# === MOVE OLLAMA GUIDES TO DOCS/GUIDES/ ===
write-host ""
write-host "Moving API/Ollama guides to docs/guides/..." -ForegroundColor Yellow
write-host ""

$guideFiles = @(
    "OLLAMA_CLOUD_GUIDE.md",
    "OLLAMA_CLOUD_TROUBLESHOOTING.md",
    "OLLAMA_GUIDE.md",
    "OLLAMA_NATIVE_API.md",
    "OLLAMA_UPDATE.md"
)

foreach ($file in $guideFiles) {
    MoveFile -Source $file -Destination "docs\guides\$file"
}

# === MOVE DEBUG/UTILITY SCRIPTS TO DEBUG/ ===
write-host ""
write-host "Moving debug/utility scripts to debug/..." -ForegroundColor Yellow
write-host ""

$debugFiles = @(
    "check_issues.py",
    "check_last_issue.py",
    "check_recent_issues.py",
    "check_transient.py",
    "check_units.py",
    "cleanup_issues.py",
    "compress_issues.py",
    "debug_api_response.py",
    "find_and_save_examples.py",
    "find_examples.py",
    "find_pulse_source.py",
    "find_working_models.py",
    "fix_duplicate_declaration.py",
    "fix_empty_response.py",
    "fix_issues_status.py",
    "fix_manual_issues.py",
    "group_issues.py",
    "mark_resolved.py",
    "quick_test.py",
    "standalone_test.py"
)

foreach ($file in $debugFiles) {
    MoveFile -Source $file -Destination "debug\$file"
}

# === DELETE TEST FILES ===
write-host ""
write-host "Deleting temporary test files..." -ForegroundColor Yellow
write-host ""

$testFiles = @(
    "test_api_configs.py",
    "test_benchmark.py",
    "test_both_models.py",
    "test_cloud_models.py",
    "test_dc_to_pulse_conversion.py",
    "test_debug_code.py",
    "test_error_handler.py",
    "test_find_u_cm_error.py",
    "test_improved_prompt.py",
    "test_integration.py",
    "test_like_streamlit.py",
    "test_like_streamlit_simulation.py",
    "test_llm_direct.py",
    "test_multiple_models.py",
    "test_native_api.py",
    "test_new_api_key.py",
    "test_ngspice.py",
    "test_ollama_cloud.py",
    "test_ollama_performance.py",
    "test_pyspice_simple.py",
    "test_ralph.py",
    "test_ralph_cloud.py",
    "test_ralph_quick.py",
    "test_rc_ac.py",
    "test_rc_pulse.py",
    "test_rc_pulse_final.py",
    "test_rc_pulse_working.py",
    "test_rc_uic.py",
    "test_rc_uic2.py",
    "test_rc_with_ic.py",
    "test_setup.py",
    "test_simple.py",
    "test_simple_circuit.py",
    "test_simple_rc.py",
    "test_simple_rc_clean.py",
    "test_streamlit_integration.py",
    "test_summary.py"
)

foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force
        Write-Host "Deleted: $file"
    }
}

write-host ""
write-host "================================" -ForegroundColor Green
write-host "REORGANIZATION COMPLETE!" -ForegroundColor Green
write-host "================================" -ForegroundColor Green
write-host ""
write-host "Files moved to:"
write-host "  - docs/archive/      (historical docs)"
write-host "  - docs/guides/       (API/Ollama guides)"
write-host "  - debug/             (debug/util scripts)"
write-host ""
write-host "Test files deleted:"
write-host "  - All test_*.py files removed"
write-host ""