import sys

class CompilerError(Exception):
    """Base class for compiler errors with position info and automatic labeling."""

    def __init__(self, message: str, line: int, column: int):
        self.line = line
        self.column = column
        error_type = self.__class__.__name__.replace("Error", " Error")
        self.formatted = f"[Line {line}, Column {column}] {error_type} | {message}"
        super().__init__(self.formatted)

    def __str__(self) -> str:
        return self.formatted

class TokenizerError(CompilerError): pass
class StyleError(CompilerError): pass
class ParseError(CompilerError): pass
class TypeCheckError(CompilerError): pass
class EvaluationError(CompilerError): pass
    
def handle_compiler_error(error: CompilerError) -> None:
    """Print a compiler error in red and exit."""
    print(f"\033[31m{error}\033[0m", file=sys.stderr)
    sys.exit(1)