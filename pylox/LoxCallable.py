from typing import Sequence, Any

from pylox.Interpreter import Interpreter

class LoxCallable:

    callee: Any
    _arity: int

    def __init__(self: "LoxCallable", callee: Any) -> None:
        self.callee = callee

    @property
    def arity(self) -> int:
        return self._arity

    def call(self: "LoxCallable",
             interpreter: Interpreter,
             arguments: Sequence[Any]) -> Any:
        raise NotImplementedError()
