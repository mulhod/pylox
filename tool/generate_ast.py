from typing import List, Tuple
from os.path import join, dirname, realpath

this_dir_path = dirname(realpath(__file__))
pylox_dir_path = join(dirname(this_dir_path), "pylox")


class GenerateAst:

    def __init__(self: "GenerateAst") -> None:
        self.print = print
        self.define_ast("Expr",
                        [("Binary", [("left", "Expr"),
                                     ("operator", "Token"),
                                     ("right", "Expr")]),
                         ("Grouping", [("expression", "Expr")]),
                         ("Literal", [("value", "Any")]),
                         ("Unary", [("operator", "Token"),
                                    ("right", "Expr")])])

    def define_ast(self: "GenerateAst",
                   base_class_name: str,
                   classes_and_parameters: List[Tuple[str, List[Tuple[str, str]]]]) -> None:

        path = join(pylox_dir_path, "{}.py".format(base_class_name))
        with open(path, "w") as file_:
            self.print = lambda x: print(x, file=file_)

            self.add_imports()
            self.add_Visitor_class()
            self.add_Expr_class()

            # The AST classes.
            for sub_class_name, parameters in classes_and_parameters:
                self.add_Expr_subclass(base_class_name,
                                       sub_class_name,
                                       parameters)

    def add_imports(self: "GenerateAst") -> None:
        self.print("from typing import Any\n"
                   "\n"
                   "from pylox.Token import Token\n"
                   "\n")

    def add_Visitor_class(self: "GenerateAst") -> None:
        self.print("class Visitor:\n"
                   "\n"
                   "    def __str__(self: \"Visitor\") -> str:\n"
                   "        return self.__class__.__name__\n"
                   "\n"
                   "    def visit(self: \"Visitor\", expr: \"Expr\") -> \"Visitor\":\n"
                   "        return self")

    def add_Expr_class(self: "GenerateAst") -> None:
        self.print("\n"
                   "\n"
                   "class Expr:\n"
                   "\n"
                   "    def accept(self: \"Expr\", visitor: Visitor) -> None:\n"
                   "        raise NotImplementedError")

    def add_Expr_subclass(self: "GenerateAst",
                          base_class_name: str,
                          sub_class_name: str,
                          parameters: List[Tuple[str, str]]) -> None:
        self.print("\n"
                   "\n"
                   "class {}({}):"
                   .format(sub_class_name, base_class_name))
        self.print("\n"
                   "    def __init__(self: \"{}\", {}) -> None:"
                   .format(sub_class_name,
                           ", ".join(["{}: {}".format(parameter, type_hint)
                                      for parameter, type_hint in parameters])))
        for parameter in parameters:
            parameter_name = parameter[0]
            self.print("        self.{0} = {0}".format(parameter_name))
        self.print("\n"
                   "    def accept(self: \"{}\", visitor: Visitor) -> \"Visitor\":\n"
                   "        return visitor.visit(self)"
                   .format(sub_class_name))


def main():
    GenerateAst()


if __name__ == "__main__":
    main()
