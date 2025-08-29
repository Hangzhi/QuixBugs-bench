#!/usr/bin/env python3
"""
Revert package declarations in fixed Java programs back to java_programs.
"""

import os
import re
from pathlib import Path

def revert_package_in_file(file_path):
    """Revert package declaration back to java_programs."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Change package fixed_java_programs back to package java_programs
    modified_content = re.sub(
        r'^package\s+fixed_java_programs\s*;',
        'package java_programs;',
        content,
        flags=re.MULTILINE
    )
    
    if modified_content != content:
        print(f"Reverting package in {file_path.name}")
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
    
    print(f"Found {len(java_files)} Java files to revert")
    print("-" * 40)
    
    reverted_count = 0
    for java_file in java_files:
        if revert_package_in_file(java_file):
            reverted_count += 1
    
    print("-" * 40)
    print(f"Reverted package declarations in {reverted_count} files")
    
    if reverted_count > 0:
        print("\nPackage declarations reverted to 'package java_programs;'")
        print("The agent should handle package changes when fixing programs.")

if __name__ == "__main__":
    main()