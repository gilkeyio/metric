from typing import Dict, Tuple, List
from .metric_ast import *
from .visitor import ASTVisitor


class TypeCheckError(Exception):
    pass


class TypeCheckVisitor(ASTVisitor):
    def __init__(self) -> None:
        self.symbol_table: Dict[str, Type | ListType] = {}
        self.function_table: Dict[str, Tuple[List[Type | ListType], Type | ListType]] = {}  # name -> (param_types, return_type)
        self.current_function_return_type: Type | ListType | None = None  # Track return type for current function
    
    def check_program(self, ast: AbstractSyntaxTree) -> None:
        """Type check an entire program."""
        for statement in ast:
            statement.accept(self)
    
    
    def visit_let(self, node: Let) -> None:
        """Type check a let statement."""
        # Check if variable is already declared
        if node.name in self.symbol_table:
            raise TypeCheckError(f"Variable '{node.name}' is already declared")
        
        # Check expression type matches declared type
        expr_type = node.expression.accept(self)
        if not self._types_equal(expr_type, node.type_annotation):
            declared_type_str = self._type_to_string(node.type_annotation)
            expr_type_str = self._type_to_string(expr_type)
            raise TypeCheckError(f"Type mismatch: cannot assign {expr_type_str} to variable '{node.name}' of type {declared_type_str}")
        
        # Add to symbol table
        self.symbol_table[node.name] = node.type_annotation
    
    def visit_set(self, node: Set) -> None:
        """Type check a set statement."""
        # Check if variable is declared
        if node.name not in self.symbol_table:
            raise TypeCheckError(f"Variable '{node.name}' is not declared")
        
        # Check expression type matches variable type
        expr_type = node.expression.accept(self)
        var_type = self.symbol_table[node.name]
        if not self._types_equal(expr_type, var_type):
            var_type_str = self._type_to_string(var_type)
            expr_type_str = self._type_to_string(expr_type)
            raise TypeCheckError(f"Type mismatch: cannot assign {expr_type_str} to variable '{node.name}' of type {var_type_str}")
    
    def visit_list_assignment(self, node: ListAssignment) -> None:
        """Type check a list assignment statement."""
        # Check if variable is declared and is a list
        if node.list_name not in self.symbol_table:
            raise TypeCheckError(f"Variable '{node.list_name}' is not declared")
        
        var_type = self.symbol_table[node.list_name]
        if not isinstance(var_type, ListType):
            var_type_str = self._type_to_string(var_type)
            raise TypeCheckError(f"Cannot index into non-list variable '{node.list_name}' of type {var_type_str}")
        
        # Check index is integer
        index_type = node.index.accept(self)
        if index_type != Type.INTEGER:
            index_type_str = self._type_to_string(index_type)
            raise TypeCheckError(f"List index must be integer, got {index_type_str}")
        
        # Check value type matches list element type
        value_type = node.value.accept(self)
        if not self._types_equal(value_type, var_type.element_type):
            list_elem_type_str = self._type_to_string(var_type.element_type)
            value_type_str = self._type_to_string(value_type)
            raise TypeCheckError(f"Type mismatch: cannot assign {value_type_str} to list element of type {list_elem_type_str}")
    
    def visit_print(self, node: Print) -> None:
        """Type check a print statement."""
        node.expression.accept(self)
    
    def visit_if(self, node: If) -> None:
        """Type check an if statement."""
        self._validate_boolean_condition(node.condition, "If")
        self._check_statement_body(node.body)
    
    def visit_while(self, node: While) -> None:
        """Type check a while statement."""
        self._validate_boolean_condition(node.condition, "While")
        self._check_statement_body(node.body)
    
    def visit_comment(self, node: Comment) -> None:
        """Type check a comment (no-op)."""
        pass
    
    def _validate_boolean_condition(self, condition: Expression, statement_type: str) -> None:
        """Validate that a condition expression is boolean."""
        cond_type = condition.accept(self)
        if cond_type != Type.BOOLEAN:
            raise TypeCheckError(f"{statement_type} condition must be boolean, got {cond_type.value.lower()}")
    
    def _check_statement_body(self, statements: List[Statement]) -> None:
        """Type check a list of statements."""
        for stmt in statements:
            stmt.accept(self)
    
    
    def visit_integer_literal(self, node: IntegerLiteral) -> Type:
        return Type.INTEGER
    
    def visit_boolean_literal(self, node: BooleanLiteral) -> Type:
        return Type.BOOLEAN
    
    def visit_float_literal(self, node: FloatLiteral) -> Type:
        return Type.FLOAT
    
    def visit_variable(self, node: Variable) -> Type | ListType:
        if node.name not in self.symbol_table:
            raise TypeCheckError(f"Variable '{node.name}' is not declared")
        return self.symbol_table[node.name]
    
    def visit_binary_op(self, node: BinaryExpression) -> Type:
        """Type check a binary expression and return its type."""
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)
        
        # Define operator categories and their type rules
        arithmetic_ops = {BinaryOperator.ADDITION, BinaryOperator.SUBTRACTION, 
                         BinaryOperator.MULTIPLICATION, BinaryOperator.DIVISION}
        modulus_ops = {BinaryOperator.MODULUS}  # Modulus requires integer operands
        comparison_ops = {BinaryOperator.LESS_THAN, BinaryOperator.GREATER_THAN,
                         BinaryOperator.LESS_THAN_OR_EQUAL, BinaryOperator.GREATER_THAN_OR_EQUAL}
        equality_ops = {BinaryOperator.EQUAL_EQUAL, BinaryOperator.NOT_EQUAL}
        logical_ops = {BinaryOperator.AND, BinaryOperator.OR}  # Logical operators require boolean operands
        
        if node.operator in arithmetic_ops:
            return self._check_arithmetic_operation(left_type, right_type, node.operator)
        elif node.operator in modulus_ops:
            self._validate_integer_operands(left_type, right_type, node.operator)
            return Type.INTEGER
        elif node.operator in comparison_ops:
            self._validate_numeric_operands(left_type, right_type, node.operator)
            return Type.BOOLEAN
        elif node.operator in equality_ops:
            self._validate_same_type_operands(left_type, right_type, node.operator)
            return Type.BOOLEAN
        elif node.operator in logical_ops:
            self._validate_boolean_operands(left_type, right_type, node.operator)
            return Type.BOOLEAN
        else:
            raise TypeCheckError(f"Unknown binary operator: {node.operator}")
    
    def visit_unary_op(self, node: UnaryExpression) -> Type:
        """Type check a unary expression and return its type."""
        operand_type = node.operand.accept(self)
        
        if node.operator == UnaryOperator.NOT:
            if operand_type != Type.BOOLEAN:
                raise TypeCheckError(f"Operator 'not' requires boolean operand, got {self._type_to_string(operand_type)}")
            return Type.BOOLEAN
        else:
            raise TypeCheckError(f"Unknown unary operator: {node.operator}")
    
    def _validate_integer_operands(self, left_type: Type, right_type: Type, operator: BinaryOperator) -> None:
        """Validate that both operands are integers."""
        if left_type != Type.INTEGER or right_type != Type.INTEGER:
            raise TypeCheckError(f"Operator {operator.value} requires integer operands")
    
    def _validate_same_type_operands(self, left_type: Type, right_type: Type, operator: BinaryOperator) -> None:
        """Validate that both operands have the same type."""
        if left_type != right_type:
            raise TypeCheckError(f"Operator {operator.value} requires operands of same type")
    
    def _validate_numeric_operands(self, left_type: Type, right_type: Type, operator: BinaryOperator) -> None:
        """Validate that both operands are numeric (integer or float)."""
        numeric_types = {Type.INTEGER, Type.FLOAT}
        if left_type not in numeric_types or right_type not in numeric_types:
            raise TypeCheckError(f"Operator {operator.value} requires numeric operands")
    
    def _validate_boolean_operands(self, left_type: Type, right_type: Type, operator: BinaryOperator) -> None:
        """Validate that both operands are booleans."""
        if left_type != Type.BOOLEAN or right_type != Type.BOOLEAN:
            raise TypeCheckError(f"Operator {operator.value} requires boolean operands")
    
    def _check_arithmetic_operation(self, left_type: Type, right_type: Type, operator: BinaryOperator) -> Type:
        """Check arithmetic operation and return result type with type promotion."""
        # Validate both operands are numeric
        self._validate_numeric_operands(left_type, right_type, operator)
        
        # Type promotion: if either operand is float, result is float
        if left_type == Type.FLOAT or right_type == Type.FLOAT:
            return Type.FLOAT
        else:
            return Type.INTEGER


    def visit_function_declaration(self, node: FunctionDeclaration) -> None:
        """Type check a function declaration."""
        # Check if function is already declared
        if node.name in self.function_table:
            raise TypeCheckError(f"Function '{node.name}' is already declared")
        
        # Extract parameter types
        param_types = [param.type_annotation for param in node.parameters]
        
        # Add function to function table
        self.function_table[node.name] = (param_types, node.return_type)
        
        # Create new scope for function parameters
        saved_symbol_table = self.symbol_table.copy()
        
        # Add parameters to symbol table
        for param in node.parameters:
            if param.name in self.symbol_table:
                raise TypeCheckError(f"Parameter '{param.name}' conflicts with existing variable")
            self.symbol_table[param.name] = param.type_annotation
        
        # Set current function return type for return statement validation
        saved_return_type = self.current_function_return_type
        self.current_function_return_type = node.return_type
        
        # Type check function body
        has_return = False
        for stmt in node.body:
            stmt.accept(self)
            if isinstance(stmt, Return):
                has_return = True
        
        # Ensure function has a return statement
        if not has_return:
            raise TypeCheckError(f"Function '{node.name}' must have a return statement")
        
        # Restore previous state
        self.symbol_table = saved_symbol_table
        self.current_function_return_type = saved_return_type
    
    def visit_return(self, node: Return) -> None:
        """Type check a return statement."""
        if self.current_function_return_type is None:
            raise TypeCheckError("Return statement must be inside a function")
        
        # Check expression type matches function return type
        expr_type = node.expression.accept(self)
        if not self._types_equal(expr_type, self.current_function_return_type):
            expected_type_str = self._type_to_string(self.current_function_return_type)
            got_type_str = self._type_to_string(expr_type)
            raise TypeCheckError(f"Return type mismatch: expected {expected_type_str}, got {got_type_str}")
    
    def visit_function_call(self, node: FunctionCall) -> Type | ListType:
        """Type check a function call and return its type."""
        # Check if function is declared
        if node.name not in self.function_table:
            raise TypeCheckError(f"Function '{node.name}' is not declared")
        
        param_types, return_type = self.function_table[node.name]
        
        # Check argument count
        if len(node.arguments) != len(param_types):
            raise TypeCheckError(f"Function '{node.name}' expects {len(param_types)} arguments, got {len(node.arguments)}")
        
        # Check argument types
        for i, (arg, expected_type) in enumerate(zip(node.arguments, param_types)):
            arg_type = arg.accept(self)
            if not self._types_equal(arg_type, expected_type):
                expected_type_str = self._type_to_string(expected_type)
                got_type_str = self._type_to_string(arg_type)
                raise TypeCheckError(f"Argument {i + 1} to function '{node.name}': expected {expected_type_str}, got {got_type_str}")
        
        return return_type
    
    def visit_list_literal(self, node: ListLiteral) -> ListType:
        """Type check a list literal and return its type."""
        if not node.elements:
            # Empty list - can't infer type, should be caught elsewhere
            raise TypeCheckError("Cannot infer type of empty list literal")
        
        # Check first element to determine list type
        first_type = node.elements[0].accept(self)
        
        # Verify all elements have the same type
        for i, element in enumerate(node.elements[1:], 1):
            elem_type = element.accept(self)
            if not self._types_equal(elem_type, first_type):
                first_type_str = self._type_to_string(first_type)
                elem_type_str = self._type_to_string(elem_type)
                raise TypeCheckError(f"List elements must be homogeneous: element 0 is {first_type_str}, element {i} is {elem_type_str}")
        
        # List must contain basic types, not other lists for now
        if isinstance(first_type, ListType):
            raise TypeCheckError("Nested lists are not supported")
        
        return ListType(first_type)
    
    def visit_list_access(self, node: ListAccess) -> Type:
        """Type check a list access and return the element type."""
        # Check that we're accessing a list
        list_type = node.list_expr.accept(self)
        if not isinstance(list_type, ListType):
            list_type_str = self._type_to_string(list_type)
            raise TypeCheckError(f"Cannot index into non-list expression of type {list_type_str}")
        
        # Check that index is integer
        index_type = node.index.accept(self)
        if index_type != Type.INTEGER:
            index_type_str = self._type_to_string(index_type)
            raise TypeCheckError(f"List index must be integer, got {index_type_str}")
        
        return list_type.element_type
    
    def visit_repeat_call(self, node: RepeatCall) -> ListType:
        """Type check a repeat call and return the list type."""
        # Check value type
        value_type = node.value.accept(self)
        if isinstance(value_type, ListType):
            raise TypeCheckError("Cannot repeat a list value")
        
        # Check count is integer
        count_type = node.count.accept(self)
        if count_type != Type.INTEGER:
            count_type_str = self._type_to_string(count_type)
            raise TypeCheckError(f"Repeat count must be integer, got {count_type_str}")
        
        return ListType(value_type)
    
    def visit_len_call(self, node: LenCall) -> Type:
        """Type check a len call and return integer type."""
        # Check that we're getting length of a list
        list_type = node.list_expr.accept(self)
        if not isinstance(list_type, ListType):
            list_type_str = self._type_to_string(list_type)
            raise TypeCheckError(f"Cannot get length of non-list expression of type {list_type_str}")
        
        return Type.INTEGER
    
    def _types_equal(self, type1: Type | ListType, type2: Type | ListType) -> bool:
        """Check if two types are equal."""
        if isinstance(type1, ListType) and isinstance(type2, ListType):
            return self._types_equal(type1.element_type, type2.element_type)
        elif isinstance(type1, Type) and isinstance(type2, Type):
            return type1 == type2
        else:
            return False
    
    def _type_to_string(self, type_obj: Type | ListType) -> str:
        """Convert a type to a string representation."""
        if isinstance(type_obj, ListType):
            elem_type_str = self._type_to_string(type_obj.element_type)
            return f"list of {elem_type_str}"
        else:
            return type_obj.value.lower()


class TypeChecker:
    """Compatibility wrapper for the visitor-based type checker."""
    def __init__(self) -> None:
        self.visitor = TypeCheckVisitor()
    
    def check_program(self, ast: AbstractSyntaxTree) -> None:
        self.visitor.check_program(ast)


def type_check(ast: AbstractSyntaxTree) -> None:
    """Type check an abstract syntax tree."""
    checker = TypeChecker()
    checker.check_program(ast)