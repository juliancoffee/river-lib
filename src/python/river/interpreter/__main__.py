import sys

from parser.parse import tokenize
from os import PathLike


def tokenize_file(src_file: PathLike):
    with open(src_file) as src:
        return tokenize(src.read().strip())


def run_and_show(filename):
    print(f">> {filename}:")
    print(tokenize_file(filename))
    print()


def main():
    args = sys.argv
    if len(args) == 1:
        print("Usage: river <source file>")
    elif args[1] == "-a":
        for filename in args[2:]:
            run_and_show(filename)
    elif len(args) == 2:
        filename = args[1]
        run_and_show(filename)
    else:
        print("For multiple files run:\n\triver -a [files, ...]")


if __name__ == "__main__":
    main()
