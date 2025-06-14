"""
Visitor pattern implementation for AST traversal.
Eliminates duplicated dispatch logic across type checker and evaluator.
"""
from __future__ import annotations
from abc import ABC, abstractmethod

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .metric_ast import (
        Let, Set, ListAssignment, Print, If, While, Comment,
        FunctionDeclaration, Return, BinaryExpression, UnaryExpression,
        IntegerLiteral, FloatLiteral, BooleanLiteral, Variable,
        FunctionCall, ListLiteral, ListAccess, RepeatCall, LenCall
    )


class ASTVisitor(ABC):
    """Abstract base class for AST visitors."""
    
    @abstractmethod
    def visit_let(self, node: Let) -> Any:
        pass
    
    @abstractmethod
    def visit_set(self, node: Set) -> Any:
        pass
    
    @abstractmethod
    def visit_list_assignment(self, node: ListAssignment) -> Any:
        pass
    
    @abstractmethod
    def visit_print(self, node: Print) -> Any:
        pass
    
    @abstractmethod
    def visit_if(self, node: If) -> Any:
        pass
    
    @abstractmethod
    def visit_while(self, node: While) -> Any:
        pass
    
    @abstractmethod
    def visit_comment(self, node: Comment) -> Any:
        pass
    
    @abstractmethod
    def visit_function_declaration(self, node: FunctionDeclaration) -> Any:
        pass
    
    @abstractmethod
    def visit_return(self, node: Return) -> Any:
        pass
    
    @abstractmethod
    def visit_binary_op(self, node: BinaryExpression) -> Any:
        pass
    
    @abstractmethod
    def visit_unary_op(self, node: UnaryExpression) -> Any:
        pass
    
    
    @abstractmethod
    def visit_integer_literal(self, node: IntegerLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_float_literal(self, node: FloatLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_boolean_literal(self, node: BooleanLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_variable(self, node: Variable) -> Any:
        pass
    
    @abstractmethod
    def visit_function_call(self, node: FunctionCall) -> Any:
        pass
    
    @abstractmethod
    def visit_list_literal(self, node: ListLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_list_access(self, node: ListAccess) -> Any:
        pass
    
    @abstractmethod
    def visit_repeat_call(self, node: RepeatCall) -> Any:
        pass
    
    @abstractmethod
    def visit_len_call(self, node: LenCall) -> Any:
        pass