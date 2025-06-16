# Metric Programming Language

This is a Python implementation of the Metric programming language - a simple statically-typed language for deterministic algorithm performance testing. It has explicit type annotations, variable assignment, arithmetic expressions, boolean literals, comparison operations, and control flow statements. The language enforces strict whitespace rules and provides compile-time type safety.

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![License](https://img.shields.io/github/license/gilkeyio/metric)
![Issues](https://img.shields.io/github/issues/gilkeyio/metric)
![Tests](https://github.com/gilkeyio/metric/workflows/Tests/badge.svg)
[![Coverage](https://gilkeyio.github.io/metric/badges/coverage.svg)](https://github.com/gilkeyio/metric/actions)


## Project Structure

```
├── metric/        # Core library modules
│   ├── __init__.py      # Package initialization with exports
│   ├── __main__.py      # Main entry point (metric)
│   ├── metric_ast.py    # Abstract syntax tree definitions with type annotations
│   ├── tokenizer.py     # Lexical analysis with strict whitespace validation
│   ├── parser.py        # Recursive descent parser building typed AST
│   ├── type_checker.py  # Static type analysis and validation
│   └── evaluator.py     # Tree-walking interpreter with environment
└── test/          # Unit tests (150+ tests)
    ├── test_tokenizer.py
    ├── test_parser.py
    ├── test_evaluator.py
    └── test_type_system.py
```

## Running the Code

### Run Metric programs:
```bash
# Run a specific .metric file
metric examples/demo.metric
metric examples/fibonacci.metric
metric examples/factorial.metric


# Show help and available examples
metric
```

### Run tests:
```bash
# run all tests:
python -m unittest discover test/

# run tests with custom test runner:
metric-test
```

## Language Features

### Data Types
- **Integers**: Positive and negative integers with `integer` type annotation (e.g., `5`, `-42`, `0`)
- **Floats**: Positive and negative decimal numbers with `float` type annotation (e.g., `3.14`, `-2.5`, `0.0`)
- **Booleans**: `true` and `false` literals with `boolean` type annotation
- **Lists**: Homogeneous collections with `list of type` annotation (e.g., `list of integer`, `list of boolean`)

### Operators
- **Arithmetic**: `+`, `-`, `*`, `/`, `%` with standard precedence (`* / %` before `+ -`)
- **Comparison**: `<`, `>`, `≤`, `≥`, `≡`, `≠` (lower precedence than arithmetic)
- **Logical**: 
  - Binary: `and`, `or` (require boolean operands, `and` has higher precedence than `or`)
  - Unary: `not` (requires boolean operand, highest precedence among logical operators)

### Language Rules
- **Identifiers**: Must start with lowercase letters, contain only letters
- **Whitespace**: Exactly one space required between tokens (except parentheses have no surrounding spaces)
- **Comma spacing**: Commas must have no space before them and exactly one space after them
- **Statements**: Separated by 1 newline, with indentation-based blocks for control flow
- **Newlines**: 
  - Maximum 2 consecutive newlines allowed; 3+ consecutive newlines are an error
  - Leading newlines (at start of file) are not allowed
  - Trailing newlines (at end of file) are not allowed
  - Only LF (`\n`) line endings allowed; CR (`\r`) and CRLF (`\r\n`) are not allowed
- **Variables**: 
  - `let` declarations create typed variables with explicit type annotations
  - `set` statements update existing variable values (type-checked at compile time)
  - All variables must declare their type and cannot be redeclared
  - Type safety enforced at compile time
  - Automatic type promotion: integer + float = float

### Control Flow
- **If statements**: `if condition` followed by indented body
- **While loops**: `while condition` followed by indented body
- **Indentation**: 4 spaces for nested blocks

### Functions
- **Function declarations**: `def name(param type, ...) returns type` followed by indented body
- **Return statements**: `return expression` (required in all functions)
- **Function calls**: `name(arg1, arg2, ...)`
- **Pass by value**: All arguments are passed by value (copied)

### Lists
- **List declarations**: `let varName list of type = value`
- **List literals**: `[element1, element2, ...]` (e.g., `[1, 2, 3]`)
- **Empty lists**: `[]` (type must be explicitly declared)
- **List creation**: `repeat(value, count)` creates a list with `count` copies of `value`
- **List access**: `listName[index]` returns element at zero-based index
- **List assignment**: `set listName[index] = value` updates element at index
- **List length**: `len(listName)` returns the number of elements
- **Type safety**: Lists are homogeneous - all elements must be the same type
- **Bounds checking**: Runtime error if index < 0 or index ≥ length

### Comments
- **Line comments**: Start with `#` and continue to end of line
- **Standalone comments**: Must follow same indentation rules as statements
- **Inline comments**: Must be separated from code by exactly one space
- Comments are ignored during execution and have no effect on program behavior

## Example Programs

### Basic Arithmetic with Type Annotations
```metric
let x integer = 5 
print x
let y integer = x + 3
print y
print 2 + 3 * 4
let pi float = 3.14
print pi
```

Output:
```
5
8
14
3.14
```

### Negative Numbers
```metric
# Negative integers and floats
let negativeInt integer = -42
let negativeFloat float = -3.14
print negativeInt
print negativeFloat

# Negative numbers in arithmetic
let temp integer = -10
let adjustment integer = 5
let final integer = temp + adjustment
print final

# Negative numbers in comparisons
let isNegative boolean = -5 < 0
print isNegative

# Mixed positive and negative arithmetic
let result integer = -10 + 5 - 2
print result

let floatResult float = -2.5 * 4.0
print floatResult
```

Output:
```
-42
-3.14
-5
true
-7
-10.0
```

### Boolean and Comparison Operations
```metric
let x integer = 10
let y integer = 5
let isGreater boolean = x > y
print isGreater
let isEqual boolean = x ≡ 10
print isEqual
let isFalse boolean = false
print isFalse
let comparison boolean = (x + y) ≥ 15
print comparison
```

Output:
```
true
true
false
true
```

### Logical Operators
```metric
# Basic logical operations
print true and true
print true and false
print false or true
print false or false

# Logical not operator
print not true
print not false
print not (true and false)
print not (false or true)

# Variables with logical operators
let a boolean = true
let b boolean = false
print a and b
print a or b
print not a
print not b

# Complex logical expressions with not
let age integer = 25
let hasLicense boolean = true
let isMinor boolean = not (age ≥ 18)
let cannotDrive boolean = not hasLicense
let canDrive boolean = age ≥ 18 and hasLicense and not cannotDrive
print isMinor
print cannotDrive
print canDrive

# Operator precedence (not has highest precedence, then and, then or)
let precedenceTest1 boolean = not true and false
let precedenceTest2 boolean = true or not false and false
print precedenceTest1
print precedenceTest2

# Double negation
let doubled boolean = not not true
print doubled
```

Output:
```
true
false
true
false
false
true
false
true
false
true
true
false
false
true
false
true
true
```

### Float Operations and Type Promotion
```metric
let pi float = 3.14159
let radius float = 2.5
let area float = pi * radius * radius
print area

let x integer = 10
let y float = 3.5
let mixed float = x + y
print mixed

let precise boolean = pi > 3.14
print precise
```

Output:
```
19.6349375
13.5
true
```

### Mixed Operations
```metric
let a integer = 15
let b integer = 10
let sum integer = a + b
let isLargeSum boolean = sum > 20
print sum
print isLargeSum
let difference integer = a - b
let isSmallDiff boolean = difference ≤ 5
print difference
print isSmallDiff
```

Output:
```
25
true
5
true
```

### Control Flow Examples

#### If Statements
```metric
let x integer = 10
if x > 5
    print x
    let message integer = 42
    print message
print done
```

Output:
```
10
42
done
```

#### While Loops with Variable Mutation
```metric
let counter integer = 1
while counter ≤ 3
    print counter
    set counter = counter + 1
print finished
```

Output:
```
1
2
3
finished
```

#### Complex Control Flow
```metric
let x integer = 10
while x > 0
    if x ≡ 5
        print halfway
    print x
    set x = x - 2
print complete
```

Output:
```
10
8
6
halfway
4
2
complete
```

#### Control Flow with Logical Operators
```metric
let age integer = 25
let hasJob boolean = true
let hasLicense boolean = true
let income integer = 50000

if age ≥ 18 and hasLicense
    print canDrive

if hasJob and income > 40000
    print goodIncome

let qualified boolean = age ≥ 21 and hasJob and income > 30000
if qualified
    print eligible

# Using not operator in control flow
if not (age < 18)
    print notAMinor

let unemployed boolean = not hasJob
if not unemployed and income > 0
    print hasIncomeAndJob

# Complex negation
let restricted boolean = age < 16 or not hasLicense
if not restricted
    print canDriveUnrestricted
```

Output:
```
canDrive
goodIncome
eligible
notAMinor
hasIncomeAndJob
canDriveUnrestricted
```

### Function Declarations and Calls

```metric
def add(x integer, y integer) returns integer
    return x + y

def factorial(n integer) returns integer
    if n ≤ 1
        return 1
    return n * factorial(n - 1)

let sum integer = add(5, 10)
print sum

let fact integer = factorial(5)
print fact

let nested integer = add(factorial(3), add(2, 3))
print nested
```

Output:
```
15
120
11
```

### Functions with Logical Operators

```metric
def isEven(n integer) returns boolean
    return n % 2 ≡ 0

def isOdd(n integer) returns boolean
    return not isEven(n)

def isPositive(n integer) returns boolean
    return n > 0

def isNegative(n integer) returns boolean
    return not isPositive(n) and n ≠ 0

def isEvenAndPositive(n integer) returns boolean
    return isEven(n) and isPositive(n)

def isInvalidScore(score integer) returns boolean
    return not (score ≥ 0 and score ≤ 100)

def isValidRange(value integer, min integer, max integer) returns boolean
    return not (value < min or value > max)

let num integer = 8
print isEven(num)
print isOdd(num)
print isPositive(num)
print isNegative(num)
print isEvenAndPositive(num)

let score integer = 85
print isInvalidScore(score)

let testValue integer = 50
print isValidRange(testValue, 0, 100)

let negativeNum integer = -5
print isNegative(negativeNum)
```

Output:
```
true
false
true
false
true
false
true
true
```

### List Operations and Manipulation

```metric
let nums list of integer = [1, 2, 3, 4, 5]
print nums
print nums[0]
print len(nums)

let zeros list of integer = repeat(0, 3)
print zeros

set nums[2] = 99
print nums

let flags list of boolean = [true, false, true]
print flags
print flags[1]

# Logical operators with lists
let hasElements boolean = len(nums) > 0
let isShort boolean = len(nums) < 10
print hasElements and isShort

if len(nums) > 3 and nums[0] > 0
    print validList
```

Output:
```
[1, 2, 3, 4, 5]
1
5
[0, 0, 0]
[1, 2, 99, 4, 5]
[true, false, true]
false
true
validList
```

### Comments in Code

```metric
# This is a standalone comment
let x integer = 5 # Inline comment after code

# Comments follow indentation rules
if x > 0
    # This comment is properly indented
    print x # Another inline comment
    
# Multi-line comment blocks
# can be used to explain
# complex logic sections

while x > 0
    # Loop iteration comment
    set x = x - 1
    # Decrement counter
```

Output:
```
5
```

## Example Programs

The `examples/` directory contains sample Metric programs:

### fibonacci.metric
Calculates the first 12 numbers in the Fibonacci sequence:
```metric
let a integer = 0
let b integer = 1
let count integer = 10
let next integer = 0

print a
print b

while count > 0
    set next = a + b
    print next
    set a = b
    set b = next
    set count = count - 1
```

### factorial.metric
Calculates 5! (factorial of 5):
```metric
let n integer = 5
let result integer = 1

print n
while n > 1
    set result = result * n
    set n = n - 1

print result
```

### demo.metric
Demonstrates basic language features including variables, arithmetic, control flow, logical operators, and type safety.

### logical_operators_demo.metric
Comprehensive demonstration of logical operators (`and`, `or`) including operator precedence, complex expressions, and integration with functions and control flow.

### logical_not_demo.metric
Focused demonstration of the logical `not` operator including De Morgan's laws, operator precedence, double negation, and practical usage in functions and control flow.

## Static Type System

Metric enforces static typing with explicit type annotations for all variable declarations:

### Type Declaration Syntax
- `let variableName integer = expression` - Declares an integer variable
- `let variableName float = expression` - Declares a float variable  
- `let variableName boolean = expression` - Declares a boolean variable

### Type Safety Features
- **Compile-time type checking**: Type mismatches are caught before execution
- **Automatic type promotion**: Mixed integer/float arithmetic promotes to float
- **Variable redeclaration prevention**: Variables cannot be redeclared
- **Expression type validation**: All expressions are type-checked

### Type Error Examples
```metric
let x integer = true    # Type Error: cannot assign boolean to integer
let y boolean = 42      # Type Error: cannot assign integer to boolean
let z float = true      # Type Error: cannot assign boolean to float
let x integer = 5       
let x integer = 10      # Type Error: variable 'x' already declared
set z = 5               # Type Error: variable 'z' not declared
```

The type checker runs before code execution and provides clear error messages for type violations.

## Development

### Setup
```bash
# Install development dependencies
pip install -e ".[dev]"
```

### Testing with Coverage
```bash
# Run tests with coverage report
metric-coverage

# Generate detailed coverage reports
coverage run -m unittest discover test/ -v
coverage report --show-missing
coverage html  # Creates htmlcov/ directory with detailed HTML report
```

### Coverage Integration
- **Minimum Coverage**: 80% threshold enforced in CI/CD
- **Current Coverage**: 85%+ across all modules
- **Coverage Reports**: Automatically generated in GitHub Actions
- **HTML Reports**: Available locally via `coverage html`

The project uses Coverage.py for test coverage analysis with configuration in `pyproject.toml`.
