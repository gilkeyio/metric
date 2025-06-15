from enum import Enum
from dataclasses import dataclass

from metric.errors import TokenizerError

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

TokenType = Token | IntegerToken | FloatToken | IdentifierToken


# Indentation configuration constants
INDENT_SIZE = 4
BASE_INDENT_LEVEL = 0

def _extract_indentation_info(line: str) -> tuple[int, str]:
    """Extract indentation level and content from a line."""
    stripped = line.lstrip(" ")
    return len(line) - len(stripped), line.strip()


def _validate_indentation_increment(spaces: int, line_num: int) -> int:
    """Validate and convert space count to indentation depth."""
    if spaces > 0 and spaces % INDENT_SIZE != 0:
        raise TokenizerError(
            f"Invalid indentation: expected multiples of {INDENT_SIZE} spaces",
            line=line_num,
            column=1
        )
    
    return spaces // INDENT_SIZE


def _handle_dedentation(target_depth: int, indent_stack: list[int]) -> list[TokenType]:
    """Handle dedentation to target depth with validation."""
    dedent_tokens: list[TokenType] = []
    
    while len(indent_stack) > 1 and indent_stack[-1] > target_depth:
        indent_stack.pop()
        dedent_tokens.append(Token.DEDENT)
    
    # Assert we landed on a valid indentation level - this should never fail
    # if the indentation logic is working correctly
    assert indent_stack[-1] == target_depth, f"Indentation logic error: expected to land on level {target_depth}, but landed on {indent_stack[-1]}"
    
    return dedent_tokens


def _handle_indentation_change(indent_depth: int, indent_stack: list[int], line_num: int) -> list[TokenType]:
    """Handle indentation changes using comprehensive pattern matching."""
    current_depth = indent_stack[-1]
    
    if indent_depth == current_depth:
        return []
    elif indent_depth == current_depth + 1:
        indent_stack.append(indent_depth)
        return [Token.INDENT]
    elif indent_depth > current_depth + 1:
        expected_spaces = (current_depth + 1) * INDENT_SIZE
        raise TokenizerError(
            f"Invalid indentation: expected {expected_spaces} spaces",
            line=line_num,
            column=1
        )

    else:  # indent_depth < current_depth
        return _handle_dedentation(indent_depth, indent_stack)


def _has_more_content_after(line_num: int, lines: list[str]) -> bool:
    """Check if there are more non-empty lines after the current line."""
    if line_num >= len(lines):
        return False
    
    # Check if there are any non-empty lines remaining
    for i in range(line_num, len(lines)):
        if lines[i].strip():
            return True
    return False


def _finalize_all_indentation(indent_stack: list[int]) -> list[TokenType]:
    """Generate final DEDENT tokens to close all remaining indentation levels."""
    final_tokens: list[TokenType] = []
    while len(indent_stack) > 1:
        indent_stack.pop()
        final_tokens.append(Token.DEDENT)
    return final_tokens


def tokenize(input_str: str) -> list[TokenType]:
    """Tokenize input string into list of tokens with indentation handling.
    
    Args:
        input_str: The source code string to tokenize
        
    Returns:
        List of tokens representing the parsed input
        
    Raises:
        TokenizerError: For invalid syntax, indentation, or characters
    """
    if not input_str.strip():
        return []
    
    lines = input_str.split('\n')
    tokens: list[TokenType] = []
    indent_stack = [BASE_INDENT_LEVEL]  # Stack to track indentation levels
    
    for line_num, line in enumerate(lines, 1):
        if not line.strip():  # Skip empty lines
            continue
        
        # Process indentation
        leading_spaces, line_content = _extract_indentation_info(line)
        indent_depth = _validate_indentation_increment(leading_spaces, line_num)
        
        # Handle indentation changes
        indentation_tokens = _handle_indentation_change(indent_depth, indent_stack, line_num)
        tokens.extend(indentation_tokens)
        
        # Process line content
        line_tokens = _tokenize_line(line_content, line_num)
        tokens.extend(line_tokens)
        
        # Add statement separator if needed
        if _has_more_content_after(line_num, lines):
            tokens.append(Token.STATEMENT_SEPARATOR)
    
    # Clean up remaining indentation
    final_tokens = _finalize_all_indentation(indent_stack)
    tokens.extend(final_tokens)
    
    return tokens

def _tokenize_line(line_content: str, line_num: int) -> list[TokenType]:
    """Tokenize a single line of content."""
    assert line_content, "line_content should not be empty"
    
    # Check for comments first
    comment_pos = line_content.find('#')
    if comment_pos != -1:
        # Tokenize the part before the comment (if any)
        code_part = line_content[:comment_pos].rstrip()
        tokens: list[TokenType] = []
        if code_part:
            tokens = _tokenize_line_without_comments(code_part, line_num)
        
        # Add the comment token
        tokens.append(Token.COMMENT)
        return tokens
    
    # No comments, tokenize normally
    return _tokenize_line_without_comments(line_content, line_num)

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
            raise TokenizerError(
                "Invalid float: missing digits after decimal point",
                line=line_num,
                column=i+1
            )
        
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


def _peek(line_content: str, pos: int, expected: str) -> bool:
    """Check if the string at pos matches the expected multi-character sequence."""
    return (pos + len(expected) <= len(line_content) and 
            line_content[pos:pos + len(expected)] == expected)


def _is_negative_number_start(line_content: str, pos: int) -> bool:
    """Check if position starts a negative number (minus immediately followed by digit)."""
    return (line_content[pos] == '-' and 
            pos + 1 < len(line_content) and 
            line_content[pos + 1].isdigit())


def _tokenize_line_without_comments(line_content: str, line_num: int) -> list[TokenType]:
    """Tokenize a single line of content without comments."""
    assert line_content, "line_content should not be empty"
    
    tokens: list[TokenType] = []
    i = 0
    
    while i < len(line_content):
        char = line_content[i]
        
        match char:
            case ' ':
                i += 1
            
            case '=' if _peek(line_content, i, '=='):
                tokens.append(Token.EQUAL_EQUAL)
                i += 2
            
            case '!' if _peek(line_content, i, '!='):
                tokens.append(Token.NOT_EQUAL)
                i += 2
            
            case '<' if _peek(line_content, i, '<='):
                tokens.append(Token.LESS_THAN_OR_EQUAL)
                i += 2
            
            case '>' if _peek(line_content, i, '>='):
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
                raise TokenizerError("Unexpected character: '\\t'", line=line_num, column=i+1)
            
            case _:
                raise TokenizerError(f"Unexpected character: '{char}'", line=line_num, column=i+1)    
    return tokens