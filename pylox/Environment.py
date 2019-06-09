from typing import Any

from pylox.Token import Token
from pylox.PyloxRuntimeError import PyloxRuntimeError


class Environment:

    values = {}

    def get(self: "Environment", name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        raise PyloxRuntimeError("Undefined variable '{}'.".format(name.lexeme),
                                token=name)

    def assign(self: "Environment",
               name: Token,
               value: Any) -> None:
        if name.lexeme  in self.values:
            self.values[name.lexeme] = value
            return
        raise PyloxRuntimeError("Undefined variable '{}'."
                                .format(name.lexeme),
                                name)

    def define(self: "Environment", name: str, value: Any) -> None:
        self.values[name] = value
