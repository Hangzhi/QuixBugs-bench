#!/usr/bin/env python3
"""
QuixBugs Benchmark Tool for automated bug fixing using LLMs
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import difflib
import re
from typing import Dict, Any, Optional, List

# OpenAI and Anthropic client imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not installed. Install with: pip install openai")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True  
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: Anthropic library not installed. Install with: pip install anthropic")

# Available programs from QuixBugs
PROGRAMS = [
    "bitcount", "breadth_first_search", "bucketsort", "depth_first_search",
    "detect_cycle", "find_first_in_sorted", "find_in_sorted", "flatten",
    "gcd", "get_factors", "hanoi", "is_valid_parenthesization",
    "kheapsort", "knapsack", "kth", "lcs_length", "levenshtein", "lis",
    "longest_common_subsequence", "max_sublist_sum", "mergesort",
    "minimum_spanning_tree", "next_palindrome", "next_permutation",
    "pascal", "possible_change", "powerset", "quicksort",
    "reverse_linked_list", "rpn_eval", "shortest_path_length",
    "shortest_path_lengths", "shortest_paths", "shunting_yard",
    "sieve", "sqrt", "subsequences", "to_base", "topological_ordering", "wrap"
]

class ModelClient:
    """Base class for model clients"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class OpenAIClient(ModelClient):
    """OpenAI API client"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key)
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed")
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that fixes bugs in Python code. Return only the fixed code without any explanation or markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=2000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

class AnthropicClient(ModelClient):
    """Anthropic API client"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key)
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not installed")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0,
                system="You are a helpful assistant that fixes bugs in Python code. Return only the fixed code without any explanation or markdown formatting.",
                messages=[{"role": "user", "content": prompt}]
            )
            # Extract text from response
            content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            return content.strip()
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

def get_model_client(model_spec: str) -> ModelClient:
    """
    Create appropriate model client based on model specification
    Format: provider/model-name (e.g., openai/gpt-4, anthropic/claude-3-sonnet)
    """
    parts = model_spec.split('/')
    if len(parts) != 2:
        raise ValueError(f"Invalid model specification: {model_spec}. Use format: provider/model-name")
    
    provider, model_name = parts
    
    if provider.lower() == 'openai':
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return OpenAIClient(api_key, model_name)
    
    elif provider.lower() == 'anthropic':
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        return AnthropicClient(api_key, model_name)
    
    else:
        raise ValueError(f"Unknown provider: {provider}. Supported: openai, anthropic")

def extract_program_name(task_path: str) -> str:
    """Extract program name from task path"""
    filename = os.path.basename(task_path)
    if filename.endswith('.py'):
        filename = filename[:-3]
    return filename

def clean_code_response(response: str) -> str:
    """Clean the model response to extract just the code"""
    # Remove markdown code blocks
    response = re.sub(r'^```python\n', '', response, flags=re.MULTILINE)
    response = re.sub(r'^```\n', '', response, flags=re.MULTILINE)
    response = re.sub(r'\n```$', '', response, flags=re.MULTILINE)
    
    # Remove any leading/trailing whitespace
    response = response.strip()
    
    return response

def count_line_changes(original: str, fixed: str) -> int:
    """Count the number of lines that differ between two code files"""
    original_lines = original.splitlines()
    fixed_lines = fixed.splitlines()
    
    differ = difflib.unified_diff(original_lines, fixed_lines, lineterm='')
    
    changes = 0
    for line in differ:
        if line.startswith('+') and not line.startswith('+++'):
            changes += 1
        elif line.startswith('-') and not line.startswith('---'):
            changes += 1
    
    return changes // 2  # Divide by 2 because each change has both + and -

def setup_experiment_folder(model_name: str) -> tuple[Path, Path]:
    """Create experiment folder structure"""
    # Clean model name for folder
    safe_model_name = model_name.replace('/', '_').replace('-', '_')
    
    exp_folder = Path(f"experiments_{safe_model_name}")
    fixed_folder = exp_folder / "fixed_python_programs"
    
    exp_folder.mkdir(exist_ok=True)
    fixed_folder.mkdir(exist_ok=True)
    
    return exp_folder, fixed_folder

def fix_program(buggy_code: str, program_name: str, model_client: ModelClient) -> str:
    """Generate fixed version of buggy program using model"""
    
    prompt = f"""There is a buggy Python program below that has exactly ONE line with a defect. Please fix it by changing ONLY the buggy line.

Here is the buggy program:

{buggy_code}

Please return the complete fixed program with only the necessary one-line change to fix the bug. Do not add any comments or explanations, just return the fixed Python code."""

    fixed_code = model_client.generate(prompt)
    fixed_code = clean_code_response(fixed_code)
    
    return fixed_code

def run_tests_for_program(program_name: str, program_folder: str, timeout: int = 10) -> Dict[str, Any]:
    """Run tests for a specific program and return results"""
    
    cmd = [
        "pytest",
        f"python_testcases/test_{program_name}.py",
        "-v", "--tb=short",
        f"--timeout={timeout}",
        "--program-folder", program_folder
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout * 2
        )
        
        output = result.stdout + result.stderr
        
        # Determine status
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
        
        # Extract test counts
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
        
        return {
            "status": status,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "return_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "return_code": -1
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "return_code": -1,
            "error": str(e)
        }

