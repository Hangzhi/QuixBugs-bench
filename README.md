# QuixBugs Benchmark [![CI Status](https://github.com/jkoppel/QuixBugs/actions/workflows/ci.yml/badge.svg)](https://github.com/jkoppel/QuixBugs/actions/workflows/ci.yml)

## LLM Agent Benchmark

This repository includes tools for benchmarking LLM agents (like Claude Code) on program repair tasks. The benchmark suite allows you to:

- **Fix programs** using LLM agents with minimal one-line changes
- **Run automated testing** on fixed programs
- **Score results** based on test success and code change minimality
- **Compare performance** across different models and approaches

**Latest Results:** Claude Code achieved **82.5% success rate** (33/40 programs) with minimal one-line fixes that pass all tests.

### Quick Start for LLM Benchmarking

1. **Fix a single program:**
   ```bash
   python3 experiments_claude_code/problem_solver_claude_code.py \
       --model-name claude-3-5-sonnet-latest \
       --buggy-program-folder python_programs \
       --fixed-program-folder experiments_claude_code/fixed_python_programs \
       --program-name bitcount
   ```

2. **Fix all programs automatically:**
   ```bash
   python3 experiments_claude_code/orchestrator_claude_code.py
   ```

3. **Test fixed programs:**
   ```bash
   python3 run_all_tests.py --program-folder experiments_claude_code.fixed_python_programs
   ```

4. **Score results:**
   ```bash
   python3 test_result_scorer.py experiments_claude_code/fixed_python_programs/test_results_*.json
   ```


## LLM Agent Benchmarking Tools

### 1. problem_solver_claude_code.py
Fix a single program using Claude Code.
```bash
python3 experiments_claude_code/problem_solver_claude_code.py \
    --buggy-program-folder python_programs \
    --fixed-program-folder experiments_claude_code/fixed_python_programs \
    --program-name bitcount
```

### 2. orchestrator_claude_code.py
Fix all 40 programs automatically with progress tracking (resumable).
```bash
python3 experiments_claude_code/orchestrator_claude_code.py
```

### 3. run_all_tests.py
Test fixed programs and generate results with diff analysis.
```bash
python3 run_all_tests.py --program-folder experiments_claude_code.fixed_python_programs
```

### 4. test_result_scorer.py
Score results based on: tests pass + exactly 1 line changed.
```bash
python3 test_result_scorer.py experiments_claude_code/fixed_python_programs/test_results_*.json
```

### Complete Workflow Example

```bash
# 1. Fix all programs
python3 experiments_claude_code/orchestrator_claude_code.py

# 2. Test the fixed programs
python3 run_all_tests.py --program-folder experiments_claude_code.fixed_python_programs

# 3. Score the results
python3 test_result_scorer.py experiments_claude_code/fixed_python_programs/test_results_*.json

# 4. View the scored results
cat experiments_claude_code/fixed_python_programs/test_results_*_scored.json
```

## Original Benchmark
For detailed information about the original QuixBugs benchmark, test usage, and program structure, see the [original QuixBugs repository](https://github.com/jkoppel/QuixBugs).
