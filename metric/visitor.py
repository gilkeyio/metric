"""
Visitor pattern implementation for AST traversal.
Eliminates duplicated dispatch logic across type checker and evaluator.
"""

from abc import ABC, abstractmethod
from typing import Any


class ASTVisitor(ABC):
    """Abstract base class for AST visitors."""
    
    @abstractmethod
    def visit_let(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_set(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_list_assignment(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_print(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_if(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_while(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_comment(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_function_declaration(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_return(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_binary_op(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_unary_op(self, node) -> Any:
        pass
    
    
    @abstractmethod
    def visit_integer_literal(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_float_literal(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_boolean_literal(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_variable(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_function_call(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_list_literal(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_list_access(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_repeat_call(self, node) -> Any:
        pass
    
    @abstractmethod
    def visit_len_call(self, node) -> Any:
        pass