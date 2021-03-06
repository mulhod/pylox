import time
from typing import Any, Dict, List, Optional, Union

import pylox
from .Environment import Environment
from .ExprOrStmt import (Assign, Block, Binary, Call, Class, Expr,
                         ExprVisitor, Expression, Function, If, Literal,
                         Logical, Get, Grouping, Print, Return, Set, Stmt,
                         StmtVisitor, Super, This, Unary, Variable, Var,
                         While)
from .PyloxRuntimeError import PyloxRuntimeError
from .Return import Return as ReturnException
from .Token import Token
from .TokenType import TokenType


class Interpreter(ExprVisitor, StmtVisitor):

    _globals: Environment = Environment()
    _environment: Environment = _globals
    _locals: Dict[Expr, int] = {}

    def __init__(self) -> None:
        self._globals.define("clock", Clock())

    def interpret(self, exprs_or_stmts: List[Union[Expr, Stmt]]) -> None:
        try:
            for expr_or_stmt in exprs_or_stmts:
                self.execute(expr_or_stmt)
        except PyloxRuntimeError as error:
            pylox.Lox.Lox.run_time_error(error)

    def visit(self,
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

        elif isinstance(expr_or_stmt, Get):

            object_: Any = self.evaluate(expr_or_stmt.object)
            if isinstance(object_, LoxInstance):
                return object_.get(expr_or_stmt.name)
            raise PyloxRuntimeError("Only instances have properties.",
                                    expr_or_stmt.name)

        elif isinstance(expr_or_stmt, Expression):

            value = self.evaluate(expr_or_stmt.expression)
            if pylox.Lox.Lox.repl: print(Interpreter.stringify(value))
            return None

        elif isinstance(expr_or_stmt, Function):

            function: LoxFunction = LoxFunction(expr_or_stmt,
                                                self._environment,
                                                False)
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

            super_class: Any = None
            if expr_or_stmt.super_class is not None:
                super_class = self.evaluate(expr_or_stmt.super_class)
                if not isinstance(super_class, LoxClass):
                    PyloxRuntimeError("Superclass must be a class.",
                                      expr_or_stmt.super_class.name)
            self._environment.define(expr_or_stmt.name.lexeme, None)
            if expr_or_stmt.super_class is not None:
                self._environment = Environment(self._environment)
                self._environment.define("super", super_class)
            methods: Dict[str, LoxFunction] = {}
            method: Function
            for method in expr_or_stmt.methods:
                function: LoxFunction = \
                    LoxFunction(method,
                                self._environment,
                                method.name.lexeme == "init")
                methods[method.name.lexeme] = function
            klass: LoxClass = LoxClass(expr_or_stmt.name.lexeme,
                                       super_class,
                                       methods)
            if super_class is not None:
                self._environment = self._environment.enclosing
            self._environment.assign(expr_or_stmt.name,
                                     klass)
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

        elif isinstance(expr_or_stmt, Set):

            object_: Any = self.evaluate(expr_or_stmt.object)
            if not isinstance(object_, LoxInstance):
                raise PyloxRuntimeError("Only instances have fields.",
                                        expr_or_stmt.name)

            value: Any = self.evaluate(expr_or_stmt.value)
            object_.set(expr_or_stmt.name, value)
            return value

        elif isinstance(expr_or_stmt, Super):

            distance: int = self._locals[expr_or_stmt]
            super_class: LoxClass = \
                self._environment.get_at(distance, "super")

            # "this" is always one level nearer than "super"'s
            # environment.
            object_: LoxInstance = self._environment.get_at(distance - 1,
                                                            "this")

            method: LoxFunction = \
                super_class.find_method(expr_or_stmt.method.lexeme)
            if method is None:
                raise PyloxRuntimeError("Undefined property '{}'."
                                        .format(expr_or_stmt.method.lexeme),
                                        expr_or_stmt.method)

            return method.bind(object_)

        elif isinstance(expr_or_stmt, This):

            return self.look_up_variable(expr_or_stmt.keyword, expr_or_stmt)

        elif isinstance(expr_or_stmt, While):

            while self.is_truthy(self.evaluate(expr_or_stmt.condition)):
                self.execute(expr_or_stmt.body)
            return None

        else:

            raise RuntimeError("Invalid expression: {}".format(expr_or_stmt))

    def evaluate(self, expr: Union[Expr, Stmt]) -> Optional[Any]:
        return expr.accept(self)

    def resolve(self, expr: Expr, depth: int) -> None:
        self._locals[expr] = depth

    def execute(self, expr_or_stmt: Union[Expr, Stmt]) -> None:
        expr_or_stmt.accept(self)

    def execute_block(self,
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

    def look_up_variable(self,
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
    _arity: int = 0

    def __init__(self, callee: Any) -> None:
        self.callee = callee

    @property
    def arity(self):
        return self._arity

    def call(self,
             interpreter: Interpreter,
             arguments: List[Any]) -> Any:
        raise NotImplementedError()


class Clock(LoxCallable):

    def __init__(self):
        super().__init__(self)

    def call(self, interpreter: Interpreter, arguments: List[Any]) -> float:
        return time.time()

    def __str__(self):
        return "<native fn>"


class LoxFunction(LoxCallable):

    _declaration: Function
    _closure: Environment
    _is_initializer: bool

    def __init__(self,
                 declaration: Function,
                 closure: Environment,
                 is_initializer: bool):
        super().__init__(self)
        self._closure = closure
        self._declaration = declaration
        self._is_initializer = is_initializer
        self._arity = len(self._declaration.params)

    def bind(self, instance: "LoxInstance") -> "LoxFunction":
        environment: Environment = Environment(self._closure)
        environment.define("this", instance)
        return LoxFunction(self._declaration,
                           environment,
                           self._is_initializer)

    def __str__(self):
        return "<fn {}>".format(self._declaration.name.lexeme)

    def __repr__(self):
        return str(self)

    def call(self, interpreter: Interpreter, arguments: List[Any]) -> None:

        environment: Environment = Environment(self._closure)
        for i, param in enumerate(self._declaration.params):
            environment.define(param.lexeme,
                               arguments[i])

        try:
            interpreter.execute_block(self._declaration.body,
                                      environment)
        except ReturnException as return_value:
            if self._is_initializer:
                return self._closure.get_at(0, "this")
            return return_value.value
        if self._is_initializer:
            return self._closure.get_at(0, "this")
        return None


class LoxClass(LoxCallable):

    name: str
    superclass: "LoxClass"
    methods: Dict[str, LoxFunction]

    def __init__(self,
                 name: str,
                 super_class: "LoxClass",
                 methods: Dict[str, LoxFunction]):
        super().__init__(self)
        self.super_class = super_class
        self.name = name
        self.methods = methods

    @property
    def arity(self) -> int:
        initializer: Optional[LoxFunction] = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity

    def find_method(self, name: str) -> Optional[LoxFunction]:
        if name in self.methods:
            return self.methods[name]
        if self.super_class is not None:
            return self.super_class.find_method(name)

    def __str__(self):
        return self.name

    def call(self,
             interpreter: Interpreter,
             arguments: List[Any]) -> "LoxInstance":
        instance: LoxInstance = LoxInstance(self)
        initializer: Optional[LoxFunction] = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance


class LoxInstance:

    klass: LoxClass
    fields: Dict[str, Any] = {}

    def __init__(self, klass: LoxClass):
        self.klass = klass

    def get(self, name: Token) -> Any:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method: Optional[LoxFunction] = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise PyloxRuntimeError("Undefined property '{}'."
                                .format(name.lexeme),
                                name)

    def set(self, name: Token, value: Any) -> None:
        self.fields[name.lexeme] = value

    def __str__(self):
        return self.klass.name + " instance"
