from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple

pylox_package_dir_path: Path = \
    Path(__file__).absolute().parent.parent / "pylox"


class GenerateAst:

    def __init__(self: "GenerateAst") -> None:
        self.print: Callable[[Any], None] = print
        self.define_ast("ExprOrStmt",
                        ["Expr", "Stmt"],
                        [[("Assign", [("name", "Token"),
                                      ("value", "Expr")]),
                          ("Binary", [("left", "Expr"),
                                      ("operator", "Token"),
                                      ("right", "Expr")]),
                          ("Call", [("callee", "Expr"),
                                    ("paren", "Token"),
                                    ("arguments", "List[Union[Expr, \"Stmt\"]]")]),
                          ("Grouping", [("expr_or_stmt", "Union[Expr, \"Stmt\"]")]),
                          ("Literal", [("value", "Any")]),
                          ("Logical", [("left", "Expr"),
                                       ("operator", "Token"),
                                       ("right", "Expr")]),
                          ("Unary", [("operator", "Token"),
                                     ("right", "Expr")]),
                          ("Variable", [("name", "Token")])],
                         [("Block", [("exprs_or_stmts", "List[Union[Expr, Stmt]]")]),
                          ("Expression", [("expression", "Union[Expr, Stmt]")]),
                          ("Function", [("name", "Token"),
                                        ("params", "List[Token]"),
                                        ("body", "List[Union[Expr, Stmt]]")]),
                          ("If", [("condition", "Union[Expr, Stmt]",),
                                  ("then_branch", "Union[Expr, Stmt]"),
                                  ("else_branch", "Union[Expr, Stmt]")]),
                          ("Print", [("expression", "Union[Expr, Stmt]")]),
                          ("Return", [("keyword", "Token"),
                                      ("value", "Union[Expr, Stmt]")]),
                          ("Var", [("name", "Token"),
                                   ("initializer", "Union[Expr, Stmt]")]),
                          ("While", [("condition", "Union[Expr, Stmt]"),
                                     ("body", "Stmt")])]],
                         extra_imports=["from .Token import Token",
                                        "from typing import List, Union"])

    def define_ast(self: "GenerateAst",
                   module_name: str,
                   base_class_names: List[str],
                   classes_and_parameters_list: List[List[Tuple[str, List[Tuple[str, str]]]]],
                   extra_imports : Optional[List[str]] = None) -> None:

        path: Path = pylox_package_dir_path / "{}.py".format(module_name)
        with path.open("w") as file_:
            self.print = lambda x: print(x, file=file_)
            self.add_imports(extra_imports=extra_imports)
            for (base_class_name,
                 classes_and_parameters) in zip(base_class_names,
                                                classes_and_parameters_list):
                self.add_Visitor_class(base_class_name)
                self.add_base_class(base_class_name)

                # The AST classes.
                for sub_class_name, parameters in classes_and_parameters:
                    self.add_subclass(base_class_name,
                                      sub_class_name,
                                      parameters)

    def add_imports(self: "GenerateAst",
                    extra_imports : Optional[List[str]] = None) -> None:
        imports: List[str] = ["from typing import Any, Optional\n\n"]
        if extra_imports is not None:
            for extra_import in extra_imports:
                imports.append("{}\n".format(extra_import))
            imports.append("\n")
        imports_list: str = "".join(imports)
        self.print(imports_list)

    def add_Visitor_class(self: "GenerateAst",
                          base_class_name: str) -> None:
        self.print("\n\nclass {0}Visitor:\n"
                   "\n"
                   "    def __str__(self: \"{0}Visitor\") -> \"str\":\n"
                   "        return self.__class__.__name__\n"
                   "\n"
                   "    def visit(self: \"{0}Visitor\", expr: \"{0}\") -> \"{0}Visitor\":\n"
                   "        return self".format(base_class_name))

    def add_base_class(self: "GenerateAst",
                       base_class_name: str) -> None:
        self.print("\n"
                   "\n"
                   "class {0}:\n"
                   "\n"
                   "    def accept(self: \"{0}\", visitor: {0}Visitor) -> Optional[Any]:\n"
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
                   "    def accept(self: \"{}\", visitor: {}Visitor) -> Optional[Any]:\n"
                   "        return visitor.visit(self)"
                   .format(sub_class_name, base_class_name))


def main():
    GenerateAst()


if __name__ == "__main__":
    main()
