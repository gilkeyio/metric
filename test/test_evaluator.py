#!/usr/bin/env python3

import sys
import unittest
import os
from contextlib import contextmanager
from io import StringIO

# Add the test directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from metric.metric_ast import *
from metric.evaluator import Environment, evaluate_expression, execute_statement, execute, EvaluationError
from metric.tokenizer import tokenize
from metric.parser import parse
from metric.type_checker import type_check
from test_utils import code_block


class TestEvaluator(unittest.TestCase):
    
    @contextmanager
    def capture_stdout(self):
        """Context manager to capture stdout."""
        captured_output = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        try:
            yield captured_output
        finally:
            sys.stdout = old_stdout
    
    def test_evaluate_integer_literal(self):
        env = Environment.empty()
        expr = IntegerLiteral(42)
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 42)
    
    def test_evaluate_variable_found(self):
        env = Environment.empty().add("x", 10)
        expr = Variable("x")
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 10)
    
    def test_evaluate_variable_not_found(self):
        env = Environment.empty()
        expr = Variable("undefined")
        with self.assertRaises(EvaluationError) as cm:
            evaluate_expression(env, expr)
        self.assertEqual(str(cm.exception), "Undefined variable: undefined")
    
    def test_evaluate_addition(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(5), BinaryOperator.ADDITION, IntegerLiteral(3))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 8)
    
    def test_evaluate_subtraction(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(10), BinaryOperator.SUBTRACTION, IntegerLiteral(4))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 6)
    
    def test_evaluate_multiplication(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(6), BinaryOperator.MULTIPLICATION, IntegerLiteral(7))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 42)
    
    def test_evaluate_division(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(15), BinaryOperator.DIVISION, IntegerLiteral(3))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 5)
    
    def test_evaluate_division_by_zero(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(10), BinaryOperator.DIVISION, IntegerLiteral(0))
        with self.assertRaises(EvaluationError) as cm:
            evaluate_expression(env, expr)
        self.assertEqual(str(cm.exception), "Division by zero")
    
    def test_evaluate_complex_expression(self):
        env = Environment.empty().add("x", 5).add("y", 3)
        expr = BinaryExpression(
            BinaryExpression(Variable("x"), BinaryOperator.MULTIPLICATION, IntegerLiteral(2)),
            BinaryOperator.ADDITION,
            BinaryExpression(Variable("y"), BinaryOperator.SUBTRACTION, IntegerLiteral(1))
        )
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 12)
    
    def test_execute_let_statement(self):
        env = Environment.empty()
        stmt = Let("x", Type.INTEGER, IntegerLiteral(42))
        new_env, result = execute_statement(env, stmt)
        self.assertIsNone(result)
        x_value = new_env.find("x")
        self.assertEqual(x_value, 42)
    
    def test_execute_let_statement_already_bound(self):
        env = Environment.empty().add("x", 5)
        stmt = Let("x", Type.INTEGER, IntegerLiteral(42))
        with self.assertRaises(EvaluationError) as cm:
            execute_statement(env, stmt)
        self.assertEqual(str(cm.exception), "Variable already bound: x")
    
    def test_execute_print_statement(self):
        env = Environment.empty()
        stmt = Print(IntegerLiteral(123))
        
        with self.capture_stdout() as captured_output:
            new_env, result = execute_statement(env, stmt)
            self.assertEqual(result, 123)
            self.assertEqual(captured_output.getvalue().strip(), "123")
    
    def test_execute_print_with_variable(self):
        env = Environment.empty().add("value", 99)
        stmt = Print(Variable("value"))
        
        with self.capture_stdout() as captured_output:
            new_env, result = execute_statement(env, stmt)
            self.assertEqual(result, 99)
            self.assertEqual(captured_output.getvalue().strip(), "99")
    
    def test_execute_single_statement(self):
        ast = [Let("x", Type.INTEGER, IntegerLiteral(5))]
        results = execute(ast)[0]
        self.assertEqual(results, [])
    
    def test_execute_multiple_statements(self):
        ast = [
            Let("x", Type.INTEGER, IntegerLiteral(10)),
            Let("y", Type.INTEGER, IntegerLiteral(5)),
            Print(BinaryExpression(Variable("x"), BinaryOperator.ADDITION, Variable("y")))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [15])
            self.assertEqual(captured_output.getvalue().strip(), "15")
    
    def test_execute_complex_program(self):
        ast = [
            Let("a", Type.INTEGER, IntegerLiteral(2)),
            Let("b", Type.INTEGER, IntegerLiteral(3)),
            Let("c", Type.INTEGER, BinaryExpression(Variable("a"), BinaryOperator.MULTIPLICATION, Variable("b"))),
            Print(Variable("c")),
            Print(BinaryExpression(Variable("c"), BinaryOperator.ADDITION, IntegerLiteral(10)))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [6, 16])
            output_lines = captured_output.getvalue().strip().split('\n')
            self.assertEqual(output_lines, ["6", "16"])
    
    def test_execute_variable_redefinition_error(self):
        ast = [
            Let("x", Type.INTEGER, IntegerLiteral(5)),
            Print(Variable("x")),
            Let("x", Type.INTEGER, IntegerLiteral(10)),  # This should fail
            Print(Variable("x"))
        ]
        
        with self.assertRaises(EvaluationError) as cm:
            execute(ast)
        self.assertEqual(str(cm.exception), "Variable already bound: x")
    
    def test_operator_precedence_in_evaluation(self):
        env = Environment.empty()
        expr = BinaryExpression(
            IntegerLiteral(2),
            BinaryOperator.ADDITION,
            BinaryExpression(IntegerLiteral(3), BinaryOperator.MULTIPLICATION, IntegerLiteral(4))
        )
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 14)
    
    def test_nested_expressions(self):
        env = Environment.empty()
        expr = BinaryExpression(
            BinaryExpression(
                BinaryExpression(IntegerLiteral(10), BinaryOperator.DIVISION, IntegerLiteral(2)),
                BinaryOperator.SUBTRACTION,
                IntegerLiteral(1)
            ),
            BinaryOperator.MULTIPLICATION,
            IntegerLiteral(3)
        )
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 12)
    
    def test_error_propagation(self):
        env = Environment.empty()
        expr = BinaryExpression(
            Variable("undefined"),
            BinaryOperator.ADDITION,
            IntegerLiteral(5)
        )
        with self.assertRaises(EvaluationError) as cm:
            evaluate_expression(env, expr)
        self.assertEqual(str(cm.exception), "Undefined variable: undefined")
    
    # Boolean literal tests
    def test_evaluate_true_literal(self):
        env = Environment.empty()
        expr = BooleanLiteral(True)
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_false_literal(self):
        env = Environment.empty()
        expr = BooleanLiteral(False)
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    # Comparison operator tests
    def test_evaluate_less_than_true(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(5), BinaryOperator.LESS_THAN, IntegerLiteral(10))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_less_than_false(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(10), BinaryOperator.LESS_THAN, IntegerLiteral(5))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_greater_than_true(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(10), BinaryOperator.GREATER_THAN, IntegerLiteral(5))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_greater_than_false(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(5), BinaryOperator.GREATER_THAN, IntegerLiteral(10))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_less_than_or_equal_true(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(5), BinaryOperator.LESS_THAN_OR_EQUAL, IntegerLiteral(5))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_greater_than_or_equal_true(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(10), BinaryOperator.GREATER_THAN_OR_EQUAL, IntegerLiteral(10))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_equal_equal_true(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(5), BinaryOperator.EQUAL_EQUAL, IntegerLiteral(5))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_equal_equal_false(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(5), BinaryOperator.EQUAL_EQUAL, IntegerLiteral(3))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_not_equal_true(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(5), BinaryOperator.NOT_EQUAL, IntegerLiteral(3))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_not_equal_false(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(5), BinaryOperator.NOT_EQUAL, IntegerLiteral(5))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    # Logical operator tests
    def test_evaluate_and_true_true(self):
        env = Environment.empty()
        expr = BinaryExpression(BooleanLiteral(True), BinaryOperator.AND, BooleanLiteral(True))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_and_true_false(self):
        env = Environment.empty()
        expr = BinaryExpression(BooleanLiteral(True), BinaryOperator.AND, BooleanLiteral(False))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_and_false_true(self):
        env = Environment.empty()
        expr = BinaryExpression(BooleanLiteral(False), BinaryOperator.AND, BooleanLiteral(True))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_and_false_false(self):
        env = Environment.empty()
        expr = BinaryExpression(BooleanLiteral(False), BinaryOperator.AND, BooleanLiteral(False))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_or_true_true(self):
        env = Environment.empty()
        expr = BinaryExpression(BooleanLiteral(True), BinaryOperator.OR, BooleanLiteral(True))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_or_true_false(self):
        env = Environment.empty()
        expr = BinaryExpression(BooleanLiteral(True), BinaryOperator.OR, BooleanLiteral(False))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_or_false_true(self):
        env = Environment.empty()
        expr = BinaryExpression(BooleanLiteral(False), BinaryOperator.OR, BooleanLiteral(True))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_or_false_false(self):
        env = Environment.empty()
        expr = BinaryExpression(BooleanLiteral(False), BinaryOperator.OR, BooleanLiteral(False))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_and_with_variables(self):
        env = Environment.empty().add("x", True).add("y", False)
        expr = BinaryExpression(Variable("x"), BinaryOperator.AND, Variable("y"))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_or_with_variables(self):
        env = Environment.empty().add("x", True).add("y", False)
        expr = BinaryExpression(Variable("x"), BinaryOperator.OR, Variable("y"))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_complex_logical_expression(self):
        env = Environment.empty().add("a", True).add("b", False).add("c", True)
        # (a and b) or c => (True and False) or True => False or True => True
        expr = BinaryExpression(
            BinaryExpression(Variable("a"), BinaryOperator.AND, Variable("b")),
            BinaryOperator.OR,
            Variable("c")
        )
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_logical_not_true(self):
        env = Environment.empty()
        expr = UnaryExpression(UnaryOperator.NOT, BooleanLiteral(True))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_logical_not_false(self):
        env = Environment.empty()
        expr = UnaryExpression(UnaryOperator.NOT, BooleanLiteral(False))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_logical_not_variable(self):
        env = Environment.empty().add("flag", True)
        expr = UnaryExpression(UnaryOperator.NOT, Variable("flag"))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_double_logical_not(self):
        env = Environment.empty()
        expr = UnaryExpression(UnaryOperator.NOT, 
                              UnaryExpression(UnaryOperator.NOT, BooleanLiteral(True)))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_logical_not_with_and(self):
        env = Environment.empty().add("x", True).add("y", False)
        # not x and y => (not True) and False => False and False => False
        expr = BinaryExpression(
            UnaryExpression(UnaryOperator.NOT, Variable("x")),
            BinaryOperator.AND,
            Variable("y")
        )
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_logical_not_with_parentheses(self):
        env = Environment.empty().add("x", True).add("y", False)
        # not (x and y) => not (True and False) => not False => True
        expr = UnaryExpression(UnaryOperator.NOT,
                              BinaryExpression(Variable("x"), BinaryOperator.AND, Variable("y")))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_not_precedence_higher_than_and(self):
        env = Environment.empty().add("x", True).add("y", True)
        # not x and y => (not True) and True => False and True => False
        expr = BinaryExpression(
            UnaryExpression(UnaryOperator.NOT, Variable("x")),
            BinaryOperator.AND,
            Variable("y")
        )
        result = evaluate_expression(env, expr)
        self.assertEqual(result, False)
    
    def test_evaluate_not_precedence_higher_than_or(self):
        env = Environment.empty().add("x", False).add("y", True)
        # not x or y => (not False) or True => True or True => True
        expr = BinaryExpression(
            UnaryExpression(UnaryOperator.NOT, Variable("x")),
            BinaryOperator.OR,
            Variable("y")
        )
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_evaluate_complex_not_precedence(self):
        env = Environment.empty().add("x", True).add("y", False).add("z", True)
        # not x and y or z => ((not True) and False) or True => (False and False) or True => False or True => True
        expr = BinaryExpression(
            BinaryExpression(
                UnaryExpression(UnaryOperator.NOT, Variable("x")),
                BinaryOperator.AND,
                Variable("y")
            ),
            BinaryOperator.OR,
            Variable("z")
        )
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    # Boolean execution tests
    def test_execute_print_boolean(self):
        ast = [Print(BooleanLiteral(True))]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [True])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "true")
    
    def test_execute_boolean_assignment_and_comparison(self):
        ast = [
            Let("x", Type.INTEGER, IntegerLiteral(10)),
            Let("y", Type.INTEGER, IntegerLiteral(5)),
            Let("result", Type.BOOLEAN, BinaryExpression(Variable("x"), BinaryOperator.GREATER_THAN, Variable("y"))),
            Print(Variable("result"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [True])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "true")
    
    def test_execute_mixed_boolean_and_integer_operations(self):
        ast = [
            Let("a", Type.INTEGER, IntegerLiteral(15)),
            Let("b", Type.INTEGER, IntegerLiteral(10)),
            Let("sum", Type.INTEGER, BinaryExpression(Variable("a"), BinaryOperator.ADDITION, Variable("b"))),
            Let("isLarge", Type.BOOLEAN, BinaryExpression(Variable("sum"), BinaryOperator.GREATER_THAN, IntegerLiteral(20))),
            Print(Variable("sum")),
            Print(Variable("isLarge"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [25, True])
            output_lines = captured_output.getvalue().strip().split('\n')
            self.assertEqual(output_lines, ["25", "true"])
    
    # If statement tests
    def test_execute_if_true(self):
        ast = [If(BooleanLiteral(True), [Print(IntegerLiteral(42))])]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [42])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "42")
    
    def test_execute_if_false(self):
        ast = [If(BooleanLiteral(False), [Print(IntegerLiteral(42))])]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "")
    
    def test_execute_if_with_comparison(self):
        ast = [
            Let("x", Type.INTEGER, IntegerLiteral(10)),
            If(BinaryExpression(Variable("x"), BinaryOperator.GREATER_THAN, IntegerLiteral(5)), [Print(Variable("x"))])
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [10])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "10")
    
    def test_execute_if_with_multiple_statements(self):
        ast = [If(BooleanLiteral(True), [
            Let("x", Type.INTEGER, IntegerLiteral(5)),
            Let("y", Type.INTEGER, IntegerLiteral(10)),
            Print(BinaryExpression(Variable("x"), BinaryOperator.ADDITION, Variable("y")))
        ])]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [15])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "15")
    
    def test_execute_if_followed_by_regular_statement(self):
        ast = [
            If(BooleanLiteral(True), [Print(IntegerLiteral(1))]),
            Print(IntegerLiteral(2))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [1, 2])
            output_lines = captured_output.getvalue().strip().split('\n')
            self.assertEqual(output_lines, ["1", "2"])
    
    def test_execute_if_variable_scoping(self):
        # Variables defined inside if should be available outside
        ast = [
            If(BooleanLiteral(True), [Let("x", Type.INTEGER, IntegerLiteral(42))]),
            Print(Variable("x"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [42])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "42")
    
    def test_execute_if_false_no_variable_definition(self):
        # Variables not defined when if condition is false
        ast = [
            If(BooleanLiteral(False), [Let("x", Type.INTEGER, IntegerLiteral(42))]),
            Print(Variable("x"))
        ]
        
        with self.assertRaises(EvaluationError) as cm:
            execute(ast)
        self.assertEqual(str(cm.exception), "Undefined variable: x")
    
    # Variable modification tests
    def test_execute_set_statement(self):
        # Test basic variable modification
        ast = [
            Let("x", Type.INTEGER, IntegerLiteral(5)),
            Set("x", IntegerLiteral(10)),
            Print(Variable("x"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [10])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "10")
    
    def test_execute_set_undefined_variable(self):
        # Test modifying undefined variable should fail
        ast = [Set("undefined", IntegerLiteral(42))]
        
        with self.assertRaises(EvaluationError) as cm:
            execute(ast)
        self.assertEqual(str(cm.exception), "Cannot set undefined variable: undefined")
    
    def test_execute_set_with_expression(self):
        # Test setting variable with complex expression
        ast = [
            Let("x", Type.INTEGER, IntegerLiteral(5)),
            Let("y", Type.INTEGER, IntegerLiteral(3)),
            Set("x", BinaryExpression(Variable("x"), BinaryOperator.ADDITION, Variable("y"))),
            Print(Variable("x"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [8])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "8")
    
    # While loop tests
    def test_execute_while_simple_countdown(self):
        # Test basic while loop counting down
        ast = [
            Let("counter", Type.INTEGER, IntegerLiteral(3)),
            While(BinaryExpression(Variable("counter"), BinaryOperator.GREATER_THAN, IntegerLiteral(0)), [
                Print(Variable("counter")),
                Set("counter", BinaryExpression(Variable("counter"), BinaryOperator.SUBTRACTION, IntegerLiteral(1)))
            ])
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [3, 2, 1])
            output_lines = captured_output.getvalue().strip().split('\n')
            self.assertEqual(output_lines, ["3", "2", "1"])
    
    def test_execute_while_false_condition(self):
        # Test while loop with false condition (should not execute body)
        ast = [
            Let("x", Type.INTEGER, IntegerLiteral(5)),
            While(BooleanLiteral(False), [
                Print(Variable("x")),
                Set("x", IntegerLiteral(10))
            ]),
            Print(Variable("x"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [5])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "5")
    
    def test_execute_while_with_complex_condition(self):
        # Test while loop with complex condition
        ast = [
            Let("sum", Type.INTEGER, IntegerLiteral(0)),
            Let("i", Type.INTEGER, IntegerLiteral(1)),
            While(BinaryExpression(Variable("i"), BinaryOperator.LESS_THAN_OR_EQUAL, IntegerLiteral(5)), [
                Set("sum", BinaryExpression(Variable("sum"), BinaryOperator.ADDITION, Variable("i"))),
                Set("i", BinaryExpression(Variable("i"), BinaryOperator.ADDITION, IntegerLiteral(1)))
            ]),
            Print(Variable("sum"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [15])  # 1+2+3+4+5 = 15
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "15")
    
    def test_execute_logical_not_program(self):
        # Test a complete program using logical not
        code = code_block("""
            let flag boolean = true
            let result boolean = not flag
            print result
            let complex boolean = not (true and false)
            print complex
        """)
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [False, True])
            output_lines = captured_output.getvalue().strip().split('\n')
            self.assertEqual(output_lines, ["false", "true"])
    
    def test_execute_logical_not_precedence_program(self):
        # Test a complete program demonstrating not precedence
        code = code_block("""
            let x boolean = true
            let y boolean = false
            let z boolean = true
            
            # not x and y should be (not x) and y = false and false = false
            let resultOne boolean = not x and y
            print resultOne
            
            # not x or z should be (not x) or z = false or true = true
            let resultTwo boolean = not x or z
            print resultTwo
            
            # not x and y or z should be ((not x) and y) or z = (false and false) or true = true
            let resultThree boolean = not x and y or z
            print resultThree
        """)
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [False, True, True])
            output_lines = captured_output.getvalue().strip().split('\n')
            self.assertEqual(output_lines, ["false", "true", "true"])
    
    def test_execute_while_nested_statements(self):
        # Test while loop with multiple statements in body
        ast = [
            Let("x", Type.INTEGER, IntegerLiteral(2)),
            Let("result", Type.INTEGER, IntegerLiteral(1)),
            While(BinaryExpression(Variable("x"), BinaryOperator.GREATER_THAN, IntegerLiteral(0)), [
                Set("result", BinaryExpression(Variable("result"), BinaryOperator.MULTIPLICATION, Variable("x"))),
                Print(Variable("result")),
                Set("x", BinaryExpression(Variable("x"), BinaryOperator.SUBTRACTION, IntegerLiteral(1)))
            ])
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [2, 2])  # result becomes 2, then stays 2 (2*1)
            output_lines = captured_output.getvalue().strip().split('\n')
            self.assertEqual(output_lines, ["2", "2"])
    
    def test_execute_while_variable_scoping(self):
        # Test that variables modified in while loop are visible outside
        ast = [
            Let("x", Type.INTEGER, IntegerLiteral(10)),
            While(BinaryExpression(Variable("x"), BinaryOperator.GREATER_THAN, IntegerLiteral(5)), [
                Set("x", BinaryExpression(Variable("x"), BinaryOperator.SUBTRACTION, IntegerLiteral(2)))
            ]),
            Print(Variable("x"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [4])  # 10 -> 8 -> 6 -> 4 (stops when x <= 5)
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "4")
    
    def test_execute_while_followed_by_regular_statement(self):
        # Test while loop followed by regular statements
        ast = [
            Let("i", Type.INTEGER, IntegerLiteral(1)),
            While(BinaryExpression(Variable("i"), BinaryOperator.LESS_THAN_OR_EQUAL, IntegerLiteral(2)), [
                Print(Variable("i")),
                Set("i", BinaryExpression(Variable("i"), BinaryOperator.ADDITION, IntegerLiteral(1)))
            ]),
            Print(IntegerLiteral(99))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [1, 2, 99])
            output_lines = captured_output.getvalue().strip().split('\n')
            self.assertEqual(output_lines, ["1", "2", "99"])
    
    def test_execute_while_boolean_condition_modification(self):
        # Test while loop that modifies boolean variables
        ast = [
            Let("done", Type.BOOLEAN, BooleanLiteral(False)),
            Let("count", Type.INTEGER, IntegerLiteral(0)),
            While(BinaryExpression(Variable("done"), BinaryOperator.EQUAL_EQUAL, BooleanLiteral(False)), [
                Set("count", BinaryExpression(Variable("count"), BinaryOperator.ADDITION, IntegerLiteral(1))),
                Print(Variable("count")),
                Set("done", BinaryExpression(Variable("count"), BinaryOperator.GREATER_THAN_OR_EQUAL, IntegerLiteral(3)))
            ])
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [1, 2, 3])
            output_lines = captured_output.getvalue().strip().split('\n')
            self.assertEqual(output_lines, ["1", "2", "3"])
    
    # Modulus operator tests
    def test_evaluate_modulus_operation(self):
        result = evaluate_expression(Environment(), BinaryExpression(IntegerLiteral(10), BinaryOperator.MODULUS, IntegerLiteral(3)))
        self.assertEqual(result, 1)
    
    def test_evaluate_modulus_zero_remainder(self):
        result = evaluate_expression(Environment(), BinaryExpression(IntegerLiteral(15), BinaryOperator.MODULUS, IntegerLiteral(5)))
        self.assertEqual(result, 0)
    
    def test_evaluate_modulus_larger_divisor(self):
        result = evaluate_expression(Environment(), BinaryExpression(IntegerLiteral(3), BinaryOperator.MODULUS, IntegerLiteral(5)))
        self.assertEqual(result, 3)
    
    def test_execute_modulus_statement(self):
        ast = [
            Let("remainder", Type.INTEGER, BinaryExpression(IntegerLiteral(17), BinaryOperator.MODULUS, IntegerLiteral(5))),
            Print(Variable("remainder"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [2])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "2")
    
    # Float literal tests
    def test_evaluate_float_literal(self):
        env = Environment.empty()
        expr = FloatLiteral(3.14)
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 3.14)
    
    def test_evaluate_float_arithmetic(self):
        env = Environment.empty()
        expr = BinaryExpression(FloatLiteral(2.5), BinaryOperator.ADDITION, FloatLiteral(1.5))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 4.0)
    
    def test_evaluate_float_subtraction(self):
        env = Environment.empty()
        expr = BinaryExpression(FloatLiteral(5.5), BinaryOperator.SUBTRACTION, FloatLiteral(2.3))
        result = evaluate_expression(env, expr)
        self.assertAlmostEqual(result, 3.2, places=10)
    
    def test_evaluate_float_multiplication(self):
        env = Environment.empty()
        expr = BinaryExpression(FloatLiteral(2.5), BinaryOperator.MULTIPLICATION, FloatLiteral(4.0))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 10.0)
    
    def test_evaluate_float_division(self):
        env = Environment.empty()
        expr = BinaryExpression(FloatLiteral(7.5), BinaryOperator.DIVISION, FloatLiteral(2.5))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 3.0)
    
    def test_evaluate_mixed_int_float_arithmetic(self):
        env = Environment.empty()
        expr = BinaryExpression(IntegerLiteral(5), BinaryOperator.ADDITION, FloatLiteral(2.5))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 7.5)
    
    def test_evaluate_float_comparison(self):
        env = Environment.empty()
        expr = BinaryExpression(FloatLiteral(3.14), BinaryOperator.GREATER_THAN, FloatLiteral(2.5))
        result = evaluate_expression(env, expr)
        self.assertEqual(result, True)
    
    def test_execute_float_let_statement(self):
        env = Environment.empty()
        stmt = Let("pi", Type.FLOAT, FloatLiteral(3.14))
        new_env, result = execute_statement(env, stmt)
        self.assertIsNone(result)
        pi_value = new_env.find("pi")
        self.assertEqual(pi_value, 3.14)
    
    def test_execute_print_float(self):
        ast = [Print(FloatLiteral(3.14))]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [3.14])
            output_lines = captured_output.getvalue().strip()
            self.assertEqual(output_lines, "3.14")
    
    def test_execute_complex_float_program(self):
        ast = [
            Let("radius", Type.FLOAT, FloatLiteral(2.5)),
            Let("pi", Type.FLOAT, FloatLiteral(3.14159)),
            Let("area", Type.FLOAT, BinaryExpression(Variable("pi"), BinaryOperator.MULTIPLICATION, 
                BinaryExpression(Variable("radius"), BinaryOperator.MULTIPLICATION, Variable("radius")))),
            Print(Variable("area"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            expected_area = 3.14159 * 2.5 * 2.5
            self.assertEqual(len(results), 1)
            self.assertAlmostEqual(results[0], expected_area, places=5)
            output_lines = captured_output.getvalue().strip()
            self.assertAlmostEqual(float(output_lines), expected_area, places=5)
    
    # Comment evaluation tests
    def test_execute_standalone_comment(self):
        """Test that standalone comments are skipped in evaluation."""
        ast = [Comment()]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [])
            self.assertEqual(captured_output.getvalue(), "")
    
    def test_execute_comment_with_statements(self):
        """Test that comments are skipped but other statements execute."""
        ast = [
            Comment(),
            Let("x", Type.INTEGER, IntegerLiteral(42)),
            Comment(),
            Print(Variable("x")),
            Comment()
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [42])
            self.assertEqual(captured_output.getvalue().strip(), "42")
    
    def test_execute_comment_only_program(self):
        """Test that a program with only comments produces no output."""
        ast = [
            Comment(),
            Comment(),
            Comment()
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [])
            self.assertEqual(captured_output.getvalue(), "")
    
    def test_execute_comment_in_if_block(self):
        """Test that comments in if blocks are properly skipped."""
        ast = [
            If(BooleanLiteral(True), [
                Comment(),
                Let("x", Type.INTEGER, IntegerLiteral(100)),
                Comment(),
                Print(Variable("x"))
            ])
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [100])
            self.assertEqual(captured_output.getvalue().strip(), "100")
    
    def test_execute_comment_in_while_block(self):
        """Test that comments in while blocks are properly skipped."""
        ast = [
            Let("counter", Type.INTEGER, IntegerLiteral(3)),
            While(BinaryExpression(Variable("counter"), BinaryOperator.GREATER_THAN, IntegerLiteral(0)), [
                Comment(),
                Print(Variable("counter")),
                Comment(),
                Set("counter", BinaryExpression(Variable("counter"), BinaryOperator.SUBTRACTION, IntegerLiteral(1)))
            ])
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [3, 2, 1])
            output_lines = captured_output.getvalue().strip().split('\n')
            self.assertEqual(output_lines, ['3', '2', '1'])
    
    def test_execute_complex_program_with_comments(self):
        """Test a complex program with comments throughout."""
        ast = [
            Comment(),  # Program start comment
            Let("n", Type.INTEGER, IntegerLiteral(5)),
            Comment(),  # Variable comment
            Let("result", Type.INTEGER, IntegerLiteral(1)),
            Comment(),  # Loop comment
            While(BinaryExpression(Variable("n"), BinaryOperator.GREATER_THAN, IntegerLiteral(0)), [
                Comment(),  # Inside loop comment
                Set("result", BinaryExpression(Variable("result"), BinaryOperator.MULTIPLICATION, Variable("n"))),
                Set("n", BinaryExpression(Variable("n"), BinaryOperator.SUBTRACTION, IntegerLiteral(1))),
                Comment()   # End of loop iteration comment
            ]),
            Comment(),  # Final comment
            Print(Variable("result"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [120])  # 5! = 120
            self.assertEqual(captured_output.getvalue().strip(), "120")
    
    # Function execution tests
    def test_execute_simple_function(self):
        """Test executing a simple function."""
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
            let result integer = add(5, 10)
            print result
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [15])
            self.assertEqual(captured_output.getvalue().strip(), "15")
    
    def test_execute_function_with_variables(self):
        """Test function that uses local variables."""
        code = code_block("""
            def multiply(a integer, b integer) returns integer
                let result integer = a * b
                return result
            let answer integer = multiply(6, 7)
            print answer
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [42])
            self.assertEqual(captured_output.getvalue().strip(), "42")
    
    def test_execute_nested_function_calls(self):
        """Test nested function calls."""
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
            def multiply(a integer, b integer) returns integer
                return a * b
            let result integer = multiply(add(2, 3), add(4, 6))
            print result
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [50])  # (2+3) * (4+6) = 5 * 10 = 50
            self.assertEqual(captured_output.getvalue().strip(), "50")
    
    # Comprehensive List Evaluation Tests
    def test_execute_list_literal_integer(self):
        """Test executing list literal with integers."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            print nums
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [1, 2, 3])
            self.assertEqual(captured_output.getvalue().strip(), "[1, 2, 3]")
    
    def test_execute_list_literal_boolean(self):
        """Test executing list literal with booleans."""
        code = code_block("""
            let flags list of boolean = [true, false, true]
            print flags
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [True, False, True])
            self.assertEqual(captured_output.getvalue().strip(), "[true, false, true]")
    
    def test_execute_empty_list_via_repeat(self):
        """Test executing empty list creation using repeat."""
        code = code_block("""
            let empty list of integer = repeat(0, 0)
            print empty
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [])
            self.assertEqual(captured_output.getvalue().strip(), "[]")
    
    def test_execute_repeat_function(self):
        """Test executing repeat function."""
        code = code_block("""
            let zeros list of integer = repeat(0, 5)
            print zeros
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [0, 0, 0, 0, 0])
            self.assertEqual(captured_output.getvalue().strip(), "[0, 0, 0, 0, 0]")
    
    def test_execute_repeat_function_with_boolean(self):
        """Test executing repeat function with boolean."""
        code = code_block("""
            let flags list of boolean = repeat(true, 3)
            print flags
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [True, True, True])
            self.assertEqual(captured_output.getvalue().strip(), "[true, true, true]")
    
    def test_execute_list_access(self):
        """Test executing list access."""
        code = code_block("""
            let nums list of integer = [10, 20, 30]
            print nums[0]
            print nums[1]
            print nums[2]
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [10, 20, 30])
            self.assertEqual(captured_output.getvalue().strip(), "10\n20\n30")
    
    def test_execute_list_access_with_variable(self):
        """Test executing list access with variable index."""
        code = code_block("""
            let nums list of integer = [10, 20, 30]
            let i integer = 1
            print nums[i]
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [20])
            self.assertEqual(captured_output.getvalue().strip(), "20")
    
    def test_execute_len_function(self):
        """Test executing len function."""
        code = code_block("""
            let nums list of integer = [1, 2, 3, 4, 5]
            print len(nums)
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [5])
            self.assertEqual(captured_output.getvalue().strip(), "5")
    
    def test_execute_len_function_empty_list(self):
        """Test executing len function on empty list."""
        code = code_block("""
            let empty list of integer = repeat(0, 0)
            print len(empty)
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [0])
            self.assertEqual(captured_output.getvalue().strip(), "0")
    
    def test_execute_list_assignment(self):
        """Test executing list assignment."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            set nums[1] = 42
            print nums
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [1, 42, 3])
            self.assertEqual(captured_output.getvalue().strip(), "[1, 42, 3]")
    
    def test_execute_list_assignment_with_expression(self):
        """Test executing list assignment with expression."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            let x integer = 10
            set nums[0] = x * 2
            print nums
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [20, 2, 3])
            self.assertEqual(captured_output.getvalue().strip(), "[20, 2, 3]")
    
    def test_execute_list_with_expressions(self):
        """Test executing list with expression elements."""
        code = code_block("""
            let x integer = 10
            let y integer = 20
            let computed list of integer = [x + 1, y * 2, 99]
            print computed
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [11, 40, 99])
            self.assertEqual(captured_output.getvalue().strip(), "[11, 40, 99]")
    
    def test_execute_complex_list_operations(self):
        """Test executing complex list operations."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            print len(nums)
            set nums[0] = len(nums) + 10
            print nums[0]
            print nums
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [3, 13, 13, 2, 3])
            self.assertEqual(captured_output.getvalue().strip(), "3\n13\n[13, 2, 3]")
    
    def test_execute_list_in_function(self):
        """Test executing list operations in function."""
        code = code_block("""
            def getfirst(nums list of integer) returns integer
                return nums[0]

            let values list of integer = [100, 200, 300]
            let first integer = getfirst(values)
            print first
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [100])
            self.assertEqual(captured_output.getvalue().strip(), "100")
    
    def test_execute_function_returning_list(self):
        """Test executing function that returns a list."""
        code = code_block("""
            def makelist() returns list of integer
                return [1, 2, 3]

            let result list of integer = makelist()
            print result
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [1, 2, 3])
            self.assertEqual(captured_output.getvalue().strip(), "[1, 2, 3]")
    
    # List error tests
    def test_execute_list_access_out_of_bounds_positive(self):
        """Test list access out of bounds (positive index)."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            print nums[5]
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.assertRaises(EvaluationError) as cm:
            execute(ast)
        self.assertIn("out of bounds", str(cm.exception).lower())
    
    def test_execute_list_access_out_of_bounds_negative(self):
        """Test list access out of bounds (negative index)."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            let negindex integer = 0 - 1
            print nums[negindex]
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.assertRaises(EvaluationError) as cm:
            execute(ast)
        self.assertIn("out of bounds", str(cm.exception).lower())
    
    def test_execute_list_assignment_out_of_bounds(self):
        """Test list assignment out of bounds."""
        code = code_block("""
            let nums list of integer = [1, 2, 3]
            set nums[10] = 42
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.assertRaises(EvaluationError) as cm:
            execute(ast)
        self.assertIn("out of bounds", str(cm.exception).lower())
    
    def test_execute_repeat_negative_count(self):
        """Test repeat with negative count."""
        code = code_block("""
            let negcount integer = 0 - 5
            let nums list of integer = repeat(1, negcount)
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.assertRaises(EvaluationError) as cm:
            execute(ast)
        self.assertIn("negative", str(cm.exception).lower())
    
    # Negative number evaluation tests
    def test_evaluate_negative_integer_literal(self):
        """Test evaluating negative integer literals."""
        env = Environment.empty()
        expr = IntegerLiteral(-42)
        result = evaluate_expression(env, expr)
        self.assertEqual(result, -42)
    
    def test_evaluate_negative_zero_integer(self):
        """Test evaluating negative zero integer."""
        env = Environment.empty()
        expr = IntegerLiteral(-0)
        result = evaluate_expression(env, expr)
        self.assertEqual(result, 0)
    
    def test_evaluate_negative_float_literal(self):
        """Test evaluating negative float literals."""
        env = Environment.empty()
        expr = FloatLiteral(-3.14)
        result = evaluate_expression(env, expr)
        self.assertEqual(result, -3.14)
    
    def test_evaluate_negative_float_zero(self):
        """Test evaluating negative float zero."""
        env = Environment.empty()
        expr = FloatLiteral(-0.0)
        result = evaluate_expression(env, expr)
        self.assertEqual(result, -0.0)
    
    def test_execute_negative_integer_let(self):
        """Test executing let statement with negative integer."""
        ast = [
            Let("x", Type.INTEGER, IntegerLiteral(-42)),
            Print(Variable("x"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [-42])
            self.assertEqual(captured_output.getvalue().strip(), "-42")
    
    def test_execute_negative_float_let(self):
        """Test executing let statement with negative float."""
        ast = [
            Let("pi", Type.FLOAT, FloatLiteral(-3.14)),
            Print(Variable("pi"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [-3.14])
            self.assertEqual(captured_output.getvalue().strip(), "-3.14")
    
    def test_execute_negative_arithmetic(self):
        """Test executing arithmetic with negative numbers."""
        ast = [
            Let("result", Type.INTEGER, BinaryExpression(IntegerLiteral(-5), BinaryOperator.ADDITION, IntegerLiteral(3))),
            Print(Variable("result"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [-2])
            self.assertEqual(captured_output.getvalue().strip(), "-2")
    
    def test_execute_mixed_negative_positive_arithmetic(self):
        """Test executing arithmetic with both negative and positive numbers."""
        ast = [
            Let("result", Type.INTEGER, BinaryExpression(
                BinaryExpression(IntegerLiteral(-10), BinaryOperator.ADDITION, IntegerLiteral(5)),
                BinaryOperator.SUBTRACTION, IntegerLiteral(2))),
            Print(Variable("result"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [-7])  # -10 + 5 - 2 = -7
            self.assertEqual(captured_output.getvalue().strip(), "-7")
    
    def test_execute_negative_float_arithmetic(self):
        """Test executing arithmetic with negative floats."""
        ast = [
            Let("result", Type.FLOAT, BinaryExpression(FloatLiteral(-2.5), BinaryOperator.MULTIPLICATION, FloatLiteral(4.0))),
            Print(Variable("result"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [-10.0])
            self.assertEqual(captured_output.getvalue().strip(), "-10.0")
    
    def test_execute_negative_comparison(self):
        """Test executing comparison with negative numbers."""
        ast = [
            Let("result", Type.BOOLEAN, BinaryExpression(IntegerLiteral(-5), BinaryOperator.LESS_THAN, IntegerLiteral(0))),
            Print(Variable("result"))
        ]
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [True])
            self.assertEqual(captured_output.getvalue().strip(), "true")
    
    def test_execute_negative_in_list(self):
        """Test executing list operations with negative numbers."""
        code = code_block("""
            let nums list of integer = [-1, -2, -3]
            print nums
            print nums[0]
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [-1, -2, -3, -1])
            self.assertEqual(captured_output.getvalue().strip(), "[-1, -2, -3]\n-1")
    
    def test_execute_negative_in_function_call(self):
        """Test executing function calls with negative arguments."""
        code = code_block("""
            def add(x integer, y integer) returns integer
                return x + y
            let result integer = add(-5, 10)
            print result
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [5])
            self.assertEqual(captured_output.getvalue().strip(), "5")
    
    def test_execute_complex_negative_program(self):
        """Test executing a complex program with negative numbers."""
        code = code_block("""
            let temp integer = -10
            let adjustment integer = 5
            let final integer = temp + adjustment
            print final
            let floatTemp float = -2.5
            let floatResult float = floatTemp * -2.0
            print floatResult
        """)
        
        tokens = tokenize(code)
        ast = parse(tokens)
        type_check(ast)
        
        with self.capture_stdout() as captured_output:
            results = execute(ast)[0]
            self.assertEqual(results, [-5, 5.0])
            self.assertEqual(captured_output.getvalue().strip(), "-5\n5.0")


if __name__ == '__main__':
    unittest.main()