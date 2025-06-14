#!/usr/bin/env python3

import sys
import os
import unittest

# Add the test directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from metric.parser import parse, ParseError
from metric.tokenizer import TokenType, tokenize, Token, IntegerToken, IdentifierToken
from metric.metric_ast import *
from test_utils import code_block


class TestParser(unittest.TestCase):
    
    # Helper methods for cleaner test construction
    def _parse_expression(self, code: str) -> Sequence[Statement]:
        """Helper to parse code string directly."""
        tokens: list[TokenType] =tokenize(code)
        return parse(tokens)
    
    def _assert_parse_equals(self, code: str, expected_ast: List[Statement]):
        """Helper to parse and assert equality."""
        actual_ast = self._parse_expression(code)
        self.assertEqual(actual_ast, expected_ast)
    
    def _assert_parse_error(self, code: str, expected_error: str):
        """Helper to assert parse errors."""
        with self.assertRaises(ParseError) as cm:
            self._parse_expression(code)
        self.assertEqual(str(cm.exception), expected_error)
    
    def _let_stmt(self, name: str, type_: Type, expr: Expression) -> Let:
        """Helper to create Let statements."""
        return Let(name, type_, expr)
    
    def _print_stmt(self, expr: Expression) -> Print:
        """Helper to create Print statements."""
        return Print(expr)
    
    def _set_stmt(self, name: str, expr: Expression) -> Set:
        """Helper to create Set statements."""
        return Set(name, expr)
    
    def _if_stmt(self, condition: Expression, body: List[Statement]) -> If:
        """Helper to create If statements."""
        return If(condition, body)
    
    def _while_stmt(self, condition: Expression, body: List[Statement]) -> While:
        """Helper to create While statements."""
        return While(condition, body)
    
    def _binary_expr(self, left: Expression, op: BinaryOperator, right: Expression) -> BinaryExpression:
        """Helper to create binary expressions."""
        return BinaryExpression(left, op, right)
    
    def _int_lit(self, value: int) -> IntegerLiteral:
        """Helper to create integer literals."""
        return IntegerLiteral(value)
    
    def _float_lit(self, value: float) -> FloatLiteral:
        """Helper to create float literals."""
        return FloatLiteral(value)
    
    def _bool_lit(self, value: bool) -> BooleanLiteral:
        """Helper to create boolean literals."""
        return BooleanLiteral(value)
    
    def _var(self, name: str) -> Variable:
        """Helper to create variables."""
        return Variable(name)
    
    def _comment(self) -> Comment:
        """Helper to create comments."""
        return Comment()
    
    def _unary_expr(self, op: 'UnaryOperator', operand: Expression) -> 'UnaryExpression':
        """Helper to create unary expressions."""
        return UnaryExpression(op, operand)
    
    # Simple expression tests
    def test_parse_simple_integer(self):
        expected: list[Statement] = [self._let_stmt("x", Type.INTEGER, self._int_lit(42))]
        self._assert_parse_equals("let x integer = 42", expected)
    
    def test_parse_simple_variable_reference(self):
        expected: List[Statement] = [self._print_stmt(self._var("x"))]
        self._assert_parse_equals("print x", expected)
    
    def test_parse_simple_addition(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER, 
                    self._binary_expr(self._int_lit(1), BinaryOperator.ADDITION, self._int_lit(2)))]
        self._assert_parse_equals("let result integer = 1 + 2", expected)
    
    def test_parse_simple_subtraction(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._int_lit(5), BinaryOperator.SUBTRACTION, self._int_lit(3)))]
        self._assert_parse_equals("let result integer = 5 - 3", expected)
    
    def test_parse_simple_multiplication(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._int_lit(3), BinaryOperator.MULTIPLICATION, self._int_lit(4)))]
        self._assert_parse_equals("let result integer = 3 * 4", expected)
    
    def test_parse_simple_division(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._int_lit(8), BinaryOperator.DIVISION, self._int_lit(2)))]
        self._assert_parse_equals("let result integer = 8 / 2", expected)
    
    def test_parse_variable_arithmetic(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._var("x"), BinaryOperator.ADDITION, self._var("y")))]
        self._assert_parse_equals("let result integer = x + y", expected)
    
    # Operator precedence tests
    def test_parse_operator_precedence_multiply_first(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._int_lit(1), BinaryOperator.ADDITION,
                                    self._binary_expr(self._int_lit(2), BinaryOperator.MULTIPLICATION, self._int_lit(3))))]
        self._assert_parse_equals("let result integer = 1 + 2 * 3", expected)
    
    def test_parse_operator_precedence_divide_first(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._int_lit(10), BinaryOperator.SUBTRACTION,
                                    self._binary_expr(self._int_lit(6), BinaryOperator.DIVISION, self._int_lit(2))))]
        self._assert_parse_equals("let result integer = 10 - 6 / 2", expected)
    
    def test_parse_left_associative_addition(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._binary_expr(self._int_lit(1), BinaryOperator.ADDITION, self._int_lit(2)),
                                    BinaryOperator.ADDITION, self._int_lit(3)))]
        self._assert_parse_equals("let result integer = 1 + 2 + 3", expected)
    
    def test_parse_left_associative_multiplication(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._binary_expr(self._int_lit(2), BinaryOperator.MULTIPLICATION, self._int_lit(3)),
                                    BinaryOperator.MULTIPLICATION, self._int_lit(4)))]
        self._assert_parse_equals("let result integer = 2 * 3 * 4", expected)
    
    # Parentheses tests
    def test_parse_parentheses_simple(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER, self._int_lit(5))]
        self._assert_parse_equals("let result integer = (5)", expected)
    
    def test_parse_parentheses_override_precedence(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._binary_expr(self._int_lit(1), BinaryOperator.ADDITION, self._int_lit(2)),
                                    BinaryOperator.MULTIPLICATION, self._int_lit(3)))]
        self._assert_parse_equals("let result integer = (1 + 2) * 3", expected)
    
    def test_parse_nested_parentheses(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._binary_expr(self._int_lit(1), BinaryOperator.ADDITION, self._int_lit(2)),
                                    BinaryOperator.MULTIPLICATION, self._int_lit(3)))]
        self._assert_parse_equals("let result integer = ((1 + 2) * 3)", expected)
    
    def test_parse_complex_expression(self):
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._int_lit(1), BinaryOperator.ADDITION,
                                    self._binary_expr(
                                        self._binary_expr(self._int_lit(2), BinaryOperator.MULTIPLICATION,
                                                        self._binary_expr(self._int_lit(3), BinaryOperator.SUBTRACTION, self._int_lit(4))),
                                        BinaryOperator.DIVISION, self._int_lit(5))))]
        self._assert_parse_equals("let result integer = 1 + 2 * (3 - 4) / 5", expected)
    
    # Statement tests
    def test_parse_print_statement_integer(self):
        expected: List[Statement] = [self._print_stmt(self._int_lit(42))]
        self._assert_parse_equals("print 42", expected)
    
    def test_parse_print_statement_expression(self):
        expected: List[Statement] = [self._print_stmt(self._binary_expr(self._int_lit(10), BinaryOperator.MULTIPLICATION, self._int_lit(5)))]
        self._assert_parse_equals("print 10 * 5", expected)
    
    # Full program parsing tests
    def test_parse_empty_program(self):
        expected: List[Statement] = []
        self._assert_parse_equals("", expected)
    
    def test_parse_multiple_statements(self):
        expected: List[Statement] = [
            self._let_stmt("x", Type.INTEGER, self._int_lit(5)),
            self._print_stmt(self._var("x"))
        ]
        self._assert_parse_equals("let x integer = 5\nprint x", expected)
    
    def test_parse_program_with_expressions(self):
        expected: List[Statement] = [
            self._let_stmt("a", Type.INTEGER, self._int_lit(10)),
            self._let_stmt("b", Type.INTEGER, self._binary_expr(self._int_lit(5), BinaryOperator.ADDITION, self._int_lit(3))),
            self._print_stmt(self._binary_expr(self._var("a"), BinaryOperator.MULTIPLICATION, self._var("b")))
        ]
        self._assert_parse_equals("let a integer = 10\nlet b integer = 5 + 3\nprint a * b", expected)
    
    def test_parse_statement_separators_only(self):
        # Using tokens directly for this edge case
        tokens: list[TokenType] = [Token.STATEMENT_SEPARATOR, Token.STATEMENT_SEPARATOR]
        ast = parse(tokens)
        self.assertEqual(ast, [])
    
    def test_parse_trailing_statement_separator(self):
        # Using tokens directly for this edge case  
        tokens: list[TokenType] =[Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, IntegerToken(1), Token.STATEMENT_SEPARATOR]
        ast = parse(tokens)
        expected: List[Statement] = [Let("x", Type.INTEGER, IntegerLiteral(1))]
        self.assertEqual(ast, expected)
    
    # Error handling tests
    def test_parse_error_empty_tokens(self):
        tokens: list[TokenType] =[]
        ast = parse(tokens)
        self.assertEqual(ast, [])
    
    def test_parse_error_invalid_statement(self):
        tokens: list[TokenType] =[IntegerToken(5)]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertEqual(str(cm.exception), "Expected 'let', 'print', 'if', 'while', 'set', 'def', 'return', or comment statement")
    
    def test_parse_error_let_missing_identifier(self):
        tokens: list[TokenType] =[Token.LET, Token.EQUALS, IntegerToken(5)]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertEqual(str(cm.exception), "Expected 'let identifier type = expression'")
    
    def test_parse_error_let_missing_equals(self):
        tokens: list[TokenType] =[Token.LET, IdentifierToken("x"), IntegerToken(5)]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertEqual(str(cm.exception), "Expected 'let identifier type = expression'")
    
    def test_parse_error_unmatched_parenthesis(self):
        tokens: list[TokenType] =[Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, Token.LEFT_PARENTHESIS, IntegerToken(5)]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertEqual(str(cm.exception), "Expected closing parenthesis")
    
    def test_parse_error_expression_invalid_token(self):
        tokens: list[TokenType] =[Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, Token.PLUS]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertEqual(str(cm.exception), "Expected integer, float, identifier, boolean, or opening parenthesis")
    
    # Integration tests with actual tokenizer
    def test_parse_from_string_simple(self):
        code = "let x integer = 5"
        tokens: list[TokenType] =tokenize(code)
        ast = parse(tokens)
        expected: List[Statement] = [Let("x", Type.INTEGER, IntegerLiteral(5))]
        self.assertEqual(ast, expected)
    
    def test_parse_from_string_complex(self):
        code = "let result integer = (10 + 5) * 2\nprint result"
        tokens: list[TokenType] =tokenize(code)
        ast = parse(tokens)
        expected: List[Statement] = [
            Let("result", Type.INTEGER, BinaryExpression(BinaryExpression(IntegerLiteral(10), BinaryOperator.ADDITION, IntegerLiteral(5)), BinaryOperator.MULTIPLICATION, IntegerLiteral(2))),
            Print(Variable("result"))
        ]
        self.assertEqual(ast, expected)
    
    def test_parse_arithmetic_precedence_integration(self):
        code = "let x integer = 1 + 2 * 3 + 4"
        tokens: list[TokenType] =tokenize(code)
        ast = parse(tokens)
        expected: List[Statement] = [
            Let("x", Type.INTEGER, BinaryExpression(
                BinaryExpression(IntegerLiteral(1), BinaryOperator.ADDITION, BinaryExpression(IntegerLiteral(2), BinaryOperator.MULTIPLICATION, IntegerLiteral(3))),
                BinaryOperator.ADDITION,
                IntegerLiteral(4)
            ))
        ]
        self.assertEqual(ast, expected)
    
    # Boolean literal tests
    def test_parse_true_literal(self):
        expected: List[Statement] = [self._let_stmt("x", Type.BOOLEAN, self._bool_lit(True))]
        self._assert_parse_equals("let x boolean = true", expected)
    
    def test_parse_false_literal(self):
        expected: List[Statement] = [self._let_stmt("x", Type.BOOLEAN, self._bool_lit(False))]
        self._assert_parse_equals("let x boolean = false", expected)
    
    def test_parse_print_boolean(self):
        expected: List[Statement] = [self._print_stmt(self._bool_lit(True))]
        self._assert_parse_equals("print true", expected)
    
    # Comparison operator tests
    def test_parse_less_than(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN, 
                    self._binary_expr(self._int_lit(5), BinaryOperator.LESS_THAN, self._int_lit(10)))]
        self._assert_parse_equals("let result boolean = 5 < 10", expected)
    
    def test_parse_greater_than(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(self._int_lit(10), BinaryOperator.GREATER_THAN, self._int_lit(5)))]
        self._assert_parse_equals("let result boolean = 10 > 5", expected)
    
    def test_parse_less_than_or_equal(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(self._int_lit(5), BinaryOperator.LESS_THAN_OR_EQUAL, self._int_lit(10)))]
        self._assert_parse_equals("let result boolean = 5 <= 10", expected)
    
    def test_parse_greater_than_or_equal(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(self._int_lit(10), BinaryOperator.GREATER_THAN_OR_EQUAL, self._int_lit(5)))]
        self._assert_parse_equals("let result boolean = 10 >= 5", expected)
    
    def test_parse_equal_equal(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(self._int_lit(5), BinaryOperator.EQUAL_EQUAL, self._int_lit(5)))]
        self._assert_parse_equals("let result boolean = 5 == 5", expected)
    
    def test_parse_not_equal(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(self._int_lit(5), BinaryOperator.NOT_EQUAL, self._int_lit(3)))]
        self._assert_parse_equals("let result boolean = 5 != 3", expected)
    
    # Logical operator tests
    def test_parse_and_operator(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(self._bool_lit(True), BinaryOperator.AND, self._bool_lit(False)))]
        self._assert_parse_equals("let result boolean = true and false", expected)
    
    def test_parse_or_operator(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(self._bool_lit(True), BinaryOperator.OR, self._bool_lit(False)))]
        self._assert_parse_equals("let result boolean = true or false", expected)
    
    def test_parse_and_with_variables(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(self._var("x"), BinaryOperator.AND, self._var("y")))]
        self._assert_parse_equals("let result boolean = x and y", expected)
    
    def test_parse_or_with_variables(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(self._var("x"), BinaryOperator.OR, self._var("y")))]
        self._assert_parse_equals("let result boolean = x or y", expected)
    
    def test_parse_complex_logical_expression(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(
                        self._binary_expr(self._var("a"), BinaryOperator.AND, self._var("b")),
                        BinaryOperator.OR,
                        self._var("c")
                    ))]
        self._assert_parse_equals("let result boolean = (a and b) or c", expected)
    
    def test_parse_logical_precedence(self):
        # AND should have higher precedence than OR (a or b and c) -> (a or (b and c))
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(
                        self._var("a"),
                        BinaryOperator.OR,
                        self._binary_expr(self._var("b"), BinaryOperator.AND, self._var("c"))
                    ))]
        self._assert_parse_equals("let result boolean = a or b and c", expected)
    
    def test_parse_mixed_comparison_and_logical(self):
        # x > 5 and y < 10
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(
                        self._binary_expr(self._var("x"), BinaryOperator.GREATER_THAN, self._int_lit(5)),
                        BinaryOperator.AND,
                        self._binary_expr(self._var("y"), BinaryOperator.LESS_THAN, self._int_lit(10))
                    ))]
        self._assert_parse_equals("let result boolean = x > 5 and y < 10", expected)
    
    def test_parse_logical_not_with_boolean_literal(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._unary_expr(UnaryOperator.NOT, self._bool_lit(True)))]
        self._assert_parse_equals("let result boolean = not true", expected)
    
    def test_parse_logical_not_with_variable(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._unary_expr(UnaryOperator.NOT, self._var("x")))]
        self._assert_parse_equals("let result boolean = not x", expected)
    
    def test_parse_logical_not_with_parentheses(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._unary_expr(UnaryOperator.NOT, 
                        self._binary_expr(self._var("x"), BinaryOperator.AND, self._var("y"))))]
        self._assert_parse_equals("let result boolean = not (x and y)", expected)
    
    def test_parse_complex_logical_with_not(self):
        # not x and y -> (not x) and y
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(
                        self._unary_expr(UnaryOperator.NOT, self._var("x")),
                        BinaryOperator.AND,
                        self._var("y")
                    ))]
        self._assert_parse_equals("let result boolean = not x and y", expected)
    
    def test_parse_double_not(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._unary_expr(UnaryOperator.NOT, 
                        self._unary_expr(UnaryOperator.NOT, self._bool_lit(True))))]
        self._assert_parse_equals("let result boolean = not not true", expected)
    
    def test_parse_not_precedence_higher_than_and(self):
        # not x and y should parse as (not x) and y
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(
                        self._unary_expr(UnaryOperator.NOT, self._var("x")),
                        BinaryOperator.AND,
                        self._var("y")
                    ))]
        self._assert_parse_equals("let result boolean = not x and y", expected)
    
    def test_parse_not_precedence_higher_than_or(self):
        # not x or y should parse as (not x) or y
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(
                        self._unary_expr(UnaryOperator.NOT, self._var("x")),
                        BinaryOperator.OR,
                        self._var("y")
                    ))]
        self._assert_parse_equals("let result boolean = not x or y", expected)
    
    def test_parse_not_precedence_with_comparison(self):
        # not x > 5 should parse as not (x > 5)
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._unary_expr(UnaryOperator.NOT,
                        self._binary_expr(self._var("x"), BinaryOperator.GREATER_THAN, self._int_lit(5))))]
        self._assert_parse_equals("let result boolean = not x > 5", expected)
    
    def test_parse_complex_not_precedence(self):
        # not x and y or z should parse as ((not x) and y) or z
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(
                        self._binary_expr(
                            self._unary_expr(UnaryOperator.NOT, self._var("x")),
                            BinaryOperator.AND,
                            self._var("y")
                        ),
                        BinaryOperator.OR,
                        self._var("z")
                    ))]
        self._assert_parse_equals("let result boolean = not x and y or z", expected)
    
    # Mixed boolean and comparison tests
    def test_parse_comparison_with_variables(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN, 
                    self._binary_expr(self._var("x"), BinaryOperator.GREATER_THAN, self._var("y")))]
        self._assert_parse_equals("let result boolean = x > y", expected)
    
    def test_parse_boolean_from_string(self):
        expected: List[Statement] = [self._let_stmt("isTrue", Type.BOOLEAN, self._bool_lit(True))]
        self._assert_parse_equals("let isTrue boolean = true", expected)
    
    def test_parse_comparison_from_string(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN, 
                    self._binary_expr(self._var("x"), BinaryOperator.LESS_THAN, self._var("y")))]
        self._assert_parse_equals("let result boolean = x < y", expected)
    
    # If statement tests
    def test_parse_simple_if_statement(self):
        expected: List[Statement] = [self._if_stmt(self._bool_lit(True), [self._print_stmt(self._int_lit(5))])]
        self._assert_parse_equals("if true\n    print 5", expected)
    
    def test_parse_if_with_expression(self):
        expected: List[Statement] = [self._if_stmt(self._binary_expr(self._var("x"), BinaryOperator.GREATER_THAN, self._int_lit(5)), 
                                 [self._print_stmt(self._var("x"))])]
        self._assert_parse_equals("if x > 5\n    print x", expected)
    
    def test_parse_if_with_multiple_statements(self):
        expected: List[Statement] = [self._if_stmt(self._bool_lit(True), 
                                 [self._let_stmt("x", Type.INTEGER, self._int_lit(5)), 
                                  self._print_stmt(self._var("x"))])]
        self._assert_parse_equals("if true\n    let x integer = 5\n    print x", expected)
    
    def test_parse_if_followed_by_regular_statement(self):
        expected: List[Statement] = [self._if_stmt(self._bool_lit(True), [self._print_stmt(self._int_lit(1))]), 
                   self._print_stmt(self._int_lit(2))]
        self._assert_parse_equals("if true\n    print 1\nprint 2", expected)
    
    def test_parse_if_from_string(self):
        expected: List[Statement] = [self._if_stmt(self._binary_expr(self._var("x"), BinaryOperator.GREATER_THAN, self._int_lit(5)), 
                                 [self._print_stmt(self._var("x"))])]
        self._assert_parse_equals("if x > 5\n    print x", expected)
    
    def test_parse_complex_if_from_string(self):
        expected: List[Statement] = [
            self._if_stmt(self._bool_lit(True), 
                         [self._let_stmt("y", Type.INTEGER, self._int_lit(10)), 
                          self._print_stmt(self._var("y"))]),
            self._print_stmt(self._var("x"))
        ]
        self._assert_parse_equals("if true\n    let y integer = 10\n    print y\nprint x", expected)
    
    # Error cases for if statements
    def test_parse_error_if_missing_condition(self):
        tokens: list[TokenType] =[Token.IF, Token.STATEMENT_SEPARATOR]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertEqual(str(cm.exception), "Expected integer, float, identifier, boolean, or opening parenthesis")
    
    def test_parse_error_if_missing_body(self):
        tokens: list[TokenType] =[Token.IF, Token.TRUE, Token.STATEMENT_SEPARATOR]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertEqual(str(cm.exception), "Expected indented block after 'if'")
    
    # Set statement tests
    def test_parse_simple_set_statement(self):
        expected: List[Statement] = [self._set_stmt("x", self._int_lit(42))]
        self._assert_parse_equals("set x = 42", expected)
    
    def test_parse_set_with_expression(self):
        expected: List[Statement] = [self._set_stmt("x", self._binary_expr(self._var("y"), BinaryOperator.ADDITION, self._int_lit(5)))]
        self._assert_parse_equals("set x = y + 5", expected)
    
    def test_parse_set_from_string(self):
        expected: List[Statement] = [self._set_stmt("counter", self._binary_expr(self._var("counter"), BinaryOperator.ADDITION, self._int_lit(1)))]
        self._assert_parse_equals("set counter = counter + 1", expected)
    
    # While loop tests
    def test_parse_simple_while_statement(self):
        expected: List[Statement] = [self._while_stmt(self._bool_lit(True), [self._print_stmt(self._int_lit(5))])]
        self._assert_parse_equals("while true\n    print 5", expected)
    
    def test_parse_while_with_condition_expression(self):
        expected: List[Statement] = [self._while_stmt(self._binary_expr(self._var("x"), BinaryOperator.GREATER_THAN, self._int_lit(0)), 
                                    [self._print_stmt(self._var("x"))])]
        self._assert_parse_equals("while x > 0\n    print x", expected)
    
    def test_parse_while_with_multiple_statements(self):
        expected: List[Statement] = [self._while_stmt(self._bool_lit(True), 
                                    [self._print_stmt(self._var("x")), 
                                     self._set_stmt("x", self._int_lit(5))])]
        self._assert_parse_equals("while true\n    print x\n    set x = 5", expected)
    
    def test_parse_while_followed_by_regular_statement(self):
        expected: List[Statement] = [self._while_stmt(self._bool_lit(False), [self._print_stmt(self._int_lit(1))]), 
                   self._print_stmt(self._int_lit(2))]
        self._assert_parse_equals("while false\n    print 1\nprint 2", expected)
    
    def test_parse_while_from_string(self):
        expected: List[Statement] = [self._while_stmt(self._binary_expr(self._var("x"), BinaryOperator.GREATER_THAN, self._int_lit(0)), [
            self._print_stmt(self._var("x")),
            self._set_stmt("x", self._binary_expr(self._var("x"), BinaryOperator.SUBTRACTION, self._int_lit(1)))
        ])]
        self._assert_parse_equals("while x > 0\n    print x\n    set x = x - 1", expected)
    
    def test_parse_complex_while_from_string(self):
        expected: List[Statement] = [
            self._while_stmt(self._binary_expr(self._var("counter"), BinaryOperator.LESS_THAN_OR_EQUAL, self._int_lit(5)), [
                self._print_stmt(self._var("counter")),
                self._set_stmt("counter", self._binary_expr(self._var("counter"), BinaryOperator.ADDITION, self._int_lit(1)))
            ]),
            self._print_stmt(self._var("done"))
        ]
        self._assert_parse_equals("while counter <= 5\n    print counter\n    set counter = counter + 1\nprint done", expected)
    
    # Error cases for while statements
    def test_parse_error_while_missing_condition(self):
        tokens: list[TokenType] =[Token.WHILE, Token.STATEMENT_SEPARATOR]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertEqual(str(cm.exception), "Expected integer, float, identifier, boolean, or opening parenthesis")
    
    def test_parse_error_while_missing_body(self):
        tokens: list[TokenType] =[Token.WHILE, Token.TRUE, Token.STATEMENT_SEPARATOR]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertEqual(str(cm.exception), "Expected indented block after 'while'")
    
    # Error cases for set statements
    def test_parse_error_set_missing_identifier(self):
        tokens: list[TokenType] =[Token.SET, Token.EQUALS, IntegerToken(5)]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertEqual(str(cm.exception), "Expected 'set identifier = expression'")
    
    def test_parse_error_set_missing_equals(self):
        tokens: list[TokenType] =[Token.SET, IdentifierToken("x"), IntegerToken(5)]
        with self.assertRaises(ParseError) as cm:
            parse(tokens)
        self.assertEqual(str(cm.exception), "Expected 'set identifier = expression'")
    
    # Modulus operator tests
    def test_parse_modulus_operation(self):
        expected: List[Statement] = [self._let_stmt("remainder", Type.INTEGER, 
                    self._binary_expr(self._int_lit(10), BinaryOperator.MODULUS, self._int_lit(3)))]
        self._assert_parse_equals("let remainder integer = 10 % 3", expected)
    
    def test_parse_modulus_precedence(self):
        # Test that % has same precedence as * and /
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER, 
                    self._binary_expr(self._int_lit(10), BinaryOperator.ADDITION, 
                                    self._binary_expr(self._int_lit(5), BinaryOperator.MODULUS, self._int_lit(3))))]
        self._assert_parse_equals("let result integer = 10 + 5 % 3", expected)
    
    # Float literal tests
    def test_parse_simple_float(self):
        expected: List[Statement] = [self._let_stmt("pi", Type.FLOAT, self._float_lit(3.14))]
        self._assert_parse_equals("let pi float = 3.14", expected)
    
    def test_parse_float_arithmetic(self):
        expected: List[Statement] = [self._let_stmt("result", Type.FLOAT, 
                    self._binary_expr(self._float_lit(2.5), BinaryOperator.ADDITION, self._float_lit(1.5)))]
        self._assert_parse_equals("let result float = 2.5 + 1.5", expected)
    
    def test_parse_mixed_int_float_arithmetic(self):
        expected: List[Statement] = [self._let_stmt("result", Type.FLOAT, 
                    self._binary_expr(self._int_lit(5), BinaryOperator.MULTIPLICATION, self._float_lit(2.0)))]
        self._assert_parse_equals("let result float = 5 * 2.0", expected)
    
    def test_parse_float_comparison(self):
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN, 
                    self._binary_expr(self._float_lit(3.14), BinaryOperator.GREATER_THAN, self._float_lit(2.5)))]
        self._assert_parse_equals("let result boolean = 3.14 > 2.5", expected)
    
    def test_parse_float_from_string(self):
        expected: List[Statement] = [self._let_stmt("value", Type.FLOAT, self._float_lit(3.14))]
        self._assert_parse_equals("let value float = 3.14", expected)
    
    def test_parse_complex_float_expression(self):
        expected: List[Statement] = [self._let_stmt("result", Type.FLOAT, 
                    self._binary_expr(self._binary_expr(self._float_lit(2.5), BinaryOperator.ADDITION, self._float_lit(1.5)), 
                                    BinaryOperator.MULTIPLICATION, self._float_lit(3.0)))]
        self._assert_parse_equals("let result float = (2.5 + 1.5) * 3.0", expected)
    
    # Comment parsing tests
    def test_parse_standalone_comment(self):
        expected: List[Statement] = [self._comment()]
        self._assert_parse_equals("# This is a comment", expected)
    
    def test_parse_comment_after_statement(self):
        expected: List[Statement] = [
            self._let_stmt("x", Type.INTEGER, self._int_lit(5)),
            self._comment()
        ]
        self._assert_parse_equals("let x integer = 5 # Comment", expected)
    
    def test_parse_comment_between_statements(self):
        expected: List[Statement] = [
            self._let_stmt("x", Type.INTEGER, self._int_lit(5)),
            self._comment(),
            self._print_stmt(self._var("x"))
        ]
        self._assert_parse_equals("let x integer = 5\n# Comment\nprint x", expected)
    
    def test_parse_comment_in_if_block(self):
        expected: List[Statement] = [
            self._if_stmt(self._bool_lit(True), [
                self._comment(),
                self._print_stmt(self._int_lit(42))
            ])
        ]
        self._assert_parse_equals("if true\n    # Comment in if block\n    print 42", expected)
    
    def test_parse_comment_in_while_block(self):
        expected: List[Statement] = [
            self._while_stmt(self._bool_lit(True), [
                self._comment(),
                self._set_stmt("x", self._int_lit(0))
            ])
        ]
        self._assert_parse_equals("while true\n    # Comment in while block\n    set x = 0", expected)
    
    def test_parse_mixed_statements_and_comments(self):
        code = code_block("""
            # Program start
            let x integer = 5 # Initialize x
            # Print the value
            print x # Output x
        """)
        expected: List[Statement] = [
            self._comment(),
            self._let_stmt("x", Type.INTEGER, self._int_lit(5)),
            self._comment(),
            self._comment(),
            self._print_stmt(self._var("x")),
            self._comment()
        ]
        self._assert_parse_equals(code, expected)
    
    def test_parse_comment_only_program(self):
        code = code_block("""
            # First comment
            # Second comment
            # Third comment
        """)
        expected: List[Statement] = [
            self._comment(),
            self._comment(),
            self._comment()
        ]
        self._assert_parse_equals(code, expected)
    
    def test_parse_complex_program_with_comments(self):
        code = code_block("""
            # Calculate factorial
            let n integer = 5 # Input number
            let result integer = 1 # Initialize result
            # Main calculation loop
            while n > 0
                # Multiply and decrement
                set result = result * n
                set n = n - 1
            # Output final result
            print result
        """)
        expected: List[Statement] = [
            self._comment(),
            self._let_stmt("n", Type.INTEGER, self._int_lit(5)),
            self._comment(),
            self._let_stmt("result", Type.INTEGER, self._int_lit(1)),
            self._comment(),
            self._comment(),
            self._while_stmt(self._binary_expr(self._var("n"), BinaryOperator.GREATER_THAN, self._int_lit(0)), [
                self._comment(),
                self._set_stmt("result", self._binary_expr(self._var("result"), BinaryOperator.MULTIPLICATION, self._var("n"))),
                self._set_stmt("n", self._binary_expr(self._var("n"), BinaryOperator.SUBTRACTION, self._int_lit(1)))
            ]),
            self._comment(),
            self._print_stmt(self._var("result"))
        ]
        self._assert_parse_equals(code, expected)
    
    # Function parsing tests
    def test_parse_simple_function_declaration(self):
        """Test parsing a simple function declaration."""
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
        """)
        expected: List[Statement] = [
            FunctionDeclaration(
                name="add",
                parameters=[
                    Parameter("x", Type.INTEGER),
                    Parameter("y", Type.INTEGER)
                ],
                return_type=Type.INTEGER,
                body=[Return(BinaryExpression(Variable("x"), BinaryOperator.ADDITION, Variable("y")))]
            )
        ]
        self._assert_parse_equals(code, expected)
    
    def test_parse_function_call_expression(self):
        """Test parsing a function call as an expression."""
        expected: List[Statement] = [self._print_stmt(FunctionCall("add", [self._int_lit(5), self._int_lit(10)]))]
        self._assert_parse_equals("print add(5, 10)", expected)
    
    def test_parse_function_call_in_let(self):
        """Test parsing a function call in a let statement."""
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER, FunctionCall("add", [self._int_lit(3), self._int_lit(7)]))]
        self._assert_parse_equals("let result integer = add(3, 7)", expected)
    
    # Comprehensive List Parsing Tests
    def test_parse_list_type_declaration(self):
        """Test parsing list type declaration."""
        expected: List[Statement] = [Let("nums", ListType(Type.INTEGER), ListLiteral([self._int_lit(1), self._int_lit(2), self._int_lit(3)]))]
        self._assert_parse_equals("let nums list of integer = [1, 2, 3]", expected)
    
    def test_parse_empty_list_literal(self):
        """Test parsing empty list literal."""
        expected: List[Statement] = [Let("empty", ListType(Type.INTEGER), ListLiteral([]))]
        self._assert_parse_equals("let empty list of integer = []", expected)
    
    def test_parse_list_with_boolean_elements(self):
        """Test parsing list with boolean elements."""
        expected: List[Statement] = [Let("flags", ListType(Type.BOOLEAN), ListLiteral([self._bool_lit(True), self._bool_lit(False)]))]
        self._assert_parse_equals("let flags list of boolean = [true, false]", expected)
    
    def test_parse_list_with_float_elements(self):
        """Test parsing list with float elements."""
        expected: List[Statement] = [Let("values", ListType(Type.FLOAT), ListLiteral([self._float_lit(1.5), self._float_lit(2.0)]))]
        self._assert_parse_equals("let values list of float = [1.5, 2.0]", expected)
    
    def test_parse_repeat_function_call(self):
        """Test parsing repeat function call."""
        expected: List[Statement] = [Let("zeros", ListType(Type.INTEGER), RepeatCall(self._int_lit(0), self._int_lit(5)))]
        self._assert_parse_equals("let zeros list of integer = repeat(0, 5)", expected)
    
    def test_parse_len_function_call(self):
        """Test parsing len function call."""
        expected: List[Statement] = [self._print_stmt(LenCall(Variable("nums")))]
        self._assert_parse_equals("print len(nums)", expected)
    
    def test_parse_list_access(self):
        """Test parsing list access."""
        expected: List[Statement] = [self._print_stmt(ListAccess(Variable("nums"), self._int_lit(0)))]
        self._assert_parse_equals("print nums[0]", expected)
    
    def test_parse_list_access_with_expression(self):
        """Test parsing list access with expression index."""
        expected: List[Statement] = [self._print_stmt(ListAccess(Variable("nums"), BinaryExpression(Variable("i"), BinaryOperator.ADDITION, self._int_lit(1))))]
        self._assert_parse_equals("print nums[i + 1]", expected)
    
    def test_parse_list_assignment(self):
        """Test parsing list assignment."""
        expected: List[Statement] = [ListAssignment("nums", self._int_lit(1), self._int_lit(42))]
        self._assert_parse_equals("set nums[1] = 42", expected)
    
    def test_parse_list_assignment_with_expression(self):
        """Test parsing list assignment with expression."""
        expected: List[Statement] = [ListAssignment("nums", Variable("i"), BinaryExpression(Variable("x"), BinaryOperator.MULTIPLICATION, self._int_lit(2)))]
        self._assert_parse_equals("set nums[i] = x * 2", expected)
    
    def test_parse_list_in_function_parameter(self):
        """Test parsing list type in function parameter."""
        expected: List[Statement] = [
            FunctionDeclaration(
                name="process",
                parameters=[Parameter("data", ListType(Type.INTEGER))],
                return_type=Type.INTEGER,
                body=[Return(LenCall(Variable("data")))]
            )
        ]
        self._assert_parse_equals("def process(data list of integer) returns integer\n    return len(data)", expected)
    
    def test_parse_list_return_type(self):
        """Test parsing list as function return type."""
        expected: List[Statement] = [
            FunctionDeclaration(
                name="create",
                parameters=[],
                return_type=ListType(Type.INTEGER),
                body=[Return(RepeatCall(self._int_lit(0), self._int_lit(3)))]
            )
        ]
        self._assert_parse_equals("def create() returns list of integer\n    return repeat(0, 3)", expected)
    
    def test_parse_list_with_variable_elements(self):
        """Test parsing list with variable elements."""
        expected: List[Statement] = [Let("numbers", ListType(Type.INTEGER), ListLiteral([Variable("x"), Variable("y"), self._int_lit(3)]))]
        self._assert_parse_equals("let numbers list of integer = [x, y, 3]", expected)
    
    def test_parse_list_with_expression_elements(self):
        """Test parsing list with expression elements."""
        expected: List[Statement] = [Let("computed", ListType(Type.INTEGER), ListLiteral([
            BinaryExpression(Variable("x"), BinaryOperator.ADDITION, self._int_lit(1)),
            BinaryExpression(Variable("y"), BinaryOperator.MULTIPLICATION, self._int_lit(2))
        ]))]
        self._assert_parse_equals("let computed list of integer = [x + 1, y * 2]", expected)
    
    def test_parse_complex_list_operations(self):
        """Test parsing complex list operations."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            print nums[0]
            set nums[1] = len(nums)
            print repeat(nums[0], 2)
        """)
        expected: List[Statement] = [
            Let("nums", ListType(Type.INTEGER), ListLiteral([self._int_lit(1), self._int_lit(2), self._int_lit(3)])),
            self._print_stmt(ListAccess(Variable("nums"), self._int_lit(0))),
            ListAssignment("nums", self._int_lit(1), LenCall(Variable("nums"))),
            self._print_stmt(RepeatCall(ListAccess(Variable("nums"), self._int_lit(0)), self._int_lit(2)))
        ]
        self._assert_parse_equals(code, expected)
    
    def test_parse_nested_list_access(self):
        """Test parsing nested list access as function argument."""
        expected: List[Statement] = [self._print_stmt(RepeatCall(ListAccess(Variable("nums"), self._int_lit(0)), LenCall(Variable("other"))))]
        self._assert_parse_equals("print repeat(nums[0], len(other))", expected)
    
    # List parsing error tests
    def test_parse_error_list_missing_of(self):
        """Test parsing error when 'of' is missing in list type."""
        with self.assertRaises(ParseError) as cm:
            parse(tokenize("let nums list integer = [1, 2, 3]"))
        self.assertEqual(str(cm.exception), "Expected 'of' after 'list'")
    
    def test_parse_error_list_missing_closing_bracket(self):
        """Test parsing error when closing bracket is missing."""
        with self.assertRaises(ParseError) as cm:
            parse(tokenize("let nums list of integer = [1, 2, 3"))
        self.assertEqual(str(cm.exception), "Expected ']' after list elements")
    
    def test_parse_error_list_access_missing_closing_bracket(self):
        """Test parsing error when list access missing closing bracket."""
        with self.assertRaises(ParseError) as cm:
            parse(tokenize("print nums[0"))
        self.assertEqual(str(cm.exception), "Expected ']' after list index")
    
    def test_parse_error_repeat_missing_parenthesis(self):
        """Test parsing error when repeat is missing parenthesis."""
        with self.assertRaises(ParseError) as cm:
            parse(tokenize("let nums list of integer = repeat 0, 5"))
        self.assertEqual(str(cm.exception), "Expected '(' after 'repeat'")
    
    def test_parse_error_len_missing_parenthesis(self):
        """Test parsing error when len is missing parenthesis."""
        with self.assertRaises(ParseError) as cm:
            parse(tokenize("print len nums"))
        self.assertEqual(str(cm.exception), "Expected '(' after 'len'")
    
    # Negative number parsing tests
    def test_parse_negative_integer(self):
        """Test parsing negative integers."""
        expected: List[Statement] = [self._let_stmt("x", Type.INTEGER, self._int_lit(-42))]
        self._assert_parse_equals("let x integer = -42", expected)
    
    def test_parse_negative_zero(self):
        """Test parsing negative zero."""
        expected: List[Statement] = [self._let_stmt("x", Type.INTEGER, self._int_lit(0))]
        self._assert_parse_equals("let x integer = -0", expected)
    
    def test_parse_negative_float(self):
        """Test parsing negative floats."""
        expected: List[Statement] = [self._let_stmt("pi", Type.FLOAT, self._float_lit(-3.14))]
        self._assert_parse_equals("let pi float = -3.14", expected)
    
    def test_parse_negative_float_zero(self):
        """Test parsing negative float zero."""
        expected: List[Statement] = [self._let_stmt("x", Type.FLOAT, self._float_lit(-0.0))]
        self._assert_parse_equals("let x float = -0.0", expected)
    
    def test_parse_negative_in_arithmetic(self):
        """Test parsing negative numbers in arithmetic expressions."""
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(self._int_lit(-5), BinaryOperator.ADDITION, self._int_lit(3)))]
        self._assert_parse_equals("let result integer = -5 + 3", expected)
    
    def test_parse_mixed_negative_positive_arithmetic(self):
        """Test parsing expressions with both negative and positive numbers."""
        expected: List[Statement] = [self._let_stmt("result", Type.INTEGER,
                    self._binary_expr(
                        self._binary_expr(self._int_lit(-10), BinaryOperator.ADDITION, self._int_lit(5)),
                        BinaryOperator.SUBTRACTION, self._int_lit(2)))]
        self._assert_parse_equals("let result integer = -10 + 5 - 2", expected)
    
    def test_parse_negative_float_arithmetic(self):
        """Test parsing negative floats in arithmetic expressions."""
        expected: List[Statement] = [self._let_stmt("result", Type.FLOAT,
                    self._binary_expr(self._float_lit(-2.5), BinaryOperator.MULTIPLICATION, self._float_lit(4.0)))]
        self._assert_parse_equals("let result float = -2.5 * 4.0", expected)
    
    def test_parse_negative_in_comparison(self):
        """Test parsing negative numbers in comparison expressions."""
        expected: List[Statement] = [self._let_stmt("result", Type.BOOLEAN,
                    self._binary_expr(self._int_lit(-5), BinaryOperator.LESS_THAN, self._int_lit(0)))]
        self._assert_parse_equals("let result boolean = -5 < 0", expected)
    
    def test_parse_negative_in_list_literal(self):
        """Test parsing negative numbers in list literals."""
        expected: List[Statement] = [Let("nums", ListType(Type.INTEGER), ListLiteral([self._int_lit(-1), self._int_lit(-2), self._int_lit(-3)]))]
        self._assert_parse_equals("let nums list of integer = [-1, -2, -3]", expected)
    
    def test_parse_negative_in_function_call(self):
        """Test parsing negative numbers as function arguments."""
        expected: List[Statement] = [self._print_stmt(FunctionCall("add", [self._int_lit(-5), self._int_lit(10)]))]
        self._assert_parse_equals("print add(-5, 10)", expected)


if __name__ == '__main__':
    unittest.main()