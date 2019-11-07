from typing import Any, MutableMapping, Optional

from .PyloxRuntimeError import PyloxRuntimeError
from .Token import Token


class Environment:

    enclosing: "Environment"
    values: MutableMapping[str, Any] = {}

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
