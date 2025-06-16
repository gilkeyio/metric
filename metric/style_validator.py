"""
Style validation for the Metric programming language.

This module provides comprehensive style and whitespace validation that runs 
post-tokenization, using both the original source code and tokenized output
to enforce strict formatting rules.
"""

from metric.errors import StyleError
from .tokenizer import Token, IntegerToken, FloatToken, IdentifierToken



def validate_style(source_code: str, tokens: list[Token | IntegerToken | FloatToken | IdentifierToken]) -> None:
    """
    Validate the style and whitespace of Metric source code.
    
    This function runs post-tokenization and uses both the original source
    and the tokenized output to enforce all whitespace and style rules.
    
    Args:
        source_code: The original source code string
        tokens: The tokenized output from the tokenizer
        
    Raises:
        StyleError: If any style validation rules are violated
    """
    # Basic structural validation
    _validate_not_empty(source_code)
    _validate_line_endings(source_code)
    _validate_leading_trailing_newlines(source_code)
    _validate_newlines(source_code)
    
    # Line-level whitespace validation
    _validate_line_whitespace(source_code)
    
    # Statement-level validation
    _validate_multiple_statements_per_line(source_code)
    
    # Token-level validation using both source 
    _validate_token_spacing(source_code)
    _validate_comment_spacing(source_code)
    _validate_comma_spacing(source_code)


def _validate_not_empty(text: str) -> None:
    """Ensure program is not empty"""
    if not text.strip():
        raise StyleError("Program must not be empty", line=1, column=1)


def _validate_line_endings(text: str) -> None:
    """Ensure text contains no carriage return characters."""
    for position, character in enumerate(text):
        if character != '\r':
            continue

        # Compute the line number (1-based)
        text_before = text[:position]
        line_number = text_before.count('\n') + 1

        # Compute the column number (1-based)
        last_newline_index = text_before.rfind('\n')
        if last_newline_index != -1:
            column_number = position - last_newline_index
        else:
            column_number = position + 1

        raise StyleError(
            f"Carriage return newlines not allowed; use \\n only",
            line=line_number,
            column=column_number
        )



def _validate_leading_trailing_newlines(input_str: str) -> None:
    """Check for leading or trailing newlines which are not allowed."""
    if not input_str:
        return

    # Leading newline at line 1, column 1
    if input_str[0] == '\n':
        raise StyleError("Leading newlines not allowed", line=1, column=1)

    # Trailing newline: report its line (the empty line after the last '\n') at column 1
    if input_str.endswith('\n'):
        # the trailing '\n' starts a new empty line
        line_no = input_str.count('\n') + 1
        raise StyleError("Trailing newlines not allowed", line=line_no, column=1)



def _validate_newlines(input_str: str) -> None:
    """Check for too many consecutive newlines (max 2 allowed)."""
    if not input_str:
        return
    
    # Count consecutive newlines by looking at the actual newline characters
    consecutive_newlines = 0
    i = 0
    line_num = 1
    
    while i < len(input_str):
        if input_str[i] == '\n':
            consecutive_newlines += 1
            if consecutive_newlines > 2:
                # Report error at the current line number (where the 3rd newline is)
                raise StyleError(f"Too many consecutive newlines: maximum 2 allowed", line=line_num, column=1)
            line_num += 1

        else:
            consecutive_newlines = 0
        i += 1


