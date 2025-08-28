#!/usr/bin/env python3
import json, argparse
from pathlib import Path

def score_results(test_results_path):
    with open(test_results_path, 'r') as f:
        data = json.load(f)
    
    fully_fixed = 0
    for result in data.get("results", []):
        is_fixed = (result.get("return_code") == 0 and 
                   result.get("failed") == 0 and 
                   result.get("diff_line_count") == 1)
        result["fully_fixed_with_one_line"] = is_fixed
        if is_fixed:
            fully_fixed += 1
    
    data["final_result"] = {
        "fully_fixed_programs": fully_fixed,
        "total_programs": len(data.get("results", [])),
        "success_rate": fully_fixed / len(data.get("results", [])) if data.get("results") else 0
    }
    
    # Save to same directory with _scored suffix
    input_file = Path(test_results_path)
    output_file = input_file.parent / f"{input_file.stem}_scored.json"
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Scored {len(data.get('results', []))} programs")
    print(f"Fully fixed: {fully_fixed}/{len(data.get('results', []))}")
    print(f"Output: {output_file}")
    
    return str(output_file)

def main():
    parser = argparse.ArgumentParser(description="Score test results")
    parser.add_argument("test_results_path", help="Path to test results JSON")
    
    try:
        score_results(parser.parse_args().test_results_path)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())