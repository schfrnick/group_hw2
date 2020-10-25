import json
import subprocess
import sys

# Crude version of testing tool for command-line programs

# read in json file representing test case
def loadTest(jsonfilename):
    jsonfile = open(jsonfilename)
    return json.load(jsonfile)

# For "build" step that must be done before running the test cases
def build(testcase):
    if 'build' in testcase.keys():
        compileResult = subprocess.run(testcase['build'])
        assert(compileResult.returncode == 0)

# takes a text file and convert it into an array
def toArray(file):
    temp = []
    
    for line in file:
        temp.append(line)
        
    return temp

# Comparing expected result to actual result of running the command
def check(expected, actual):
    if expected == None:
        return actual == None
    success = True
    
    for line1 in expected:
      if line1 != actual.readline():
        success = False
        break
    
    line = actual.readline()
    if line: # True if not at eof
        print('actual still has: ' + line)
        success = False
    return success

# checks actual file for expected output word by word
def checkByWord(expected, actual):
    if expected == None:
        return actual == None
    success = True

    expected_array = []
    actual_array = []

    expected_array = toArray(expected)
    actual_array = toArray(actual)

    if len(expected_array) != len(actual_array):
        success = False
    else:
        for i in range(len(expected_array)):
            print(expected_array[i])
            print(actual_array[i])
            if expected_array[i] != actual_array[i]:
                success = False
                break
    return success

# checks actual file specifically for expected output
def checkSpecific(expected, actual):
    if expected == None:
        return actual == None
    success = True

    expected_array = []
    actual_array = []

    expected_array = toArray(expected)
    actual_array = toArray(actual)

    temp = 0
    marker = 0

    for i in range(len(expected_array)):
        for j in range(marker, len(actual_array)):
            if j > len(actual_array) - 1:
                success = False
            if expected_array[i] == actual_array[j]:
                marker = j + 1
                temp += 1
                break;
    if temp != len(expected_array):
        success = False
    return success

# Running the test cases
def run(cmd):
    failures = 0
    successes = 0
    
    for case in cmd['cases']:
        case_pass = True
        case_keys = case.keys()
        # print(case.keys())
        has_infile = 'in' in case_keys
        has_args = 'args' in case_keys
        has_expected = 'expected' in case_keys
        has_err = 'expected_err' in case_keys

        # checks .json file for requirement 1
        if 'by word' in case_keys:
            by_word = case['by word']
        else:
            by_word = False
        # checks .json file for requirement 2
        if 'specific' in case_keys:
            specific = case['specific']
        else: specific = False
        
        if 'expected_return_code' in case_keys:
            expected_return_code = case['expected_return_code']
        else: expected_return_code = 0
        if has_infile:
            infile = open(case['in'])
        if has_args:
            cmd_text = cmd['cmd'] + ' ' + case['args']
        else: cmd_text = cmd['cmd']
        if has_expected:
            outname = case['name'] + '__actual.txt'
            actual = open(outname, 'w')
            expected = open(case['expected'])
        else:
            actual = None
            expected = None
        if has_err:
            errname = '__actual_err.txt'
            actual_err = open(errname, 'w')
            expected_err = open(case['expected_err'])
        else:
            actual_err = None
            expected_err = None
        if not has_infile:
            runResult = subprocess.run(cmd_text,text=True,stdout=actual,stderr=actual_err)
        else: runResult = subprocess.run(cmd_text,text=True,stdin=infile,stdout=actual,stderr=actual_err)
        if runResult.returncode != expected_return_code:
            print("Case " + case['name'] + " expected " + str(expected_return_code) + ", but actual returncode = " + str(runResult.returncode))
            case_pass = False
        if has_expected: actual = open(outname)
        if has_err: actual_err = open(errname)

        # if case_pass isn't already false, do the check asked by user, the default being checking line by line for equality to the actual file
        if by_word and case_pass:
            case_pass = checkByWord(expected, actual) and checkByWord(expected_err, actual_err)
        elif specific and case_pass:
            case_pass = checkSpecific(expected, actual) and checkSpecific(expected_err, actual_err)
        else:
            case_pass = check(expected, actual) and check(expected_err, actual_err)

        if case_pass:
            print("Case " + case['name'] + " passes")
            successes += 1
        else:
            print("Case " + case['name'] + " fails because actual output did not match expected output")
            failures += 1
        if has_infile: infile.close()
        if has_expected:
            actual.close()
            expected.close()
        if has_err:
            actual_err.close()
            expected_err.close()
    return (successes, failures)

usage = "python runtest.py testfile"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(usage)
        exit(1)
    testcase = loadTest(sys.argv[1])
    build(testcase)
    print(run(testcase))
