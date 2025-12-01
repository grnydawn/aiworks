#!/bin/bash

# Exit on error
set -e

echo "Running verification..."

# Example 1: Build.xml with specific warnings and errors (detailed and simple)
echo "Generating Build.xml..."
python3 generate_build_xml.py \
    --build-name "unitest-develop-gnu" \
    --build-stamp "20251101-0601-Experimental" \
    --site-name "chrysalis" \
    --warning "Simple Warning" \
    --warning "Detailed Warning:src/main.c:42:100:int main():return 0;:1" \
    --error "Simple Error" \
    --separator "|" \
    --error "Detailed Error|src/error.c|99|200|void err()|exit(1)|1" \
    --output "Generated_Build.xml"

if [ -f "Generated_Build.xml" ]; then
    echo "Generated_Build.xml created successfully."
    # Check for specific content
    if grep -q "Simple Warning" "Generated_Build.xml" && grep -q "Detailed Warning" "Generated_Build.xml"; then
        echo "Generated_Build.xml contains expected warning text."
    else
        echo "Generated_Build.xml missing expected warning text."
        exit 1
    fi
    if grep -q "src/main.c" "Generated_Build.xml" && grep -q "42" "Generated_Build.xml"; then
         echo "Generated_Build.xml contains detailed warning info."
    else
         echo "Generated_Build.xml missing detailed warning info."
         exit 1
    fi
    if grep -q "Simple Error" "Generated_Build.xml" && grep -q "Detailed Error" "Generated_Build.xml"; then
        echo "Generated_Build.xml contains expected error text."
    else
        echo "Generated_Build.xml missing expected error text."
        exit 1
    fi
else
    echo "Failed to create Generated_Build.xml"
    exit 1
fi

# Example 2: Test.xml with specific test details and custom separator
echo "Generating Test.xml..."
python3 generate_test_xml.py \
    --build-name "unitest-develop-gnu" \
    --build-stamp "20251101-0601-Experimental" \
    --site-name "chrysalis" \
    --test "TEST_A:passed:Output for Test A" \
    --test "TEST_B:failed:Error in Test B\nAssertion failed" \
    --separator "|" \
    --test "TEST_C|passed|Output with | separator" \
    --test "TEST_D|failed|Output with escaped separator \| inside" \
    --output "Generated_Test.xml"

if [ -f "Generated_Test.xml" ]; then
    echo "Generated_Test.xml created successfully."
    # Check for passed and failed tests
    if grep -q 'Status="passed"' "Generated_Test.xml" && grep -q 'Status="failed"' "Generated_Test.xml"; then
        echo "Generated_Test.xml contains passed and failed tests."
    else
        echo "Generated_Test.xml missing status checks."
        exit 1
    fi
    
    # Check if TEST_D exists (verifies escaping worked to parse the name correctly)
    if grep -q "TEST_D" "Generated_Test.xml"; then
        echo "TEST_D found, escaping likely worked."
    else
        echo "TEST_D not found."
        exit 1
    fi
else
    echo "Failed to create Generated_Test.xml"
    exit 1
fi

echo "Verification complete!"
