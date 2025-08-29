#!/bin/bash

# Script to test a fixed Java program
# Usage: ./test_fixed_java.sh PROGRAM_NAME

if [ $# -eq 0 ]; then
    echo "Usage: $0 PROGRAM_NAME"
    echo "Example: $0 BITCOUNT"
    exit 1
fi

PROGRAM=$1
FIXED_DIR="experiments_claude_code/fixed_java_programs"
BUGGY_DIR="java_programs"

# Check if fixed program exists
if [ ! -f "$FIXED_DIR/$PROGRAM.java" ]; then
    echo "Error: $FIXED_DIR/$PROGRAM.java not found"
    exit 1
fi

echo "Testing fixed version of $PROGRAM..."

# Backup original
if [ -f "$BUGGY_DIR/$PROGRAM.java" ]; then
    cp "$BUGGY_DIR/$PROGRAM.java" "$BUGGY_DIR/$PROGRAM.java.backup"
fi

# Copy fixed version
cp "$FIXED_DIR/$PROGRAM.java" "$BUGGY_DIR/$PROGRAM.java"

# Run test
echo "Running tests..."
gradle test --tests "java_testcases.junit.${PROGRAM}_TEST" --rerun-tasks

# Save test result
TEST_RESULT=$?

# Restore original
if [ -f "$BUGGY_DIR/$PROGRAM.java.backup" ]; then
    mv "$BUGGY_DIR/$PROGRAM.java.backup" "$BUGGY_DIR/$PROGRAM.java"
fi

# Report result
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ Tests PASSED for fixed $PROGRAM"
else
    echo "❌ Tests FAILED for fixed $PROGRAM"
fi

exit $TEST_RESULT