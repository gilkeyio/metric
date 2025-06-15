#!/usr/bin/env python3
"""Main entry point for the Metric language interpreter."""

from typing import Generator

from metric.errors import CompilerError, handle_compiler_error
from . import tokenize, parse, execute
from .type_checker import type_check
from .style_validator import validate_style
import sys
import argparse
import os
import time
from contextlib import contextmanager

@contextmanager
def timer() -> Generator[None, None, None]:
    start = time.perf_counter()
    yield
    print(f"Execution time: {time.perf_counter() - start:.4f} seconds")


def run_program(program_text: str) -> None:
    """Execute a Metric program from source text."""
    try:
        tokens = tokenize(program_text)
        validate_style(program_text, tokens)
        ast = parse(tokens)
        type_check(ast)

        with timer():
            _, operation_count = execute(ast)

        print(f"Operation count: {operation_count}")

    except CompilerError as error:
        handle_compiler_error(error)


def run_file(filepath: str) -> None:
    """Execute a Metric program from a file."""
    # Check file extension
    if not filepath.endswith('.metric'):
        print(f"\033[31mError: File '{filepath}' does not have .metric extension\033[0m", file=sys.stderr)
        print("Metric programs should use the .metric file extension", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(filepath, 'r') as f:
            program_text = f.read()
        run_program(program_text)
    except FileNotFoundError:
        print(f"\033[31mError: File '{filepath}' not found\033[0m", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"\033[31mError reading file '{filepath}': {e}\033[0m", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Metric Programming Language Interpreter",
        epilog="Examples:\n  python -m metric examples/fibonacci.metric\n  python -m metric examples/factorial.metric",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'file', 
        nargs='?',
        help='Metric source file to execute (.metric extension required)'
    )
    
    args = parser.parse_args()
    
    if args.file:
        # Run file
        run_file(args.file)
    else:
        # No file provided
        print("Usage: python -m metric <file.metric>", file=sys.stderr)
        print("\nAvailable examples:", file=sys.stderr)
        examples_dir = os.path.join(os.path.dirname(__file__), '..', 'examples')
        if os.path.exists(examples_dir):
            for file in sorted(os.listdir(examples_dir)):
                if file.endswith('.metric'):
                    print(f"  examples/{file}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()