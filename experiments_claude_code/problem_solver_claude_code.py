#!/usr/bin/env python3
import argparse
import json
import os
import shlex
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile
import shutil


class ClaudeCodeAgent:
    ALLOWED_TOOLS = ["Bash", "Edit", "Write", "Read", "Glob", "Grep", "LS", 
                     "WebFetch", "NotebookEdit", "TodoRead", "TodoWrite", "Agent"]
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name
        self.env = self._setup_environment()
    
    def _setup_environment(self) -> Dict[str, str]:
        env = os.environ.copy()
        if "ANTHROPIC_API_KEY" not in env:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        if self.model_name:
            env["ANTHROPIC_MODEL"] = self.model_name.removeprefix("anthropic/")
        elif "ANTHROPIC_MODEL" not in env:
            env["ANTHROPIC_MODEL"] = "claude-3-7-sonnet-20250219"
        
        env.update(
            {"FORCE_AUTO_BACKGROUND_TASKS": "1", 
            "ENABLE_BACKGROUND_TASKS": "1",
            "BASH_MAX_TIMEOUT_MS": "20000"
            })
        return env
    
    def run_agent(self, instruction: str, working_dir: Path) -> Dict[str, Any]:
        # Use shlex.quote to properly escape the instruction
        command = (f"timeout 120 claude --verbose --output-format stream-json "
                  f"-p {shlex.quote(instruction)} --allowedTools {' '.join(self.ALLOWED_TOOLS)}")
        
        start_time = time.time()
        result = {"success": False, "agent_output": None, "duration_ms": 0,
                 "error": None, "command": command}
        
        try:
            process = subprocess.Popen(command, shell=True, cwd=working_dir,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, env=self.env)
            
            stdout_lines = []
            
            # Read stdout
            for line in process.stdout:
                stdout_lines.append(line)
            
            return_code = process.wait()
            stderr = process.stderr.read()
            
            result["duration_ms"] = int((time.time() - start_time) * 1000)
            full_output = ''.join(stdout_lines)
            result["agent_output"] = full_output
            
            if return_code == 0:
                result["success"] = True
            else:
                result["error"] = f"Process exited with code {return_code}. Stderr: {stderr}"
        
                
        except Exception as e:
            result["error"] = str(e)
            result["duration_ms"] = int((time.time() - start_time) * 1000)
        
        return result


