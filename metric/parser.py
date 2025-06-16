from __future__ import annotations
from typing import Callable
from .metric_ast import *
from .tokenizer import Token, IntegerToken, IdentifierToken, FloatToken, TokenType


class ParseError(Exception):
    pass


def parse_binary_rest(left_expr: Expression, tokens: list[TokenType], operators: dict[Token, BinaryOperator], next_level_parser: Callable[[list[TokenType]], tuple[Expression, list[TokenType]]]) -> tuple[Expression, list[TokenType]]:
    """Generic helper for left-associative binary operators."""
    while tokens and isinstance(tokens[0], Token) and tokens[0] in operators:
        op_token = tokens[0]
        right_expr, remaining = next_level_parser(tokens[1:])
        operator = operators[op_token]
        left_expr = BinaryExpression(left_expr, operator, right_expr)
        tokens = remaining
    return left_expr, tokens



def parse_factor(tokens: list[TokenType]) -> tuple[Expression, list[TokenType]]:
    """Parse factor: integer | float | identifier | boolean | '(' expression ')'"""
    if not tokens:
        raise ParseError("Expected integer, float, identifier, boolean, or opening parenthesis")
    
    if isinstance(tokens[0], IntegerToken):
        return IntegerLiteral(tokens[0].value), tokens[1:]
    elif isinstance(tokens[0], FloatToken):
        return FloatLiteral(tokens[0].value), tokens[1:]
    elif isinstance(tokens[0], IdentifierToken):
        identifier_name = tokens[0].name
        remaining = tokens[1:]
        
        # Check if this is a function call (identifier followed by '(')
        if remaining and remaining[0] == Token.LEFT_PARENTHESIS:
            # Parse function call
            remaining = remaining[1:]  # consume '('
            
            # Parse arguments
            arguments: list[Expression] = []
            if remaining and remaining[0] != Token.RIGHT_PARENTHESIS:
                # Parse first argument
                arg_expr, remaining = parse_expression(remaining)
                arguments.append(arg_expr)
                
                # Parse additional arguments
                while remaining and remaining[0] == Token.COMMA:
                    remaining = remaining[1:]  # consume comma
                    arg_expr, remaining = parse_expression(remaining)
                    arguments.append(arg_expr)
            
            # Expect closing parenthesis
            if not remaining or remaining[0] != Token.RIGHT_PARENTHESIS:
                raise ParseError("Expected ')' after function arguments")
            remaining = remaining[1:]
            
            return FunctionCall(identifier_name, arguments), remaining
        elif remaining and remaining[0] == Token.LEFT_BRACKET:
            # Parse list access: identifier[index]
            remaining = remaining[1:]  # consume '['
            
            # Parse index expression
            index_expr, remaining = parse_expression(remaining)
            
            # Expect closing bracket
            if not remaining or remaining[0] != Token.RIGHT_BRACKET:
                raise ParseError("Expected ']' after list index")
            remaining = remaining[1:]
            
            return ListAccess(Variable(identifier_name), index_expr), remaining
        else:
            # Regular variable reference
            return Variable(identifier_name), remaining
    elif tokens[0] == Token.TRUE:
        return BooleanLiteral(True), tokens[1:]
    elif tokens[0] == Token.FALSE:
        return BooleanLiteral(False), tokens[1:]
    elif tokens[0] == Token.LEFT_PARENTHESIS:
        expr, remaining = parse_expression(tokens[1:])
        if not remaining or remaining[0] != Token.RIGHT_PARENTHESIS:
            raise ParseError("Expected closing parenthesis")
        return expr, remaining[1:]
    elif tokens[0] == Token.LEFT_BRACKET:
        # Parse list literal: [expr, expr, ...]
        remaining = tokens[1:]  # consume '['
        elements: list[Expression] = []
        
        # Handle empty list
        if remaining and remaining[0] == Token.RIGHT_BRACKET:
            return ListLiteral([]), remaining[1:]
        
        # Parse first element
        if remaining:
            elem_expr, remaining = parse_expression(remaining)
            elements.append(elem_expr)
        
        # Parse additional elements
        while remaining and remaining[0] == Token.COMMA:
            remaining = remaining[1:]  # consume comma
            elem_expr, remaining = parse_expression(remaining)
            elements.append(elem_expr)
        
        # Expect closing bracket
        if not remaining or remaining[0] != Token.RIGHT_BRACKET:
            raise ParseError("Expected ']' after list elements")
        remaining = remaining[1:]
        
        return ListLiteral(elements), remaining
    elif tokens[0] == Token.REPEAT:
        # Parse repeat(value, count)
        if len(tokens) < 2 or tokens[1] != Token.LEFT_PARENTHESIS:
            raise ParseError("Expected '(' after 'repeat'")
        remaining = tokens[2:]  # consume 'repeat' and '('
        
        # Parse value argument
        value_expr, remaining = parse_expression(remaining)
        
        # Expect comma
        if not remaining or remaining[0] != Token.COMMA:
            raise ParseError("Expected ',' after repeat value")
        remaining = remaining[1:]
        
        # Parse count argument
        count_expr, remaining = parse_expression(remaining)
        
        # Expect closing parenthesis
        if not remaining or remaining[0] != Token.RIGHT_PARENTHESIS:
            raise ParseError("Expected ')' after repeat arguments")
        remaining = remaining[1:]
        
        return RepeatCall(value_expr, count_expr), remaining
    elif tokens[0] == Token.LEN:
        # Parse len(list_expr)
        if len(tokens) < 2 or tokens[1] != Token.LEFT_PARENTHESIS:
            raise ParseError("Expected '(' after 'len'")
        remaining = tokens[2:]  # consume 'len' and '('
        
        # Parse list expression
        list_expr, remaining = parse_expression(remaining)
        
        # Expect closing parenthesis
        if not remaining or remaining[0] != Token.RIGHT_PARENTHESIS:
            raise ParseError("Expected ')' after len argument")
        remaining = remaining[1:]
        
        return LenCall(list_expr), remaining
    else:
        raise ParseError("Expected integer, float, identifier, boolean, or opening parenthesis")


