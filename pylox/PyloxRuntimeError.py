from typing import Optional

from pylox.Token import Token


class PyloxRuntimeError(RuntimeError):

    token = None # type: Optional[Token]
    message = None # type: str

    def __init__(self: "PyloxRuntimeError",
                 message: str,
                 token: Token = None) -> None:
        super()
        self.token = token
        self.message = message
