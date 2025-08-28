#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/home/ubuntu/QuixBugs-bench")
EXPERIMENTS_DIR = BASE_DIR / "experiments_claude_code"
PROGRESS_FILE = EXPERIMENTS_DIR / "orchestrator_progress.json"

def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"completed": [], "failed": []}

def save_progress(progress):
    progress["timestamp"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def run_solver(program):
    cmd = [
        "python3", str(EXPERIMENTS_DIR / "problem_solver_claude_code.py"),
        "--model-name", "claude-3-7-sonnet-latest",
        "--buggy-program-folder", str(BASE_DIR / "python_programs"),
        "--fixed-program-folder", str(EXPERIMENTS_DIR / "fixed_python_programs"),
        "--program-name", program
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        return result.returncode == 0
    except KeyboardInterrupt:
        raise  # Re-raise to propagate ctrl+c
    except:
        return False

def main():
    # Load program list
    with open(EXPERIMENTS_DIR / "test_counts_required.json", 'r') as f:
        programs = list(json.load(f).keys())
    
    # Load/init progress
    progress = load_progress()
    remaining = [p for p in programs if p not in progress["completed"]]
    
    print(f"📊 {len(progress['completed'])}/{len(programs)} done, {len(remaining)} to go")
    
    # Run remaining programs
    for i, program in enumerate(remaining, 1):
        print(f"[{i}/{len(remaining)}] {program}...", end=" ")
        
        if run_solver(program):
            progress["completed"].append(program)
            print("✅")
        else:
            progress["failed"].append(program)
            print("❌")
        
        save_progress(progress)
    
    print(f"\n✅ Done: {len(progress['completed'])}/{len(programs)}")
    if progress["failed"]:
        print(f"❌ Failed: {progress['failed']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted. Run again to resume.")
        sys.exit(0)