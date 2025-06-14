#!/usr/bin/env python3
"""
Test runner for the Metric programming language.

This module provides a convenient way to run all tests for the Metric project.
"""

import unittest
import sys
import os
import argparse
import subprocess

def run_with_coverage() -> None:
    """Run tests with coverage analysis."""
    try:
        # Run tests with coverage
        subprocess.run(['coverage', 'run', '-m', 'unittest', 'discover', 'test/', '-v'], check=True)
        print("\n" + "="*50)
        print("COVERAGE REPORT")
        print("="*50)
        # Show coverage report
        subprocess.run(['coverage', 'report', '--show-missing'], check=True)
        print("\n" + "="*50)
        print("HTML report generated: run 'coverage html' for detailed view")
        print("="*50)
    except subprocess.CalledProcessError as e:
        print(f"Error running coverage: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Coverage.py not installed. Install with: pip install coverage")
        sys.exit(1)

def main() -> None:
    """Run tests for the Metric project."""
    parser = argparse.ArgumentParser(description='Run tests for the Metric programming language')
    parser.add_argument('pattern', nargs='?', default='test_*.py',
                       help='Test file pattern (default: test_*.py)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet output')
    parser.add_argument('-c', '--coverage', action='store_true',
                       help='Run tests with coverage analysis')
    
    args = parser.parse_args()
    
    # Handle coverage option
    if args.coverage:
        run_with_coverage()
        return
    
    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(current_dir)
    
    # Add project root to Python path
    sys.path.insert(0, project_root)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    test_dir = os.path.join(project_root, 'test')
    
    if not os.path.exists(test_dir):
        print(f"Error: Test directory not found at {test_dir}")
        sys.exit(1)
    
    # Discover tests
    suite = loader.discover(test_dir, pattern=args.pattern)
    
    # Set verbosity level
    verbosity = 1  # Default
    if args.verbose:
        verbosity = 2
    elif args.quiet:
        verbosity = 0
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    if verbosity > 0:
        tests_run = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        
        print(f"\nRan {tests_run} tests")
        if result.wasSuccessful():
            print("OK")
        else:
            print(f"FAILED (failures={failures}, errors={errors})")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == '__main__':
    main()