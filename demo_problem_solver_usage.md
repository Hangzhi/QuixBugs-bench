# Problem Solver Claude Code - Language Support Demo

## Updated Features

The `problem_solver_claude_code.py` script now supports both **Python** and **Java** languages for fixing buggy programs.

## Usage Examples

### 1. Fixing a Python Program (existing functionality)

```bash
python3 experiments_claude_code/problem_solver_claude_code.py \
    --buggy-program-folder /home/ubuntu/QuixBugs-bench/python_programs \
    --fixed-program-folder /home/ubuntu/QuixBugs-bench/experiments_claude_code/fixed_python_programs \
    --program-name bitcount \
    --language python
```

**What happens:**
- Reads `python_programs/bitcount.py` (lowercase)
- Analyzes the buggy Python code
- Fixes exactly one line
- Writes fixed program to `fixed_python_programs/bitcount.py`

### 2. Fixing a Java Program (NEW functionality)

```bash
python3 experiments_claude_code/problem_solver_claude_code.py \
    --buggy-program-folder /home/ubuntu/QuixBugs-bench/java_programs \
    --fixed-program-folder /home/ubuntu/QuixBugs-bench/experiments_claude_code/fixed_java_programs \
    --program-name knapsack \
    --language java
```

**What happens:**
- Automatically converts program name to uppercase: `knapsack` → `KNAPSACK`
- Reads `java_programs/KNAPSACK.java`
- Analyzes the buggy Java code
- Fixes exactly one line
- Writes fixed program to `fixed_java_programs/KNAPSACK.java`

## Key Changes Made

### 1. **Language Parameter**
- Added `--language` parameter with choices: `python` or `java`
- Default is `python` for backward compatibility

### 2. **Automatic Name Conversion**
- Python: keeps lowercase names (`bitcount.py`)
- Java: converts to uppercase names (`KNAPSACK.java`)

### 3. **Language-Specific Prompts**
- Python prompt asks to fix `.py` files
- Java prompt asks to fix `.java` files
- Both maintain the same requirements (one-line fix, minimal change)

### 4. **File Extension Handling**
- Automatically uses `.py` for Python
- Automatically uses `.java` for Java

## Command Line Options

```
--model-name          Claude model to use (default: claude-3-7-sonnet-latest)
--buggy-program-folder  Path to folder with buggy programs (required)
--fixed-program-folder  Path to save fixed programs (required)
--program-name        Program name without extension (required)
--language           Language: python or java (default: python)
```

## Examples for Multiple Programs

### Fix multiple Python programs:
```bash
for prog in bitcount gcd quicksort; do
    python3 experiments_claude_code/problem_solver_claude_code.py \
        --buggy-program-folder python_programs \
        --fixed-program-folder fixed_python_programs \
        --program-name $prog \
        --language python
done
```

### Fix multiple Java programs:
```bash
for prog in knapsack gcd quicksort; do
    python3 experiments_claude_code/problem_solver_claude_code.py \
        --buggy-program-folder java_programs \
        --fixed-program-folder fixed_java_programs \
        --program-name $prog \
        --language java
done
```

## Testing Fixed Programs

### For Python:
```bash
python3 run_all_python_tests.py \
    --program-folder experiments_claude_code/fixed_python_programs \
    --programs bitcount gcd quicksort
```

### For Java:
```bash
python3 run_all_java_tests.py \
    --program-folder experiments_claude_code/fixed_java_programs \
    --programs KNAPSACK GCD QUICKSORT
```

## Notes

1. The script maintains backward compatibility - existing Python workflows work unchanged
2. Java program names are automatically converted to uppercase to match QuixBugs conventions
3. The agent log is saved to `agent_log_claude.json` in the fixed program folder
4. Both languages use the same one-line fix requirement for consistency