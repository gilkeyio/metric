from enum import Enum
from dataclasses import dataclass

class Token(Enum):
    INTEGER = "Integer"
    IDENTIFIER = "Identifier"
    LET = "Let"
    PRINT = "Print"
    TRUE = "True"
    FALSE = "False"
    PLUS = "Plus"
    MINUS = "Minus"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"
    MODULUS = "Modulus"
    LEFT_PARENTHESIS = "LeftParenthesis"
    RIGHT_PARENTHESIS = "RightParenthesis"
    EQUALS = "Equals"
    LESS_THAN = "LessThan"
    GREATER_THAN = "GreaterThan"
    LESS_THAN_OR_EQUAL = "LessThanOrEqual"
    GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
    EQUAL_EQUAL = "EqualEqual"
    NOT_EQUAL = "NotEqual"
    STATEMENT_SEPARATOR = "StatementSeparator"
    IF = "If"
    WHILE = "While"
    SET = "Set"
    INDENT = "Indent"
    DEDENT = "Dedent"
    INTEGER_TYPE = "IntegerType"
    BOOLEAN_TYPE = "BooleanType"
    FLOAT_TYPE = "FloatType"
    COMMENT = "Comment"
    DEF = "Def"
    RETURNS = "Returns"
    RETURN = "Return"
    COMMA = "Comma"
    LIST = "List"
    OF = "Of"
    LEFT_BRACKET = "LeftBracket"
    RIGHT_BRACKET = "RightBracket"
    REPEAT = "Repeat"
    LEN = "Len"
    AND = "And"
    OR = "Or"
    NOT = "Not"


@dataclass
class IntegerToken:
    value: int


@dataclass
class FloatToken:
    value: float


@dataclass
class IdentifierToken:
    name: str


@dataclass
class Position:
    line: int
    column: int


class TokenizerError(Exception):
    pass


TokenType = Token | IntegerToken | FloatToken | IdentifierToken


def tokenize(input_str: str) -> list[TokenType]:
    """Tokenize input string into list of tokens with indentation handling."""
    lines = input_str.split('\n')
    tokens: list[TokenType] = []
    indent_stack = [0]  # Stack to track indentation levels
    
    for line_num, line in enumerate(lines, 1):
        if not line.strip():  # Skip empty lines
            continue
            
        # Calculate indentation
        indent_level = 0
        for char in line:
            if char == ' ':
                indent_level += 1
            else:
                break
        
        # Validate indentation (must be multiple of 4, unless it's 0)
        if indent_level > 0 and indent_level % 4 != 0:
            raise TokenizerError(f"Invalid indentation: expected 4 spaces at line {line_num}")
        
        indent_depth = indent_level // 4
        
        # Handle indentation changes
        if indent_depth > indent_stack[-1]:
            if indent_depth != indent_stack[-1] + 1:
                raise TokenizerError(f"Invalid indentation: expected {(indent_stack[-1] + 1) * 4} spaces at line {line_num}")
            indent_stack.append(indent_depth)
            tokens.append(Token.INDENT)
        elif indent_depth < indent_stack[-1]:
            while len(indent_stack) > 1 and indent_stack[-1] > indent_depth:
                indent_stack.pop()
                tokens.append(Token.DEDENT)
            if indent_stack[-1] != indent_depth:
                raise TokenizerError(f"Invalid indentation: expected {indent_stack[-1] * 4} spaces at line {line_num}")
        
        # Tokenize the content of the line
        line_content = line.strip()
        line_tokens = tokenize_line(line_content, line_num)
        tokens.extend(line_tokens)
        
        # Add statement separator if not the last line and there are more non-empty lines
        if line_num < len(lines) and any(l.strip() for l in lines[line_num:]):
            tokens.append(Token.STATEMENT_SEPARATOR)
    
    # Add any remaining DEDENT tokens
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token.DEDENT)
    
    return tokens

def tokenize_line(line_content: str, line_num: int) -> list[TokenType]:
    """Tokenize a single line of content."""
    assert line_content, "line_content should not be empty"
    
    # Check for comments first
    comment_pos = line_content.find('#')
    if comment_pos != -1:
        # Tokenize the part before the comment (if any)
        code_part = line_content[:comment_pos].rstrip()
        tokens: list[TokenType] = []
        if code_part:
            tokens = tokenize_line_without_comments(code_part, line_num)
        
        # Add the comment token
        tokens.append(Token.COMMENT)
        return tokens
    
    # No comments, tokenize normally
    return tokenize_line_without_comments(line_content, line_num)