def _validate_line_whitespace(input_str: str) -> None:
    """Enforce two rules:
       1. No trailing spaces.
       2. Indentation must be multiples of 4 spaces (if any spaces are used).
    """
    for line_num, line in enumerate(input_str.split('\n'), 1):

        # ---------- rule 1: trailing spaces ---------------------------------
        if line and line[-1] == ' ':                    # at least one trailing space
            column = len(line.rstrip()) + 1            # first trailing space (1-indexed)
            raise StyleError(
                "Trailing spaces not allowed",
                line=line_num,
                column=column
            )

        # ---------- rule 2: indentation multiple of 4 -----------------------
        leading_spaces = len(line) - len(line.lstrip(' '))
        if leading_spaces and leading_spaces % 4 != 0:
            # first “bad” space is the one after the last full 4-space group
            first_bad_col = (leading_spaces // 4) * 4 + 1  # 1-indexed
            raise StyleError(
                "Indentation must be in multiples of 4 spaces",
                line=line_num,
                column=first_bad_col
            )



def _validate_multiple_statements_per_line(input_str: str) -> None:
    """Raise an error if a line contains more than one statement."""
    statement_keywords = {"let", "print", "if", "while", "set", "def", "return"}

    for line_num, line in enumerate(input_str.split('\n'), 1):
        # Strip comments from the line
        code_part = line.split('#', 1)[0]
        trimmed = code_part.strip()
        if not trimmed:
            continue

        words = trimmed.split()
        keyword_count = 0
        current_pos = 0
        for word in words:
            # Find the position of this word in the line starting from current_pos
            word_pos = line.find(word, current_pos)
            if word in statement_keywords:
                keyword_count += 1
                if keyword_count == 2:
                    raise StyleError(
                        f"Statements must be separated by a newline"
                        , line=line_num, column=word_pos + 1
                    )
            # Update current_pos to search for next word after this one
            current_pos = word_pos + len(word)


def _validate_token_spacing(source_code: str) -> None:
    """
    Validate token-level spacing rules using both source and tokens.
    
    This function analyzes the relationship between the original source
    and the tokenized output to ensure proper spacing around operators,
    identifiers, and other tokens.
    """
    lines = source_code.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip empty lines and comment-only lines
        code_part = line.split('#', 1)[0]
        if not code_part.strip():
            continue
            
        # Check for multiple spaces between tokens
        _check_multiple_spaces_in_line(code_part, line_num)
        
        # Check for proper spacing around operators
        _check_operator_spacing_in_line(code_part, line_num)
        
        # Check for proper spacing after identifiers and numbers
        _check_identifier_number_spacing_in_line(code_part, line_num)


def _check_multiple_spaces_in_line(line: str, line_num: int) -> None:
    """
    Disallow more than one consecutive space between tokens.
    Leading indentation is ignored (that's handled elsewhere).
    """
    # Skip indentation
    i = 0
    while i < len(line) and line[i] == ' ':
        i += 1

    # Scan the remainder of the line
    while i < len(line) - 1:
        if line[i] == ' ' and line[i + 1] == ' ':
            # First space of the run is the violation
            raise StyleError(
                "Multiple spaces not allowed between tokens",
                line=line_num,
                column=i + 1   
            )
        i += 1



def _check_operator_spacing_in_line(line: str, line_num: int) -> None:
    """Check for proper spacing before operators."""
    operators = ['+', '-', '*', '/', '%', '=', '<', '>', '!']
    
    for i, char in enumerate(line):
        if char in operators and i > 0:
            # Check if previous character is alphanumeric (identifier or number)
            if line[i - 1].isalnum():
                raise StyleError(f"Expected space before operator '{char}'", line=line_num, column=i+1)


def _check_identifier_number_spacing_in_line(line: str, line_num: int) -> None:
    """Check for proper spacing after identifiers and numbers."""
    i = 0
    while i < len(line):
        if line[i].isalpha():
            # Found start of identifier
            start = i
            while i < len(line) and line[i].isalpha():
                i += 1
            
            # Check if identifier is followed immediately by alphanumeric
            if i < len(line) and line[i].isalnum():
                identifier = line[start:i]
                raise StyleError(f"Expected space after identifier '{identifier}'", line=line_num, column=i+1)
                
        elif line[i].isdigit():
            # Found start of number
            start = i
            while i < len(line) and (line[i].isdigit() or line[i] == '.'):
                i += 1
            
            # Check if number is followed immediately by alphanumeric
            if i < len(line) and line[i].isalnum():
                number = line[start:i]
                raise StyleError(f"Expected space after number '{number}'", line=line_num, column=i+1)
        else:
            i += 1


def _validate_comment_spacing(input_str: str) -> None:
    """Validate spacing around comments."""
    lines = input_str.split('\n')

    for line_num, line in enumerate(lines, 1):
        comment_pos = line.find('#')
        if comment_pos <= 0:
            continue

        # Must have exactly one space before the comment
        if line[comment_pos - 1] != ' ' or (comment_pos > 1 and line[comment_pos - 2] == ' '):
            raise StyleError(f"Comments must be separated from code by exactly one space", line=line_num, column=comment_pos+1)



def _validate_comma_spacing(input_str: str) -> None:
    """Validate spacing around commas."""
    lines = input_str.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Strip comments to avoid checking commas in comments
        code_part = line.split('#', 1)[0]
        
        for i, char in enumerate(code_part):
            if char == ',':
                # Check for space before comma (not allowed)
                if i > 0 and code_part[i - 1] == ' ':
                    raise StyleError(f"Space before comma not allowed", line=line_num, column=i+1)
                
                # Check for space after comma (required)
                if i + 1 >= len(code_part):
                    raise StyleError(f"Space required after comma", line=line_num, column=i+1)
                elif code_part[i + 1] != ' ':
                    raise StyleError(f"Space required after comma", line=line_num, column=i+1)


