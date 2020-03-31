import time
from typing import Any, Dict, List, Optional, Union

import pylox
from .Environment import Environment
from .ExprOrStmt import (Assign, Block, Binary, Call, Class, Expr,
                         ExprVisitor, Expression, Function, If, Literal,
                         Logical, Grouping, Print, Return, Stmt, StmtVisitor,
                         Unary, Variable, Var, While)
from .LoxClass import LoxClass
from .PyloxRuntimeError import PyloxRuntimeError
from .Return import Return as ReturnException
from .Token import Token
from .TokenType import TokenType


class Interpreter(ExprVisitor, StmtVisitor):

    _globals: Environment = Environment()
    _environment: Environment = _globals
    _locals: Dict[Expr, int] = {}

    def __init__(self: "Interpreter") -> None:
        self._globals.define("clock", Clock)

    def interpret(self: "Interpreter",
                  exprs_or_stmts: List[Union[Expr, Stmt]]) -> None:
        try:
            for expr_or_stmt in exprs_or_stmts:
                self.execute(expr_or_stmt)
        except PyloxRuntimeError as error:
            pylox.Lox.Lox.run_time_error(error)

    def visit(self: "Interpreter",
              expr_or_stmt: Union[Expr, Stmt]) -> Optional[Any]:

        value: Optional[Any]
        left: Optional[Any]
        righ: Optional[Any]
        if isinstance(expr_or_stmt, Literal):

            return expr_or_stmt.value

        elif isinstance(expr_or_stmt, Unary):

            right = self.evaluate(expr_or_stmt.right)
            if expr_or_stmt.operator.token_type == TokenType.BANG:
                return not self.is_truthy(right)
            elif expr_or_stmt.operator.token_type == TokenType.MINUS:
                Interpreter.check_number_operand(expr_or_stmt.operator, right)
                return -float(right)

            # Unreachable.
            return None

        elif isinstance(expr_or_stmt, Variable):

            return self.look_up_variable(expr_or_stmt.name,
                                         expr_or_stmt)

        elif isinstance(expr_or_stmt, Grouping):

            return self.evaluate(expr_or_stmt.expr_or_stmt)

        elif isinstance(expr_or_stmt, Binary):

            left = self.evaluate(expr_or_stmt.left)
            right = self.evaluate(expr_or_stmt.right)

            if expr_or_stmt.operator.token_type == TokenType.GREATER:
                Interpreter.check_number_operands(expr_or_stmt.operator, left, right)
                return float(left) > float(right)
            elif expr_or_stmt.operator.token_type == TokenType.GREATER_EQUAL:
                Interpreter.check_number_operands(expr_or_stmt.operator, left, right)
                return float(left) >= float(right)
            elif expr_or_stmt.operator.token_type == TokenType.LESS:
                Interpreter.check_number_operands(expr_or_stmt.operator, left, right)
                return float(left) < float(right)
            elif expr_or_stmt.operator.token_type == TokenType.LESS_EQUAL:
                Interpreter.check_number_operands(expr_or_stmt.operator, left, right)
                return float(left) <= float(right)
            elif expr_or_stmt.operator.token_type == TokenType.MINUS:
                Interpreter.check_number_operands(expr_or_stmt.operator, left, right)
                return float(left) - float(right)
            elif expr_or_stmt.operator.token_type == TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                raise PyloxRuntimeError("Operands must be two numbers or two strings.",
                                        token=expr_or_stmt.operator)
            elif expr_or_stmt.operator.token_type == TokenType.SLASH:
                Interpreter.check_number_operands(expr_or_stmt.operator, left, right)
                return float(left)/float(right)
            elif expr_or_stmt.operator.token_type == TokenType.STAR:
                Interpreter.check_number_operands(expr_or_stmt.operator, left, right)
                return float(left)*float(right)
            elif expr_or_stmt.operator.token_type == TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            elif expr_or_stmt.operator.token_type == TokenType.EQUAL_EQUAL:
                return Interpreter.is_equal(left, right)

            # Unreachable.
            return None

        elif isinstance(expr_or_stmt, Call):

            callee: Any = self.evaluate(expr_or_stmt.callee)

            arguments: List[Union[Expr, Stmt]] = []
            argument: Union[Expr, Stmt]
            for i in range(len(expr_or_stmt.arguments)):
                argument = expr_or_stmt.arguments[i]
                arguments.append(self.evaluate(argument))

            if not isinstance(callee, LoxCallable):
                raise PyloxRuntimeError("Can only call functions and classes.",
                                        expr_or_stmt.paren)

            func: LoxCallable = callee
            if len(arguments) != func.arity:
                raise PyloxRuntimeError("Expected {} arguments but got {}."
                                        .format(func.arity,
                                                len(arguments)),
                                        expr_or_stmt.paren)
            return func.call(self, arguments)

        elif isinstance(expr_or_stmt, Expression):

            value = self.evaluate(expr_or_stmt.expression)
            if pylox.Lox.Lox.repl: print(Interpreter.stringify(value))
            return None

        elif isinstance(expr_or_stmt, Function):

            function: LoxFunction = LoxFunction(expr_or_stmt, self._environment)
            self._environment.define(expr_or_stmt.name.lexeme, function)
            return None

        elif isinstance(expr_or_stmt, Print):

            value = self.evaluate(expr_or_stmt.expression)
            print(Interpreter.stringify(value))
            return None

        if isinstance(expr_or_stmt, Return):

            value = None
            if expr_or_stmt.value is not None:
                value = self.evaluate(expr_or_stmt.value)
            raise ReturnException(value)

        elif isinstance(expr_or_stmt, Var):

            value = None
            if expr_or_stmt.initializer is not None:
                value = self.evaluate(expr_or_stmt.initializer)
            self._environment.define(expr_or_stmt.name.lexeme, value)
            return None

        elif isinstance(expr_or_stmt, Assign):

            value = self.evaluate(expr_or_stmt.value)
            distance: int = self._locals.get(expr_or_stmt)
            if distance is not None:
                self._environment.assign_at(distance,
                                            expr_or_stmt.name,
                                            value)
            else:
                self._globals.assign(expr_or_stmt.name, value)
            return value

        elif isinstance(expr_or_stmt, Block):

            self.execute_block(expr_or_stmt.exprs_or_stmts,
                               Environment(self._environment))
            return None

        elif isinstance(expr_or_stmt, Class):

            self._environment.define(expr_or_stmt.name.lexeme, None)
            klass: LoxClass = LoxClass(expr_or_stmt.name.lexeme)
            self._environment.assign(expr_or_stmt.name, klass)
            return None

        elif isinstance(expr_or_stmt, If):

            if self.is_truthy(self.evaluate(expr_or_stmt.condition)):
                self.execute(expr_or_stmt.then_branch)
            elif expr_or_stmt.else_branch is not None:
                self.execute(expr_or_stmt.else_branch)
            return None

        elif isinstance(expr_or_stmt, Logical):

            left = self.evaluate(expr_or_stmt.left)
            if expr_or_stmt.operator.token_type == TokenType.OR:
                if self.is_truthy(left): return left
            else:
                if not self.is_truthy(left): return left
            return self.evaluate(expr_or_stmt.right)

        elif isinstance(expr_or_stmt, While):

            while self.is_truthy(self.evaluate(expr_or_stmt.condition)):
                self.execute(expr_or_stmt.body)
            return None

        else:

            raise RuntimeError("Invalid expression: {}".format(expr_or_stmt))

    def evaluate(self: "Interpreter", expr: Union[Expr, Stmt]) -> Optional[Any]:
        return expr.accept(self)

    def resolve(self: "Interpreter", expr: Expr, depth: int) -> None:
        self._locals[expr] = depth

    def execute(self: "Interpreter", expr_or_stmt: Union[Expr, Stmt]) -> None:
        expr_or_stmt.accept(self)

    def execute_block(self: "Interpreter",
                      exprs_or_stmts: List[Union[Expr, Stmt]],
                      environment: Environment) -> None:
        previous: Environment = self._environment
        try:
            self._environment = environment
            for expr_or_stmt in exprs_or_stmts:
                self.execute(expr_or_stmt)
        finally:
            self._environment = previous

    @staticmethod
    def is_truthy(obj: Optional[Any]) -> bool:
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True

    @staticmethod
    def is_equal(a: Optional[Any],
                 b: Optional[Any]) -> bool:

        # nil is only equal to nil.
        if a is None and b is None: return True
        if a is None: return False
        return a == b

    @staticmethod
    def stringify(obj: Optional[Any]) -> str:
        if obj is None: return "nil"

        if isinstance(obj, bool): return "true" if obj else "false"

        text: str = str(obj)

        # Hack. Work around Python adding ".0" to
        # integer-valued floats.
        if isinstance(obj, float) and text.endswith(".0"):
            return text.rsplit(".")[0]

        return text

    @staticmethod
    def check_number_operand(operator: Token,
                             operand) -> None:
        if isinstance(operand, float): return
        raise PyloxRuntimeError("Operand must be a number.",
                                token=operator)

    @staticmethod
    def check_number_operands(operator: Token,
                              left,
                              right) -> None:
        if isinstance(left, float) and isinstance(right, float): return
        raise PyloxRuntimeError("Operands must be numbers.",
                                token=operator)

    def look_up_variable(self: "Interpreter",
                         name: Token,
                         expr: Expr) -> Any:
        distance: int = self._locals.get(expr)
        if distance is not None:
            return self._environment.get_at(distance,
                                            name.lexeme)
        else:
            return self._globals.get(name)