def parse_multiplicative_expression(tokens: list[TokenType]) -> tuple[Expression, list[TokenType]]:
    """Parse multiplicative expression: factor (('*' | '/' | '%') factor)*"""
    left_expr, remaining = parse_factor(tokens)
    
    operators = {
        Token.MULTIPLY: BinaryOperator.MULTIPLICATION,
        Token.DIVIDE: BinaryOperator.DIVISION,
        Token.MODULUS: BinaryOperator.MODULUS
    }
    
    return parse_binary_rest(left_expr, remaining, operators, parse_factor)


def parse_additive_expression(tokens: list[TokenType]) -> tuple[Expression, list[TokenType]]:
    """Parse additive expression: multiplicative (('+' | '-') multiplicative)*"""
    left_expr, remaining = parse_multiplicative_expression(tokens)
    
    operators = {
        Token.PLUS: BinaryOperator.ADDITION,
        Token.MINUS: BinaryOperator.SUBTRACTION
    }
    
    return parse_binary_rest(left_expr, remaining, operators, parse_multiplicative_expression)


def parse_comparison_expression(tokens: list[TokenType]) -> tuple[Expression, list[TokenType]]:
    """Parse comparison expression: additive (('<' | '>' | '<=' | '>=' | '==' | '!=') additive)*"""
    left_expr, remaining = parse_additive_expression(tokens)
    
    operators = {
        Token.LESS_THAN: BinaryOperator.LESS_THAN,
        Token.GREATER_THAN: BinaryOperator.GREATER_THAN,
        Token.LESS_THAN_OR_EQUAL: BinaryOperator.LESS_THAN_OR_EQUAL,
        Token.GREATER_THAN_OR_EQUAL: BinaryOperator.GREATER_THAN_OR_EQUAL,
        Token.IDENTICAL_TO: BinaryOperator.IDENTICAL_TO,
        Token.NOT_EQUAL: BinaryOperator.NOT_EQUAL
    }
    
    return parse_binary_rest(left_expr, remaining, operators, parse_additive_expression)


def parse_unary_logical_expression(tokens: list[TokenType]) -> tuple[Expression, list[TokenType]]:
    """Parse unary logical expression: 'not' unary_logical | comparison"""
    if tokens and tokens[0] == Token.NOT:
        # Parse 'not' unary expression
        operand, remaining = parse_unary_logical_expression(tokens[1:])  # Right-associative for consecutive nots
        return UnaryExpression(UnaryOperator.NOT, operand), remaining
    else:
        return parse_comparison_expression(tokens)


def parse_logical_and_expression(tokens: list[TokenType]) -> tuple[Expression, list[TokenType]]:
    """Parse logical AND expression: unary_logical ('and' unary_logical)*"""
    left_expr, remaining = parse_unary_logical_expression(tokens)
    
    operators = {
        Token.AND: BinaryOperator.AND
    }
    
    return parse_binary_rest(left_expr, remaining, operators, parse_unary_logical_expression)


