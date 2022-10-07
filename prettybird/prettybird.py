import argparse
import pathlib

from lark import Lark

from prettybird import PrettyBirdInterpreter

def get_args():
    """Parse command line arguments

    Returns:
        argparse.Namespace: Parsed arguments object
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file", help=".pbd file to compile", type=str)

    return parser.parse_args()

def main():
    # Get command-line arguments
    args = get_args()

    # Parse the grammar file
    parser = Lark(open(pathlib.Path(__file__).parent / "grammar.lark"))

    # Setup Interpreter
    interpreter = PrettyBirdInterpreter()

    with open(args.input_file, "r") as input_file:
        # Parse the source file into an AST
        AST = parser.parse(input_file.read())
        # Pass the AST through the Interpreter
        interpreter.visit(AST)
    
    for symbol in interpreter.symbols_dict.values():
        print(symbol)


if __name__ == "__main__":
    main()
