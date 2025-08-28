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

See detailed usage instructions below.

---

The QuixBugs benchmark consists of 40 programs from the Quixey Challenge translated into both Python and Java. Each contains a one-line defect, along with passing (when possible) and failing testcases. Defects fall into one of 14 defect classes. Corrected Python programs are also supplied. Quixbugs is intended for investigating cross-language performance by _multi-lingual_ program repair tools. 

For more details, see the ["QuixBugs: A Multi-Lingual Program Repair Benchmark Set Based on the Quixey Challenge"](quixbugs.pdf). Researchers at KTH have run 5 repair systems on the Java version of Quixbugs programs, see ["A Comprehensive Study of Automatic Program Repair on the QuixBugs Benchmark"](http://arxiv.org/pdf/1805.03454).

# Background: Quixey Challenge
From 2011 to 2013, mobile app search startup Quixey ran a challenge in which programmers were given an implementation of a classic algorithm with a bug on a single line, and had one minute to supply a fix. Success entailed $100 and a possible interview. These programs were developed as challenges for humans by people unaware of program repair.

# Installation & Usage
Simply clone the repo. 

    git clone https://github.com/jkoppel/QuixBugs
    
The Java programs are already compiled (see `*.class` files in `java_programs`). Note the all java programs are in the same package called `java_programs`. The utility class `JavaDeserialization.java` requires you to download the external library Gson.

All Python is written in Python3.

To run both defective versions of a program against their tests, as well as the corrected Python version, use the test driver:

> python3 tester.py _program\_name_

Output is printed for visual comparison.

## Using JUnit tests

There are JUnit tests in the `java_testcases/junit` folder for the Java version. Running `TestsGenerator.java` can regenerate them if needed.

To run these tests, you can use [Gradle](https://gradle.org/) tasks provided by the `build.gradle` file. First, install Gradle. Then,

- `gradle test` can be used to run tests on the buggy programs (Runs JUnit tests from the `java_testcases/junit` folder);
- `gradle crtTest` can be used to run tests on the correct programs (Runs JUnit tests from the `java_testcases/junit/crt_program` folder).

It is also possible to run tests for a single program with the `--tests` option:

```bash
$ gradle test --tests KNAPSACK_TEST

> Task :test

java_testcases.junit.KNAPSACK_TEST > test_1 FAILED
    java.lang.AssertionError at KNAPSACK_TEST.java:14

java_testcases.junit.KNAPSACK_TEST > test_3 FAILED
    java.lang.AssertionError at KNAPSACK_TEST.java:26

java_testcases.junit.KNAPSACK_TEST > test_4 FAILED
    java.lang.AssertionError at KNAPSACK_TEST.java:32

java_testcases.junit.KNAPSACK_TEST > test_5 FAILED
    java.lang.AssertionError at KNAPSACK_TEST.java:38

java_testcases.junit.KNAPSACK_TEST > test_6 FAILED
    java.lang.AssertionError at KNAPSACK_TEST.java:44

java_testcases.junit.KNAPSACK_TEST > test_7 FAILED
    java.lang.AssertionError at KNAPSACK_TEST.java:50

10 tests completed, 6 failed
```

```bash
$ gradle crtTest --tests KNAPSACK_TEST

BUILD SUCCESSFUL in 4s
```

## Using pytest tests

For the Python version, there are [pytest](https://pytest.org/) tests for each program in the `python_testcases` folder. To run them, install pytest using `pip` and then, from the root of the repository, call `pytest` to run tests for a single program or target the whole directory to run every test inside it.

For detailed information about the original QuixBugs benchmark, test usage, and program structure, see the [original QuixBugs repository](https://github.com/jkoppel/QuixBugs).

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

```bash
pip install pytest
pytest python_testcases/test_quicksort.py
# Or
pytest python_testcases
```

Tests work for both buggy and correct versions of programs. The default test calls the buggy version, but there is a custom `--correct` flag that uses the correct version of a program.

```bash
pytest --correct python_testcases
```

Most of the tests run fast and finish in less than a second, but two tests are slow. The first one is the last test case of the `knapsack` program, and the second one is the fourth test case of the `levenshtein` program. The default behavior skips both these tests. For the `knapsack` test case, using the `--runslow` pytest option will include it in the running tests. However, the `levenshtein` test case is always skipped since it takes a long time to pass and is ignored by the JUnit tests as well.

```bash
$ pytest --correct --runslow python_testcases/test_knapsack.py

collected 10 items
python_testcases/test_knapsack.py ..........     [100%]

========== 10 passed in 240.97s (0:04:00) ========== 
```

```bash
$ pytest --correct python_testcases/test_knapsack.py

collected 10 items
python_testcases/test_knapsack.py ..........     [100%]

========== 9 passed, 1 skipped in 0.08s ========== 
```

Some tests, such as the `bitcount` ones, need a timeout. pytest itself doesn't have a timeout mechanism, but there is a [pytest-timeout](https://github.com/pytest-dev/pytest-timeout) plugin for it. Installing pytest-timeout adds additional options to the `pytest` CLI so, for example, to timeout `bitcount` tests after five seconds, you can do like this:

```bash
pip install pytest-timeout
pytest --timeout=5 python_testcases/test_bitcount.py
```
Make sure to check pytest-timeout's documentation to understand its caveats and how it handles timeouts on different systems.

There is also a [pytest-xdist](https://github.com/pytest-dev/pytest-xdist) plugin that runs tests in parallel and can be used similarly to the timeout plugin.

# Structure & Details

The root folder holds the test driver. It deserializes the JSON testcases for a selected program, then runs them against the defective versions located in java\_programs/ and python\_programs/. The exception is graph-based programs, for which the testcases are located in the same folder as the corresponding program (they are still run with the test driver in the same manner).

For reference, corrected versions of the Python programs are in correct\_python\_programs/.

Programs include:
- bitcount
- breadth\_first\_search\*
- bucketsort
- depth\_first\_search\*
- detect\_cycle\*
- find\_first\_in\_sorted
- find\_in\_sorted
- flatten
- gcd
- get\_factors
- hanoi
- is\_valid\_parenthesization
- kheapsort
- knapsack
- kth
- lcs\_length
- levenshtein
- lis
- longest\_common\_subsequence
- max\_sublist\_sum
- mergesort
- minimum\_spanning\_tree\*
- next\_palindrome
- next\_permutation
- pascal
- possible\_change
- powerset
- quicksort
- reverse\_linked\_list\*
- rpn\_eval
- shortest\_path\_length\*
- shortest\_path\_lengths\*
- shortest\_paths\*
- shunting\_yard
- sieve
- sqrt
- subsequences
- to\_base
- topological\_ordering\*
- wrap

\* - graph-based algorithm


# Authors
Contact Derrick Lin @drrckln, Angela Chen @angchen, or James Koppel @jkoppel for questions.
