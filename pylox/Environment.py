from typing import Any, Dict, Optional

from .PyloxRuntimeError import PyloxRuntimeError
from .Token import Token


class Environment:

    enclosing: "Environment"
    values: Dict[str, Any] = {}

    def __init__(self: "Environment",
                 enclosing: Optional["Environment"] = None) -> None:
        self.enclosing = enclosing
        self.values = {}

    def __str__(self: "Environment") -> str:
        return "Environment: {}".format(self.values)

    def __repr__(self: "Environment") -> str:
        return str(self)

    def get(self: "Environment", name: Token) -> Any:

        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise PyloxRuntimeError("Undefined variable '{}'.".format(name.lexeme),
                                token=name)

    def assign(self: "Environment",
               name: Token,
               value: Any) -> None:

        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise PyloxRuntimeError("Undefined variable '{}'."
                                .format(name.lexeme),
                                name)

    def define(self: "Environment", name: str, value: Any) -> None:
        self.values[name] = value

    def get_at(self: "Environment", distance: int, name: str) -> Any:
        return self.ancestor(distance).values[name]

    def assign_at(self: "Environment",
                  distance: int,
                  name: Token,
                  value: Any) -> None:
        x = self.ancestor(distance).values
        x[name.lexeme] = value

    def ancestor(self: "Environment", distance: int) -> "Environment":
        environment: Environment = self
        i: int = 0
        while i < distance:
            environment = environment.enclosing
            i += 1
        return environment
