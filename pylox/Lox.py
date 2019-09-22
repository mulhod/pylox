import sys
from typing import Sequence
from os.path import realpath, exists

from pylox.Token import Token
from pylox.Parser import Parser
from pylox.Scanner import Scanner
from pylox.TokenType import TokenType
from pylox.Interpreter import Interpreter
from pylox.PyloxRuntimeError import PyloxRuntimeError
from pylox.Stmt import Stmt


class Lox:
    interpreter: Interpreter = Interpreter()
    had_error: bool = False
    had_runtime_error: bool = False
    repl: bool = False

    @classmethod
    def run(cls: "Lox", args: Sequence[str]) -> None:
        if len(args) > 1:
            print("Usage: pylox [script]")
            sys.exit(64)
        elif len(args) == 1:
            path : str = realpath(args[0])
            if not exists(path):
                raise RuntimeError("{} does not exist!".format(path))
            cls.run_file(path)
        else:
            cls.repl = True
            cls.run_prompt()

    @classmethod
    def run_file(cls: "Lox", path: str) -> None:
        with open(path) as input_file:
            source_input: str = input_file.read()
        cls.run_from_string(source_input)

        # Indicate an error in the exit code.
        if cls.had_error:
            sys.exit(65)
        if cls.had_runtime_error:
            sys.exit(70)

    @classmethod
    def run_prompt(cls: "Lox",
                   keyboard_interrupt: bool = False) -> None:
        while True:
            print("> ", end="")
            try:
                if not keyboard_interrupt:
                    cls.run_from_string(input())
                else:
                    raise KeyboardInterrupt()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            cls.had_error = False

    @classmethod
    def run_from_string(cls: "Lox", source: str) -> None:
        scanner: Scanner = Scanner(source)
        tokens: Sequence[Token] = scanner.scan_tokens()
        parser: Parser = Parser(tokens)
        expression : Sequence[Stmt] = parser.parse()

        # Stop if there was a syntax error.
        if cls.had_error: return

        cls.interpreter.interpret(expression)

    @classmethod
    def error(cls: "Lox",
              line_number: int,
              message: str) -> None:
        cls.report(line_number, "", message)

    @classmethod
    def report(cls: "Lox",
               line_number: int,
               where: str,
               message: str) -> None:
        print("[line {}] Error {}: {}".format(line_number, where, message))        
        cls.had_error = True

    @classmethod
    def token_error(cls: "Lox", token: Token, message: str) -> None:
        if token.token_type == TokenType.EOF:
            cls.report(token.line_number, "at end", message)
        else:
            cls.report(token.line_number,
                       "at '{}'".format(token.lexeme),
                       message)

    @classmethod
    def run_time_error(cls: "Lox", error: PyloxRuntimeError) -> None:
        print("{}\n[line {}]".format(error.message,
                                     error.token.line_number))
        cls.had_runtime_error = True
