# Orchestrator Claude Code - Language Support

The updated `orchestrator_claude_code.py` now supports both Python and Java languages with separate progress tracking.

## Usage

### Python Programs (Default)
```bash
# Fix all Python programs
python3 experiments_claude_code/orchestrator_claude_code.py

# Or explicitly specify Python
python3 experiments_claude_code/orchestrator_claude_code.py --language python
```

### Java Programs
```bash
# Fix all Java programs
python3 experiments_claude_code/orchestrator_claude_code.py --language java
```

## Key Features

### 1. Language-Specific Progress Files
- **Python**: `orchestrator_python_progress.json`
- **Java**: `orchestrator_java_progress.json`

This allows you to run both languages independently without interfering with each other's progress.

### 2. Language-Specific Test Counts
- **Python**: Uses `experiments_claude_code/python_test_counts_required.json`
- **Java**: Uses `java_test_counts_required.json`

### 3. Language-Specific Folders
- **Python**:
  - Buggy: `python_programs/`
  - Fixed: `experiments_claude_code/fixed_python_programs/`
  
- **Java**:
  - Buggy: `java_programs/`
  - Fixed: `experiments_claude_code/fixed_java_programs/`

## Progress Tracking

Each language maintains its own progress file:

```json
{
  "completed": ["bitcount", "gcd", "quicksort"],
  "failed": ["knapsack"],
  "language": "python",
  "timestamp": "2025-08-29T21:30:00"
}
```

## Resume Capability

The orchestrator automatically resumes from where it left off:

```bash
# Start fixing Java programs
python3 experiments_claude_code/orchestrator_claude_code.py --language java
# (Interrupt with Ctrl+C after a few programs)

# Resume later - will continue from where it stopped
python3 experiments_claude_code/orchestrator_claude_code.py --language java
```

## Complete Workflow

### For Python:
```bash
# 1. Fix all Python programs
python3 experiments_claude_code/orchestrator_claude_code.py --language python

# 2. Test the fixed programs
python3 run_all_python_tests.py \
    --program-folder experiments_claude_code.fixed_python_programs

# 3. Score the results
python3 test_result_scorer.py \
    experiments_claude_code/fixed_python_programs/test_results_*.json
```

### For Java:
```bash
# 1. Fix all Java programs
python3 experiments_claude_code/orchestrator_claude_code.py --language java

# 2. Test the fixed programs
python3 run_all_java_tests.py \
    --program-folder experiments_claude_code/fixed_java_programs

# 3. Analyze results
cat experiments_claude_code/fixed_java_programs/test_results_*.json
```

## Checking Progress

### View Python progress:
```bash
cat experiments_claude_code/orchestrator_python_progress.json | jq .
```

### View Java progress:
```bash
cat experiments_claude_code/orchestrator_java_progress.json | jq .
```

## Notes

1. **Name Conversion**: Java program names are automatically converted:
   - Stored as uppercase in `java_test_counts_required.json` (e.g., "KNAPSACK")
   - Converted to lowercase for processing (e.g., "knapsack")
   - Converted back to uppercase when saving (e.g., "KNAPSACK.java")

2. **Backward Compatibility**: The default language is Python, so existing workflows continue to work without modification.

3. **Independent Progress**: You can work on Python and Java programs simultaneously in different terminals without conflict.

4. **Interrupt Safety**: Use Ctrl+C to safely interrupt at any time. Progress is saved after each program.