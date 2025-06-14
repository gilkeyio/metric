#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import unittest

from metric.tokenizer import tokenize, Token, IntegerToken, IdentifierToken
from metric.parser import parse, ParseError
from metric.type_checker import type_check, TypeCheckError
from metric.metric_ast import *
from test_utils import code_block


class TestTypeSystem(unittest.TestCase):
    
    def _compile_and_check(self, code: str):
        """Helper to compile code and run type checking."""
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        return ast
    
    def _expect_type_error(self, code: str, expected_message: str):
        """Helper to expect a type error with specific message."""
        tokens = tokenize(code)
        ast = parse(tokens)
        with self.assertRaises(TypeCheckError) as cm:
            type_check(ast)
        self.assertIn(expected_message, str(cm.exception))
    
    def _compile_and_compare(self, code: str, expected_ast):
        """Helper to compile code and compare AST."""
        tokens = tokenize(code)
        ast = parse(tokens)
        self.assertEqual(ast, expected_ast)
        return ast
    
    def test_valid_integer_declaration(self):
        """Test valid integer variable declaration."""
        code = "let x integer = 5"
        expected = [Let("x", Type.INTEGER, IntegerLiteral(5))]
        ast = self._compile_and_compare(code, expected)
        type_check(ast)
    
    def test_valid_boolean_declaration(self):
        """Test valid boolean variable declaration."""
        code = "let flag boolean = true"
        expected = [Let("flag", Type.BOOLEAN, BooleanLiteral(True))]
        ast = self._compile_and_compare(code, expected)
        type_check(ast)
    
    def test_type_mismatch_integer_boolean(self):
        """Test type mismatch: integer variable assigned boolean value."""
        code = "let x integer = true"
        self._expect_type_error(code, "boolean to variable 'x' of type integer")
    
    def test_type_mismatch_boolean_integer(self):
        """Test type mismatch: boolean variable assigned integer value."""
        code = "let flag boolean = 42"
        self._expect_type_error(code, "integer to variable 'flag' of type boolean")
    
    def test_variable_redeclaration_error(self):
        """Test error when variable is declared twice."""
        code = code_block("""
            let x integer = 5
            let x integer = 10
        """)
        tokens = tokenize(code)
        ast = parse(tokens)
        with self.assertRaises(TypeCheckError) as cm:
            type_check(ast)
        self.assertIn("Variable 'x' is already declared", str(cm.exception))
    
    def test_set_statement_type_check(self):
        """Test set statement with correct type."""
        code = code_block("""
            let x integer = 5
            set x = 10
        """)
        self._compile_and_check(code)
    
    def test_set_statement_type_mismatch(self):
        """Test set statement with incorrect type."""
        code = code_block("""
            let x integer = 5
            set x = true
        """)
        tokens = tokenize(code)
        ast = parse(tokens)
        with self.assertRaises(TypeCheckError) as cm:
            type_check(ast)
        self.assertIn("Type mismatch", str(cm.exception))
        self.assertIn("boolean to variable 'x' of type integer", str(cm.exception))
    
    def test_set_undeclared_variable(self):
        """Test set statement on undeclared variable."""
        code = "set x = 5"
        tokens = tokenize(code)
        ast = parse(tokens)
        with self.assertRaises(TypeCheckError) as cm:
            type_check(ast)
        self.assertIn("Variable 'x' is not declared", str(cm.exception))
    
    def test_arithmetic_expressions_type_check(self):
        """Test arithmetic expressions with correct types."""
        code = code_block("""
            let x integer = 5
            let y integer = 10
            let sum integer = x + y
        """)
        tokens = tokenize(code)
        ast = parse(tokens)
        # Should type check without error
        type_check(ast)
    
    def test_comparison_expressions_type_check(self):
        """Test comparison expressions producing boolean."""
        code = code_block("""
            let x integer = 5
            let y integer = 10
            let result boolean = x < y
        """)
        tokens = tokenize(code)
        ast = parse(tokens)
        # Should type check without error
        type_check(ast)
    
    def test_logical_and_type_check(self):
        """Test logical and expressions with boolean operands."""
        code = code_block("""
            let x boolean = true
            let y boolean = false
            let result boolean = x and y
        """)
        self._compile_and_check(code)
    
    def test_logical_or_type_check(self):
        """Test logical or expressions with boolean operands."""
        code = code_block("""
            let x boolean = true
            let y boolean = false
            let result boolean = x or y
        """)
        self._compile_and_check(code)
    
    def test_logical_and_with_literals(self):
        """Test logical and with boolean literals."""
        code = code_block("""
            let result boolean = true and false
        """)
        self._compile_and_check(code)
    
    def test_logical_or_with_literals(self):
        """Test logical or with boolean literals."""
        code = code_block("""
            let result boolean = true or false
        """)
        self._compile_and_check(code)
    
    def test_complex_logical_expression_type_check(self):
        """Test complex logical expressions."""
        code = code_block("""
            let a boolean = true
            let b boolean = false
            let c boolean = true
            let result boolean = (a and b) or c
        """)
        self._compile_and_check(code)
    
    def test_logical_and_type_error_integer_operand(self):
        """Test logical and with integer operand."""
        code = code_block("""
            let x boolean = true
            let y integer = 5
            let result boolean = x and y
        """)
        self._expect_type_error(code, "Operator And requires boolean operands")
    
    def test_logical_or_type_error_integer_operand(self):
        """Test logical or with integer operand."""
        code = code_block("""
            let x boolean = true
            let y integer = 5
            let result boolean = x or y
        """)
        self._expect_type_error(code, "Operator Or requires boolean operands")
    
    def test_logical_and_type_error_float_operand(self):
        """Test logical and with float operand."""
        code = code_block("""
            let x boolean = true
            let y float = 3.14
            let result boolean = x and y
        """)
        self._expect_type_error(code, "Operator And requires boolean operands")
    
    def test_logical_or_type_error_float_operand(self):
        """Test logical or with float operand."""
        code = code_block("""
            let x boolean = true
            let y float = 3.14
            let result boolean = x or y
        """)
        self._expect_type_error(code, "Operator Or requires boolean operands")
    
    def test_logical_and_type_error_both_non_boolean(self):
        """Test logical and with both operands non-boolean."""
        code = code_block("""
            let x integer = 5
            let y integer = 10
            let result boolean = x and y
        """)
        self._expect_type_error(code, "Operator And requires boolean operands")
    
    def test_logical_or_type_error_both_non_boolean(self):
        """Test logical or with both operands non-boolean."""
        code = code_block("""
            let x integer = 5
            let y integer = 10
            let result boolean = x or y
        """)
        self._expect_type_error(code, "Operator Or requires boolean operands")
    
    def test_mixed_comparison_and_logical_type_check(self):
        """Test mixed comparison and logical operations."""
        code = code_block("""
            let x integer = 5
            let y integer = 10
            let z boolean = true
            let result boolean = (x < y) and z
        """)
        self._compile_and_check(code)
    
    def test_logical_not_type_check(self):
        """Test logical not with boolean operand."""
        code = code_block("""
            let x boolean = true
            let result boolean = not x
        """)
        self._compile_and_check(code)
    
    def test_logical_not_with_boolean_literal(self):
        """Test logical not with boolean literal."""
        code = code_block("""
            let result boolean = not true
        """)
        self._compile_and_check(code)
    
    def test_logical_not_with_expression(self):
        """Test logical not with complex boolean expression."""
        code = code_block("""
            let x boolean = true
            let y boolean = false
            let result boolean = not (x and y)
        """)
        self._compile_and_check(code)
    
    def test_logical_not_type_error_integer_operand(self):
        """Test type error when using not with integer operand."""
        code = code_block("""
            let x integer = 5
            let result boolean = not x
        """)
        self._expect_type_error(code, "Operator 'not' requires boolean operand")
    
    def test_logical_not_type_error_float_operand(self):
        """Test type error when using not with float operand."""
        code = code_block("""
            let x float = 5.0
            let result boolean = not x
        """)
        self._expect_type_error(code, "Operator 'not' requires boolean operand")
    
    def test_double_logical_not_type_check(self):
        """Test double logical not."""
        code = code_block("""
            let x boolean = true
            let result boolean = not not x
        """)
        self._compile_and_check(code)
    
    def test_logical_not_precedence_with_and(self):
        """Test logical not precedence with and operator."""
        code = code_block("""
            let x boolean = true
            let y boolean = false
            let result boolean = not x and y
        """)
        self._compile_and_check(code)
    
    def test_logical_not_precedence_with_or(self):
        """Test logical not precedence with or operator."""
        code = code_block("""
            let x boolean = false
            let y boolean = true
            let result boolean = not x or y
        """)
        self._compile_and_check(code)
    
    def test_logical_not_precedence_with_comparison(self):
        """Test logical not with comparison operators."""
        code = code_block("""
            let x integer = 10
            let result boolean = not x > 5
        """)
        self._compile_and_check(code)
    
    def test_complex_logical_not_precedence(self):
        """Test complex expression with not precedence."""
        code = code_block("""
            let x boolean = true
            let y boolean = false
            let z boolean = true
            let result boolean = not x and y or z
        """)
        self._compile_and_check(code)
    
    def test_if_condition_type_check(self):
        """Test if statement with boolean condition."""
        code = code_block("""
            let flag boolean = true
            if flag
                print 1
        """)
        tokens = tokenize(code)
        ast = parse(tokens)
        # Should type check without error
        type_check(ast)
    
    def test_if_condition_type_error(self):
        """Test if statement with non-boolean condition."""
        code = code_block("""
            let x integer = 5
            if x
                print 1
        """)
        tokens = tokenize(code)
        ast = parse(tokens)
        with self.assertRaises(TypeCheckError) as cm:
            type_check(ast)
        self.assertIn("If condition must be boolean", str(cm.exception))
    
    def test_while_condition_type_check(self):
        """Test while statement with boolean condition."""
        code = code_block("""
            let flag boolean = true
            while flag
                set flag = false
        """)
        tokens = tokenize(code)
        ast = parse(tokens)
        # Should type check without error
        type_check(ast)
    
    def test_while_condition_type_error(self):
        """Test while statement with non-boolean condition."""
        code = code_block("""
            let x integer = 5
            while x
                set x = 0
        """)
        tokens = tokenize(code)
        ast = parse(tokens)
        with self.assertRaises(TypeCheckError) as cm:
            type_check(ast)
        self.assertIn("While condition must be boolean", str(cm.exception))
    
    def test_undeclared_variable_usage(self):
        """Test using undeclared variable in expression."""
        code = "print x"
        tokens = tokenize(code)
        ast = parse(tokens)
        with self.assertRaises(TypeCheckError) as cm:
            type_check(ast)
        self.assertIn("Variable 'x' is not declared", str(cm.exception))
    
    def test_complex_valid_program(self):
        """Test complex but valid typed program."""
        code = code_block("""
            let x integer = 10
            let y integer = 5
            let sum integer = x + y
            let isLarge boolean = sum > 12
            if isLarge
                print sum
                let bonus integer = 100
                print bonus
            while x > 0
                print x
                set x = x - 1
        """)
        tokens = tokenize(code)
        ast = parse(tokens)
        # Should type check without error
        type_check(ast)
    
    def test_parser_error_missing_type(self):
        """Test parser error when type annotation is missing."""
        tokens = [Token.LET, IdentifierToken("x"), Token.EQUALS, IntegerToken(5)]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertIn("Expected 'let identifier type = expression'", str(cm.exception))
    
    def test_parser_error_invalid_type(self):
        """Test parser error when invalid type is provided."""
        tokens = [Token.LET, IdentifierToken("x"), IdentifierToken("string"), Token.EQUALS, IntegerToken(5)]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertIn("Expected type annotation (integer, boolean, or float)", str(cm.exception))
    
    def test_parser_error_missing_equals(self):
        """Test parser error when equals is missing after type."""
        tokens = [Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, IntegerToken(5)]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertIn("Expected 'let identifier type = expression'", str(cm.exception))
    
    def test_modulus_operation_type_check(self):
        """Test modulus operation type checking."""
        code = code_block("""
            let remainder integer = 10 % 3
        """)
        self._compile_and_check(code)
    
    def test_modulus_type_mismatch(self):
        """Test modulus with non-integer operands."""
        code = code_block("""
            let x integer = 5
            let flag boolean = true
            let result integer = x % flag
        """)
        self._expect_type_error(code, "Operator Modulus requires integer operands")
    
    # Float type system tests
    def test_valid_float_declaration(self):
        """Test valid float variable declaration."""
        code = "let pi float = 3.14"
        expected = [Let("pi", Type.FLOAT, FloatLiteral(3.14))]
        ast = self._compile_and_compare(code, expected)
        type_check(ast)
    
    def test_float_arithmetic_type_check(self):
        """Test float arithmetic expressions."""
        code = code_block("""
            let x float = 2.5
            let y float = 1.5
            let sum float = x + y
        """)
        self._compile_and_check(code)
    
    def test_mixed_arithmetic_type_check(self):
        """Test mixed integer/float arithmetic."""
        code = code_block("""
            let x integer = 5
            let y float = 2.5
            let result float = x + y
        """)
        self._compile_and_check(code)
    
    def test_float_comparison_type_check(self):
        """Test float comparison expressions."""
        code = code_block("""
            let x float = 3.14
            let y float = 2.5
            let result boolean = x > y
        """)
        self._compile_and_check(code)
    
    def test_type_mismatch_float_integer(self):
        """Test type mismatch: float variable assigned integer value."""
        code = "let x float = 42"
        self._expect_type_error(code, "integer to variable 'x' of type float")
    
    def test_type_mismatch_integer_float(self):
        """Test type mismatch: integer variable assigned float value."""
        code = "let x integer = 3.14"
        self._expect_type_error(code, "float to variable 'x' of type integer")
    
    def test_type_mismatch_boolean_float(self):
        """Test type mismatch: boolean variable assigned float value."""
        code = "let flag boolean = 3.14"
        self._expect_type_error(code, "float to variable 'flag' of type boolean")
    
    def test_float_set_statement_type_check(self):
        """Test set statement with float type."""
        code = code_block("""
            let pi float = 3.0
            set pi = 3.14159
        """)
        self._compile_and_check(code)
    
    def test_float_set_statement_type_mismatch(self):
        """Test set statement with incorrect float type."""
        code = code_block("""
            let pi float = 3.14
            set pi = 42
        """)
        self._expect_type_error(code, "integer to variable 'pi' of type float")
    
    def test_float_division_result_type(self):
        """Test that division with floats returns float type."""
        code = code_block("""
            let x float = 7.5
            let y float = 2.5
            let result float = x / y
        """)
        self._compile_and_check(code)
    
    def test_mixed_division_type_promotion(self):
        """Test mixed integer/float division type promotion."""
        code = code_block("""
            let x integer = 7
            let y float = 2.0
            let result float = x / y
        """)
        self._compile_and_check(code)
    
    # Function type checking tests
    def test_simple_function_declaration(self):
        """Test that a simple function declaration type checks correctly."""
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
        """)
        # Should not raise any errors
        self._compile_and_check(code)
    
    def test_function_call_type_check(self):
        """Test that function calls are type checked correctly."""
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
            let result integer = add(5, 10)
        """)
        # Should not raise any errors
        self._compile_and_check(code)
    
    def test_function_call_wrong_argument_count(self):
        """Test that function calls with wrong argument count cause error."""
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
            let result integer = add(5)
        """)
        self._expect_type_error(code, "Function 'add' expects 2 arguments, got 1")
    
    def test_function_call_wrong_argument_type(self):
        """Test that function calls with wrong argument types cause error."""
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
            let result integer = add(5, true)
        """)
        self._expect_type_error(code, "Argument 2 to function 'add': expected integer, got boolean")
    
    def test_function_missing_return_statement(self):
        """Test that functions without return statements cause error."""
        code = code_block("""
            def add(x integer, y integer) returns integer
                let z integer = x + y
        """)
        self._expect_type_error(code, "Function 'add' must have a return statement")
    
    def test_function_return_type_mismatch(self):
        """Test that return type mismatches cause error."""
        code = code_block("""
            def add(x integer, y integer) returns integer
                return true
        """)
        self._expect_type_error(code, "Return type mismatch: expected integer, got boolean")
    
    def test_function_redeclaration_error(self):
        """Test that redeclaring a function causes error."""
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
            def add(a integer, b integer) returns integer
                return a - b
        """)
        self._expect_type_error(code, "Function 'add' is already declared")
    
    def test_return_outside_function_error(self):
        """Test that return statements outside functions cause error."""
        code = "return 5"
        self._expect_type_error(code, "Return statement must be inside a function")
    
    # Comprehensive List Type System Tests
    def test_valid_list_declaration_integer(self):
        """Test valid list declaration with integer elements."""
        code = "let nums list of integer = [1, 2, 3]"
        self._compile_and_check(code)
    
    def test_valid_list_declaration_boolean(self):
        """Test valid list declaration with boolean elements."""
        code = "let flags list of boolean = [true, false, true]"
        self._compile_and_check(code)
    
    def test_valid_list_declaration_float(self):
        """Test valid list declaration with float elements."""
        code = "let values list of float = [1.5, 2.0, 3.14]"
        self._compile_and_check(code)
    
    def test_valid_empty_list_declaration(self):
        """Test valid empty list declaration."""
        code = "let empty list of integer = repeat(0, 0)"
        self._compile_and_check(code)
    
    def test_list_homogeneity_type_error_integer_boolean(self):
        """Test list homogeneity error: mixing integers and booleans."""
        code = "let mixed list of integer = [1, true, 3]"
        self._expect_type_error(code, "List elements must be homogeneous")
    
    def test_list_homogeneity_type_error_float_integer(self):
        """Test list homogeneity error: mixing floats and integers."""
        code = "let mixed list of float = [1.5, 42, 3.14]"
        self._expect_type_error(code, "List elements must be homogeneous")
    
    def test_list_homogeneity_type_error_boolean_integer(self):
        """Test list homogeneity error: mixing booleans and integers."""
        code = "let mixed list of boolean = [true, 5, false]"
        self._expect_type_error(code, "List elements must be homogeneous")
    
    def test_list_type_annotation_mismatch_integer(self):
        """Test list type annotation mismatch: declared integer, contains boolean."""
        code = "let nums list of integer = [true, false]"
        self._expect_type_error(code, "cannot assign list of boolean to variable 'nums' of type list of integer")
    
    def test_list_type_annotation_mismatch_boolean(self):
        """Test list type annotation mismatch: declared boolean, contains integer."""
        code = "let flags list of boolean = [1, 2, 3]"
        self._expect_type_error(code, "cannot assign list of integer to variable 'flags' of type list of boolean")
    
    def test_repeat_function_type_check_integer(self):
        """Test repeat function with integer value."""
        code = "let zeros list of integer = repeat(0, 5)"
        self._compile_and_check(code)
    
    def test_repeat_function_type_check_boolean(self):
        """Test repeat function with boolean value."""
        code = "let flags list of boolean = repeat(true, 3)"
        self._compile_and_check(code)
    
    def test_repeat_function_type_check_float(self):
        """Test repeat function with float value."""
        code = "let values list of float = repeat(3.14, 2)"
        self._compile_and_check(code)
    
    def test_repeat_function_type_mismatch_value(self):
        """Test repeat function with wrong value type."""
        code = "let nums list of integer = repeat(true, 5)"
        self._expect_type_error(code, "cannot assign list of boolean to variable 'nums' of type list of integer")
    
    def test_repeat_function_type_mismatch_count(self):
        """Test repeat function with non-integer count."""
        code = "let nums list of integer = repeat(0, true)"
        self._expect_type_error(code, "Repeat count must be integer")
    
    def test_len_function_type_check(self):
        """Test len function returns integer."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            let length integer = len(nums)
        """)
        self._compile_and_check(code)
    
    def test_len_function_on_non_list(self):
        """Test len function type error on non-list."""
        code = code_block("""
            let x integer = 5
            print len(x)
        """)
        self._expect_type_error(code, "Cannot get length of non-list")
    
    def test_list_access_type_check(self):
        """Test list access returns correct element type."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            let first integer = nums[0]
        """)
        self._compile_and_check(code)
    
    def test_list_access_wrong_index_type(self):
        """Test list access with non-integer index."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            print nums[true]
        """)
        self._expect_type_error(code, "List index must be integer")
    
    def test_list_access_on_non_list(self):
        """Test list access type error on non-list."""
        code = code_block("""
            let x integer = 5
            print x[0]
        """)
        self._expect_type_error(code, "Cannot index into non-list")
    
    def test_list_assignment_type_check(self):
        """Test list assignment with correct type."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            set nums[1] = 42
        """)
        self._compile_and_check(code)
    
    def test_list_assignment_type_mismatch(self):
        """Test list assignment with wrong value type."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            set nums[1] = true
        """)
        self._expect_type_error(code, "cannot assign boolean to list element of type integer")
    
    def test_list_assignment_wrong_index_type(self):
        """Test list assignment with non-integer index."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            set nums[true] = 42
        """)
        self._expect_type_error(code, "List index must be integer")
    
    def test_list_assignment_on_non_list(self):
        """Test list assignment on non-list variable."""
        code = code_block("""
            let x integer = 5
            set x[0] = 42
        """)
        self._expect_type_error(code, "Cannot index into non-list variable 'x' of type integer")
    
    def test_list_with_variable_elements_type_check(self):
        """Test list with variable elements of correct type."""
        code = code_block("""
            let x integer = 10
            let y integer = 20
            let nums list of integer = [x, y, 30]
        """)
        self._compile_and_check(code)
    
    def test_list_with_expression_elements_type_check(self):
        """Test list with expression elements of correct type."""
        code = code_block("""
            let x integer = 10
            let y integer = 20
            let computed list of integer = [x + 1, y * 2]
        """)
        self._compile_and_check(code)
    
    def test_list_with_wrong_variable_type(self):
        """Test list with variable elements of wrong type."""
        code = code_block("""
            let x integer = 10
            let flag boolean = true
            let nums list of integer = [x, flag]
        """)
        self._expect_type_error(code, "List elements must be homogeneous")
    
    def test_list_with_wrong_expression_type(self):
        """Test list with expression elements of wrong type."""
        code = code_block("""
            let x integer = 10
            let computed list of integer = [x + 1, x > 5]
        """)
        self._expect_type_error(code, "List elements must be homogeneous")
    
    def test_nested_list_operations_type_check(self):
        """Test complex nested list operations."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            let length integer = len(nums)
            let doubled list of integer = repeat(nums[0] * 2, length)
        """)
        self._compile_and_check(code)
    
    def test_list_in_function_parameter_type_check(self):
        """Test list type in function parameter."""
        code = code_block("""
            def getfirst(data list of integer) returns integer
                return data[0]
            let nums list of integer = [1, 2, 3]
            let first integer = getfirst(nums)
        """)
        self._compile_and_check(code)
    
    def test_list_function_parameter_type_mismatch(self):
        """Test list function parameter with wrong argument type."""
        code = code_block("""
            def getfirst(data list of integer) returns integer
                return data[0]
            let x integer = 5
            let first integer = getfirst(x)
        """)
        self._expect_type_error(code, "expected list of integer, got integer")
    
    def test_list_function_parameter_element_type_mismatch(self):
        """Test list function parameter with wrong element type."""
        code = code_block("""
            def getfirst(data list of integer) returns integer
                return data[0]
            let flags list of boolean = [true, false]
            let first integer = getfirst(flags)
        """)
        self._expect_type_error(code, "expected list of integer, got list of boolean")
    
    def test_list_return_type_check(self):
        """Test function returning list type."""
        code = code_block("""
            def makelist() returns list of integer
                return [1, 2, 3]
            let nums list of integer = makelist()
        """)
        self._compile_and_check(code)
    
    def test_list_return_type_mismatch(self):
        """Test function returning wrong list type."""
        code = code_block("""
            def makelist() returns list of integer
                return [true, false]
            let nums list of integer = makelist()
        """)
        self._expect_type_error(code, "Return type mismatch: expected list of integer")
    
    def test_list_return_element_type_mismatch(self):
        """Test function returning list with wrong element type."""
        code = code_block("""
            def makelist() returns list of integer
                return repeat(true, 3)
            let nums list of integer = makelist()
        """)
        self._expect_type_error(code, "Return type mismatch: expected list of integer, got list of boolean")
    
    def test_complex_list_program_type_check(self):
        """Test complex program with multiple list operations."""
        code = code_block("""
            def sumlist(nums list of integer) returns integer
                let total integer = 0
                let i integer = 0
                while i < len(nums)
                    set total = total + nums[i]
                    set i = i + 1
                return total

            def createlist(size integer, value integer) returns list of integer
                return repeat(value, size)

            let data list of integer = [1, 2, 3, 4, 5]
            let sum integer = sumlist(data)
            let zeros list of integer = createlist(sum, 0)
            set zeros[0] = len(data)
            let final integer = zeros[0]
        """)
        self._compile_and_check(code)
    
    def test_list_variable_shadowing_type_check(self):
        """Test list variable shadowing in different scopes."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            if true
                let other list of boolean = [true, false]
                print other[0]
            print nums[0]
        """)
        self._compile_and_check(code)
    
    def test_empty_list_works_with_repeat(self):
        """Test that empty lists work using repeat."""
        code = "let empty list of integer = repeat(0, 0)"
        # This should work fine since we have explicit typing
        self._compile_and_check(code)
    
    def test_list_operations_with_variables_work(self):
        """Test that list operations with proper variable names work."""
        code = code_block("""
            let first list of integer = [1, 2, 3]
            let second list of integer = [4, 5, 6]
            let result integer = first[0] + second[0]
        """)
        self._compile_and_check(code)


if __name__ == '__main__':
    unittest.main()