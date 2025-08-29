#!/usr/bin/env python3
import json, subprocess, sys, argparse
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/home/ubuntu/QuixBugs-bench")
EXPERIMENTS_DIR = BASE_DIR / "experiments_claude_code"

def get_language_config(language):
    """Get configuration for the specified language."""
    if language == "python":
        return {
            "progress_file": EXPERIMENTS_DIR / "orchestrator_python_progress.json",
            "test_counts_file": BASE_DIR / "experiments_claude_code" / "python_test_counts_required.json",
            "buggy_folder": BASE_DIR / "python_programs",
            "fixed_folder": EXPERIMENTS_DIR / "fixed_python_programs",
            "extension": ".py"
        }
    elif language == "java":
        return {
            "progress_file": EXPERIMENTS_DIR / "orchestrator_java_progress.json",
            "test_counts_file": EXPERIMENTS_DIR / "java_test_counts_required.json",
            "buggy_folder": BASE_DIR / "java_programs",
            "fixed_folder": EXPERIMENTS_DIR / "fixed_java_programs",
            "extension": ".java"
        }
    else:
        raise ValueError(f"Unsupported language: {language}")

def load_progress(progress_file):
    if progress_file.exists():
        with open(progress_file, 'r') as f:
            return json.load(f)
    return {"completed": [], "failed": [], "language": None}

def save_progress(progress, progress_file, language):
    progress["timestamp"] = datetime.now().isoformat()
    progress["language"] = language
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)

def run_solver(program, language, config):
    cmd = [
        "python3", str(EXPERIMENTS_DIR / "problem_solver_claude_code.py"),
        "--model-name", "claude-3-7-sonnet-latest",
        "--buggy-program-folder", str(config["buggy_folder"]),
        "--fixed-program-folder", str(config["fixed_folder"]),
        "--program-name", program,
        "--language", language
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        return result.returncode == 0
    except KeyboardInterrupt:
        raise  # Re-raise to propagate ctrl+c
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description='Orchestrate fixing of buggy programs')
    parser.add_argument('--language', type=str, choices=['python', 'java'], 
                       default='python', help='Programming language (default: python)')
    args = parser.parse_args()
    
    # Get language-specific configuration
    config = get_language_config(args.language)
    
    # Load program list from language-specific test counts file
    if not config["test_counts_file"].exists():
        print(f"❌ Test counts file not found: {config['test_counts_file']}")
        print(f"   Please ensure {config['test_counts_file'].name} exists")
        sys.exit(1)
    
    with open(config["test_counts_file"], 'r') as f:
        test_counts = json.load(f)
        # For Java, convert uppercase names to lowercase for consistency with problem_solver
        if args.language == "java":
            programs = [name.lower() for name in test_counts.keys()]
        else:
            programs = list(test_counts.keys())
    
    # Load/init progress
    progress = load_progress(config["progress_file"])
    
    # Check if switching languages
    if progress.get("language") and progress["language"] != args.language:
        print(f"⚠️  Switching from {progress['language']} to {args.language}")
        print(f"   Progress file: {config['progress_file']}")
    
    remaining = [p for p in programs if p not in progress["completed"]]
    
    print(f"🔧 Language: {args.language.upper()}")
    print(f"📁 Buggy folder: {config['buggy_folder']}")
    print(f"📁 Fixed folder: {config['fixed_folder']}")
    print(f"📊 Progress: {len(progress['completed'])}/{len(programs)} done, {len(remaining)} to go")
    print("-" * 60)
    
    # Create fixed folder if it doesn't exist
    config["fixed_folder"].mkdir(parents=True, exist_ok=True)
    
    # Run remaining programs
    for i, program in enumerate(remaining, 1):
        print(f"[{i}/{len(remaining)}] Fixing {program}{config['extension']}...", end=" ")
        
        if run_solver(program, args.language, config):
            progress["completed"].append(program)
            print("✅")
        else:
            if program not in progress["failed"]:
                progress["failed"].append(program)
            print("❌")
        
        save_progress(progress, config["progress_file"], args.language)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"✅ Completed: {len(progress['completed'])}/{len(programs)}")
    
    if progress["failed"]:
        print(f"❌ Failed ({len(progress['failed'])}): {', '.join(progress['failed'])}")
    
    if len(progress['completed']) == len(programs):
        print(f"\n🎉 All {args.language.upper()} programs fixed!")
    
    print(f"\n📝 Progress saved to: {config['progress_file']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted. Run again to resume.")
        sys.exit(0)