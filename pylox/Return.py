from typing import Any


class Return(RuntimeError):

    value: Any

    def __init__(self, value: Any):
        super()
        self.value = value
