"""Metric evaluator with deterministic operation counting.

Changes vs. previous version
----------------------------
* `Environment` now tracks a `_cost` counter and exposes `increment_cost()` / `cost()`.
* Every semantic operation (variable read/write, arithmetic, logic, list ops, function call, etc.) increments the counter by **1**.
* `execute()` now returns a tuple `(results: List[RuntimeValue], cost: int)` so callers can inspect the total operation count.

This keeps the language semantics intact while giving you a simple, portable cost model suitable for algorithmic comparison.
"""

from typing import Dict, List, Optional, Tuple, Union
from .metric_ast import *  # noqa: F403, F401 – import all AST node classes


class EvaluationError(Exception):
    """Run‑time error reported to the user program."""


RuntimeValue = Union[int, bool, float, List[Union[int, bool, float]]]


class Environment:
    """Persistent environment mapping names ⇒ runtime values & functions.

    Immutability for the *bindings* is preserved (each mutation returns a fresh
    `Environment`), but a shared *cost* counter is held by reference so that
    every copy sees the same running tally.
    """

    def __init__(self, cost_ref: Optional[List[int]] = None):
        self._env: Dict[str, RuntimeValue] = {}
        self._functions: Dict[str, FunctionDeclaration] = {}
        # use a one‑element list so that copies share the same counter object
        self._cost_ref: List[int] = cost_ref if cost_ref is not None else [0]

    # ---------------------------------------------------------------------
    # cost utilities
    # ---------------------------------------------------------------------
    def increment_cost(self, amount: int = 1) -> None:
        self._cost_ref[0] += amount

    def cost(self) -> int:
        return self._cost_ref[0]

    # ---------------------------------------------------------------------
    # binding manipulation – each returns a *new* Environment that shares the
    # same cost counter.
    # ---------------------------------------------------------------------
    def _clone(self) -> "Environment":
        new_env = Environment(self._cost_ref)
        new_env._env = self._env.copy()
        new_env._functions = self._functions.copy()
        return new_env

    def add(self, name: str, value: RuntimeValue) -> "Environment":
        new_env = self._clone()
        new_env._env[name] = value
        return new_env

    def set(self, name: str, value: RuntimeValue) -> "Environment":
        if name not in self._env:
            raise KeyError(f"Variable not found: {name}")
        new_env = self._clone()
        new_env._env[name] = value
        return new_env

    def set_list_element(self, name: str, index: int, value: RuntimeValue) -> "Environment":
        if name not in self._env:
            raise KeyError(f"Variable not found: {name}")
        current_value = self._env[name]
        if not isinstance(current_value, list):
            raise EvaluationError(f"Variable '{name}' is not a list")
        if index < 0 or index >= len(current_value):
            raise EvaluationError(
                f"List index {index} out of bounds (list length: {len(current_value)})")
        new_list = current_value.copy()
        new_list[index] = value
        new_env = self._clone()
        new_env._env[name] = new_list
        return new_env

    # ------------------------------------------------------------------
    # function handling
    # ------------------------------------------------------------------
    def add_function(self, name: str, func_decl: FunctionDeclaration) -> "Environment":
        new_env = self._clone()
        new_env._functions[name] = func_decl
        return new_env

    def get_function(self, name: str) -> FunctionDeclaration:
        if name not in self._functions:
            raise KeyError(f"Function not found: {name}")
        return self._functions[name]

    def has_function(self, name: str) -> bool:
        return name in self._functions

    # ------------------------------------------------------------------
    # value lookup helpers
    # ------------------------------------------------------------------
    def find(self, name: str) -> RuntimeValue:
        if name not in self._env:
            raise KeyError(f"Variable not found: {name}")
        return self._env[name]

    def mem(self, name: str) -> bool:
        return name in self._env

    @classmethod
    def empty(cls) -> "Environment":
        return cls()


# ---------------------------------------------------------------------------
# Expression evaluation with cost tracking
# ---------------------------------------------------------------------------

