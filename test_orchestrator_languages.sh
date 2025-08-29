#!/bin/bash

echo "Testing orchestrator language support..."
echo "========================================="

# Test Python configuration
echo -e "\n1. Testing Python configuration:"
python3 experiments_claude_code/orchestrator_claude_code.py --language python --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Python configuration loads successfully"
else
    echo "✗ Python configuration failed"
fi

# Test Java configuration  
echo -e "\n2. Testing Java configuration:"
python3 experiments_claude_code/orchestrator_claude_code.py --language java --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Java configuration loads successfully"
else
    echo "✗ Java configuration failed"
fi

# Check for test count files
echo -e "\n3. Checking test count files:"
if [ -f "experiments_claude_code/python_test_counts_required.json" ]; then
    count=$(cat experiments_claude_code/python_test_counts_required.json | grep -c '"')
    echo "✓ Python test counts: $((count/2)) programs"
else
    echo "✗ Python test counts file missing"
fi

if [ -f "experiments_claude_code/java_test_counts_required.json" ]; then
    count=$(cat experiments_claude_code/java_test_counts_required.json | grep -c '"')
    echo "✓ Java test counts: $((count/2)) programs"
else
    echo "✗ Java test counts file missing"
fi

echo -e "\n========================================="
echo "Configuration test complete!"