from typing import MutableSequence, Sequence, Tuple, Optional, Callable
from os.path import join, dirname, realpath

this_dir_path = dirname(realpath(__file__))
pylox_dir_path = join(dirname(this_dir_path), "pylox")


class GenerateAst:

    def __init__(self: "GenerateAst") -> None:
        self.print: Callable = print
        self.define_ast("Expr",
                        [("Assign", [("name", "Token"),
                                     ("value", "Expr")]),
                         ("Binary", [("left", "Expr"),
                                     ("operator", "Token"),
                                     ("right", "Expr")]),
                         ("Call", [("callee", "Expr"),
                                   ("paren", "Token"),
                                   ("arguments", "Sequence[Expr]")]),
                         ("Grouping", [("expression", "Expr")]),
                         ("Literal", [("value", "Any")]),
                         ("Logical", [("left", "Expr"),
                                      ("operator", "Token"),
                                      ("right", "Expr")]),
                         ("Unary", [("operator", "Token"),
                                    ("right", "Expr")]),
                         ("Variable", [("name", "Token")])],
                         extra_imports=["from pylox.Token import Token",
                                        "from typing import Sequence"])
        self.define_ast("Stmt",
                        [("Block", [("statements", "Sequence[Stmt]")]),
                         ("Expression", [("expression", "Union[Expr, Stmt]")]),
                         ("Function", [("name", "Token"),
                                       ("params", "Sequence[Token]"),
                                       ("body", "Sequence[Stmt]")]),
                         ("If", [("condition", "Union[Expr, Stmt]",),
                                 ("then_branch", "Union[Expr, Stmt]"),
                                 ("else_branch", "Union[Expr, Stmt]")]),
                         ("Print", [("expression", "Union[Expr, Stmt]")]),
                         ("Return", [("keyword", "Token"),
                                     ("value", "Union[Expr, Stmt]")]),
                         ("Var", [("name", "Token"),
                                  ("initializer", "Union[Expr, Stmt]")]),
                         ("While", [("condition", "Union[Expr, Stmt]"),
                                    ("body", "Stmt")])],
                        extra_imports=["from typing import Sequence, Union",
                                       "from pylox.Token import Token",
                                       "from pylox.Expr import Expr"])

    def define_ast(self: "GenerateAst",
                   base_class_name: str,
                   classes_and_parameters: Sequence[Tuple[str, Sequence[Tuple[str, str]]]],
                   extra_imports : Optional[Sequence[str]] = None) -> None:

        path: str = join(pylox_dir_path, "{}.py".format(base_class_name))
        with open(path, "w") as file_:
            self.print = lambda x: print(x, file=file_)

            self.add_imports(extra_imports=extra_imports)
            self.add_Visitor_class(base_class_name)
            self.add_base_class(base_class_name)

            # The AST classes.
            for sub_class_name, parameters in classes_and_parameters:
                self.add_subclass(base_class_name,
                                  sub_class_name,
                                  parameters)

    def add_imports(self: "GenerateAst",
                    extra_imports : Optional[Sequence[str]] = None) -> None:
        imports: MutableSequence[str] = ["from typing import Optional, Any\n\n"]
        if extra_imports is not None:
            for extra_import in extra_imports:
                imports.append("{}\n".format(extra_import))
            imports.append("\n")
        imports_list: Sequence[str] = "".join(imports)
        self.print(imports_list)

    def add_Visitor_class(self: "GenerateAst",
                          base_class_name: str) -> None:
        self.print("class Visitor:\n"
                   "\n"
                   "    def __str__(self: \"Visitor\") -> \"str\":\n"
                   "        return self.__class__.__name__\n"
                   "\n"
                   "    def visit(self: \"Visitor\", expr: \"{}\") -> \"Visitor\":\n"
                   "        return self".format(base_class_name))

    def add_base_class(self: "GenerateAst",
                       base_class_name: str) -> None:
        self.print("\n"
                   "\n"
                   "class {0}:\n"
                   "\n"
                   "    def accept(self: \"{0}\", visitor: Visitor) -> Optional[Any]:\n"
                   "        return visitor.visit(self)".format(base_class_name))

    def add_subclass(self: "GenerateAst",
                     base_class_name: str,
                     sub_class_name: str,
                     parameters: Sequence[Tuple[str, str]]) -> None:
        self.print("\n"
                   "\n"
                   "class {}({}):"
                   "\n"
                   .format(sub_class_name, base_class_name))
        parameter_name: str
        parameter_type: str
        for parameter in parameters:
            parameter_name = parameter[0]
            parameter_type = parameter[1]
            self.print("    {}: {}"
                       .format(parameter_name,
                               parameter_type))
        self.print("\n"
                   "    def __init__(self: \"{}\", {}) -> None:"
                   .format(sub_class_name,
                           ", ".join(["{}: {}".format(parameter, type_hint)
                                      for parameter, type_hint in parameters])))
        for parameter in parameters:
            parameter_name = parameter[0]
            self.print("        self.{0} = {0}".format(parameter_name))
        self.print("\n"
                   "    def accept(self: \"{}\", visitor: Visitor) -> Optional[Any]:\n"
                   "        return visitor.visit(self)"
                   .format(sub_class_name))


def main():
    GenerateAst()


if __name__ == "__main__":
    main()
