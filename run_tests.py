#!/usr/bin/env python3
"""
Test runner script for TaskManagerAPI
Provides different test execution options
"""

import subprocess
import sys
import os
import argparse

def run_pytest_tests(verbose=False, coverage=True):
    """Run pytest unit tests."""
    cmd = ['python', '-m', 'pytest']
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app', '--cov-report=term-missing', '--cov-report=html'])
    
    cmd.append('tests/')
    
    print("Running pytest unit tests...")
    return subprocess.run(cmd)

def run_curl_tests():
    """Run curl-based integration tests."""
    print("Running curl-based integration tests...")
    print("Make sure the API is running on localhost:5125")
    
    # Check if API is running
    try:
        import requests
        response = requests.get('http://localhost:5125/api', timeout=2)
        if response.status_code != 200:
            print("ERROR: API is not responding correctly")
            return 1
    except:
        print("ERROR: API is not running on localhost:5125")
        print("Please start the API first: python app.py")
        return 1
    
    # Run curl tests
    return subprocess.run(['bash', 'tests/test_curl.sh'])

def run_all_tests(verbose=False):
    """Run all tests."""
    print("=" * 50)
    print("Running all tests for TaskManagerAPI")
    print("=" * 50)
    
    # Run pytest tests
    result1 = run_pytest_tests(verbose=verbose)
    
    print("\n" + "=" * 50)
    
    # Run curl tests
    result2 = run_curl_tests()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Pytest tests: {'PASSED' if result1.returncode == 0 else 'FAILED'}")
    print(f"Curl tests: {'PASSED' if result2.returncode == 0 else 'FAILED'}")
    
    return result1.returncode or result2.returncode

def main():
    parser = argparse.ArgumentParser(description='TaskManagerAPI Test Runner')
    parser.add_argument('--type', choices=['pytest', 'curl', 'all'], default='all',
                       help='Type of tests to run')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--no-coverage', action='store_true',
                       help='Skip coverage reporting')
    
    args = parser.parse_args()
    
    if args.type == 'pytest':
        return run_pytest_tests(verbose=args.verbose, coverage=not args.no_coverage)
    elif args.type == 'curl':
        return run_curl_tests()
    elif args.type == 'all':
        return run_all_tests(verbose=args.verbose)

if __name__ == '__main__':
    sys.exit(main())