def process_single_program(program_name: str, model_client: ModelClient, 
                         exp_folder: Path, fixed_folder: Path) -> Dict[str, Any]:
    """Process a single program: fix it, test it, and analyze the fix"""
    
    print(f"Processing {program_name}...")
    
    # Read buggy program
    buggy_path = f"python_programs/{program_name}.py"
    try:
        with open(buggy_path, 'r') as f:
            buggy_code = f.read()
    except FileNotFoundError:
        return {
            "program": program_name,
            "status": "ERROR",
            "error": f"Buggy program not found: {buggy_path}"
        }
    
    # Generate fix
    try:
        print(f"  Generating fix...")
        fixed_code = fix_program(buggy_code, program_name, model_client)
        
        # Save fixed program
        fixed_path = fixed_folder / f"{program_name}.py"
        with open(fixed_path, 'w') as f:
            f.write(fixed_code)
        
        print(f"  Fixed program saved to {fixed_path}")
        
    except Exception as e:
        return {
            "program": program_name,
            "status": "FIX_ERROR",
            "error": str(e)
        }
    
    # Run tests on fixed program
    print(f"  Running tests...")
    test_results = run_tests_for_program(
        program_name,
        f"experiments_{exp_folder.name.replace('experiments_', '')}/fixed_python_programs"
    )
    
    # Check if it's a one-line change
    line_changes = count_line_changes(buggy_code, fixed_code)
    is_one_line_change = (line_changes == 1)
    
    # Prepare result
    result = {
        "program": program_name,
        "fix_status": "SUCCESS",
        "test_status": test_results["status"],
        "tests_passed": test_results["passed"],
        "tests_failed": test_results["failed"],
        "tests_skipped": test_results["skipped"],
        "is_one_line_change": is_one_line_change,
        "line_changes": line_changes,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"  Test Status: {test_results['status']} (Passed: {test_results['passed']}, Failed: {test_results['failed']})")
    print(f"  One-line change: {is_one_line_change} (Changes: {line_changes})")
    
    return result

def main():
    parser = argparse.ArgumentParser(description="QuixBugs benchmark tool for automated bug fixing")
    parser.add_argument("--model", required=True, 
                       help="Model specification (e.g., openai/gpt-4, anthropic/claude-3-sonnet)")
    parser.add_argument("--task", required=True,
                       help="Path to buggy program or 'all' to process all programs")
    parser.add_argument("--timeout", type=int, default=10,
                       help="Test timeout in seconds (default: 10)")
    parser.add_argument("--output", help="Custom output file path")
    
    args = parser.parse_args()
    
    # Initialize model client
    try:
        model_client = get_model_client(args.model)
    except Exception as e:
        print(f"Error initializing model client: {e}")
        sys.exit(1)
    
    # Setup experiment folders
    safe_model_name = args.model.replace('/', '_').replace('-', '_')
    exp_folder, fixed_folder = setup_experiment_folder(safe_model_name)
    
    # Determine output file
    output_file = args.output or (exp_folder / f"experiments_{safe_model_name}_results.json")
    
    print(f"Experiment folder: {exp_folder}")
    print(f"Output file: {output_file}")
    print("-" * 60)
    
    # Process programs
    results = {
        "metadata": {
            "model": args.model,
            "timestamp": datetime.now().isoformat(),
            "timeout": args.timeout
        },
        "results": []
    }
    
    if args.task.lower() == 'all':
        # Process all programs
        programs_to_process = PROGRAMS
    else:
        # Process single program
        program_name = extract_program_name(args.task)
        if program_name not in PROGRAMS:
            print(f"Error: Unknown program: {program_name}")
            print(f"Available programs: {', '.join(PROGRAMS)}")
            sys.exit(1)
        programs_to_process = [program_name]
    
    # Statistics
    total = len(programs_to_process)
    passed = 0
    failed = 0
    errors = 0
    one_line_fixes = 0
    
    # Process each program
    for i, program_name in enumerate(programs_to_process, 1):
        print(f"\n[{i}/{total}] {program_name}")
        result = process_single_program(program_name, model_client, exp_folder, fixed_folder)
        results["results"].append(result)
        
        # Update statistics
        if result.get("test_status") == "PASSED":
            passed += 1
        elif result.get("test_status") in ["FAILED", "PARTIAL", "TIMEOUT"]:
            failed += 1
        else:
            errors += 1
        
        if result.get("is_one_line_change", False):
            one_line_fixes += 1
        
        # Save results after each program (in case of interruption)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    # Add summary
    results["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "one_line_fixes": one_line_fixes,
        "success_rate": f"{(passed/total)*100:.1f}%" if total > 0 else "0%"
    }
    
    # Save final results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)
    print(f"Total Programs: {total}")
    print(f"✓ Passed: {passed} ({(passed/total)*100:.1f}%)")
    print(f"✗ Failed: {failed}")
    print(f"⚠ Errors: {errors}")
    print(f"One-line fixes: {one_line_fixes} ({(one_line_fixes/total)*100:.1f}%)")
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()