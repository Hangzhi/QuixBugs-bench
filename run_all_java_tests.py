#!/usr/bin/env python3
"""
Test runner script that executes all Java tests using Gradle.
Can test both buggy and correct versions of programs from specified folders.
"""

import subprocess
import json
import sys
from datetime import datetime
import argparse
import difflib
import os
import re
import shutil
from pathlib import Path

# List of all programs to test (converted to uppercase for Java)
PROGRAMS = [
    "BITCOUNT",
    "BREADTH_FIRST_SEARCH",
    "BUCKETSORT",
    "DEPTH_FIRST_SEARCH",
    "DETECT_CYCLE",
    "FIND_FIRST_IN_SORTED",
    "FIND_IN_SORTED",
    "FLATTEN",
    "GCD",
    "GET_FACTORS",
    "HANOI",
    "IS_VALID_PARENTHESIZATION",
    "KHEAPSORT",
    "KNAPSACK",
    "KTH",
    "LCS_LENGTH",
    "LEVENSHTEIN",
    "LIS",
    "LONGEST_COMMON_SUBSEQUENCE",
    "MAX_SUBLIST_SUM",
    "MERGESORT",
    "MINIMUM_SPANNING_TREE",
    "NEXT_PALINDROME",
    "NEXT_PERMUTATION",
    "PASCAL",
    "POSSIBLE_CHANGE",
    "POWERSET",
    "QUICKSORT",
    "REVERSE_LINKED_LIST",
    "RPN_EVAL",
    "SHORTEST_PATH_LENGTH",
    "SHORTEST_PATH_LENGTHS",
    "SHORTEST_PATHS",
    "SHUNTING_YARD",
    "SIEVE",
    "SQRT",
    "SUBSEQUENCES",
    "TO_BASE",
    "TOPOLOGICAL_ORDERING",
    "WRAP"
]

def calculate_diff_lines(program_name, program_folder):
    """Calculate number of different lines between tested program and buggy version."""
    try:
        # Compare against buggy version (not correct version) for fixed programs
        original_program_path = f"/tmp/java_programs/{program_name}.java"
        
        # Path to tested version
        if program_folder:
            # Handle both / and . separators
            folder_path = program_folder.replace('.', '/')
            tested_path = f"{folder_path}/{program_name}.java"
        else:
            # Default to buggy java_programs
            tested_path = f"java_programs/{program_name}.java"
        
        # Read both files
        if not os.path.exists(original_program_path) or not os.path.exists(tested_path):
            return -1
            
        with open(original_program_path, 'r') as f:
            original_lines = [line.rstrip() for line in f.readlines()]
        
        with open(tested_path, 'r') as f:
            tested_lines = [line.rstrip() for line in f.readlines()]
        
        # Filter out package declarations and empty lines for comparison
        def filter_lines(lines):
            filtered = []
            for line in lines:
                stripped = line.strip()
                # Skip empty lines
                if not stripped:
                    continue
                # Skip package declarations (handles different package names)
                if stripped.startswith('package ') and stripped.endswith(';'):
                    continue
                filtered.append(line)
            return filtered
        
        # Filter both sets of lines
        original_filtered = filter_lines(original_lines)
        tested_filtered = filter_lines(tested_lines)
        
        # Use SequenceMatcher to find actual changes
        matcher = difflib.SequenceMatcher(None, original_filtered, tested_filtered)
        
        changed_blocks = 0
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                changed_blocks += max(i2 - i1, j2 - j1)
            elif tag == 'delete':
                changed_blocks += i2 - i1
            elif tag == 'insert':
                changed_blocks += j2 - j1
        
        return changed_blocks
        
    except Exception:
        return -1

def parse_html_report(gradle_task):
    """Parse the HTML test report to get test counts."""
    report_path = f"/home/ubuntu/QuixBugs-bench/build/reports/tests/{gradle_task}/index.html"
    return parse_html_report_from_path(report_path)

def parse_html_report_from_path(report_path):
    """Parse HTML test report from a specific path."""
    try:
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                content = f.read()
                
            # Parse test counts from HTML
            # Look for: <div class="counter">X</div><p>tests</p>
            tests_match = re.search(r'<div class="counter">(\d+)</div>\s*<p>tests</p>', content)
            failures_match = re.search(r'<div class="counter">(\d+)</div>\s*<p>failures</p>', content)
            
            if tests_match:
                total = int(tests_match.group(1))
                failed = int(failures_match.group(1)) if failures_match else 0
                passed = total - failed
                return passed, failed, total > 0
        
    except Exception:
        pass
    
    return 0, 0, False