def solve_problem(
    model_name: str,
    buggy_python_program_folder: str,
    fixed_python_program_folder: str,
    program_name: str,
    language: str = "python"
) -> Dict[str, Any]:
    """
    Solve a single buggy program using Claude Code.
    
    Args:
        model_name: The Claude model to use
        buggy_python_program_folder: Absolute path to folder containing buggy programs
        fixed_python_program_folder: Absolute path to folder where fixed programs should be saved
        program_name: Name of the program to fix (without extension)
        language: Programming language ("python" or "java")
        
    Returns:
        A dictionary containing the results
    """
    # Convert paths to Path objects
    buggy_folder = Path(buggy_python_program_folder).absolute()
    fixed_folder = Path(fixed_python_program_folder).absolute()
    
    # Ensure folders exist
    if not buggy_folder.exists():
        raise ValueError(f"Buggy program folder does not exist: {buggy_folder}")
    
    fixed_folder.mkdir(parents=True, exist_ok=True)
    
    # Determine file extension based on language
    if language.lower() == "java":
        extension = ".java"
        # Convert program name to uppercase for Java
        program_name = program_name.upper()
    else:
        extension = ".py"
        # Keep lowercase for Python
        program_name = program_name.lower()
    
    # Check if buggy program exists
    buggy_python_program_path = buggy_folder / f"{program_name}{extension}"
    if not buggy_python_program_path.exists():
        raise ValueError(f"Buggy program not found: {buggy_python_program_path}")
    
    # Create a temporary working directory for the agent
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Copy the buggy program to temp directory
        temp_buggy_path = temp_path / f"{program_name}{extension}"
        shutil.copy2(buggy_python_program_path, temp_buggy_path)
        
        # Prepare the instruction for Claude based on language
        if language.lower() == "java":
            instruction = f"""Task:
1. Read the buggy program from: {program_name}.java
2. Analyze the code to identify the ONE line that contains a bug
3. Fix ONLY that buggy line with a minimal change
4. Write the complete fixed program to fixed_{program_name}.java
5. The package should be package fixed_java_programs rather than java_programs 

Requirements:
1. The fix should be exactly one line change
2. Do not add comments or make other modifications
3. Ensure the fixed code is syntactically correct and complete
4. The program should maintain the same functionality but with the bug fixed"""
        else:
            instruction = f"""Task:
1. Read the buggy program from: {program_name}.py
2. Analyze the code to identify the ONE line that contains a bug
3. Fix ONLY that buggy line with a minimal change
4. Write the complete fixed program to fixed_{program_name}.py

Requirements:
1. The fix should be exactly one line change
2. Do not add comments or make other modifications
3. Ensure the fixed code is syntactically correct and complete
4. The program should maintain the same functionality but with the bug fixed"""
        
        # Initialize and run the agent
        agent = ClaudeCodeAgent(model_name)
        
        print(f"Running Claude Code agent to fix {program_name}...")
        claude_result = agent.run_agent(instruction, temp_path)
        
        # Check if the fixed program was created
        fixed_python_program_path = fixed_folder / f"{program_name}{extension}"
        temp_fixed_path = temp_path / f"fixed_{program_name}{extension}"
        success = False
        error = None
        
        if temp_fixed_path.exists():
            # Copy the fixed program from temp to fixed folder
            shutil.copy2(temp_fixed_path, fixed_python_program_path)
            success = True
        else:
            error = f"Fixed file not created: {fixed_python_program_path}"
            success = False
        
        # Prepare the result
        result = {
            "program": program_name,
            "language": language,
            "success": success,
            "error": error,
            "claude_result": claude_result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save the agent log
        log_file_path = fixed_folder / "agent_log_claude.json"
        
        # Load existing results if file exists
        existing_results = []
        if log_file_path.exists():
            try:
                with open(log_file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "results" in data:
                        existing_results = data["results"]
                    elif isinstance(data, list):
                        existing_results = data
            except (json.JSONDecodeError, IOError):
                pass
        
        # Append new result
        existing_results.append(result)
        
        # Save updated results
        log_data = {
            "results": existing_results
        }
        
        with open(log_file_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"Results saved to {log_file_path}")
        
        if success:
            print(f"Successfully fixed {program_name}")
        else:
            print(f"Failed to fix {program_name}: {error}")
        
        return result


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Fix buggy programs using Claude Code agent')
    parser.add_argument('--model-name', type=str, default='claude-3-7-sonnet-latest',
                        help='Claude model name to use')
    parser.add_argument('--buggy-program-folder', type=str, required=True,
                        help='Absolute path to folder containing buggy programs')
    parser.add_argument('--fixed-program-folder', type=str, required=True,
                        help='Absolute path to folder where fixed programs should be saved')
    parser.add_argument('--program-name', type=str, required=True,
                        help='Name of the program to fix (without extension)')
    parser.add_argument('--language', type=str, default='python', choices=['python', 'java'],
                        help='Programming language of the program to fix (default: python)')
    
    args = parser.parse_args()
    
    try:
        result = solve_problem(
            model_name=args.model_name,
            buggy_python_program_folder=args.buggy_program_folder,
            fixed_python_program_folder=args.fixed_program_folder,
            program_name=args.program_name,
            language=args.language
        )
        
        # Print summary
        if result['success']:
            print(f"\n✓ Successfully fixed {args.program_name}")
        else:
            print(f"\n✗ Failed to fix {args.program_name}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
                
        # Print Claude result summary
        if result.get('claude_result'):
            cr = result['claude_result']
            print(f"\nClaude Code Statistics:")
            print(f"  Duration: {cr.get('duration_ms', 0) / 1000:.2f} seconds")
            
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())