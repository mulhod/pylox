import sys

from .Lox import Lox

def main():
    Lox.run(sys.argv[1:])


if __name__ == "__main__":
    main()
