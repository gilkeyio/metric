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
    if not line_content:
        return []
    
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

def tokenize_line_without_comments(line_content: str, line_num: int) -> list[TokenType]:
    """Tokenize a single line of content without comments."""
    if not line_content:
        return []
    
    tokens: list[TokenType] = []
    i = 0
    
    while i < len(line_content):
        char = line_content[i]
        
        if char == ' ':
            i += 1
            
        elif char in '+-*/%()=<>!,[]':
            # Handle operators (single and multi-character)
            if char == '=' and i + 1 < len(line_content) and line_content[i + 1] == '=':
                tokens.append(Token.EQUAL_EQUAL)
                i += 2
            elif char == '!' and i + 1 < len(line_content) and line_content[i + 1] == '=':
                tokens.append(Token.NOT_EQUAL)
                i += 2
            elif char == '<' and i + 1 < len(line_content) and line_content[i + 1] == '=':
                tokens.append(Token.LESS_THAN_OR_EQUAL)
                i += 2
            elif char == '>' and i + 1 < len(line_content) and line_content[i + 1] == '=':
                tokens.append(Token.GREATER_THAN_OR_EQUAL)
                i += 2
            elif char == '-' and i + 1 < len(line_content) and line_content[i + 1].isdigit():
                # Handle negative numbers (minus immediately followed by digit)
                start = i
                i += 1  # skip the minus sign
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
                    tokens.append(FloatToken(float(number_str)))
                else:
                    number_str = line_content[start:i]
                    tokens.append(IntegerToken(int(number_str)))
            else:
                # Handle single character operators
                if char == ',':
                    tokens.append(Token.COMMA)
                    i += 1
                else:
                    token_map = {
                        '+': Token.PLUS,
                        '-': Token.MINUS,
                        '*': Token.MULTIPLY,
                        '/': Token.DIVIDE,
                        '%': Token.MODULUS,
                        '(': Token.LEFT_PARENTHESIS,
                        ')': Token.RIGHT_PARENTHESIS,
                        '=': Token.EQUALS,
                        '<': Token.LESS_THAN,
                        '>': Token.GREATER_THAN,
                        '[': Token.LEFT_BRACKET,
                        ']': Token.RIGHT_BRACKET
                    }
                    if char in token_map:
                        tokens.append(token_map[char])
                        i += 1
                    else:
                        raise TokenizerError(f"Unexpected character: {char} at line {line_num}")
            
        elif char.isdigit():
            # Handle numbers (integers and floats)
            start = i
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
                
                tokens.append(FloatToken(float(number_str)))
            else:
                number_str = line_content[start:i]
                
                tokens.append(IntegerToken(int(number_str)))
            
        elif char.isalpha():
            # Handle identifiers and keywords
            start = i
            while i < len(line_content) and line_content[i].isalpha():
                i += 1
            identifier = line_content[start:i]
            
            # Convert to appropriate token
            if identifier == "let":
                tokens.append(Token.LET)
            elif identifier == "print":
                tokens.append(Token.PRINT)
            elif identifier == "true":
                tokens.append(Token.TRUE)
            elif identifier == "false":
                tokens.append(Token.FALSE)
            elif identifier == "if":
                tokens.append(Token.IF)
            elif identifier == "while":
                tokens.append(Token.WHILE)
            elif identifier == "set":
                tokens.append(Token.SET)
            elif identifier == "integer":
                tokens.append(Token.INTEGER_TYPE)
            elif identifier == "boolean":
                tokens.append(Token.BOOLEAN_TYPE)
            elif identifier == "float":
                tokens.append(Token.FLOAT_TYPE)
            elif identifier == "def":
                tokens.append(Token.DEF)
            elif identifier == "returns":
                tokens.append(Token.RETURNS)
            elif identifier == "return":
                tokens.append(Token.RETURN)
            elif identifier == "list":
                tokens.append(Token.LIST)
            elif identifier == "of":
                tokens.append(Token.OF)
            elif identifier == "repeat":
                tokens.append(Token.REPEAT)
            elif identifier == "len":
                tokens.append(Token.LEN)
            elif identifier == "and":
                tokens.append(Token.AND)
            elif identifier == "or":
                tokens.append(Token.OR)
            elif identifier == "not":
                tokens.append(Token.NOT)
            else:
                tokens.append(IdentifierToken(identifier))
            
        elif char == '\t':
            raise TokenizerError(f"Unexpected character: \\t at line {line_num}")
            
        else:
            raise TokenizerError(f"Unexpected character: {char} at line {line_num}")
    
    return tokens