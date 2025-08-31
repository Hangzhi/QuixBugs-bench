# QuixBugs Benchmark 

## LLM Agent Benchmark

**Original Dataset** https://github.com/jkoppel/QuixBugs

This repository includes tools for benchmarking LLM agents (like Claude Code) on program repair tasks. The benchmark suite supports both **Python and Java** programs and allows you to:

- **Fix programs** using LLM agents with minimal one-line changes
- **Run automated testing** on fixed programs  
- **Score results** based on test success and code change minimality
- **Compare performance** across different models and approaches

**Latest Results:** 
- **Python:** Claude Code achieved **86.5 ± 2% success rate** with minimal one-line fixes
  - [Agent Log](experiments_claude_code/fixed_python_programs/agent_log_claude.json)
  - [Run1 - Run5](experiments_claude_code/fixed_python_programs/)
- **Java:** Claude Code achieved **75.0% success rate** (30/40 programs) with minimal one-line fixes
  - [Agent Log](experiments_claude_code/fixed_java_programs/agent_log_claude.json)
  - [Test Results (Scored)](experiments_claude_code/fixed_java_programs/test_results_2025_08_30_075919_scored.json)

**Quick Start - Python:**
```bash
python3 experiments_claude_code/orchestrator_claude_code.py && python3 run_all_tests.py --program-folder experiments_claude_code.fixed_python_programs && python3 test_result_scorer.py experiments_claude_code/fixed_python_programs/test_results_*.json
```

**Quick Start - Java:**
```bash
python3 experiments_claude_code/orchestrator_claude_code.py --language java && python3 run_all_java_tests.py --program-folder experiments_claude_code/fixed_java_programs && python3 test_result_scorer.py experiments_claude_code/fixed_java_programs/test_results_*.json
```

## LLM Agent QuixBugs Benchmarking Tools

### 1. problem_solver_claude_code.py
Fix a single program using Claude Code. Supports both Python and Java.

**Python Example:**
```bash
python3 experiments_claude_code/problem_solver_claude_code.py \
    --buggy-program-folder python_programs \
    --fixed-program-folder experiments_claude_code/fixed_python_programs \
    --program-name bitcount \
    --language python
```

**Java Example:**
```bash
python3 experiments_claude_code/problem_solver_claude_code.py \
    --buggy-program-folder java_programs \
    --fixed-program-folder experiments_claude_code/fixed_java_programs \
    --program-name BITCOUNT \
    --language java
```

### 2. orchestrator_claude_code.py
Fix all 40 programs automatically with progress tracking (resumable). Supports both languages.

**Python:**
```bash
python3 experiments_claude_code/orchestrator_claude_code.py --language python
```

**Java:**
```bash
python3 experiments_claude_code/orchestrator_claude_code.py --language java
```

### 3. run_all_tests.py (Python)
Test fixed Python programs and generate results with diff analysis.
```bash
python3 run_all_python_tests.py --program-folder experiments_claude_code.fixed_python_programs
```

### 4. run_all_java_tests.py (Java)
Test fixed Java programs using Gradle. Features:
- Automatic compilation and testing with JUnit
- Support for buggy, correct, and fixed program versions
- HTML test report parsing for accurate test counts
- Diff analysis against correct versions
- Handles package declarations and dependencies

**Test Fixed Java Programs:**
```bash
python3 run_all_java_tests.py --program-folder experiments_claude_code/fixed_java_programs
```

**Test Specific Programs:**
```bash
python3 run_all_java_tests.py --programs BITCOUNT GCD QUICKSORT --program-folder experiments_claude_code/fixed_java_programs
```

**Options:**
- `--program-folder`: Folder containing programs to test
- `--programs`: Specific programs to test (default: all 40)
- `--timeout`: Test timeout in seconds (default: 10)
- `--output`: Output JSON file path

### 5. test_result_scorer.py
Score results based on: tests pass + exactly 1 line changed. Works for both Python and Java results.
```bash
python3 test_result_scorer.py experiments_claude_code/fixed_python_programs/test_results_2025_08_30_081207.json
# or
python3 test_result_scorer.py experiments_claude_code/fixed_java_programs/test_results_2025_08_30_073722.json
```

### Complete Workflow Examples

**Python Workflow:**
```bash
# 1. Fix all Python programs
python3 experiments_claude_code/orchestrator_claude_code.py --language python

# 2. Test the fixed programs
python3 run_all_tests.py --program-folder experiments_claude_code.fixed_python_programs

# 3. Score the results
python3 test_result_scorer.py experiments_claude_code/fixed_python_programs/test_results_*.json

# 4. View the scored results
cat experiments_claude_code/fixed_python_programs/test_results_*_scored.json
```

**Java Workflow:**
```bash
# 1. Fix all Java programs
python3 experiments_claude_code/orchestrator_claude_code.py --language java

# 2. Test the fixed programs
python3 run_all_java_tests.py --program-folder experiments_claude_code/fixed_java_programs

# 3. Score the results
python3 test_result_scorer.py experiments_claude_code/fixed_java_programs/test_results_*.json

# 4. View the scored results
cat experiments_claude_code/fixed_java_programs/test_results_*_scored.json
```

## Original Benchmark
For detailed information about the original QuixBugs benchmark, test usage, and program structure, see the [original QuixBugs repository](https://github.com/jkoppel/QuixBugs).
