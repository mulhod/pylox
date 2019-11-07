from typing import Any


class Return(RuntimeError):

    value: Any

    def __init__(self: "Return", value: Any) -> None:
        super()
        self.value = value