def evaluate_expression(env: Environment, expr: Expression) -> RuntimeValue:  # noqa: C901 – long but straightforward
    def eval_expr(e: Expression) -> RuntimeValue:  # local helper so we can recurse
        # literals – no cost for just reading a constant
        if isinstance(e, IntegerLiteral):
            return e.value
        if isinstance(e, BooleanLiteral):
            return e.value
        if isinstance(e, FloatLiteral):
            return e.value

        # variable access
        if isinstance(e, Variable):
            env.increment_cost()
            try:
                return env.find(e.name)
            except KeyError:
                raise EvaluationError(f"Undefined variable: {e.name}")

        # unary op – only NOT exists so far
        if isinstance(e, UnaryExpression):
            operand_val = eval_expr(e.operand)
            env.increment_cost()
            if e.operator == UnaryOperator.NOT:  # noqa: F405 – imported from metric_ast
                return not operand_val
            raise EvaluationError(f"Unknown unary operator: {e.operator}")

        # binary op
        if isinstance(e, BinaryExpression):
            left = eval_expr(e.left)
            # short‑circuit for AND / OR: only eval right if needed
            if e.operator == BinaryOperator.AND:  # noqa: F405
                if not left:
                    env.increment_cost()
                    return False
                right = eval_expr(e.right)
                env.increment_cost()
                return left and right
            if e.operator == BinaryOperator.OR:  # noqa: F405
                if left:
                    env.increment_cost()
                    return True
                right = eval_expr(e.right)
                env.increment_cost()
                return left or right

            # normal case: evaluate both sides unconditionally
            right = eval_expr(e.right)
            env.increment_cost()
            op = e.operator
            if op == BinaryOperator.ADDITION:
                return left + right
            if op == BinaryOperator.SUBTRACTION:
                return left - right
            if op == BinaryOperator.MULTIPLICATION:
                return left * right
            if op == BinaryOperator.DIVISION:
                if right == 0:
                    raise EvaluationError("Division by zero")
                return left / right if isinstance(left, float) or isinstance(right, float) else left // right
            if op == BinaryOperator.MODULUS:
                if right == 0:
                    raise EvaluationError("Modulus by zero")
                return left % right
            if op == BinaryOperator.LESS_THAN:
                return left < right
            if op == BinaryOperator.GREATER_THAN:
                return left > right
            if op == BinaryOperator.LESS_THAN_OR_EQUAL:
                return left <= right
            if op == BinaryOperator.GREATER_THAN_OR_EQUAL:
                return left >= right
            if op == BinaryOperator.EQUAL_EQUAL:
                return left == right
            if op == BinaryOperator.NOT_EQUAL:
                return left != right
            raise EvaluationError(f"Unknown binary operator: {op}")

        # function call
        if isinstance(e, FunctionCall):
            return evaluate_function_call(env, e)

        # list literal – treat construction as 1 cost (plus cost of each element eval inside recursion)
        if isinstance(e, ListLiteral):
            env.increment_cost()
            return [eval_expr(el) for el in e.elements]

        # list access
        if isinstance(e, ListAccess):
            list_val = eval_expr(e.list_expr)
            idx_val = eval_expr(e.index)
            if not isinstance(list_val, list):
                raise EvaluationError("Cannot index into non-list value")
            if not isinstance(idx_val, int):
                raise EvaluationError("List index must be integer")
            if idx_val < 0 or idx_val >= len(list_val):
                raise EvaluationError(
                    f"List index {idx_val} out of bounds (length {len(list_val)})")
            env.increment_cost()
            return list_val[idx_val]

        # repeat(value, n)
        if isinstance(e, RepeatCall):
            val = eval_expr(e.value)
            count = eval_expr(e.count)
            if not isinstance(count, int):
                raise EvaluationError("Repeat count must be integer")
            if count < 0:
                raise EvaluationError("Repeat count cannot be negative")
            env.increment_cost()
            return [val] * count

        # len(list)
        if isinstance(e, LenCall):
            list_val = eval_expr(e.list_expr)
            if not isinstance(list_val, list):
                raise EvaluationError("Cannot get length of non-list value")
            env.increment_cost()
            return len(list_val)

        raise EvaluationError(f"Unknown expression type: {type(e)}")

    return eval_expr(expr)


# ---------------------------------------------------------------------------
# Function call handling (with cost)
# ---------------------------------------------------------------------------

class ReturnException(Exception):
    def __init__(self, value: RuntimeValue):
        self.value = value


def evaluate_function_call(env: Environment, call: FunctionCall) -> RuntimeValue:  # noqa: C901
    if not env.has_function(call.name):
        raise EvaluationError(f"Undefined function: {call.name}")
    func_decl = env.get_function(call.name)

    # evaluate arguments first (their cost is already counted via evaluate_expression)
    arg_vals = [evaluate_expression(env, arg) for arg in call.arguments]

    # count the *call* itself
    env.increment_cost()

    # create function-local environment (shares cost counter) and bind params
    func_env = Environment(env._cost_ref)
    func_env._functions = env._functions  # share function table
    for param, arg_val in zip(func_decl.parameters, arg_vals):
        func_env = func_env.add(param.name, arg_val)

    # execute body
    try:
        for stmt in func_decl.body:
            func_env, _ = execute_statement(func_env, stmt)
        raise EvaluationError(f"Function '{call.name}' did not return a value")
    except ReturnException as ret:
        return ret.value


