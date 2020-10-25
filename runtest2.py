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

# Comparing expected result to actual result of running the command
def check(expected, actual):
    if expected == None:
        return actual == None
    success = True
    for line in expected:
        text1 = line.split()
        text2 = actual.readline().split()
        for x in range(len(text1)):
            if text1[x] != text2[x]:
                success = False
                break
    if actual.readline(): # True if not at eof
        print('actual still has: ' + line)
        success = False
    return success

# function for checking requirement 2
def checkSpecific(expected, actual):
    if expected == None:
        return actual == None
    success = True

    expected_array = []
    actual_array = []

    for line in expected:
        expected_array.append(line)
    for line in actual:
        actual_array.append(line)

    temp = 0
    marker = 0

    print(len(actual_array) - 1)
    for i in range(len(expected_array)):
        print("RESTART")
        print(range(marker, len(actual_array)))
        for j in range(marker, len(actual_array)):
            print("j")
            print(j)
            print(expected_array[i])
            print(actual_array[j])
            print("-----------------------------------------------------")
            if j > len(actual_array) - 1:
                success = False
            if expected_array[i] == actual_array[j]:
                marker = j + 1
                print(marker)
                temp += 1
                break;
    print("temp")
    print(temp)
    print("exp")
    print(len(expected_array))
    if temp != len(expected_array):
        success = False
    print("TEST END")
    return success
# end

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

        # checks .json file for requirement 2
        if 'specific' in case_keys:
            specific = case['specific']
        else: specific = False
        # end
        
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

        # if case_pass isn't already false, and requirement 2 is asked by user
        if specific and case_pass:
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
