#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from io import StringIO
import sys

from metric.tokenizer import tokenize, TokenizerError
from metric.parser import parse, ParseError
from metric.type_checker import type_check, TypeCheckError
from metric.evaluator import execute, EvaluationError
from test_utils import code_block


class TestListFeatures(unittest.TestCase):
    """Comprehensive integration tests for list features."""
    
    def _run_code(self, code):
        """Helper to run code through full pipeline and capture output."""
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        captured_output = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            results = execute(ast)[0]
            output = captured_output.getvalue().strip()
            return results, output
        finally:
            sys.stdout = old_stdout
    
    def _expect_error(self, code, error_type, error_keyword):
        """Helper to expect a specific error."""
        try:
            self._run_code(code)
            self.fail(f"Expected {error_type.__name__} containing '{error_keyword}'")
        except error_type as e:
            self.assertIn(error_keyword.lower(), str(e).lower())
    
    def test_list_basic_operations(self):
        """Test basic list operations work together."""
        code = code_block("""
            let nums list of integer = [1, 2, 3, 4, 5]
            print nums
            print len(nums)
            print nums[0]
            print nums[4]
            set nums[2] = 99
            print nums
            print nums[2]
        """)
        
        results, output = self._run_code(code)
        expected_output = "[1, 2, 3, 4, 5]\n5\n1\n5\n[1, 2, 99, 4, 5]\n99"
        self.assertEqual(output, expected_output)
        self.assertEqual(results, [1, 2, 3, 4, 5, 5, 1, 5, 1, 2, 99, 4, 5, 99])
    
    def test_list_with_repeat_function(self):
        """Test repeat function creates correct lists."""
        code = code_block("""
            let zeros list of integer = repeat(0, 4)
            print zeros
            print len(zeros)
            let ones list of boolean = repeat(true, 3)
            print ones
            set zeros[1] = 42
            print zeros
        """)
        
        results, output = self._run_code(code)
        expected_output = "[0, 0, 0, 0]\n4\n[true, true, true]\n[0, 42, 0, 0]"
        self.assertEqual(output, expected_output)
    
    def test_list_with_expressions(self):
        """Test lists containing expressions."""
        code = code_block("""
            let x integer = 10
            let y integer = 20
            let computed list of integer = [x + 1, y * 2, x + y]
            print computed
            set computed[0] = x * y
            print computed
        """)
        
        results, output = self._run_code(code)
        expected_output = "[11, 40, 30]\n[200, 40, 30]"
        self.assertEqual(output, expected_output)
    
    def test_list_in_loops(self):
        """Test lists work correctly in loops."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            let i integer = 0
            while i < len(nums)
                print nums[i]
                set nums[i] = nums[i] * 2
                set i = i + 1
            print nums
        """)
        
        results, output = self._run_code(code)
        expected_output = "1\n2\n3\n[2, 4, 6]"
        self.assertEqual(output, expected_output)
    
    def test_list_in_conditionals(self):
        """Test lists work correctly in if statements."""
        code = code_block("""
            let nums list of integer = [5, 10, 15]
            if len(nums) > 2
                print nums[0]
                if nums[1] == 10
                    set nums[1] = 100
                    print nums[1]
            print nums
        """)
        
        results, output = self._run_code(code)
        expected_output = "5\n100\n[5, 100, 15]"
        self.assertEqual(output, expected_output)
    
    def test_list_with_functions(self):
        """Test lists work correctly with functions."""
        code = code_block("""
            def sumlist(nums list of integer) returns integer
                let total integer = 0
                let i integer = 0
                while i < len(nums)
                    set total = total + nums[i]
                    set i = i + 1
                return total

            def createlist(size integer) returns list of integer
                return repeat(42, size)

            let values list of integer = [1, 2, 3, 4, 5]
            let sum integer = sumlist(values)
            print sum

            let newlist list of integer = createlist(3)
            print newlist
            print sumlist(newlist)
        """)
        
        results, output = self._run_code(code)
        expected_output = "15\n[42, 42, 42]\n126"
        self.assertEqual(output, expected_output)
    
    def test_list_complex_access_patterns(self):
        """Test complex list access patterns."""
        code = code_block("""
            let data list of integer = [10, 20, 30, 40, 50]
            let indices list of integer = [0, 2, 4]
            let i integer = 0
            while i < len(indices)
                print data[indices[i]]
                set i = i + 1

            set data[indices[1]] = 999
            print data
        """)
        
        results, output = self._run_code(code)
        expected_output = "10\n30\n50\n[10, 20, 999, 40, 50]"
        self.assertEqual(output, expected_output)
    
    def test_list_boolean_operations(self):
        """Test lists with boolean elements."""
        code = code_block("""
            let flags list of boolean = [true, false, true, false]
            print flags
            print len(flags)
            print flags[0]
            print flags[1]
            set flags[1] = true
            print flags
            let allfalse list of boolean = repeat(false, 2)
            print allfalse
        """)
        
        results, output = self._run_code(code)
        expected_output = "[true, false, true, false]\n4\ntrue\nfalse\n[true, true, true, false]\n[false, false]"
        self.assertEqual(output, expected_output)
    
    def test_list_empty_operations(self):
        """Test operations on empty lists."""
        code = code_block("""
            let empty list of integer = repeat(0, 0)
            print empty
            print len(empty)
            let fromrepeat list of boolean = repeat(true, 0)
            print fromrepeat
            print len(fromrepeat)
        """)
        
        results, output = self._run_code(code)
        expected_output = "[]\n0\n[]\n0"
        self.assertEqual(output, expected_output)
    
    def test_list_function_parameters_and_returns(self):
        """Test lists as function parameters and return values."""
        code = code_block("""
            def reverse(nums list of integer) returns list of integer
                let result list of integer = repeat(0, 0)
                let i integer = len(nums)
                while i > 0
                    set i = i - 1
                    # Can't append, so just demonstrate with fixed size
                return repeat(nums[0], 1)

            def getlast(nums list of integer) returns integer
                return nums[len(nums) - 1]

            let original list of integer = [1, 2, 3]
            let last integer = getlast(original)
            print last
            let single list of integer = reverse(original)
            print single
        """)
        
        results, output = self._run_code(code)
        expected_output = "3\n[1]"
        self.assertEqual(output, expected_output)
    
    # Error handling tests
    def test_list_type_errors(self):
        """Test list type checking errors."""
        error_cases = [
            ("let mixed list of integer = [1, true]", TypeCheckError, "homogeneous"),
            ("let nums list of integer = [1, 2]\nset nums[0] = true", TypeCheckError, "type mismatch"),
            ("let nums list of integer = [1, 2]\nprint nums[true]", TypeCheckError, "index must be integer"),
            ("let x integer = 5\nprint x[0]", TypeCheckError, "cannot index into non-list"),
            ("let x integer = 5\nprint len(x)", TypeCheckError, "cannot get length of non-list"),
        ]
        
        for code, error_type, keyword in error_cases:
            with self.subTest(code=code):
                self._expect_error(code, error_type, keyword)
    
    def test_list_runtime_errors(self):
        """Test list runtime errors."""
        error_cases = [
            ("let nums list of integer = [1, 2, 3]\nprint nums[5]", EvaluationError, "out of bounds"),
            ("let nums list of integer = [1, 2, 3]\nlet negindex integer = 0 - 1\nprint nums[negindex]", EvaluationError, "out of bounds"),
            ("let nums list of integer = [1, 2, 3]\nset nums[10] = 42", EvaluationError, "out of bounds"),
            ("let negcount integer = 0 - 5\nlet nums list of integer = repeat(1, negcount)", EvaluationError, "negative"),
        ]
        
        for code, error_type, keyword in error_cases:
            with self.subTest(code=code):
                self._expect_error(code, error_type, keyword)
    
    def test_list_parser_errors(self):
        """Test list parsing errors."""
        error_cases = [
            ("let nums list integer = [1, 2, 3]", ParseError, "of"),
            ("let nums list of integer = [1, 2, 3", ParseError, "]"),
            ("print nums[0", ParseError, "]"),
            ("let nums list of integer = repeat 0, 5", ParseError, "("),
            ("print len nums", ParseError, "("),
        ]
        
        for code, error_type, keyword in error_cases:
            with self.subTest(code=code):
                self._expect_error(code, error_type, keyword)
    
    def test_list_comprehensive_program(self):
        """Test a comprehensive program using all list features."""
        code = code_block("""
            def findmax(nums list of integer) returns integer
                let max integer = nums[0]
                let i integer = 1
                while i < len(nums)
                    if nums[i] > max
                        set max = nums[i]
                    set i = i + 1
                return max

            def contains(nums list of integer, target integer) returns boolean
                let i integer = 0
                while i < len(nums)
                    if nums[i] == target
                        return true
                    set i = i + 1
                return false

            let data list of integer = [3, 1, 4, 1, 5, 9, 2, 6]
            print data
            print len(data)

            let maximum integer = findmax(data)
            print maximum

            let hasfive boolean = contains(data, 5)
            print hasfive

            let hasten boolean = contains(data, 10)
            print hasten

            set data[0] = maximum
            print data

            let doubled list of integer = repeat(maximum * 2, 3)
            print doubled
        """)
        
        results, output = self._run_code(code)
        expected_lines = [
            "[3, 1, 4, 1, 5, 9, 2, 6]",
            "8",
            "9",
            "true",
            "false",
            "[9, 1, 4, 1, 5, 9, 2, 6]",
            "[18, 18, 18]"
        ]
        self.assertEqual(output, "\n".join(expected_lines))


if __name__ == '__main__':
    unittest.main()