# ---------------------------------------------------------------------------
# Statement execution (cost tracked where appropriate)
# ---------------------------------------------------------------------------

def execute_statement(env: Environment, stmt: Statement) -> Tuple[Environment, Optional[RuntimeValue]]:  # noqa: C901
    # let binding
    if isinstance(stmt, Let):
        if env.mem(stmt.name):
            raise EvaluationError(f"Variable already bound: {stmt.name}")
        value = evaluate_expression(env, stmt.expression)
        env = env.add(stmt.name, value)
        env.increment_cost()  # write cost
        return env, None

    # print
    if isinstance(stmt, Print):
        value = evaluate_expression(env, stmt.expression)
        env.increment_cost()  # I/O cost (optional; remove if undesired)
        if isinstance(value, bool):
            print("true" if value else "false")
        elif isinstance(value, list):
            list_str = "[" + ", ".join(
                str(el if not isinstance(el, bool) else ("true" if el else "false")) for el in value
            ) + "]"
            print(list_str)
        else:
            print(value)
        return env, value

    # set variable
    if isinstance(stmt, Set):
        if not env.mem(stmt.name):
            raise EvaluationError(f"Cannot set undefined variable: {stmt.name}")
        value = evaluate_expression(env, stmt.expression)
        env = env.set(stmt.name, value)
        env.increment_cost()
        return env, None

    # list[index] = value
    if isinstance(stmt, ListAssignment):
        if not env.mem(stmt.list_name):
            raise EvaluationError(f"Cannot set undefined variable: {stmt.list_name}")
        idx_val = evaluate_expression(env, stmt.index)
        if not isinstance(idx_val, int):
            raise EvaluationError("List index must be integer")
        elem_val = evaluate_expression(env, stmt.value)
        env = env.set_list_element(stmt.list_name, idx_val, elem_val)
        env.increment_cost()
        return env, None

    # if
    if isinstance(stmt, If):
        cond = evaluate_expression(env, stmt.condition)
        if not isinstance(cond, bool):
            raise EvaluationError("If condition must be boolean")
        env.increment_cost()  # condition test
        if cond:
            cur = env
            res: List[RuntimeValue] = []
            for body_stmt in stmt.body:
                cur, r = execute_statement(cur, body_stmt)
                if isinstance(r, list):
                    res.extend(r)
                elif r is not None:
                    res.append(r)
            return cur, res if res else None
        return env, None

    # while
    if isinstance(stmt, While):
        cur = env
        res: List[RuntimeValue] = []
        while True:
            cond_val = evaluate_expression(cur, stmt.condition)
            if not isinstance(cond_val, bool):
                raise EvaluationError("While condition must be boolean")
            cur.increment_cost()  # condition test each iteration
            if not cond_val:
                break
            for body_stmt in stmt.body:
                cur, r = execute_statement(cur, body_stmt)
                if isinstance(r, list):
                    res.extend(r)
                elif r is not None:
                    res.append(r)
        return cur, res if res else None

    # comment – no cost
    if isinstance(stmt, Comment):
        return env, None

    # function declaration – no cost (compile‑time)
    if isinstance(stmt, FunctionDeclaration):
        if env.has_function(stmt.name):
            raise EvaluationError(f"Function already declared: {stmt.name}")
        env = env.add_function(stmt.name, stmt)
        return env, None

    # return
    if isinstance(stmt, Return):
        val = evaluate_expression(env, stmt.expression)
        raise ReturnException(val)

    raise EvaluationError(f"Unknown statement type: {type(stmt)}")


# ---------------------------------------------------------------------------
# Program entry point
# ---------------------------------------------------------------------------

def execute(ast: AbstractSyntaxTree) -> Tuple[List[RuntimeValue], int]:
    """Execute a whole programme and return (print_results, total_cost)."""
    env = Environment.empty()
    results: List[RuntimeValue] = []

    def collect(stmt_res: Optional[RuntimeValue | List[RuntimeValue]]):
        if isinstance(stmt_res, list):
            results.extend(stmt_res)
        elif stmt_res is not None:
            results.append(stmt_res)

    for statement in ast:
        env, r = execute_statement(env, statement)
        collect(r)

    return results, env.cost()