def _parse_number(line_content: str, start: int, line_num: int) -> tuple[TokenType, int]:
    """Parse a number (integer or float) starting at the given position.
    Returns the token and the new position.
    """
    i = start
    is_negative = line_content[i] == '-'
    if is_negative:
        i += 1
    
    # Parse integer part
    while i < len(line_content) and line_content[i].isdigit():
        i += 1
    
    # Check for decimal point
    if i < len(line_content) and line_content[i] == '.':
        i += 1  # consume the decimal point
        decimal_start = i
        while i < len(line_content) and line_content[i].isdigit():
            i += 1
        
        # Check if we have digits after decimal point
        if i == decimal_start:
            raise TokenizerError(f"Invalid float: missing digits after decimal point at line {line_num}")
        
        number_str = line_content[start:i]
        return FloatToken(float(number_str)), i
    else:
        number_str = line_content[start:i]
        return IntegerToken(int(number_str)), i


def _get_keyword_token(identifier: str) -> TokenType:
    """Convert identifier to appropriate keyword token or return identifier token."""
    match identifier:
        case "let":
            return Token.LET
        case "print":
            return Token.PRINT
        case "true":
            return Token.TRUE
        case "false":
            return Token.FALSE
        case "if":
            return Token.IF
        case "while":
            return Token.WHILE
        case "set":
            return Token.SET
        case "integer":
            return Token.INTEGER_TYPE
        case "boolean":
            return Token.BOOLEAN_TYPE
        case "float":
            return Token.FLOAT_TYPE
        case "def":
            return Token.DEF
        case "returns":
            return Token.RETURNS
        case "return":
            return Token.RETURN
        case "list":
            return Token.LIST
        case "of":
            return Token.OF
        case "repeat":
            return Token.REPEAT
        case "len":
            return Token.LEN
        case "and":
            return Token.AND
        case "or":
            return Token.OR
        case "not":
            return Token.NOT
        case _:
            return IdentifierToken(identifier)


def _lookahead_matches(line_content: str, pos: int, expected: str) -> bool:
    """Check if the string at pos matches the expected multi-character sequence."""
    return (pos + len(expected) <= len(line_content) and 
            line_content[pos:pos + len(expected)] == expected)


def _is_negative_number_start(line_content: str, pos: int) -> bool:
    """Check if position starts a negative number (minus immediately followed by digit)."""
    return (line_content[pos] == '-' and 
            pos + 1 < len(line_content) and 
            line_content[pos + 1].isdigit())


def tokenize_line_without_comments(line_content: str, line_num: int) -> list[TokenType]:
    """Tokenize a single line of content without comments."""
    assert line_content, "line_content should not be empty"
    
    tokens: list[TokenType] = []
    i = 0
    
    while i < len(line_content):
        char = line_content[i]
        
        match char:
            case ' ':
                i += 1
            
            case '=' if _lookahead_matches(line_content, i, '=='):
                tokens.append(Token.EQUAL_EQUAL)
                i += 2
            
            case '!' if _lookahead_matches(line_content, i, '!='):
                tokens.append(Token.NOT_EQUAL)
                i += 2
            
            case '<' if _lookahead_matches(line_content, i, '<='):
                tokens.append(Token.LESS_THAN_OR_EQUAL)
                i += 2
            
            case '>' if _lookahead_matches(line_content, i, '>='):
                tokens.append(Token.GREATER_THAN_OR_EQUAL)
                i += 2
            
            case '-' if _is_negative_number_start(line_content, i):
                token, new_pos = _parse_number(line_content, i, line_num)
                tokens.append(token)
                i = new_pos
            
            case '+':
                tokens.append(Token.PLUS)
                i += 1
            case '-':
                tokens.append(Token.MINUS)
                i += 1
            case '*':
                tokens.append(Token.MULTIPLY)
                i += 1
            case '/':
                tokens.append(Token.DIVIDE)
                i += 1
            case '%':
                tokens.append(Token.MODULUS)
                i += 1
            case '(':
                tokens.append(Token.LEFT_PARENTHESIS)
                i += 1
            case ')':
                tokens.append(Token.RIGHT_PARENTHESIS)
                i += 1
            case '=':
                tokens.append(Token.EQUALS)
                i += 1
            case '<':
                tokens.append(Token.LESS_THAN)
                i += 1
            case '>':
                tokens.append(Token.GREATER_THAN)
                i += 1
            case ',':
                tokens.append(Token.COMMA)
                i += 1
            case '[':
                tokens.append(Token.LEFT_BRACKET)
                i += 1
            case ']':
                tokens.append(Token.RIGHT_BRACKET)
                i += 1
            
            case c if c.isdigit():
                token, new_pos = _parse_number(line_content, i, line_num)
                tokens.append(token)
                i = new_pos
            
            case c if c.isalpha():
                start = i
                while i < len(line_content) and line_content[i].isalpha():
                    i += 1
                identifier = line_content[start:i]
                tokens.append(_get_keyword_token(identifier))
            
            case '\t':
                raise TokenizerError(f"Unexpected character: \\t at line {line_num}")
            
            case _:
                raise TokenizerError(f"Unexpected character: {char} at line {line_num}")
    
    return tokens