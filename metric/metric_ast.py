from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:
    from .visitor import ASTVisitor


class Type(Enum):
    INTEGER = "Integer"
    BOOLEAN = "Boolean"
    FLOAT = "Float"


@dataclass(frozen=True)
class ListType:
    element_type: Type


class BinaryOperator(Enum):
    ADDITION = "Addition"
    SUBTRACTION = "Subtraction"
    MULTIPLICATION = "Multiplication"
    DIVISION = "Division"
    MODULUS = "Modulus"
    LESS_THAN = "LessThan"
    GREATER_THAN = "GreaterThan"
    LESS_THAN_OR_EQUAL = "LessThanOrEqual"
    GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
    EQUAL_EQUAL = "EqualEqual"
    NOT_EQUAL = "NotEqual"
    AND = "And"
    OR = "Or"


class UnaryOperator(Enum):
    NOT = "Not"


@dataclass(frozen=True)
class IntegerLiteral:
    value: int
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_integer_literal(self)


@dataclass(frozen=True)
class Variable:
    name: str
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_variable(self)


@dataclass(frozen=True)
class BooleanLiteral:
    value: bool
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_boolean_literal(self)


@dataclass(frozen=True)
class FloatLiteral:
    value: float
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_float_literal(self)


@dataclass(frozen=True)
class BinaryExpression:
    left: Expression
    operator: BinaryOperator
    right: Expression
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_binary_op(self)


@dataclass(frozen=True)
class UnaryExpression:
    operator: UnaryOperator
    operand: Expression
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_unary_op(self)


@dataclass(frozen=True)
class FunctionCall:
    name: str
    arguments: list[Expression]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_function_call(self)


@dataclass(frozen=True)
class ListLiteral:
    elements: list[Expression]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_list_literal(self)


@dataclass(frozen=True)
class ListAccess:
    list_expr: Expression
    index: Expression
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_list_access(self)


@dataclass(frozen=True)
class RepeatCall:
    value: Expression
    count: Expression
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_repeat_call(self)


@dataclass(frozen=True)
class LenCall:
    list_expr: Expression
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_len_call(self)


Expression = IntegerLiteral | Variable | BooleanLiteral | FloatLiteral | BinaryExpression | UnaryExpression | FunctionCall | ListLiteral | ListAccess | RepeatCall | LenCall


@dataclass(frozen=True)
class Let:
    name: str
    type_annotation: Type | ListType
    expression: Expression
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_let(self)


@dataclass(frozen=True)
class Print:
    expression: Expression
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_print(self)


@dataclass(frozen=True)
class If:
    condition: Expression
    body: list[Statement]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_if(self)


@dataclass(frozen=True)
class While:
    condition: Expression
    body: list[Statement]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_while(self)


@dataclass(frozen=True)
class Set:
    name: str
    expression: Expression
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_set(self)


@dataclass(frozen=True)
class ListAssignment:
    list_name: str
    index: Expression
    value: Expression
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_list_assignment(self)


@dataclass(frozen=True)
class Comment:
    pass
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_comment(self)


@dataclass(frozen=True)
class Parameter:
    name: str
    type_annotation: Type | ListType


@dataclass(frozen=True)
class FunctionDeclaration:
    name: str
    parameters: list[Parameter]
    return_type: Type | ListType
    body: list[Statement]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_function_declaration(self)


@dataclass(frozen=True)
class Return:
    expression: Expression
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_return(self)


Statement = Let | Print | If | While | Set | ListAssignment | Comment | FunctionDeclaration | Return

AbstractSyntaxTree = Sequence[Statement]