from pylox.Token import Token


class PyloxRuntimeError(RuntimeError):

    token = None
    message = None

    def __init__(self: "PyloxRuntimeError",
                 token: Token,
                 message: str) -> None:
        super(message)
        self.token = token
        self.message = message

    def get_message(self: "PyloxRuntimeError") -> str:
        return self.message
