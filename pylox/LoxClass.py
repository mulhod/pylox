
class LoxClass:

    name: str

    def __init__(self: "LoxClass", name: str):
        self.name = name

    def __str__(self):
        return self.name
