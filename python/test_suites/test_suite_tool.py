import re

# Updated parse_vectors function to accommodate flexible param fields
def parse_vectors(vectors, param_fields):
    # Dynamically create regex pattern based on param_fields
    field_patterns = []
    for field in param_fields:
        # Each field's value is expected to be in hexadecimal format
        field_patterns.append(fr"{field} = ([0-9a-f]*)")
    
    # Join the individual field patterns with whitespace in between to form the full pattern
    pattern_str = r"\s+".join(field_patterns)
    
    # Compile the dynamic regex pattern
    pattern = re.compile(pattern_str, re.MULTILINE)
    
    # Find all matches
    matches = [match.groups() for match in pattern.finditer(vectors)]
    return matches
"""
def parse_vectors(vectors, param_fields):
    # Compile regex to capture each field individually
    pattern = re.compile(
        r"Count = (\d+)\s+"
        r"Key = ([0-9a-f]+)\s+"
        r"param_00 = ([0-9a-f]+)\s+"
        r"param_01 = ([0-9a-f]+)\s+"
        r"param_02 = ([0-9a-f]+)\s+"
        r"Tag = ([0-9a-f]+)\s+"
        r"result_expected = ([0-9a-f]+)", re.MULTILINE
    )
    
    # Find all matches
    matches = [match.groups() for match in pattern.finditer(vectors)]
    return matches
"""

# Dummy function for test_x_00
def test_x_00(key_hex, param_00_hex, param_01_hex, param_02_hex, tag_hex, result_expected_hex):
    # Convert hex values to integers
    param_01_int = int(param_01_hex, 16)
    param_02_int = int(param_02_hex, 16)
    
    # Perform dummy addition operation
    result = param_01_int + param_02_int
    
    # Example condition for passing or failing the test
    return result == int(result_expected_hex, 16)

# Function to print the extracted fields for each test case
def print_fields_extracted(param_fields, values):
    print("Extracted Fields:")
    for field, value in zip(param_fields, values):
        print(f"{field}: {value}")
    print("")

# Usage
# load test vectors
# Open the file and read the contents into test_vectors
with open('./sample_data/test_vectors.txt', 'r') as file:
    test_vectors = file.read()

""" './sample_data/test_vectors.txt'
# Test vectors as a string
# T1 1.0
# Test vector parser test information
# Generated on 2013-01-25_1721hr_03sec

[key.length = 16 bytes]
[param_00.length = 12 bytes]
[param_01.length = 2]
[param_02.length = 5]
[tag.length = 10]
[result_expected.length = 2]

Count = 0
Key = 11754cd72aec309bf52f7687212e8957
param_00 = 3c819d9a9bed087615030b65
param_01 = 3c81
param_02 = 3c813c8181
Tag = 250327c674aaf477aef2675748cf6971
result_expected = 3c813cbe02

Count = 1
Key = ca47248ac0b6f8372a97ac43508308ed
param_00 = ffd2b598feabc9019262d2be
param_01 = ffd2
param_02 = ffd2ffd2d2
Tag = 60d20404af527d248d893ae495707d1a
result_expected = 0011

Count = 2
Key = ca47248ac0b6f8372a97ac43508308ed
param_00 = ffd2b598feabc9019262d2be
param_01 = ffd2
param_02 = ffd2ffd2d2
Tag = 60d20404af527d248d893ae495707d1a
result_expected = ffd300d2a4

=================== EOF
"""

# Output test_vectors to verify
#print(test_vectors)

param_fields = ["Count", "Key", "param_00", "param_01", "param_02", "Tag", "result_expected"]
test_cases = parse_vectors(test_vectors, param_fields)

print(f"test_cases: {test_cases}")

# start run tests
count_pass = 0
count_fail = 0

# Execute tests
for count, (count_val, key_hex, param_00_hex, param_01_hex, param_02_hex, tag_hex, result_expected_hex) in enumerate(test_cases):
    print_fields_extracted(param_fields, (count_val, key_hex, param_00_hex, param_01_hex, param_02_hex, tag_hex, result_expected_hex))
    result = test_x_00(key_hex, param_00_hex, param_01_hex, param_02_hex, tag_hex, result_expected_hex)
    print(f"Test Count {count}: {'Passed' if result else 'Failed'}")    
    print('---------'*5)
    if result:
        count_pass += 1
    else:
        count_fail += 1

print(f"Passed: {count_pass}")
print(f"Failed: {count_fail}")  

"""
test_cases: [('0', '11754cd72aec309bf52f7687212e8957', '3c819d9a9bed087615030b65', '3c81', '3c813c8181', '250327c674aaf477aef2675748cf6971', '3c813cbe02'), ('1', 'ca47248ac0b6f8372a97ac43508308ed', 'ffd2b598feabc9019262d2be', 'ffd2', 'ffd2ffd2d2', '60d20404af527d248d893ae495707d1a', '0011'), ('2', 'ca47248ac0b6f8372a97ac43508308ed', 'ffd2b598feabc9019262d2be', 'ffd2', 'ffd2ffd2d2', '60d20404af527d248d893ae495707d1a', 'ffd300d2a4')]
Extracted Fields:
Count: 0
Key: 11754cd72aec309bf52f7687212e8957
param_00: 3c819d9a9bed087615030b65
param_01: 3c81
param_02: 3c813c8181
Tag: 250327c674aaf477aef2675748cf6971
result_expected: 3c813cbe02

Test Count 0: Passed
---------------------------------------------
Extracted Fields:
Count: 1
Key: ca47248ac0b6f8372a97ac43508308ed
param_00: ffd2b598feabc9019262d2be
param_01: ffd2
param_02: ffd2ffd2d2
Tag: 60d20404af527d248d893ae495707d1a
result_expected: 0011

Test Count 1: Failed
---------------------------------------------
Extracted Fields:
Count: 2
Key: ca47248ac0b6f8372a97ac43508308ed
param_00: ffd2b598feabc9019262d2be
param_01: ffd2
param_02: ffd2ffd2d2
Tag: 60d20404af527d248d893ae495707d1a
result_expected: ffd300d2a4

Test Count 2: Passed
---------------------------------------------
Passed: 2
Failed: 1
"""