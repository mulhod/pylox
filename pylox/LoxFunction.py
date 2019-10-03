from typing import Any, Sequence

from pylox.Stmt import Function
from . import Interpreter
from pylox.LoxCallable import LoxCallable
from pylox.Environment import Environment
from pylox.Return import Return

class LoxFunction(LoxCallable):

    declaration: Function

    def __init__(self: "LoxFunction", declaration: Function) -> None:
        super().__init__(self)
        self.declaration = declaration
        self.arity = len(self.declaration.params)

    def __str__(self: "LoxFunction") -> str:
        return "<fn {}>".format(self.declaration.name.lexeme)

    def __repr__(self: "LoxFunction") -> str:
        return str(self)

    def call(self: "LoxFunction",
             interpreter: Interpreter,
             arguments: Sequence[Any]) -> None:

        environment: Environment = Environment(interpreter.globals)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme,
                               arguments[i])

        try:
            interpreter.execute_block(self.declaration.body,
                                      environment)
        except Return as return_value:
            return return_value.value
        return None