def temporarily_move_conflicting_folders(target_folder):
    """Move conflicting folders to /tmp to avoid duplicate class definitions."""
    moved_folders = []
    experiments_path = Path("/home/ubuntu/QuixBugs-bench/experiments_claude_code")
    java_programs_path = Path("/home/ubuntu/QuixBugs-bench/java_programs")
    
    # Convert target_folder to absolute path for comparison
    target_folder_abs = Path(target_folder).resolve() if target_folder else None
    
    # Create temp directories if they don't exist
    Path("/tmp/experiments_claude_code").mkdir(parents=True, exist_ok=True)
    
    # Move original java_programs folder if it exists (to avoid conflicts)
    if target_folder and "fixed_java_programs" in target_folder:
        if java_programs_path.exists():
            temp_java_programs = Path("/tmp/java_programs_backup")
            # Remove old backup if exists
            if temp_java_programs.exists():
                shutil.rmtree(temp_java_programs)
            # Move original java_programs to backup
            shutil.move(str(java_programs_path), str(temp_java_programs))
            moved_folders.append((str(java_programs_path), str(temp_java_programs)))
            print(f"  Moved original java_programs to /tmp")
    
    # Find all fixed_java_programs* folders in experiments_claude_code except the target
    if experiments_path.exists():
        for folder in experiments_path.glob("fixed_java_programs*"):
            # Don't move the folder we're testing
            if not target_folder_abs or folder.resolve() != target_folder_abs:
                if folder.is_dir():
                    temp_path = Path("/tmp/experiments_claude_code") / folder.name
                    if folder.exists():
                        shutil.move(str(folder), str(temp_path))
                        moved_folders.append((str(folder), str(temp_path)))
                        print(f"  Temporarily moved: {folder.name}")
    
    if target_folder and "fixed_java_programs" in target_folder:
        print(f"  Using fixed programs from: {target_folder}")
    
    return moved_folders

def restore_moved_folders(moved_folders):
    """Restore folders that were temporarily moved."""
    for original_path, temp_path in moved_folders:
        if Path(temp_path).exists():
            # Simply move back from temp location
            shutil.move(temp_path, original_path)
            print(f"  Restored: {Path(original_path).name}")

def run_fixed_program_test(program_name, program_folder, timeout=10):
    """Run tests for fixed programs using root gradle project."""
    
    # Verify the program file exists
    source_path = Path(program_folder) / f"{program_name}.java"
    if not source_path.exists():
        return {
            "program": program_name,
            "status": "ERROR",
            "passed": 0,
            "skipped": 0,
            "failed": 0,
            "return_code": -1,
            "error": "Program file not found",
            "command": "N/A",
            "diff_line_count": -1,
            "gradle_task": "test"
        }
    
    try:
        # Run gradle test directly - gradle will compile from the fixed_java_programs folder
        gradle_task = "test"
        test_class = f"java_testcases.junit.{program_name}_TEST"
        cmd = ["gradle", gradle_task, "--tests", test_class, "--rerun-tasks"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/home/ubuntu/QuixBugs-bench"
        )
        
        output = result.stdout + result.stderr
        
        # Parse results
        status = "UNKNOWN"
        passed = failed = skipped = 0
        
        if "BUILD SUCCESSFUL" in output:
            # Parse HTML report from root project
            passed, failed, tests_ran = parse_html_report(gradle_task)
            
            if tests_ran:
                status = "PASSED" if failed == 0 else "FAILED"
            else:
                status = "NO_TESTS"
        elif "BUILD FAILED" in output:
            # Parse HTML report even for failed builds
            passed, failed, tests_ran = parse_html_report(gradle_task)
            
            if tests_ran:
                status = "FAILED"
            else:
                if "Compilation failed" in output or "error: " in output.lower():
                    status = "COMPILATION_ERROR"
                else:
                    status = "FAILED"
        
        # Calculate diff line count
        diff_count = calculate_diff_lines(program_name, program_folder)
        
        return {
            "program": program_name,
            "status": status,
            "passed": passed,
            "skipped": skipped,
            "failed": failed,
            "return_code": result.returncode,
            "command": " ".join(cmd),
            "diff_line_count": diff_count,
            "gradle_task": gradle_task
        }
        
    except subprocess.TimeoutExpired:
        diff_count = calculate_diff_lines(program_name, program_folder)
        return {
            "program": program_name,
            "status": "TIMEOUT",
            "passed": 0,
            "skipped": 0,
            "failed": 0,
            "return_code": -1,
            "command": " ".join(cmd) if 'cmd' in locals() else "N/A",
            "diff_line_count": diff_count,
            "gradle_task": "test"
        }
    except Exception as e:
        diff_count = calculate_diff_lines(program_name, program_folder)
        return {
            "program": program_name,
            "status": "ERROR",
            "passed": 0,
            "skipped": 0,
            "failed": 0,
            "return_code": -1,
            "error": str(e),
            "command": " ".join(cmd) if 'cmd' in locals() else "N/A",
            "diff_line_count": diff_count,
            "gradle_task": "test"
        }

