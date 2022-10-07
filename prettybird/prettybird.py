import argparse
import pathlib

from lark import Lark

from prettybird import PrettyBirdTransformer

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file", help=".pbd file to compile", type=str)

    return parser.parse_args()

def main():
    args = get_args()

    parser = Lark(open(pathlib.Path(__file__).parent / "grammar.lark"))

    with open(args.input_file, "r") as input_file:
        AST = parser.parse(input_file.read())
        PrettyBirdTransformer().transform(AST)


if __name__ == "__main__":
    main()
