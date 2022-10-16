import argparse
import os
import pathlib

from lark import Lark

from prettybird import PrettyBirdInterpreter
from prettybird.formats import *


def get_args():
    """Parse command line arguments

    Returns:
        argparse.Namespace: Parsed arguments object
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file", help=".pbd file to compile", type=str)
    parser.add_argument(
        "--format",
        "-f",
        default="BDF",
        help="Format to convert to. Supported: [BDF, TTF]",
        type=str,
    )
    parser.add_argument(
        "--font-name",
        "-n",
        default=None,
        help="Name to give to the output font",
        type=str,
    )
    parser.add_argument(
        "--stdout",
        default=False,
        action="store_true",
        help="Print compiled characters' IR to stdout",
    )

    return parser.parse_args()


def get_format(format_name: str) -> Format:
    format_name = format_name.upper()
    if format_name == "BDF":
        return BDF
    elif format_name == "SVG":
        return SVG
    raise NotImplementedError(f"Font format {format_name} is not supported")


def main():
    # Get command-line arguments
    args = get_args()

    if args.font_name is None:
        args.font_name = pathlib.Path(args.input_file).stem
    args.format == args.format.lower()

    # Parse the grammar file
    parser = Lark(open(pathlib.Path(__file__).parent / "grammar.lark"))

    # Setup Interpreter
    interpreter = PrettyBirdInterpreter()

    with open(args.input_file, "r") as input_file:
        # Parse the source file into a parse_tree
        parse_tree = parser.parse(input_file.read())
        # Pass the AST through the Interpreter
        interpreter.visit(parse_tree)
        """
        # Need some way to separate language compile errors (shouldn't show backtrace) with compile*R* errors (should show backtrace)
        try:
            interpreter.visit(parse_tree)
        except Exception as e:
            print(type(e).__name__ + ":", e)
            exit(1)
        """

    for symbol in interpreter.symbols_dict.values():
        symbol.compile()
        if args.stdout:
            print(symbol)

    """
    font = BDF(
        filename=f"{args.font_name}.bdf",
        version="0.1",
        font_name=args.font_name,
        point_size=16,
        bounding_box=(6, 8),
        properties=[("FONT_ASCENT", 14), ("FONT_DESCENT", 2)],
    )
    """
    font = get_format(args.format)(args.font_name, "0.1")
    font.add_symbols(list(interpreter.symbols_dict.values()))
    font.compile()

    """
    if args.format == "ttf":
        font.convert_to_ttf()
        os.remove(font.filename)
    """


if __name__ == "__main__":
    main()