def run_test(program_name, program_folder=None, timeout=10):
    """Run gradle test for a specific program and return the results."""
    
    # Check if this is a fixed program folder
    is_fixed_folder = program_folder and "fixed_java_programs" in program_folder.lower()
    
    if is_fixed_folder:
        # Use separate test project for fixed programs
        return run_fixed_program_test(program_name, program_folder, timeout)
    
    # Determine which gradle task to use based on the program folder
    if program_folder and "correct" in program_folder.lower():
        # Testing correct programs - use crtTest task
        gradle_task = "crtTest"
        test_class = f"java_testcases.junit.crt_program.{program_name}_TEST"
    else:
        # Testing buggy programs - use test task
        gradle_task = "test"
        test_class = f"java_testcases.junit.{program_name}_TEST"
    
    cmd = ["gradle", gradle_task, "--tests", test_class, "--rerun-tasks"]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/home/ubuntu/QuixBugs-bench"
        )
        
        output = result.stdout + result.stderr
        
        # Parse Gradle output for test results
        status = "UNKNOWN"
        passed = failed = skipped = 0
        
        # Look for BUILD SUCCESSFUL or BUILD FAILED
        if "BUILD SUCCESSFUL" in output:
            # Parse HTML report for actual test counts
            passed, failed, tests_ran = parse_html_report(gradle_task)
            
            if tests_ran:
                status = "PASSED" if failed == 0 else "FAILED"
            else:
                status = "NO_TESTS"
        elif "BUILD FAILED" in output:
            # Parse HTML report even for failed builds
            passed, failed, tests_ran = parse_html_report(gradle_task)
            
            if tests_ran:
                status = "FAILED"
            else:
                # Check for compilation errors
                if "Compilation failed" in output or "error: " in output.lower():
                    status = "COMPILATION_ERROR"
                else:
                    status = "FAILED"
        
        # Look for skipped tests
        match = re.search(r'(\d+) skipped', output)
        if match:
            skipped = int(match.group(1))
        
        # Calculate diff line count
        diff_count = calculate_diff_lines(program_name, program_folder)
        
        return {
            "program": program_name,
            "status": status,
            "passed": passed,
            "skipped": skipped,
            "failed": failed,
            "return_code": result.returncode,
            "command": " ".join(cmd),
            "diff_line_count": diff_count,
            "gradle_task": gradle_task
        }
        
    except subprocess.TimeoutExpired:
        diff_count = calculate_diff_lines(program_name, program_folder)
        return {
            "program": program_name,
            "status": "TIMEOUT",
            "passed": 0,
            "skipped": 0,
            "failed": 0,
            "return_code": -1,
            "command": " ".join(cmd),
            "diff_line_count": diff_count,
            "gradle_task": gradle_task
        }
    except Exception as e:
        diff_count = calculate_diff_lines(program_name, program_folder)
        return {
            "program": program_name,
            "status": "ERROR",
            "passed": 0,
            "skipped": 0,
            "failed": 0,
            "return_code": -1,
            "error": str(e),
            "command": " ".join(cmd),
            "diff_line_count": diff_count,
            "gradle_task": gradle_task if 'gradle_task' in locals() else "unknown"
        }