def parse_logical_or_expression(tokens: list[TokenType]) -> tuple[Expression, list[TokenType]]:
    """Parse logical OR expression: logical_and ('or' logical_and)*"""
    left_expr, remaining = parse_logical_and_expression(tokens)
    
    operators = {
        Token.OR: BinaryOperator.OR
    }
    
    return parse_binary_rest(left_expr, remaining, operators, parse_logical_and_expression)


def parse_expression(tokens: list[TokenType]) -> tuple[Expression, list[TokenType]]:
    """Parse expression: logical OR expression"""
    return parse_logical_or_expression(tokens)


def parse_statement(tokens: list[TokenType]) -> tuple[Statement, list[TokenType]]:
    """Parse statement: let statement | print statement | if statement | while statement | set statement | comment"""
    if not tokens:
        raise ParseError("Expected 'let', 'print', 'if', 'while', 'set', 'def', 'return', or comment statement")
    
    # Only Token enum values are valid statement starters
    if not isinstance(tokens[0], Token):
        raise ParseError("Expected 'let', 'print', 'if', 'while', 'set', 'def', 'return', or comment statement")
    
    # Dispatch table for statement parsing
    statement_parsers = {
        Token.LET: _parse_let_statement,
        Token.PRINT: _parse_print_statement,
        Token.IF: parse_if_statement,
        Token.WHILE: parse_while_statement,
        Token.SET: _parse_set_statement,
        Token.COMMENT: _parse_comment_statement,
        Token.DEF: _parse_function_declaration,
        Token.RETURN: _parse_return_statement
    }
    
    if tokens[0] in statement_parsers:
        return statement_parsers[tokens[0]](tokens)
    else:
        raise ParseError("Expected 'let', 'print', 'if', 'while', 'set', 'def', 'return', or comment statement")


def _parse_let_statement(tokens: list[TokenType]) -> tuple[Statement, list[TokenType]]:
    """Parse let statement: 'let' identifier type '=' expression"""
    if len(tokens) < 5 or not isinstance(tokens[1], IdentifierToken):
        raise ParseError("Expected 'let identifier type = expression'")
    
    name = tokens[1].name
    
    # Parse type (could be list type)
    type_annotation, remaining_after_type = _parse_type(tokens[2:])
    
    if not remaining_after_type or remaining_after_type[0] != Token.ASSIGN:
        raise ParseError("Expected '=' after type annotation")
    
    expr, remaining = parse_expression(remaining_after_type[1:])
    return Let(name, type_annotation, expr), remaining


def _parse_print_statement(tokens: list[TokenType]) -> tuple[Statement, list[TokenType]]:
    """Parse print statement: 'print' expression"""
    expr, remaining = parse_expression(tokens[1:])
    return Print(expr), remaining


def _parse_set_statement(tokens: list[TokenType]) -> tuple[Statement, list[TokenType]]:
    """Parse set statement: 'set' identifier '=' expression | 'set' identifier '[' expression ']' '=' expression"""
    if len(tokens) < 4 or not isinstance(tokens[1], IdentifierToken):
        raise ParseError("Expected 'set identifier = expression'")
    
    name = tokens[1].name
    remaining = tokens[2:]
    
    # Check for list assignment: set list[index] = value
    if remaining and remaining[0] == Token.LEFT_BRACKET:
        remaining = remaining[1:]  # consume '['
        
        # Parse index expression
        index_expr, remaining = parse_expression(remaining)
        
        # Expect closing bracket
        if not remaining or remaining[0] != Token.RIGHT_BRACKET:
            raise ParseError("Expected ']' after list index")
        remaining = remaining[1:]
        
        # Expect equals
        if not remaining or remaining[0] != Token.ASSIGN:
            raise ParseError("Expected '=' after list index")
        remaining = remaining[1:]
        
        # Parse value expression
        value_expr, remaining = parse_expression(remaining)
        
        return ListAssignment(name, index_expr, value_expr), remaining
    
    # Regular variable assignment: set var = value
    elif remaining and remaining[0] == Token.ASSIGN:
        remaining = remaining[1:]  # consume '='
        value_expr, remaining = parse_expression(remaining)
        return Set(name, value_expr), remaining
    else:
        raise ParseError("Expected 'set identifier = expression'")


def _parse_comment_statement(tokens: list[TokenType]) -> tuple[Statement, list[TokenType]]:
    """Parse comment statement: just consume the comment token"""
    if not tokens or tokens[0] != Token.COMMENT:
        raise ParseError("Expected comment")
    
    return Comment(), tokens[1:]


