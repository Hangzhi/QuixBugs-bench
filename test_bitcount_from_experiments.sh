#!/bin/bash

# Self-contained shell script to test experiments_claude_code/fixed_java_programs/BITCOUNT.java
# This script reads the actual file and creates a test project

set -e  # Exit on error

echo "Testing experiments_claude_code/fixed_java_programs/BITCOUNT.java"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Create project structure
mkdir -p "$TEMP_DIR/src/fixed_java_programs"
mkdir -p "$TEMP_DIR/src/java_testcases/junit"
mkdir -p "$TEMP_DIR/lib"
mkdir -p "$TEMP_DIR/build"

# Copy the actual BITCOUNT.java from experiments folder
cp /home/ubuntu/QuixBugs-bench/experiments_claude_code/fixed_java_programs/BITCOUNT.java "$TEMP_DIR/src/fixed_java_programs/"

# Write BITCOUNT_TEST.java inline (modified to test fixed_java_programs package)
cat > "$TEMP_DIR/src/java_testcases/junit/BITCOUNT_TEST.java" << 'EOF'
package java_testcases.junit;


public class BITCOUNT_TEST {
    @org.junit.Test(timeout = 3000)
    public void test_0() throws java.lang.Exception {
        int result = fixed_java_programs.BITCOUNT.bitcount((int)127);
        org.junit.Assert.assertEquals( (int) 7, result);
    }

    @org.junit.Test(timeout = 3000)
    public void test_1() throws java.lang.Exception {
        int result = fixed_java_programs.BITCOUNT.bitcount((int)128);
        org.junit.Assert.assertEquals( (int) 1, result);
    }

    @org.junit.Test(timeout = 3000)
    public void test_2() throws java.lang.Exception {
        int result = fixed_java_programs.BITCOUNT.bitcount((int)3005);
        org.junit.Assert.assertEquals( (int) 9, result);
    }

    @org.junit.Test(timeout = 3000)
    public void test_3() throws java.lang.Exception {
        int result = fixed_java_programs.BITCOUNT.bitcount((int)13);
        org.junit.Assert.assertEquals( (int) 3, result);
    }

    @org.junit.Test(timeout = 3000)
    public void test_4() throws java.lang.Exception {
        int result = fixed_java_programs.BITCOUNT.bitcount((int)14);
        org.junit.Assert.assertEquals( (int) 3, result);
    }

    @org.junit.Test(timeout = 3000)
    public void test_5() throws java.lang.Exception {
        int result = fixed_java_programs.BITCOUNT.bitcount((int)27);
        org.junit.Assert.assertEquals( (int) 4, result);
    }

    @org.junit.Test(timeout = 3000)
    public void test_6() throws java.lang.Exception {
        int result = fixed_java_programs.BITCOUNT.bitcount((int)834);
        org.junit.Assert.assertEquals( (int) 4, result);
    }

    @org.junit.Test(timeout = 3000)
    public void test_7() throws java.lang.Exception {
        int result = fixed_java_programs.BITCOUNT.bitcount((int)254);
        org.junit.Assert.assertEquals( (int) 7, result);
    }

    @org.junit.Test(timeout = 3000)
    public void test_8() throws java.lang.Exception {
        int result = fixed_java_programs.BITCOUNT.bitcount((int)256);
        org.junit.Assert.assertEquals( (int) 1, result);
    }
}
EOF

# Write QuixFixOracleHelper.java inline
cat > "$TEMP_DIR/src/java_testcases/junit/QuixFixOracleHelper.java" << 'EOF'
package java_testcases.junit;


/**
 * Methods to format the output from the subject programs.
 *
 * @author Matias Martinez
 *
 */

public class QuixFixOracleHelper {

    public static String format(Object out, boolean cutDecimal) {
        Object jsonOutObtained = transformToString(out, cutDecimal);
        String obtained = removeSymbols(jsonOutObtained.toString());
        return obtained;
    }

    public static String removeSymbols(String r) {

        r = r.replaceAll("\\(", "[").replaceAll("\\)", "]").replace(" ", "").replaceAll("\"", "");
        return r;
    }

    public static String transformToString(Object out, boolean mustRemoveDecimal) {
        if (out instanceof Iterable) {
            String r = "[";
            for (Object o : (Iterable) out) {
                r += transformToString(o, mustRemoveDecimal) + ",";
            }
            if (r.length() >= 2) {
                r = r.trim().substring(0, r.length() - 1);
            }

            return r + "]";
        } else {
            String s = "";
            if (out instanceof String && !isInteger(out.toString()))
                s += out.toString();
            else {
                s = (mustRemoveDecimal && out.toString().endsWith(".0")
                        ? out.toString().substring(0, out.toString().length() - 2) : out.toString());
            }
            return s;
        }

    }

    public static boolean isInteger(String s) {
        boolean isValidInteger = false;
        try {
            Integer.parseInt(s);
            isValidInteger = true;
        } catch (NumberFormatException ex) {
        }

        return isValidInteger;
    }
}
EOF

# Download JUnit and Hamcrest jars if not available
echo "Downloading JUnit and Hamcrest..."
cd "$TEMP_DIR/lib"
if ! command -v wget &> /dev/null; then
    # Use curl if wget is not available
    curl -L -o junit-4.13.2.jar https://repo1.maven.org/maven2/junit/junit/4.13.2/junit-4.13.2.jar
    curl -L -o hamcrest-core-1.3.jar https://repo1.maven.org/maven2/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar
else
    wget -q https://repo1.maven.org/maven2/junit/junit/4.13.2/junit-4.13.2.jar
    wget -q https://repo1.maven.org/maven2/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar
fi

# Compile the source files
echo "Compiling source files..."
cd "$TEMP_DIR"
javac -cp "lib/junit-4.13.2.jar:lib/hamcrest-core-1.3.jar" -d build src/fixed_java_programs/BITCOUNT.java src/java_testcases/junit/QuixFixOracleHelper.java src/java_testcases/junit/BITCOUNT_TEST.java

# Run the tests
echo "Running tests..."
echo "================================"
java -cp "build:lib/junit-4.13.2.jar:lib/hamcrest-core-1.3.jar" org.junit.runner.JUnitCore java_testcases.junit.BITCOUNT_TEST

# Store exit code
TEST_RESULT=$?

# Cleanup
echo "================================"
echo "Cleaning up temporary directory..."
rm -rf "$TEMP_DIR"

# Exit with test result
if [ $TEST_RESULT -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed!"
    exit 1
fi