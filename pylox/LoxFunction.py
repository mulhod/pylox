from typing import Any, Sequence

from . import Interpreter
from .Environment import Environment
from .LoxCallable import LoxCallable
from .Return import Return
from .Stmt import Function


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
             arguments: Sequence[Any]) -> None:

        environment: Environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme,
                               arguments[i])

        try:
            interpreter.execute_block(self.declaration.body,
                                      environment)
        except Return as return_value:
            return return_value.value
        return None
