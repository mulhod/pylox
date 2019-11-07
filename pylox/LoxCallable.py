from typing import List, Any

from . import Interpreter


class LoxCallable:

    callee: Any
    arity: int

    def __init__(self: "LoxCallable", callee: Any) -> None:
        self.callee = callee

    def call(self: "LoxCallable",
             interpreter: Interpreter,
             arguments: List[Any]) -> Any:
        raise NotImplementedError()