def main():
    parser = argparse.ArgumentParser(description="Run all QuixBugs Java tests using Gradle")
    parser.add_argument("--program-folder", type=str,
                       help="Specify the folder containing programs to test (e.g., 'java_programs' or 'correct_java_programs')")
    parser.add_argument("--output", type=str, default="test_results.json",
                       help="Output file for test results (default: test_results.json)")
    parser.add_argument("--timeout", type=int, default=10,
                       help="Timeout in seconds for each test (default: 10)")
    parser.add_argument("--programs", type=str, nargs='+',
                       help="Specific programs to test (default: all)")
    
    args = parser.parse_args()
    
    # Check if we're testing fixed programs
    is_fixed_folder = args.program_folder and "fixed_java_programs" in args.program_folder.lower()
    
    # Move folders ONCE before all tests if testing fixed programs
    moved_folders = []
    if is_fixed_folder:
        print("Preparing test environment...")
        moved_folders = temporarily_move_conflicting_folders(args.program_folder)
    
    # Convert program names to uppercase if specified
    if args.programs:
        programs_to_test = [p.upper() for p in args.programs]
    else:
        programs_to_test = PROGRAMS
    
    # Validate program names
    invalid_programs = [p for p in programs_to_test if p not in PROGRAMS]
    if invalid_programs:
        print(f"Warning: Invalid program names will be skipped: {invalid_programs}")
        programs_to_test = [p for p in programs_to_test if p in PROGRAMS]
    
    # Determine output file path
    output_file = args.output
    
    # Create timestamped file in program folder if output not explicitly provided
    if args.program_folder and args.output == "test_results.json":
        folder_path = args.program_folder.replace('.', '/')
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        output_file = f"{folder_path}/test_results_{timestamp}.json"
    
    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "program_folder": args.program_folder or "java_programs",
            "timeout": args.timeout,
            "total_programs": len(programs_to_test)
        },
        "results": []
    }
    
    print(f"Running Java tests for {len(programs_to_test)} programs...")
    print(f"Configuration: folder={args.program_folder or 'java_programs'}, timeout={args.timeout}s")
    print("-" * 60)
    
    # Statistics
    passed_count = 0
    failed_count = 0
    error_count = 0
    timeout_count = 0
    no_tests_count = 0
    
    for i, program in enumerate(programs_to_test, 1):
        print(f"[{i}/{len(programs_to_test)}] Testing {program}...", end=" ")
        
        result = run_test(
            program,
            program_folder=args.program_folder,
            timeout=args.timeout
        )
        
        results["results"].append(result)
        
        # Update statistics
        if result["status"] == "PASSED":
            passed_count += 1
            print(f"✓ PASSED ({result['passed']} tests)")
        elif result["status"] == "FAILED":
            failed_count += 1
            print(f"✗ FAILED ({result['failed']} failed, {result['passed']} passed)")
        elif result["status"] == "TIMEOUT":
            timeout_count += 1
            print("⏱ TIMEOUT")
        elif result["status"] == "NO_TESTS":
            no_tests_count += 1
            print("⚠ NO TESTS RAN")
        else:
            error_count += 1
            print(f"⚠ {result['status']}")
    
    # Add summary statistics
    results["summary"] = {
        "passed": passed_count,
        "failed": failed_count,
        "errors": error_count,
        "timeouts": timeout_count,
        "no_tests": no_tests_count,
        "total": len(programs_to_test)
    }
    
    # Save results to file
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("-" * 60)
    print(f"Test run complete! Results saved to {output_file}")
    print(f"\nSummary:")
    print(f"  ✓ Passed:   {passed_count}/{len(programs_to_test)}")
    print(f"  ✗ Failed:   {failed_count}/{len(programs_to_test)}")
    print(f"  ⚠ Errors:   {error_count}/{len(programs_to_test)}")
    print(f"  ⏱ Timeouts:  {timeout_count}/{len(programs_to_test)}")
    print(f"  ⊘ No Tests: {no_tests_count}/{len(programs_to_test)}")
    
    # Restore folders ONCE after all tests if we moved them
    if moved_folders:
        print("\nRestoring original folders...")
        restore_moved_folders(moved_folders)
    
    # Return non-zero exit code if there were failures
    sys.exit(0 if failed_count == 0 and error_count == 0 and timeout_count == 0 else 1)

if __name__ == "__main__":
    main()