class LoxCallable:

    callee: Any
    arity: int

    def __init__(self: "LoxCallable", callee: Any) -> None:
        self.callee = callee

    def call(self: "LoxCallable",
             interpreter: Interpreter,
             arguments: List[Any]) -> Any:
        raise NotImplementedError()


class Clock(LoxCallable):

    def __init__(self):
        super().__init__(self)
        self.arity = 0

    def call(self,
             interpreter: "Interpreter",
             arguments: List[Any]) -> float:
        return time.time()/1000.0

    def __str__(self) -> str:
        return "<native fn>"


class LoxFunction(LoxCallable):

    declaration: Function
    closure: Environment

    def __init__(self: "LoxFunction",
                 declaration: Function,
                 closure: Environment) -> None:
        super().__init__(self)
        self.closure = closure
        self.declaration = declaration
        self.arity = len(self.declaration.params)

    def __str__(self: "LoxFunction") -> str:
        return "<fn {}>".format(self.declaration.name.lexeme)

    def __repr__(self: "LoxFunction") -> str:
        return str(self)

    def call(self: "LoxFunction",
             interpreter: Interpreter,
             arguments: List[Any]) -> None:

        environment: Environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme,
                               arguments[i])

        try:
            interpreter.execute_block(self.declaration.body,
                                      environment)
        except ReturnException as return_value:
            return return_value.value
        return None
