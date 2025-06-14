#!/usr/bin/env python3

import unittest
import sys
import os

# Add the test directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from metric.style_validator import StyleError, validate_style
from metric.tokenizer import tokenize
from test_utils import code_block


class TestStyleValidation(unittest.TestCase):
    """Comprehensive tests for Metric language whitespace and style validation."""
    
    # ========================================================================
    # Line Ending Validation Tests
    # ========================================================================
    
    def test_carriage_return_at_start(self):
        code = code_block("""
                    let x integer = 5
                    let y integer = 10
                    print x + y
                """)
        
        code = "\r" + code

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Carriage return newlines not allowed; use \\n only at line 1, column 1")
    
    def test_carriage_return_in_middle(self):   
        code = code_block("""
            let x integer = 5
            let y integer = 10\r
            print x + y
        """)

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Carriage return newlines not allowed; use \\n only at line 2, column 19")
    
    def test_carriage_return_at_end(self):
        code = code_block("""
                    let x integer = 5
                    let y integer = 10
                    print x + y
                """).strip()
        
        code = code + "\r"
    
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Carriage return newlines not allowed; use \\n only at line 3, column 12")
    
    def test_crlf_line_ending_detection(self):
        code = code_block("""
            let x integer = 5\r
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Carriage return newlines not allowed; use \\n only at line 1, column 18")
    
    def test_multiple_carriage_returns(self):
        code = code_block("""
            let x integer = 5\r
            let y integer = 10\r
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        # Should detect the first one
        self.assertEqual(str(cm.exception), "Carriage return newlines not allowed; use \\n only at line 1, column 18")
    
    def test_valid_lf_only_line_endings(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_carriage_return_with_indentation(self):
        code = code_block("""
            let x integer = 5
            if x > 0\r
                print x
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Carriage return newlines not allowed; use \\n only at line 2, column 9")
    
    # ========================================================================
    # Leading/Trailing Newline Tests  
    # ========================================================================
    
    def test_leading_newline_single(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """)

        code = "\n" + code

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Leading newlines not allowed")
    
    def test_leading_newlines_multiple(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        code = "\n\n" + code

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Leading newlines not allowed")
    
    def test_trailing_newline_single(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        code = code + "\n"

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Trailing newlines not allowed")
    
    def test_trailing_newlines_multiple(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        code = code + "\n\n"

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Trailing newlines not allowed")
    
    def test_both_leading_and_trailing_newlines(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """)

        code = "\n" + code + "\n"

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Leading newlines not allowed")
    
    def test_only_newlines_file(self):
        code = "\n"

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Program must not be empty")
    
    def test_valid_no_boundary_newlines(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_empty_string(self):
        code = ""

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Program must not be empty")
    
    # ========================================================================
    # Consecutive Newline Tests
    # ========================================================================
    
    def test_single_newline_valid(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_double_newline_valid(self):

        code = code_block("""
            let x integer = 5
            
            let y integer = 10
            print x + y
        """).strip()

        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_triple_newline_invalid(self):
        code = code_block("""
            let x integer = 5
            
            
            let y integer = 10
            print x + y
        """).strip()

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Too many consecutive newlines: maximum 2 allowed at line 4")
    
    def test_quadruple_newline_invalid(self):

        code = code_block("""
            let x integer = 5
            
            
            
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Too many consecutive newlines: maximum 2 allowed at line 4")
    
    def test_many_consecutive_newlines_invalid(self):

        code = code_block("""
            let x integer = 5
            
            
            
            
            
            
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Too many consecutive newlines: maximum 2 allowed at line 4")
    
    def test_mixed_valid_and_invalid_newlines(self):
        code = code_block("""
            let x integer = 5
            
            let y integer = 10
            
            
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Too many consecutive newlines: maximum 2 allowed at line 6")
    
    def test_multiple_invalid_newline_sections(self):
        code = code_block("""
            let x integer = 5
            
            
            let y integer = 10
            
            
            
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        # Should detect the first violation
        self.assertEqual(str(cm.exception), "Too many consecutive newlines: maximum 2 allowed at line 4")
    
    def test_complex_valid_newline_patterns(self):
        code = code_block("""
            let x integer = 5
            
            let y integer = 10
            let sum integer = x + y
            
            if sum > 10
                print sum
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    # ========================================================================
    # Line Whitespace Tests
    # ========================================================================
    
    def test_trailing_spaces_first_line(self):
        code = code_block("""
            let x integer = 5 
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Trailing spaces not allowed at line 1")
    
    def test_trailing_spaces_middle_line(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10 
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Trailing spaces not allowed at line 2")
    
    def test_trailing_spaces_last_line(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        code = code + " "

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Trailing spaces not allowed at line 3")
    
    def test_trailing_spaces_multiple_lines(self):
        code = code_block("""
            let x integer = 5 
            let y integer = 10 
            print x + y
        """).strip()

        code = code + " "

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Trailing spaces not allowed at line 1")
    
    def test_invalid_leading_spaces_outside_of_block(self):
        code = code_block("""
            let x integer = 5 
            let y integer = 10 
            print x + y
        """).strip()

        code = "  " + code 

        with self.assertRaises(Exception) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)

        self.assertIn("Invalid indentation", str(cm.exception))
    
    def test_invalid_leading_spaces_three(self):
        code = code_block("""
            let x integer = 5
            if x > 0
               print x
               let y integer = 10
        """).strip()
        with self.assertRaises(Exception) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        
        self.assertIn("Invalid indentation", str(cm.exception))
    
    def test_invalid_leading_spaces_five(self):
        code = code_block("""
            let x integer = 5
            if x > 0
                 print x
                 let y integer = 10
        """).strip()
        with self.assertRaises(Exception) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        
        self.assertIn("Invalid indentation", str(cm.exception))
    
    def test_valid_indentation_four_spaces(self):
        code = code_block("""
            let x integer = 5
            if x > 0
                print x
                let y integer = 10
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_valid_indentation_eight_spaces(self):
        code = code_block("""
            let x integer = 5
            if x > 0
                if x > 3
                    print x
                    let y integer = 10
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_mixed_valid_and_invalid_indentation(self):
        code = code_block("""
            let x integer = 5
            if x > 0
                if x > 3
                     print x
                     let y integer = 10
        """).strip()

        with self.assertRaises(Exception) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        
        self.assertIn("Invalid indentation", str(cm.exception))
    
    # ========================================================================
    # Token Spacing Tests
    # ========================================================================
    
    def test_multiple_spaces_between_tokens_start(self):
        code = code_block("""
            let  x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Multiple spaces not allowed between tokens at line 1")
        
    def test_multiple_spaces_between_tokens_middle(self):
        code = code_block("""
            let x integer = 5
            let  y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Multiple spaces not allowed between tokens at line 2")
        
    def test_multiple_spaces_between_tokens_end(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print  x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Multiple spaces not allowed between tokens at line 3")
        
    def test_no_space_before_operator_start(self):
        code = code_block("""
            let x integer = 5+ 3
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Expected space before operator '+' at line 1")
        
    def test_no_space_before_operator_middle(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10+ 3
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Expected space before operator '+' at line 2")
        
    def test_no_space_before_operator_end(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x* y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Expected space before operator '*' at line 3")
        
    def test_no_space_after_identifier_start(self):
        code = code_block("""
            let x5 = 5
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Expected space after identifier: x at line 1")
        
    def test_no_space_after_identifier_middle(self):
        code = code_block("""
            let x integer = 5
            let y5 = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Expected space after identifier: y at line 2")
        
    def test_no_space_after_number_start(self):
        code = code_block("""
            let x integer = 5let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Expected space after number: 5 at line 1")
    
    # ========================================================================
    # Comment Spacing Tests
    # ========================================================================
    
    def test_no_space_before_inline_comment_start(self):
        code = code_block("""
            let x integer = 5# comment
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Comments must be separated from code by exactly one space at line 1")
        
    def test_no_space_before_inline_comment_middle(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10# comment
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Comments must be separated from code by exactly one space at line 2")
        
    def test_no_space_before_inline_comment_end(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y# comment
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Comments must be separated from code by exactly one space at line 3")
        
    def test_multiple_spaces_before_inline_comment_start(self):
        code = code_block("""
            let x integer = 5  # comment
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Multiple spaces not allowed between tokens at line 1")
        
    def test_multiple_spaces_before_inline_comment_middle(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10  # comment
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Multiple spaces not allowed between tokens at line 2")
        
    def test_valid_inline_comment_spacing(self):
        code = code_block("""
            let x integer = 5 # Initialize x
            let y integer = 10 # Initialize y
            print x + y # Print sum
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
        
    def test_comment_indentation_invalid(self):
        code = code_block("""
            let x integer = 5
            if x > 0
              # Wrong indentation for comment
                print x
        """).strip()
        with self.assertRaises(Exception) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        
        self.assertIn("Invalid indentation", str(cm.exception))
    
    # ========================================================================
    # Comma Spacing Tests
    # ========================================================================
    
    def test_space_before_comma_function_params(self):
        code = code_block("""
            def add(x integer , y integer) returns integer
                return x + y
            print add(5, 10)
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Space before comma not allowed at line 1")
        
    def test_space_before_comma_function_call(self):
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
            print add(5 , 10)
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Space before comma not allowed at line 3")
        
    def test_no_space_after_comma_function_params(self):
        code = code_block("""
            def add(x integer,y integer) returns integer
                return x + y
            print add(5, 10)
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Space required after comma at line 1")
        
    def test_no_space_after_comma_function_call(self):
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
            print add(5,10)
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Space required after comma at line 3")
        
    def test_no_space_after_comma_list_literal(self):
        code = code_block("""
            let nums list of integer = [1,2,3]
            let first integer = nums[0]
            print first
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Space required after comma at line 1")
        
    def test_valid_comma_spacing(self):
        code = code_block("""
            def process(data list of integer, size integer) returns integer
                return data[0] + size
            let nums list of integer = [1, 2, 3]
            print process(nums, len(nums))
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    # ========================================================================
    # Multiple Statement Validation Tests
    # ========================================================================
    
    def test_multiple_statements_first_line(self):
        code = code_block("""
            let x integer = 5 print x
            let y integer = 10
            print y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Statements must be separated by a newline at line 1, column 19")
    
    def test_multiple_statements_middle_line(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10 print y
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Statements must be separated by a newline at line 2, column 20")
    
    def test_multiple_statements_last_line(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x print y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Statements must be separated by a newline at line 3, column 9")
    
    def test_multiple_statements_complex_keywords(self):
        code = code_block("""
            let x integer = 5
            if x > 0 print x
            print 999
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Statements must be separated by a newline at line 2, column 10")
    
    def test_multiple_statements_function_keywords(self):
        code = code_block("""
            def add(x integer, y integer) returns integer return x + y
            print add(5, 10)
            print 999
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "Statements must be separated by a newline at line 1, column 47")
    
    def test_keywords_in_comments_valid(self):
        code = code_block("""
            let x integer = 5 # This comment has let and print keywords
            let y integer = 10
            print x + y
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_valid_single_statements_per_line(self):
        code = code_block("""
            let x integer = 5
            let y integer = 10
            let sum integer = x + y
            if sum > 12
                print sum
                let bonus integer = 100
                print bonus
            while x > 0
                print x
                set x = x - 1
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)


if __name__ == '__main__':
    unittest.main()