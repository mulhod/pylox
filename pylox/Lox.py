import sys
from os.path import realpath, exists

from pylox.Scanner import Scanner


class Lox:

    had_error = False

    @classmethod
    def run(cls, args):
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
    def run_file(cls, path):
        with open(path) as input_file:
            source_input = input_file.read()
        cls.run_from_string(source_input)

        # Indicate an error in the exit code.
        if cls.had_error:
            sys.exit(65)

    @classmethod
    def run_prompt(cls):
        while True:
            print("> ", end="")
            cls.run_from_string(input())
            cls.had_error = False

    @staticmethod
    def run_from_string(source):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        # For now, just print the tokens.
        for token in tokens:
            print(token)

    @classmethod
    def error(cls, line_number, message):
        cls.report(line_number, "", message)

    @classmethod
    def report(cls, line_number, where, message):
        print("[line {}] Error {}: {}".format(line_number, where, message))        
        cls.had_error = True
