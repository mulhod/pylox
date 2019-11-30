import sys

import pylox

def main():
    pylox.Lox.Lox.run(sys.argv[1:])


if __name__ == "__main__":
    main()
