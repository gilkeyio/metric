#!/usr/bin/env python3
import unittest

from metric.tokenizer import TokenType, tokenize, Token, IntegerToken, IdentifierToken, FloatToken, TokenizerError
from test.test_utils import code_block


class TestTokenizer(unittest.TestCase):
    
    def test_tokenize_empty_string(self)  -> None:
        result = tokenize("")
        self.assertEqual(result, [])
    
    def test_tokenize_multiple_newlines(self)  -> None:
        # Multiple newlines now just create empty lines which are skipped
        result = tokenize("let x integer = 5\n\nprint x")
        expected: list[TokenType] = [Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, IntegerToken(5), Token.STATEMENT_SEPARATOR, 
                   Token.PRINT, IdentifierToken("x")]
        self.assertEqual(result, expected)
    
    def test_tokenize_single_digit(self)  -> None:
        result = tokenize("5")
        self.assertEqual(result, [IntegerToken(5)])
    
    def test_tokenize_multiple_digits(self)  -> None:
        result = tokenize("123")
        self.assertEqual(result, [IntegerToken(123)])
    
    def test_tokenize_zero(self)  -> None:
        result = tokenize("0")
        self.assertEqual(result, [IntegerToken(0)])
    
    def test_tokenize_large_number(self)  -> None:
        result = tokenize("999999")
        self.assertEqual(result, [IntegerToken(999999)])
    
    def test_tokenize_single_letter_identifier(self)  -> None:
        result = tokenize("x")
        self.assertEqual(result, [IdentifierToken("x")])
    
    def test_tokenize_multiple_letter_identifier(self)  -> None:
        result = tokenize("variable")
        self.assertEqual(result, [IdentifierToken("variable")])
    
    def test_tokenize_let_keyword(self)  -> None:
        result = tokenize("let")
        self.assertEqual(result, [Token.LET])
    
    def test_tokenize_print_keyword(self)  -> None:
        result = tokenize("print")
        self.assertEqual(result, [Token.PRINT])
    
    def test_tokenize_while_keyword(self)  -> None:
        result = tokenize("while")
        self.assertEqual(result, [Token.WHILE])
    
    def test_tokenize_set_keyword(self)  -> None:
        result = tokenize("set")
        self.assertEqual(result, [Token.SET])
    
    def test_tokenize_and_keyword(self)  -> None:
        result = tokenize("and")
        self.assertEqual(result, [Token.AND])
    
    def test_tokenize_or_keyword(self)  -> None:
        result = tokenize("or")
        self.assertEqual(result, [Token.OR])
    
    def test_tokenize_not_keyword(self)  -> None:
        result = tokenize("not")
        self.assertEqual(result, [Token.NOT])
    
    def test_tokenize_logical_and_expression(self)  -> None:
        result = tokenize("true and false")
        self.assertEqual(result, [Token.TRUE, Token.AND, Token.FALSE])
    
    def test_tokenize_logical_or_expression(self)  -> None:
        result = tokenize("true or false")
        self.assertEqual(result, [Token.TRUE, Token.OR, Token.FALSE])
    
    def test_tokenize_logical_not_expression(self)  -> None:
        result = tokenize("not true")
        self.assertEqual(result, [Token.NOT, Token.TRUE])
    
    def test_tokenize_complex_logical_expression(self)  -> None:
        result = tokenize("x and y or z")
        expected: list[TokenType] = [IdentifierToken("x"), Token.AND, IdentifierToken("y"), Token.OR, IdentifierToken("z")]
        self.assertEqual(result, expected)
    
    def test_tokenize_complex_logical_with_not_expression(self)  -> None:
        result = tokenize("not x and y")
        expected: list[TokenType] = [Token.NOT, IdentifierToken("x"), Token.AND, IdentifierToken("y")]
        self.assertEqual(result, expected)
    
    def test_tokenize_plus_operator(self)  -> None:
        result = tokenize("+")
        self.assertEqual(result, [Token.PLUS])
    
    def test_tokenize_minus_operator(self)  -> None:
        result = tokenize("-")
        self.assertEqual(result, [Token.MINUS])
    
    def test_tokenize_multiply_operator(self)  -> None:
        result = tokenize("*")
        self.assertEqual(result, [Token.MULTIPLY])
    
    def test_tokenize_divide_operator(self)  -> None:
        result = tokenize("/")
        self.assertEqual(result, [Token.DIVIDE])
    
    def test_tokenize_left_parenthesis(self)  -> None:
        result = tokenize("(")
        self.assertEqual(result, [Token.LEFT_PARENTHESIS])
    
    def test_tokenize_right_parenthesis(self)  -> None:
        result = tokenize(")")
        self.assertEqual(result, [Token.RIGHT_PARENTHESIS])
    
    def test_tokenize_equals(self)  -> None:
        result = tokenize("=")
        self.assertEqual(result, [Token.EQUALS])
    
    def test_tokenize_simple_expression_with_spaces(self)  -> None:
        result = tokenize("1 + 2")
        self.assertEqual(result, [IntegerToken(1), Token.PLUS, IntegerToken(2)])
    
    def test_tokenize_let_statement(self)  -> None:
        result = tokenize("let x integer = 5")
        self.assertEqual(result, [Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, IntegerToken(5)])
    
    def test_tokenize_print_statement(self)  -> None:
        result = tokenize("print x")
        self.assertEqual(result, [Token.PRINT, IdentifierToken("x")])
    
    def test_tokenize_complex_expression(self)  -> None:
        result = tokenize("(1 + 2) * 3")
        expected: list[TokenType] = [Token.LEFT_PARENTHESIS, IntegerToken(1), Token.PLUS, IntegerToken(2), 
                   Token.RIGHT_PARENTHESIS, Token.MULTIPLY, IntegerToken(3)]
        self.assertEqual(result, expected)
    
    def test_tokenize_multiple_statements_with_newlines(self)  -> None:
        result = tokenize("let x integer = 5\nprint x")
        expected: list[TokenType] = [Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, IntegerToken(5), 
                   Token.STATEMENT_SEPARATOR, Token.PRINT, IdentifierToken("x")]
        self.assertEqual(result, expected)
    
    def test_tokenize_identifier_followed_by_end_of_input(self)  -> None:
        result = tokenize("x")
        self.assertEqual(result, [IdentifierToken("x")])
    
    def test_tokenize_number_followed_by_end_of_input(self)  -> None:
        result = tokenize("42")
        self.assertEqual(result, [IntegerToken(42)])
    
    def test_tokenize_identifier_followed_by_parenthesis(self)  -> None:
        result = tokenize("x(")
        self.assertEqual(result, [IdentifierToken("x"), Token.LEFT_PARENTHESIS])
    
    def test_tokenize_number_followed_by_parenthesis(self)  -> None:
        result = tokenize("42)")
        self.assertEqual(result, [IntegerToken(42), Token.RIGHT_PARENTHESIS])

    # Boolean literal tests
    def test_tokenize_true_literal(self)  -> None:
        result = tokenize("true")
        self.assertEqual(result, [Token.TRUE])
    
    def test_tokenize_false_literal(self)  -> None:
        result = tokenize("false")
        self.assertEqual(result, [Token.FALSE])
    
    # Comparison operator tests
    def test_tokenize_less_than(self)  -> None:
        result = tokenize("5 < 10")
        self.assertEqual(result, [IntegerToken(5), Token.LESS_THAN, IntegerToken(10)])
    
    def test_tokenize_greater_than(self)  -> None:
        result = tokenize("10 > 5")
        self.assertEqual(result, [IntegerToken(10), Token.GREATER_THAN, IntegerToken(5)])
    
    def test_tokenize_less_than_or_equal(self)  -> None:
        result = tokenize("5 <= 10")
        self.assertEqual(result, [IntegerToken(5), Token.LESS_THAN_OR_EQUAL, IntegerToken(10)])
    
    def test_tokenize_greater_than_or_equal(self)  -> None:
        result = tokenize("10 >= 5")
        self.assertEqual(result, [IntegerToken(10), Token.GREATER_THAN_OR_EQUAL, IntegerToken(5)])
    
    def test_tokenize_equal_equal(self)  -> None:
        result = tokenize("5 == 5")
        self.assertEqual(result, [IntegerToken(5), Token.EQUAL_EQUAL, IntegerToken(5)])
    
    def test_tokenize_not_equal(self)  -> None:
        result = tokenize("5 != 3")
        self.assertEqual(result, [IntegerToken(5), Token.NOT_EQUAL, IntegerToken(3)])
    
    # Boolean expressions with variables
    def test_tokenize_boolean_expression(self)  -> None:
        result = tokenize("let result = x > y")
        expected: list[TokenType] = [Token.LET, IdentifierToken("result"), Token.EQUALS, IdentifierToken("x"), Token.GREATER_THAN, IdentifierToken("y")]
        self.assertEqual(result, expected)
    
    def test_tokenize_print_boolean(self)  -> None:
        result = tokenize("print true")
        self.assertEqual(result, [Token.PRINT, Token.TRUE])
    
    # If statement and indentation tests
    def test_tokenize_if_keyword(self)  -> None:
        result = tokenize("if true")
        self.assertEqual(result, [Token.IF, Token.TRUE])
    
    def test_tokenize_simple_if_block(self)  -> None:
        code = code_block("""if x > 5
    print x""")
        result = tokenize(code)
        expected: list[TokenType] = [Token.IF, IdentifierToken("x"), Token.GREATER_THAN, IntegerToken(5), Token.STATEMENT_SEPARATOR, Token.INDENT, Token.PRINT, IdentifierToken("x"), Token.DEDENT]
        self.assertEqual(result, expected)
    
    def test_tokenize_if_with_multiple_indented_statements(self)  -> None:
        code = code_block("""if true
    let x = 5
    print x""")
        result = tokenize(code)
        expected: list[TokenType] = [
            Token.IF, Token.TRUE, Token.STATEMENT_SEPARATOR,
            Token.INDENT, Token.LET, IdentifierToken("x"), Token.EQUALS, IntegerToken(5), Token.STATEMENT_SEPARATOR,
            Token.PRINT, IdentifierToken("x"), Token.DEDENT
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_if_with_dedent(self)  -> None:
        code = code_block("""if true
    print x
print y""")
        result = tokenize(code)
        expected: list[TokenType] = [
            Token.IF, Token.TRUE, Token.STATEMENT_SEPARATOR,
            Token.INDENT, Token.PRINT, IdentifierToken("x"), Token.STATEMENT_SEPARATOR,
            Token.DEDENT, Token.PRINT, IdentifierToken("y")
        ]
        self.assertEqual(result, expected)
    
    # While loop and set statement tests
    def test_tokenize_simple_while_block(self)  -> None:
        code = code_block("""while x > 0
    print x""")
        result = tokenize(code)
        expected: list[TokenType]= [Token.WHILE, IdentifierToken("x"), Token.GREATER_THAN, IntegerToken(0), Token.STATEMENT_SEPARATOR, Token.INDENT, Token.PRINT, IdentifierToken("x"), Token.DEDENT]
        self.assertEqual(result, expected)
    
    def test_tokenize_while_with_set(self)  -> None:
        code = code_block("""while true
    set x = x + 1""")
        result = tokenize(code)
        expected: list[TokenType] = [Token.WHILE, Token.TRUE, Token.STATEMENT_SEPARATOR, Token.INDENT, Token.SET, IdentifierToken("x"), Token.EQUALS, IdentifierToken("x"), Token.PLUS, IntegerToken(1), Token.DEDENT]
        self.assertEqual(result, expected)
    
    def test_tokenize_set_statement(self)  -> None:
        result = tokenize("set counter = counter + 1")
        expected: list[TokenType] = [Token.SET, IdentifierToken("counter"), Token.EQUALS, IdentifierToken("counter"), Token.PLUS, IntegerToken(1)]
        self.assertEqual(result, expected)
    
    # Type annotation tests
    def test_tokenize_integer_type(self)  -> None:
        result = tokenize("integer")
        self.assertEqual(result, [Token.INTEGER_TYPE])
    
    def test_tokenize_boolean_type(self)  -> None:
        result = tokenize("boolean")
        self.assertEqual(result, [Token.BOOLEAN_TYPE])
    
    def test_tokenize_typed_let_statement(self)  -> None:
        result = tokenize("let x integer = 5")
        expected: list[TokenType] = [Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, IntegerToken(5)]
        self.assertEqual(result, expected)
    
    def test_tokenize_typed_boolean_let(self)  -> None:
        result = tokenize("let flag boolean = true")
        expected: list[TokenType] = [Token.LET, IdentifierToken("flag"), Token.BOOLEAN_TYPE, Token.EQUALS, Token.TRUE]
        self.assertEqual(result, expected)
    
    def test_tokenize_complex_typed_program(self)  -> None:
        code = code_block("""let x integer = 10
let y boolean = x > 5
print y""")
        result = tokenize(code)
        expected: list[TokenType] = [
            Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, IntegerToken(10), Token.STATEMENT_SEPARATOR,
            Token.LET, IdentifierToken("y"), Token.BOOLEAN_TYPE, Token.EQUALS, IdentifierToken("x"), Token.GREATER_THAN, IntegerToken(5), Token.STATEMENT_SEPARATOR,
            Token.PRINT, IdentifierToken("y")
        ]
        self.assertEqual(result, expected)
    
    # Modulus operator tests
    def test_tokenize_modulus_operator(self)  -> None:
        result = tokenize("5 % 3")
        self.assertEqual(result, [IntegerToken(5), Token.MODULUS, IntegerToken(3)])
    
    def test_tokenize_modulus_expression(self)  -> None:
        result = tokenize("let remainder integer = x % y")
        expected: list[TokenType] = [Token.LET, IdentifierToken("remainder"), Token.INTEGER_TYPE, Token.EQUALS, IdentifierToken("x"), Token.MODULUS, IdentifierToken("y")]
        self.assertEqual(result, expected)
    
    # Float literal tests
    def test_tokenize_float_literal(self)  -> None:
        result = tokenize("3.14")
        self.assertEqual(result, [FloatToken(3.14)])
    
    def test_tokenize_float_zero(self)  -> None:
        result = tokenize("0.0")
        self.assertEqual(result, [FloatToken(0.0)])
    
    def test_tokenize_float_with_trailing_zeros(self)  -> None:
        result = tokenize("1.500")
        self.assertEqual(result, [FloatToken(1.5)])
    
    def test_tokenize_float_expression(self)  -> None:
        result = tokenize("3.14 + 2.5")
        expected: list[TokenType] = [FloatToken(3.14), Token.PLUS, FloatToken(2.5)]
        self.assertEqual(result, expected)
    
    def test_tokenize_float_type_annotation(self)  -> None:
        result = tokenize("float")
        self.assertEqual(result, [Token.FLOAT_TYPE])
    
    def test_tokenize_typed_float_let(self)  -> None:
        result = tokenize("let pi float = 3.14")
        expected: list[TokenType] = [Token.LET, IdentifierToken("pi"), Token.FLOAT_TYPE, Token.EQUALS, FloatToken(3.14)]
        self.assertEqual(result, expected)
    
    def test_tokenize_mixed_int_float_expression(self)  -> None:
        result = tokenize("let result float = 5 + 3.14")
        expected: list[TokenType] = [Token.LET, IdentifierToken("result"), Token.FLOAT_TYPE, Token.EQUALS, IntegerToken(5), Token.PLUS, FloatToken(3.14)]
        self.assertEqual(result, expected)
    
    def test_tokenize_fails_with_incomplete_float(self)  -> None:
        with self.assertRaises(TokenizerError) as cm:
            tokenize("3.")
        self.assertEqual(str(cm.exception), "Invalid float: missing digits after decimal point at line 1")
    
    def test_tokenize_fails_with_multiple_decimal_points(self)  -> None:
        with self.assertRaises(TokenizerError) as cm:
            tokenize("3.14.5")
        self.assertEqual(str(cm.exception), "Unexpected character: . at line 1")
    
    # Comment tokenization tests
    def test_tokenize_standalone_comment(self)  -> None:
        result = tokenize("# This is a comment")
        expected = [Token.COMMENT]
        self.assertEqual(result, expected)
    
    def test_tokenize_comment_after_statement(self)  -> None:
        result = tokenize("let x integer = 5 # This is a comment")
        expected: list[TokenType] = [Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, IntegerToken(5), Token.COMMENT]
        self.assertEqual(result, expected)
    
    def test_tokenize_comment_with_proper_indentation(self)  -> None:
        result = tokenize("    # Indented comment")
        expected = [Token.INDENT, Token.COMMENT, Token.DEDENT]
        self.assertEqual(result, expected)
    
    def test_tokenize_mixed_statements_and_comments(self)  -> None:
        code = code_block("""let x integer = 5 # Initialize x
print x # Print the value""")
        result = tokenize(code)
        expected: list[TokenType] = [
            Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, IntegerToken(5), Token.COMMENT, Token.STATEMENT_SEPARATOR,
            Token.PRINT, IdentifierToken("x"), Token.COMMENT
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_empty_comment(self)  -> None:
        result = tokenize("#")
        expected = [Token.COMMENT]
        self.assertEqual(result, expected)
    
    def test_tokenize_comment_with_special_characters(self)  -> None:
        result = tokenize("# Comment with !@#$%^&*()=+")
        expected = [Token.COMMENT]
        self.assertEqual(result, expected)
    
    def test_tokenize_comment_only_program(self)  -> None:
        code = code_block("""# First comment
# Second comment
# Third comment""")
        result = tokenize(code)
        expected = [
            Token.COMMENT, Token.STATEMENT_SEPARATOR,
            Token.COMMENT, Token.STATEMENT_SEPARATOR,
            Token.COMMENT
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_comment_between_statements(self)  -> None:
        code = code_block("""let x integer = 5
# This is a comment
print x""")
        result = tokenize(code)
        expected: list[TokenType] = [
            Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, IntegerToken(5), Token.STATEMENT_SEPARATOR,
            Token.COMMENT, Token.STATEMENT_SEPARATOR,
            Token.PRINT, IdentifierToken("x")
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_comment_with_indented_blocks(self)  -> None:
        code = code_block("""if true
    # Comment in if block
    print x
# Comment after if block""")
        result = tokenize(code)
        expected: list[TokenType] = [
            Token.IF, Token.TRUE, Token.STATEMENT_SEPARATOR,
            Token.INDENT, Token.COMMENT, Token.STATEMENT_SEPARATOR,
            Token.PRINT, IdentifierToken("x"), Token.STATEMENT_SEPARATOR,
            Token.DEDENT, Token.COMMENT
        ]
        self.assertEqual(result, expected)
    
    # Function token tests
    def test_tokenize_def_keyword(self)  -> None:
        """Test that 'def' keyword is tokenized correctly."""
        result = tokenize("def")
        self.assertEqual(result, [Token.DEF])
    
    def test_tokenize_returns_keyword(self)  -> None:
        """Test that 'returns' keyword is tokenized correctly."""
        result = tokenize("returns")
        self.assertEqual(result, [Token.RETURNS])
    
    def test_tokenize_return_keyword(self)  -> None:
        """Test that 'return' keyword is tokenized correctly."""
        result = tokenize("return")
        self.assertEqual(result, [Token.RETURN])
    
    def test_tokenize_comma_operator(self)  -> None:
        """Test that comma operator is tokenized correctly."""
        result = tokenize("x, y")
        self.assertEqual(result, [IdentifierToken("x"), Token.COMMA, IdentifierToken("y")])
    
    def test_tokenize_simple_function_declaration(self)  -> None:
        """Test tokenizing a simple function declaration."""
        code = "def add(x integer, y integer) returns integer"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.DEF, IdentifierToken("add"), Token.LEFT_PARENTHESIS,
            IdentifierToken("x"), Token.INTEGER_TYPE, Token.COMMA,
            IdentifierToken("y"), Token.INTEGER_TYPE, Token.RIGHT_PARENTHESIS,
            Token.RETURNS, Token.INTEGER_TYPE
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_function_call(self)  -> None:
        """Test tokenizing a simple function call."""
        code = "add(5, 10)"
        result = tokenize(code)
        expected : list[TokenType] = [
            IdentifierToken("add"), Token.LEFT_PARENTHESIS,
            IntegerToken(5), Token.COMMA, IntegerToken(10), Token.RIGHT_PARENTHESIS
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_return_statement(self)  -> None:
        """Test tokenizing a return statement."""
        code = "return x + y"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.RETURN, IdentifierToken("x"), Token.PLUS, IdentifierToken("y")
        ]
        self.assertEqual(result, expected)
    
    # Comprehensive List Token Tests
    def test_tokenize_list_type_declaration(self)  -> None:
        """Test list type declaration tokenization."""
        code = "let nums list of integer = [1, 2, 3]"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.LET, IdentifierToken("nums"), Token.LIST, Token.OF, Token.INTEGER_TYPE,
            Token.EQUALS, Token.LEFT_BRACKET, IntegerToken(1), Token.COMMA, IntegerToken(2),
            Token.COMMA, IntegerToken(3), Token.RIGHT_BRACKET
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_empty_list_literal(self)  -> None:
        """Test empty list literal tokenization."""
        code = "[]"
        result = tokenize(code)
        expected : list[TokenType] = [Token.LEFT_BRACKET, Token.RIGHT_BRACKET]
        self.assertEqual(result, expected)
    
    def test_tokenize_list_with_boolean_elements(self)  -> None:
        """Test list with boolean elements."""
        code = "[true, false, true]"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.LEFT_BRACKET, Token.TRUE, Token.COMMA, Token.FALSE,
            Token.COMMA, Token.TRUE, Token.RIGHT_BRACKET
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_list_with_float_elements(self)  -> None:
        """Test list with float elements."""
        code = "[1.5, 2.0, 3.14]"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.LEFT_BRACKET, FloatToken(1.5), Token.COMMA, FloatToken(2.0),
            Token.COMMA, FloatToken(3.14), Token.RIGHT_BRACKET
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_repeat_function_call(self)  -> None:
        """Test repeat function call tokenization."""
        code = "repeat(0, 5)"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.REPEAT, Token.LEFT_PARENTHESIS, IntegerToken(0),
            Token.COMMA, IntegerToken(5), Token.RIGHT_PARENTHESIS
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_len_function_call(self)  -> None:
        """Test len function call tokenization."""
        code = "len(nums)"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.LEN, Token.LEFT_PARENTHESIS, IdentifierToken("nums"), Token.RIGHT_PARENTHESIS
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_list_access(self)  -> None:
        """Test list access tokenization."""
        code = "nums[0]"
        result = tokenize(code)
        expected : list[TokenType] = [
            IdentifierToken("nums"), Token.LEFT_BRACKET, IntegerToken(0), Token.RIGHT_BRACKET
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_list_assignment(self)  -> None:
        """Test list assignment tokenization."""
        code = "set nums[1] = 42"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.SET, IdentifierToken("nums"), Token.LEFT_BRACKET, IntegerToken(1),
            Token.RIGHT_BRACKET, Token.EQUALS, IntegerToken(42)
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_nested_list_access(self)  -> None:
        """Test nested list access expressions."""
        code = "nums[i + 1]"
        result = tokenize(code)
        expected : list[TokenType] = [
            IdentifierToken("nums"), Token.LEFT_BRACKET, IdentifierToken("i"),
            Token.PLUS, IntegerToken(1), Token.RIGHT_BRACKET
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_complex_list_declaration(self)  -> None:
        """Test complex list declaration with repeat."""
        code = "let zeros list of boolean = repeat(false, len(other))"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.LET, IdentifierToken("zeros"), Token.LIST, Token.OF, Token.BOOLEAN_TYPE,
            Token.EQUALS, Token.REPEAT, Token.LEFT_PARENTHESIS, Token.FALSE, Token.COMMA,
            Token.LEN, Token.LEFT_PARENTHESIS, IdentifierToken("other"), Token.RIGHT_PARENTHESIS,
            Token.RIGHT_PARENTHESIS
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_list_in_function_parameter(self)  -> None:
        """Test list type in function parameter."""
        code = "def process(data list of integer) returns integer"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.DEF, IdentifierToken("process"), Token.LEFT_PARENTHESIS,
            IdentifierToken("data"), Token.LIST, Token.OF, Token.INTEGER_TYPE,
            Token.RIGHT_PARENTHESIS, Token.RETURNS, Token.INTEGER_TYPE
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_list_return_type(self)  -> None:
        """Test list as function return type."""
        code = "def create() returns list of integer"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.DEF, IdentifierToken("create"), Token.LEFT_PARENTHESIS,
            Token.RIGHT_PARENTHESIS, Token.RETURNS, Token.LIST, Token.OF, Token.INTEGER_TYPE
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_list_with_expressions(self)  -> None:
        """Test list with expression elements."""
        code = "[x + 1, y * 2, z]"
        result = tokenize(code)
        expected : list[TokenType] = [
            Token.LEFT_BRACKET, IdentifierToken("x"), Token.PLUS, IntegerToken(1),
            Token.COMMA, IdentifierToken("y"), Token.MULTIPLY, IntegerToken(2),
            Token.COMMA, IdentifierToken("z"), Token.RIGHT_BRACKET
        ]
        self.assertEqual(result, expected)
    
    def test_tokenize_list_keywords_are_recognized(self)  -> None:
        """Test that list keywords are properly tokenized as keywords, not identifiers."""
        result = tokenize("repeat(1, 5)")
        expected : list[TokenType] = [Token.REPEAT, Token.LEFT_PARENTHESIS, IntegerToken(1), Token.COMMA, IntegerToken(5), Token.RIGHT_PARENTHESIS]
        self.assertEqual(result, expected)
    
    # Negative number tests
    def test_tokenize_negative_integer(self)  -> None:
        """Test tokenizing negative integers with no space between minus and number."""
        result = tokenize("-5")
        self.assertEqual(result, [IntegerToken(-5)])
    
    def test_tokenize_negative_zero(self)  -> None:
        """Test tokenizing negative zero."""
        result = tokenize("-0")
        self.assertEqual(result, [IntegerToken(0)])
    
    def test_tokenize_negative_large_integer(self)  -> None:
        """Test tokenizing negative large integers."""
        result = tokenize("-999999")
        self.assertEqual(result, [IntegerToken(-999999)])
    
    def test_tokenize_negative_integer_in_expression(self)  -> None:
        """Test tokenizing negative integers in expressions."""
        result = tokenize("let x integer = -42")
        expected : list[TokenType] = [Token.LET, IdentifierToken("x"), Token.INTEGER_TYPE, Token.EQUALS, IntegerToken(-42)]
        self.assertEqual(result, expected)
    
    def test_tokenize_negative_integer_arithmetic(self)  -> None:
        """Test tokenizing negative integers in arithmetic expressions."""
        result = tokenize("-5 + 3")
        expected : list[TokenType] = [IntegerToken(-5), Token.PLUS, IntegerToken(3)]
        self.assertEqual(result, expected)
    
    def test_tokenize_negative_float(self)  -> None:
        """Test tokenizing negative floats with no space between minus and number."""
        result = tokenize("-3.14")
        self.assertEqual(result, [FloatToken(-3.14)])
    
    def test_tokenize_negative_float_zero(self)  -> None:
        """Test tokenizing negative float zero."""
        result = tokenize("-0.0")
        self.assertEqual(result, [FloatToken(-0.0)])
    
    def test_tokenize_negative_float_with_trailing_zeros(self)  -> None:
        """Test tokenizing negative floats with trailing zeros."""
        result = tokenize("-1.500")
        self.assertEqual(result, [FloatToken(-1.5)])
    
    def test_tokenize_negative_float_in_expression(self)  -> None:
        """Test tokenizing negative floats in expressions."""
        result = tokenize("let pi float = -3.14")
        expected : list[TokenType] = [Token.LET, IdentifierToken("pi"), Token.FLOAT_TYPE, Token.EQUALS, FloatToken(-3.14)]
        self.assertEqual(result, expected)
    
    def test_tokenize_negative_float_arithmetic(self)  -> None:
        """Test tokenizing negative floats in arithmetic expressions."""
        result = tokenize("-2.5 * 4.0")
        expected : list[TokenType] = [FloatToken(-2.5), Token.MULTIPLY, FloatToken(4.0)]
        self.assertEqual(result, expected)
    
    def test_tokenize_mixed_negative_positive(self)  -> None:
        """Test tokenizing expressions with both negative and positive numbers."""
        result = tokenize("-5 + 10 - 3")
        expected : list[TokenType] = [IntegerToken(-5), Token.PLUS, IntegerToken(10), Token.MINUS, IntegerToken(3)]
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()