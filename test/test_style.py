#!/usr/bin/env python3

import unittest

from metric.errors import StyleError
from metric.style_validator import validate_style
from metric.tokenizer import tokenize
from test.test_utils import code_block


class TestStyleValidation(unittest.TestCase):
    """Comprehensive tests for Metric language whitespace and style validation."""
    
    # Line Ending Validation Tests
    
    def test_carriage_return_at_start(self)  -> None:
        code = code_block("""
                    let x integer = 5
                    let y integer = 10
                    print x + y
                """)
        
        code = "\r" + code

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 1] Style Error | Carriage return newlines not allowed; use \\n only")
    
    def test_carriage_return_in_middle(self)  -> None:   
        code = code_block("""
            let x integer = 5
            let y integer = 10\r
            print x + y
        """)

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 2, Column 19] Style Error | Carriage return newlines not allowed; use \\n only")
    
    def test_carriage_return_at_end(self)  -> None:
        code = code_block("""
                    let x integer = 5
                    let y integer = 10
                    print x + y
                """).strip()
        
        code = code + "\r"
    
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 3, Column 12] Style Error | Carriage return newlines not allowed; use \\n only")
    
    def test_crlf_line_ending_detection(self)  -> None:
        code = code_block("""
            let x integer = 5\r
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 18] Style Error | Carriage return newlines not allowed; use \\n only")
    
    def test_multiple_carriage_returns(self)  -> None:
        code = code_block("""
            let x integer = 5\r
            let y integer = 10\r
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        # Should detect the first one
        self.assertEqual(str(cm.exception), "[Line 1, Column 18] Style Error | Carriage return newlines not allowed; use \\n only")
    
    def test_valid_lf_only_line_endings(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_carriage_return_with_indentation(self)  -> None:
        code = code_block("""
            let x integer = 5
            if x > 0\r
                print x
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 2, Column 9] Style Error | Carriage return newlines not allowed; use \\n only")
    
    # Leading/Trailing Newline Tests  
    
    def test_leading_newline_single(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """)

        code = "\n" + code

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 1] Style Error | Leading newlines not allowed")
    
    def test_leading_newlines_multiple(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        code = "\n\n" + code

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 1] Style Error | Leading newlines not allowed")
    
    def test_trailing_newline_single(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        code = code + "\n"

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 4, Column 1] Style Error | Trailing newlines not allowed")
    
    def test_trailing_newlines_multiple(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        code = code + "\n\n"

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 5, Column 1] Style Error | Trailing newlines not allowed")
    
    def test_both_leading_and_trailing_newlines(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """)

        code = "\n" + code + "\n"

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 1] Style Error | Leading newlines not allowed")
    
    def test_only_newlines_file(self)  -> None:
        code = "\n"

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 1] Style Error | Program must not be empty")
    
    def test_valid_no_boundary_newlines(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_empty_string(self)  -> None:
        code = ""

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 1] Style Error | Program must not be empty")
    
    # Consecutive Newline Tests
    
    def test_single_newline_valid(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_double_newline_valid(self)  -> None:

        code = code_block("""
            let x integer = 5
            
            let y integer = 10
            print x + y
        """).strip()

        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_triple_newline_invalid(self)  -> None:
        code = code_block("""
            let x integer = 5
            
            
            let y integer = 10
            print x + y
        """).strip()

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 3, Column 1] Style Error | Too many consecutive newlines: maximum 2 allowed")
    
    def test_quadruple_newline_invalid(self)  -> None:

        code = code_block("""
            let x integer = 5
            
            
            
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 3, Column 1] Style Error | Too many consecutive newlines: maximum 2 allowed")
    
    def test_many_consecutive_newlines_invalid(self)  -> None:

        code = code_block("""
            let x integer = 5
            
            
            
            
            
            
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 3, Column 1] Style Error | Too many consecutive newlines: maximum 2 allowed")
    
    def test_mixed_valid_and_invalid_newlines(self)  -> None:
        code = code_block("""
            let x integer = 5
            
            let y integer = 10
            
            
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 5, Column 1] Style Error | Too many consecutive newlines: maximum 2 allowed")
    
    def test_multiple_invalid_newline_sections(self)  -> None:
        code = code_block("""
            let x integer = 5
            
            
            let y integer = 10
            
            
            
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        # Should detect the first violation
        self.assertEqual(str(cm.exception), "[Line 3, Column 1] Style Error | Too many consecutive newlines: maximum 2 allowed")
    
    def test_complex_valid_newline_patterns(self)  -> None:
        code = code_block("""
            let x integer = 5
            
            let y integer = 10
            let sum integer = x + y
            
            if sum > 10
                print sum
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    # Line Whitespace Tests
    
    def test_trailing_spaces_first_line(self)  -> None:
        code = code_block("""
            let x integer = 5 
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 18] Style Error | Trailing spaces not allowed")
    
    def test_trailing_spaces_middle_line(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10 
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 2, Column 19] Style Error | Trailing spaces not allowed")
    
    def test_trailing_spaces_last_line(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        code = code + " "

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 3, Column 12] Style Error | Trailing spaces not allowed")
    
    def test_trailing_spaces_multiple_lines(self)  -> None:
        code = code_block("""
            let x integer = 5 
            let y integer = 10 
            print x + y
        """).strip()

        code = code + " "

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 18] Style Error | Trailing spaces not allowed")
    
    def test_invalid_leading_spaces_outside_of_block(self)  -> None:
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
    
    def test_invalid_leading_spaces_three(self)  -> None:
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
    
    def test_invalid_leading_spaces_five(self)  -> None:
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
    
    def test_valid_indentation_four_spaces(self)  -> None:
        code = code_block("""
            let x integer = 5
            if x > 0
                print x
                let y integer = 10
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_valid_indentation_eight_spaces(self)  -> None:
        code = code_block("""
            let x integer = 5
            if x > 0
                if x > 3
                    print x
                    let y integer = 10
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_mixed_valid_and_invalid_indentation(self)  -> None:
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
    
    # Token Spacing Tests
    
    def test_multiple_spaces_between_tokens_start(self)  -> None:
        code = code_block("""
            let  x integer = 5
            let y integer = 10
            print x + y
        """).strip()

        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 4] Style Error | Multiple spaces not allowed between tokens")
        
    def test_multiple_spaces_between_tokens_middle(self)  -> None:
        code = code_block("""
            let x integer = 5
            let  y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 2, Column 4] Style Error | Multiple spaces not allowed between tokens")
        
    def test_multiple_spaces_between_tokens_end(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print  x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 3, Column 6] Style Error | Multiple spaces not allowed between tokens")
        
    def test_no_space_before_operator_start(self)  -> None:
        code = code_block("""
            let x integer = 5+ 3
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 18] Style Error | Expected space before operator '+'")
        
    def test_no_space_before_operator_middle(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10+ 3
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 2, Column 19] Style Error | Expected space before operator '+'")
        
    def test_no_space_before_operator_end(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x* y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 3, Column 8] Style Error | Expected space before operator '*'")
        
    def test_no_space_after_identifier_start(self)  -> None:
        code = code_block("""
            let x5 = 5
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 6] Style Error | Expected space after identifier 'x'")
        
    def test_no_space_after_identifier_middle(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y5 = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 2, Column 6] Style Error | Expected space after identifier 'y'")
        
    def test_no_space_after_number_start(self)  -> None:
        code = code_block("""
            let x integer = 5let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 18] Style Error | Expected space after number '5'")
    
    # Comment Spacing Tests
    
    def test_no_space_before_inline_comment_start(self)  -> None:
        code = code_block("""
            let x integer = 5# comment
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 18] Style Error | Comments must be separated from code by exactly one space")
        
    def test_no_space_before_inline_comment_middle(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10# comment
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 2, Column 19] Style Error | Comments must be separated from code by exactly one space")        
    
    def test_no_space_before_inline_comment_end(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x + y# comment
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 3, Column 12] Style Error | Comments must be separated from code by exactly one space")

    def test_multiple_spaces_before_inline_comment_start(self)  -> None:
        code = code_block("""
            let x integer = 5  # comment
            let y integer = 10
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 18] Style Error | Multiple spaces not allowed between tokens")
        
    def test_multiple_spaces_before_inline_comment_middle(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10  # comment
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 2, Column 19] Style Error | Multiple spaces not allowed between tokens")
        
    def test_valid_inline_comment_spacing(self)  -> None:
        code = code_block("""
            let x integer = 5 # Initialize x
            let y integer = 10 # Initialize y
            print x + y # Print sum
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
        
    def test_comment_indentation_invalid(self)  -> None:
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
    
    # Comma Spacing Tests
    
    def test_space_before_comma_function_params(self)  -> None:
        code = code_block("""
            def add(x integer , y integer) returns integer
                return x + y
            print add(5, 10)
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 19] Style Error | Space before comma not allowed")
        
    def test_space_before_comma_function_call(self)  -> None:
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
            print add(5 , 10)
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 3, Column 13] Style Error | Space before comma not allowed")
        
    def test_no_space_after_comma_function_params(self)  -> None:
        code = code_block("""
            def add(x integer,y integer) returns integer
                return x + y
            print add(5, 10)
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 18] Style Error | Space required after comma")
        
    def test_no_space_after_comma_function_call(self)  -> None:
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
            print add(5,10)
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 3, Column 12] Style Error | Space required after comma")
        
    def test_no_space_after_comma_list_literal(self)  -> None:
        code = code_block("""
            let nums list of integer = [1,2,3]
            let first integer = nums[0]
            print first
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 30] Style Error | Space required after comma")
        
    def test_valid_comma_spacing(self)  -> None:
        code = code_block("""
            def process(data list of integer, size integer) returns integer
                return data[0] + size
            let nums list of integer = [1, 2, 3]
            print process(nums, len(nums))
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    # Multiple Statement Validation Tests
    
    def test_multiple_statements_first_line(self)  -> None:
        code = code_block("""
            let x integer = 5 print x
            let y integer = 10
            print y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 19] Style Error | Statements must be separated by a newline")
    
    def test_multiple_statements_middle_line(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10 print y
            print x + y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 2, Column 20] Style Error | Statements must be separated by a newline")
    
    def test_multiple_statements_last_line(self)  -> None:
        code = code_block("""
            let x integer = 5
            let y integer = 10
            print x print y
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 3, Column 9] Style Error | Statements must be separated by a newline")
    
    def test_multiple_statements_complex_keywords(self)  -> None:
        code = code_block("""
            let x integer = 5
            if x > 0 print x
            print 999
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 2, Column 10] Style Error | Statements must be separated by a newline")
    
    def test_multiple_statements_function_keywords(self)  -> None:
        code = code_block("""
            def add(x integer, y integer) returns integer return x + y
            print add(5, 10)
            print 999
        """).strip()
        with self.assertRaises(StyleError) as cm:
            tokens = tokenize(code)
            validate_style(code, tokens)
        self.assertEqual(str(cm.exception), "[Line 1, Column 47] Style Error | Statements must be separated by a newline")
    
    def test_keywords_in_comments_valid(self)  -> None:
        code = code_block("""
            let x integer = 5 # This comment has let and print keywords
            let y integer = 10
            print x + y
        """).strip()
        
        tokens = tokenize(code)
        validate_style(code, tokens)
    
    def test_valid_single_statements_per_line(self)  -> None:
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