def parse_if_statement(tokens: list[TokenType]) -> tuple[Statement, list[TokenType]]:
    """Parse if statement: 'if' expression STATEMENT_SEPARATOR INDENT statements DEDENT"""
    condition, body, remaining = _parse_control_flow_statement(tokens, Token.IF, "if")
    return If(condition, body), remaining


def parse_while_statement(tokens: list[TokenType]) -> tuple[Statement, list[TokenType]]:
    """Parse while statement: 'while' expression STATEMENT_SEPARATOR INDENT statements DEDENT"""
    condition, body, remaining = _parse_control_flow_statement(tokens, Token.WHILE, "while")
    return While(condition, body), remaining


def _parse_control_flow_statement(tokens: list[TokenType], 
                                 expected_token: Token, 
                                 statement_name: str) -> tuple[Expression, list[Statement], list[TokenType]]:
    """Parse a control flow statement (if/while) with condition and indented body."""
    if not tokens or tokens[0] != expected_token:
        raise ParseError(f"Expected '{statement_name}'")
    
    tokens = tokens[1:]  # consume keyword
    
    if not tokens:
        raise ParseError(f"Expected expression after '{statement_name}'")
    
    # Parse condition expression
    condition, remaining = parse_expression(tokens)
    
    if not remaining or remaining[0] != Token.STATEMENT_SEPARATOR:
        raise ParseError(f"Expected newline after '{statement_name}' condition")
    
    remaining = remaining[1:]  # consume STATEMENT_SEPARATOR
    
    if not remaining or remaining[0] != Token.INDENT:
        raise ParseError(f"Expected indented block after '{statement_name}'")
    
    remaining = remaining[1:]  # consume INDENT
    
    # Parse body statements
    body_statements, remaining = _parse_indented_block(remaining)
    
    if not remaining or remaining[0] != Token.DEDENT:
        raise ParseError(f"Expected dedent after '{statement_name}' body")
    
    remaining = remaining[1:]  # consume DEDENT
    
    return condition, body_statements, remaining


def _parse_indented_block(tokens: list[TokenType]) -> tuple[list[Statement], list[TokenType]]:
    """Parse an indented block of statements and return statements plus remaining tokens."""
    statements: list[Statement] = []
    remaining = tokens
    
    while remaining and remaining[0] != Token.DEDENT:
        if remaining[0] == Token.STATEMENT_SEPARATOR:
            remaining = remaining[1:]  # skip separators
            continue
        if remaining[0] == Token.INDENT:
            remaining = remaining[1:]  # skip nested indents
            continue
        
        stmt, remaining = parse_statement(remaining)
        statements.append(stmt)
    
    return statements, remaining


def _parse_type_annotation(token: Token | IntegerToken | FloatToken | IdentifierToken) -> Type:
    """Parse a type annotation token and return the corresponding Type."""
    if token == Token.INTEGER_TYPE:
        return Type.INTEGER
    elif token == Token.BOOLEAN_TYPE:
        return Type.BOOLEAN
    elif token == Token.FLOAT_TYPE:
        return Type.FLOAT
    else:
        raise ParseError("Expected type annotation (integer, boolean, or float)")


def _parse_type(tokens: list[TokenType]) -> tuple[Type | ListType, list[TokenType]]:
    """Parse a type from tokens and return the type and remaining tokens."""
    if not tokens:
        raise ParseError("Expected type")
    
    # Check for list type: "list of type"
    if tokens[0] == Token.LIST:
        if len(tokens) < 3 or tokens[1] != Token.OF:
            raise ParseError("Expected 'of' after 'list'")
        
        element_type = _parse_type_annotation(tokens[2])
        return ListType(element_type), tokens[3:]
    else:
        # Regular type
        type_annotation = _parse_type_annotation(tokens[0])
        return type_annotation, tokens[1:]


def parse_statements(tokens: list[TokenType]) -> list[Statement]:
    """Parse sequence of statements separated by statement separators."""
    statements: list[Statement] = []
    
    while tokens:
        # Skip statement separators at the beginning
        if tokens[0] == Token.STATEMENT_SEPARATOR:
            tokens = tokens[1:]
            continue
            
        stmt, remaining = parse_statement(tokens)
        statements.append(stmt)
        tokens = remaining
        
        # Skip optional statement separator after statement
        if tokens and tokens[0] == Token.STATEMENT_SEPARATOR:
            tokens = tokens[1:]
    
    return statements


