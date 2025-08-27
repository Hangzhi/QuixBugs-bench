#!/usr/bin/env python3
"""
Test runner script that executes all tests and stores results in a file.
Can test both buggy and correct versions of programs from specified folders.
"""

import subprocess
import json
import sys
from datetime import datetime
import argparse

# List of all programs to test
PROGRAMS = [
    "bitcount",
    "breadth_first_search",
    "bucketsort", 
    "depth_first_search",
    "detect_cycle",
    "find_first_in_sorted",
    "find_in_sorted",
    "flatten",
    "gcd",
    "get_factors",
    "hanoi",
    "is_valid_parenthesization",
    "kheapsort",
    "knapsack",
    "kth",
    "lcs_length",
    "levenshtein",
    "lis",
    "longest_common_subsequence",
    "max_sublist_sum",
    "mergesort",
    "minimum_spanning_tree",
    "next_palindrome",
    "next_permutation",
    "pascal",
    "possible_change",
    "powerset",
    "quicksort",
    "reverse_linked_list",
    "rpn_eval",
    "shortest_path_length",
    "shortest_path_lengths",
    "shortest_paths",
    "shunting_yard",
    "sieve",
    "sqrt",
    "subsequences",
    "to_base",
    "topological_ordering",
    "wrap"
]

def run_test(program_name, correct=False, run_slow=False, program_folder=None, timeout=10):
    """Run pytest for a specific program and return the results."""
    
    cmd = ["pytest", f"python_testcases/test_{program_name}.py", 
           "-v", "--tb=short", f"--timeout={timeout}"]
    
    if correct:
        cmd.append("--correct")
    
    if run_slow:
        cmd.append("--runslow")
    
    if program_folder:
        cmd.extend(["--program-folder", program_folder])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout * 2  # Give some buffer for pytest timeout
        )
        
        # Parse the output to determine success/failure
        output = result.stdout + result.stderr
        
        # Check for various pytest result patterns
        if "FAILED" in output or "ERROR" in output:
            status = "FAILED"
        elif "passed" in output:
            if "failed" in output:
                status = "PARTIAL"
            else:
                status = "PASSED"
        elif "SKIPPED" in output:
            status = "SKIPPED"
        else:
            status = "UNKNOWN"
        
        # Extract test counts if possible
        import re
        # Look for different pytest output patterns
        passed = failed = skipped = 0
        
        # Pattern 1: "X failed, Y passed"
        match = re.search(r'(\d+) failed(?:, (\d+) passed)?', output)
        if match:
            failed = int(match.group(1))
            passed = int(match.group(2)) if match.group(2) else 0
        
        # Pattern 2: "X passed, Y failed"  
        match = re.search(r'(\d+) passed(?:, (\d+) failed)?', output)
        if match:
            passed = int(match.group(1))
            if match.group(2):
                failed = int(match.group(2))
        
        # Look for skipped tests
        match = re.search(r'(\d+) skipped', output)
        if match:
            skipped = int(match.group(1))
        
        # If no matches found, set to -1
        if passed == 0 and failed == 0 and skipped == 0 and "passed" not in output and "failed" not in output:
            passed = skipped = failed = -1
        
        return {
            "program": program_name,
            "status": status,
            "passed": passed,
            "skipped": skipped,
            "failed": failed,
            "return_code": result.returncode,
            "command": " ".join(cmd)
        }
        
    except subprocess.TimeoutExpired:
        return {
            "program": program_name,
            "status": "TIMEOUT",
            "passed": 0,
            "skipped": 0,
            "failed": 0,
            "return_code": -1,
            "command": " ".join(cmd)
        }
    except Exception as e:
        return {
            "program": program_name,
            "status": "ERROR",
            "passed": 0,
            "skipped": 0,
            "failed": 0,
            "return_code": -1,
            "error": str(e),
            "command": " ".join(cmd)
        }

def main():
    parser = argparse.ArgumentParser(description="Run all QuixBugs tests and save results")
    parser.add_argument("--correct", action="store_true", 
                       help="Test the correct version of programs")
    parser.add_argument("--runslow", action="store_true",
                       help="Include slow tests")
    parser.add_argument("--program-folder", type=str,
                       help="Specify the folder containing programs to test")
    parser.add_argument("--output", type=str, default="test_results.json",
                       help="Output file for test results (default: test_results.json)")
    parser.add_argument("--timeout", type=int, default=10,
                       help="Timeout in seconds for each test (default: 10)")
    parser.add_argument("--programs", type=str, nargs='+',
                       help="Specific programs to test (default: all)")
    
    args = parser.parse_args()
    
    programs_to_test = args.programs if args.programs else PROGRAMS
    
    # Validate program names
    invalid_programs = [p for p in programs_to_test if p not in PROGRAMS]
    if invalid_programs:
        print(f"Warning: Invalid program names will be skipped: {invalid_programs}")
        programs_to_test = [p for p in programs_to_test if p in PROGRAMS]
    
    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "correct_version": args.correct,
            "run_slow": args.runslow,
            "program_folder": args.program_folder or "default",
            "timeout": args.timeout,
            "total_programs": len(programs_to_test)
        },
        "results": []
    }
    
    print(f"Running tests for {len(programs_to_test)} programs...")
    print(f"Configuration: correct={args.correct}, run_slow={args.runslow}, "
          f"folder={args.program_folder or 'default'}, timeout={args.timeout}s")
    print("-" * 60)
    
    # Statistics
    passed_count = 0
    failed_count = 0
    error_count = 0
    timeout_count = 0
    
    for i, program in enumerate(programs_to_test, 1):
        print(f"[{i}/{len(programs_to_test)}] Testing {program}...", end=" ")
        
        result = run_test(
            program,
            correct=args.correct,
            run_slow=args.runslow,
            program_folder=args.program_folder,
            timeout=args.timeout
        )
        
        results["results"].append(result)
        
        # Update statistics
        if result["status"] == "PASSED":
            passed_count += 1
            print(f"✓ PASSED ({result['passed']} tests)")
        elif result["status"] == "FAILED" or result["status"] == "PARTIAL":
            failed_count += 1
            print(f"✗ FAILED ({result['failed']} failed, {result['passed']} passed)")
        elif result["status"] == "TIMEOUT":
            timeout_count += 1
            print("⏱ TIMEOUT")
        else:
            error_count += 1
            print(f"⚠ {result['status']}")
    
    # Add summary statistics
    results["summary"] = {
        "passed": passed_count,
        "failed": failed_count,
        "errors": error_count,
        "timeouts": timeout_count,
        "total": len(programs_to_test)
    }
    
    # Save results to file
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("-" * 60)
    print(f"Test run complete! Results saved to {args.output}")
    print(f"\nSummary:")
    print(f"  ✓ Passed:  {passed_count}/{len(programs_to_test)}")
    print(f"  ✗ Failed:  {failed_count}/{len(programs_to_test)}")
    print(f"  ⚠ Errors:  {error_count}/{len(programs_to_test)}")
    print(f"  ⏱ Timeouts: {timeout_count}/{len(programs_to_test)}")
    
    # Return non-zero exit code if there were failures
    sys.exit(0 if failed_count == 0 and error_count == 0 and timeout_count == 0 else 1)

if __name__ == "__main__":
    main()