#!/usr/bin/env python3
"""
Generate java_test_counts_required.json from test results
"""

import json

# Read the test results
with open('/home/ubuntu/QuixBugs-bench/correct_java_programs/test_results_2025_08_29_210313.json', 'r') as f:
    data = json.load(f)

# Create the test counts dictionary
# Using uppercase names to match Java convention
test_counts = {}

for result in data['results']:
    program_name = result['program']
    passed_count = result['passed']
    test_counts[program_name] = passed_count

# Sort alphabetically for consistency
test_counts_sorted = dict(sorted(test_counts.items()))

# Save to java_test_counts_required.json
output_path = '/home/ubuntu/QuixBugs-bench/java_test_counts_required.json'
with open(output_path, 'w') as f:
    json.dump(test_counts_sorted, f, indent=2)

print(f"Generated {output_path}")
print(f"Total programs: {len(test_counts)}")
print(f"Total tests: {sum(test_counts.values())}")

# Also create a lowercase version for compatibility if needed
test_counts_lowercase = {k.lower(): v for k, v in test_counts.items()}
test_counts_lowercase_sorted = dict(sorted(test_counts_lowercase.items()))

output_path_lowercase = '/home/ubuntu/QuixBugs-bench/java_test_counts_required_lowercase.json'
with open(output_path_lowercase, 'w') as f:
    json.dump(test_counts_lowercase_sorted, f, indent=2)

print(f"Also generated lowercase version: {output_path_lowercase}")