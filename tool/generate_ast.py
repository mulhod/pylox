from typing import List, Tuple, Optional
from os.path import join, dirname, realpath

this_dir_path = dirname(realpath(__file__))
pylox_dir_path = join(dirname(this_dir_path), "pylox")


class GenerateAst:

    def __init__(self: "GenerateAst") -> None:
        self.print = print
        self.define_ast("Expr",
                        [("Assign", [("name", "Token"),
                                     ("value", "Expr")]),
                         ("Binary", [("left", "Expr"),
                                     ("operator", "Token"),
                                     ("right", "Expr")]),
                         ("Grouping", [("expression", "Expr")]),
                         ("Literal", [("value", "Any")]),
                         ("Unary", [("operator", "Token"),
                                    ("right", "Expr")]),
                         ("Variable", [("name", "Token")])],
                         extra_imports=["from pylox.Token import Token"])
        self.define_ast("Stmt",
                        [("Block", [("statements", "List[Stmt]")]),
                         ("Expression", [("expression", "Expr")]),
                         ("Print", [("expression", "Expr")]),
                         ("Var", [("name", "Token"), ("initializer", "Expr")])],
                        extra_imports=["from typing import List",
                                       "from pylox.Token import Token",
                                       "from pylox.Expr import Expr"])

    def define_ast(self: "GenerateAst",
                   base_class_name: str,
                   classes_and_parameters: List[Tuple[str, List[Tuple[str, str]]]],
                   extra_imports : Optional[List[str]] = None) -> None:

        path = join(pylox_dir_path, "{}.py".format(base_class_name))
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
                    extra_imports : Optional[List[str]] = None) -> None:
        imports = ["from typing import Optional, Any\n\n"]
        if extra_imports is not None:
            for extra_import in extra_imports:
                imports.append("{}\n".format(extra_import))
            imports.append("\n")
        imports = "".join(imports)
        self.print(imports)

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
                     parameters: List[Tuple[str, str]]) -> None:
        self.print("\n"
                   "\n"
                   "class {}({}):"
                   "\n"
                   .format(sub_class_name, base_class_name))
        for parameter in parameters:
            parameter_name = parameter[0] # type: str
            parameter_type = parameter[1] # type: str
            self.print("    {} = None # type: Optional[{}]"
                       .format(parameter_name,
                               parameter_type))
        self.print("\n"
                   "    def __init__(self: \"{}\", {}) -> None:"
                   .format(sub_class_name,
                           ", ".join(["{}: {}".format(parameter, type_hint)
                                      for parameter, type_hint in parameters])))
        for parameter in parameters:
            parameter_name = parameter[0] # type: str
            self.print("        self.{0} = {0}".format(parameter_name))
        self.print("\n"
                   "    def accept(self: \"{}\", visitor: Visitor) -> Optional[Any]:\n"
                   "        return visitor.visit(self)"
                   .format(sub_class_name))


def main():
    GenerateAst()


if __name__ == "__main__":
    main()