def _parse_function_declaration(tokens: list[TokenType]) -> tuple[Statement, list[TokenType]]:
    """Parse function declaration: 'def' identifier '(' parameters ')' 'returns' type body"""
    if len(tokens) < 6:
        raise ParseError("Expected 'def identifier(parameters) returns type'")
    
    # Parse 'def'
    if tokens[0] != Token.DEF:
        raise ParseError("Expected 'def'")
    
    # Parse function name
    if not isinstance(tokens[1], IdentifierToken):
        raise ParseError("Expected function name")
    function_name = tokens[1].name
    
    # Parse '('
    if tokens[2] != Token.LEFT_PARENTHESIS:
        raise ParseError("Expected '(' after function name")
    
    # Parse parameters
    parameters, remaining_after_params = _parse_parameter_list(tokens[3:])
    
    # Parse ')'
    if not remaining_after_params or remaining_after_params[0] != Token.RIGHT_PARENTHESIS:
        raise ParseError("Expected ')' after parameters")
    remaining_after_params = remaining_after_params[1:]
    
    # Parse 'returns'
    if not remaining_after_params or remaining_after_params[0] != Token.RETURNS:
        raise ParseError("Expected 'returns'")
    remaining_after_params = remaining_after_params[1:]
    
    # Parse return type
    if not remaining_after_params:
        raise ParseError("Expected return type")
    return_type, remaining_after_type = _parse_type(remaining_after_params)
    
    # Parse body (expect STATEMENT_SEPARATOR, INDENT, statements, DEDENT)
    if not remaining_after_type or remaining_after_type[0] != Token.STATEMENT_SEPARATOR:
        raise ParseError("Expected newline after function signature")
    remaining_after_type = remaining_after_type[1:]
    
    if not remaining_after_type or remaining_after_type[0] != Token.INDENT:
        raise ParseError("Expected indented function body")
    remaining_after_type = remaining_after_type[1:]
    
    # Parse function body statements
    body: list[Statement] = []
    while remaining_after_type and remaining_after_type[0] != Token.DEDENT:
        stmt, remaining_after_type = parse_statement(remaining_after_type)
        body.append(stmt)
        if remaining_after_type and remaining_after_type[0] == Token.STATEMENT_SEPARATOR:
            remaining_after_type = remaining_after_type[1:]
    
    # Parse DEDENT
    if not remaining_after_type or remaining_after_type[0] != Token.DEDENT:
        raise ParseError("Expected dedent after function body")
    remaining_after_type = remaining_after_type[1:]
    
    function_decl = FunctionDeclaration(function_name, parameters, return_type, body)
    return function_decl, remaining_after_type


def _parse_parameter_list(tokens: list[TokenType]) -> tuple[list[Parameter], list[TokenType]]:
    """Parse parameter list: parameter (',' parameter)*"""
    parameters: list[Parameter] = []
    
    # Handle empty parameter list
    if tokens and tokens[0] == Token.RIGHT_PARENTHESIS:
        return parameters, tokens
    
    # Parse first parameter
    if not tokens or not isinstance(tokens[0], IdentifierToken):
        raise ParseError("Expected parameter name")
    
    param_name = tokens[0].name
    tokens = tokens[1:]
    
    # Parse parameter type
    if not tokens:
        raise ParseError("Expected parameter type")
    param_type, tokens = _parse_type(tokens)
    
    parameters.append(Parameter(param_name, param_type))
    
    # Parse additional parameters
    while tokens and tokens[0] == Token.COMMA:
        tokens = tokens[1:]  # consume comma
        
        if not tokens or not isinstance(tokens[0], IdentifierToken):
            raise ParseError("Expected parameter name after comma")
        
        param_name = tokens[0].name
        tokens = tokens[1:]
        
        if not tokens:
            raise ParseError("Expected parameter type")
        param_type, tokens = _parse_type(tokens)
        
        parameters.append(Parameter(param_name, param_type))
    
    return parameters, tokens


def _parse_return_statement(tokens: list[TokenType]) -> tuple[Statement, list[TokenType]]:
    """Parse return statement: 'return' expression"""
    if len(tokens) < 2:
        raise ParseError("Expected 'return expression'")
    
    if tokens[0] != Token.RETURN:
        raise ParseError("Expected 'return'")
    
    # Parse expression
    expression, remaining = parse_expression(tokens[1:])
    
    return Return(expression), remaining


def parse(tokens: list[TokenType]) -> AbstractSyntaxTree:
    """Parse tokens into an abstract syntax tree."""
    statements = parse_statements(tokens)
    return statements