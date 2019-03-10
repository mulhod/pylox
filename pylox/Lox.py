import sys
from typing import List
from os.path import realpath, exists

from pylox.Token import Token
from pylox.Scanner import Scanner


class Lox:

    had_error = False

    @classmethod
    def run(cls: "Lox", args: List[str]) -> None:
        if len(args) > 1:
            print("Usage: pylox [script]")
            sys.exit(64)
        elif len(args) == 1:
            path = realpath(args[0])
            if not exists(path):
                raise RuntimeError("{} does not exist!".format(path))
            cls.run_file(path)
        else:
            cls.run_prompt()

    @classmethod
    def run_file(cls: "Lox", path: str) -> None:
        with open(path) as input_file:
            source_input = input_file.read()
        cls.run_from_string(source_input)

        # Indicate an error in the exit code.
        if cls.had_error:
            sys.exit(65)

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
            except KeyboardInterrupt:
                print()
                break
            cls.had_error = False

    @staticmethod
    def run_from_string(source: str) -> List[Token]:
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        # For now, just print the tokens.
        for token in tokens:
            print(token)

        return tokens

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
