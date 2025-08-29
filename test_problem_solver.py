#!/usr/bin/env python3
"""
Test script to verify problem_solver_claude_code.py works with both Python and Java
"""

import subprocess
import sys
import os

def test_python():
    """Test fixing a Python program"""
    print("Testing Python program fixing...")
    cmd = [
        "python3", "experiments_claude_code/problem_solver_claude_code.py",
        "--buggy-program-folder", "/home/ubuntu/QuixBugs-bench/python_programs",
        "--fixed-program-folder", "/home/ubuntu/QuixBugs-bench/test_fixed_python",
        "--program-name", "gcd",
        "--language", "python"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Python test result: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def test_java():
    """Test fixing a Java program"""
    print("\nTesting Java program fixing...")
    cmd = [
        "python3", "experiments_claude_code/problem_solver_claude_code.py",
        "--buggy-program-folder", "/home/ubuntu/QuixBugs-bench/java_programs",
        "--fixed-program-folder", "/home/ubuntu/QuixBugs-bench/test_fixed_java",
        "--program-name", "gcd",  # Will be converted to uppercase GCD
        "--language", "java"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Java test result: {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def main():
    # Check if ANTHROPIC_API_KEY is set
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY environment variable is not set")
        print("Please set it before running tests")
        return 1
    
    python_success = test_python()
    java_success = test_java()
    
    print("\n" + "="*50)
    print("Test Summary:")
    print(f"  Python: {'✓ PASSED' if python_success else '✗ FAILED'}")
    print(f"  Java:   {'✓ PASSED' if java_success else '✗ FAILED'}")
    
    return 0 if (python_success and java_success) else 1

if __name__ == "__main__":
    sys.exit(main())