from pylox.Token import Token


class PyloxRuntimeError(RuntimeError):

    token = None
    message = None

    def __init__(self: "PyloxRuntimeError",
                 message: str,
                 token: Token = None) -> None:
        super()
        self.token = token
        self.message = message
