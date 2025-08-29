#!/usr/bin/env python3
"""
Fix package declarations in fixed Java programs to avoid compilation conflicts.
"""

import os
import re
from pathlib import Path

def fix_package_in_file(file_path):
    """Fix package declaration in a single Java file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace package java_programs with package fixed_java_programs
    modified_content = re.sub(
        r'^package\s+java_programs\s*;',
        'package fixed_java_programs;',
        content,
        flags=re.MULTILINE
    )
    
    if modified_content != content:
        print(f"Fixing package in {file_path.name}")
        with open(file_path, 'w') as f:
            f.write(modified_content)
        return True
    return False

def main():
    fixed_dir = Path("/home/ubuntu/QuixBugs-bench/experiments_claude_code/fixed_java_programs")
    
    if not fixed_dir.exists():
        print(f"Directory not found: {fixed_dir}")
        return
    
    java_files = list(fixed_dir.glob("*.java"))
    
    if not java_files:
        print("No Java files found")
        return
    
    print(f"Found {len(java_files)} Java files to process")
    print("-" * 40)
    
    fixed_count = 0
    for java_file in java_files:
        if fix_package_in_file(java_file):
            fixed_count += 1
    
    print("-" * 40)
    print(f"Fixed package declarations in {fixed_count} files")
    
    if fixed_count > 0:
        print("\nNow the fixed programs use 'package fixed_java_programs;'")
        print("This avoids compilation conflicts with the original buggy programs.")

if __name__ == "__main__":
    main()