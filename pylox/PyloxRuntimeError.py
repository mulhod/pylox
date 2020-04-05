from .Token import Token


class PyloxRuntimeError(RuntimeError):

    token: Token
    message: str

    def __init__(self, message: str, token: Token = None):
        super()
        self.token = token
        self.message = message
