from enum import Enum
from typing import Union, List

import pylox
from .ExprOrStmt import (Assign, Binary, Block, Call, Class, Expr, Expression,
                         ExprVisitor, Function, Get, Grouping, If, Literal,
                         Logical, Print, Return, Set, Stmt, StmtVisitor,
                         Variable, Var, While)
from .Interpreter import Interpreter
from .Token import Token


class ScopeDict(dict):
    """
    Sub-class of ``dict`` that enforces keys of type ``str`` and values
    of type ``bool``.
    """

    def __init__(self: "ScopeDict", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __setitem__(self: "ScopeDict", key: str, val: bool) -> None:
        if not isinstance(key, str):
            raise ValueError("{} is not of type {}!"
                             .format(key, str))
        elif not isinstance(val, bool):
            raise ValueError("{} is not of type {}!"
                             .format(val, bool))
        else:
            dict.__setitem__(self, key, val)


class FunctionType(Enum):
    NONE = 1
    FUNCTION = 2


class Resolver(ExprVisitor, StmtVisitor):

    _interpreter: Interpreter
    _scopes: List[ScopeDict]
    _current_function: FunctionType

    def __init__(self: "Resolver", interpreter: Interpreter) -> None:
        self._interpreter = interpreter
        self._scopes = []
        self._current_function = FunctionType.NONE

    def visit(self: "Resolver", expr_or_stmt: Union[Expr, Stmt]) -> None:

        if isinstance(expr_or_stmt, Block):

            self.begin_scope()
            self.resolve_multi(expr_or_stmt.exprs_or_stmts)
            self.end_scope()

        elif isinstance(expr_or_stmt, Class):

            self.declare(expr_or_stmt.name)
            self.define(expr_or_stmt.name)

        elif isinstance(expr_or_stmt, Expression):

            self.resolve_single(expr_or_stmt.expression)

        elif isinstance(expr_or_stmt, Function):

            self.declare(expr_or_stmt.name)
            self.define(expr_or_stmt.name)
            self.resolve_function(expr_or_stmt, FunctionType.FUNCTION)

        elif isinstance(expr_or_stmt, If):

            self.resolve_single(expr_or_stmt.condition)
            self.resolve_single(expr_or_stmt.then_branch)
            if expr_or_stmt.else_branch is not None:
                self.resolve_single(expr_or_stmt.else_branch)

        elif isinstance(expr_or_stmt, Print):

            self.resolve_single(expr_or_stmt.expression)

        elif isinstance(expr_or_stmt, Return):

            if self._current_function == FunctionType.NONE:
                pylox.Lox.Lox.token_error(expr_or_stmt.keyword,
                                          "Cannot return from top-level code.")

            if expr_or_stmt.value is not None:
                self.resolve_single(expr_or_stmt.value)

        elif isinstance(expr_or_stmt, Var):

            self.declare(expr_or_stmt.name)
            if expr_or_stmt.initializer is not None:
                self.resolve_single(expr_or_stmt.initializer)
            self.define(expr_or_stmt.name)

        elif isinstance(expr_or_stmt, While):

            self.resolve_single(expr_or_stmt.condition)
            self.resolve_single(expr_or_stmt.body)

        elif isinstance(expr_or_stmt, Variable):

            if (self._scopes and
                self._scopes[-1].get(expr_or_stmt.name.lexeme) == False):
                pylox.Lox.Lox.token_error(expr_or_stmt.name,
                                          "Cannot read local variable in its "
                                          "own initializer.")
            self.resolve_local(expr_or_stmt, expr_or_stmt.name)

        elif isinstance(expr_or_stmt, Assign):

            self.resolve_single(expr_or_stmt.value)
            self.resolve_local(expr_or_stmt, expr_or_stmt.name)

        elif isinstance(expr_or_stmt, Binary):

            self.resolve_single(expr_or_stmt.left)
            self.resolve_single(expr_or_stmt.right)

        elif isinstance(expr_or_stmt, Call):

            self.resolve_single(expr_or_stmt.callee)
            argument: Union[Expr, Stmt]
            for argument in expr_or_stmt.arguments:
                self.resolve_single(argument)

        elif isinstance(expr_or_stmt, Get):

            self.resolve_single(expr_or_stmt.object)

        elif isinstance(expr_or_stmt, Grouping):

            self.resolve_single(expr_or_stmt.expr_or_stmt)

        elif isinstance(expr_or_stmt, Literal):

            pass

        elif isinstance(expr_or_stmt, Logical):

            self.resolve_single(expr_or_stmt.left)
            self.resolve_single(expr_or_stmt.right)

        elif isinstance(expr_or_stmt, Logical):

            self.resolve_single(expr_or_stmt.right)

        elif isinstance(expr_or_stmt, Set):

            self.resolve_single(expr_or_stmt.value)
            self.resolve_single(expr_or_stmt.object)

        return None

    def resolve_single(self: "Resolver",
                       expr_or_stmt: Union[Expr, Stmt]) -> None:
        expr_or_stmt.accept(self)

    def resolve_multi(self: "Resolver",
                      expr_or_stmts: List[Union[Stmt, Expr]]) -> None:
        for expr_or_stmt in expr_or_stmts:
            self.resolve_single(expr_or_stmt)

    def resolve_function(self: "Resolver",
                         function: Function,
                         type_: FunctionType) -> None:

        enclosing_function: FunctionType = self._current_function
        self._current_function: FunctionType = type_
        self.begin_scope()
        param: Token
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve_multi(function.body)
        self.end_scope()
        self._current_function = enclosing_function

    def begin_scope(self: "Resolver") -> None:
        self._scopes.append(ScopeDict())
        return

    def end_scope(self: "Resolver") -> None:
        self._scopes.pop()
        return

    def declare(self: "Resolver", name: Token) -> None:
        if not self._scopes: return
        scope: ScopeDict = self._scopes[-1]
        if name.lexeme in scope:
            pylox.Lox.Lox.token_error(name,
                                      "Variable with this name already "
                                      "declared in this scope.")
        scope[name.lexeme] = False

    def define(self: "Resolver", name: Token) -> None:
        if not self._scopes: return
        scope: ScopeDict = self._scopes[-1]
        scope[name.lexeme] = True

    def resolve_local(self: "Resolver", expr: Expr, name: Token) -> None:
        max_scope_i: int = len(self._scopes) - 1
        i: int = int(max_scope_i)
        while i >= 0:
            if name.lexeme in self._scopes[i]:
                self._interpreter.resolve(expr, max_scope_i - i)
                return
            i -= 1
