import argparse
import pathlib

from lark import Lark

from .interpreter import PrettyBirdInterpreter
from .formats import Format, BDF, SVG
from .utils import get_progressbar

from typing import Type

from progressbar import FormatLabel  # type: ignore


def get_args():
    """Parse command line arguments

    Returns:
        argparse.Namespace: Parsed arguments object
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file", help=".pbd file to compile", type=str)
    parser.add_argument(
        "--bitmap",
        "-b",
        default=False,
        action="store_true",
        help="Will render a bitmap font onto an SVG or TTF font",
    )
    parser.add_argument(
        "--format",
        "-f",
        default="TTF",
        help="Format to convert to. Supported: [BDF, SVG, TTF]",
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
        help="Print compiled glyph IR to stdout",
    )

    return parser.parse_args()


def get_format(format_name: str) -> Type[Format]:
    format_name = format_name.upper()
    if format_name == "BDF":
        return BDF
    elif format_name == "SVG":
        return SVG
    elif format_name == "TTF":
        return SVG
    raise NotImplementedError(f"Font format {format_name} is not supported")


def main():
    # Get command-line arguments
    args = get_args()

    if args.font_name is None:
        args.font_name = pathlib.Path(args.input_file).stem
    args.format = args.format.lower()

    if not args.bitmap and args.format == "bdf":
        raise RuntimeError(
            "The '--bitmap' option must be used to render BDF files")

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

    if args.bitmap:
        pbar, widgets = get_progressbar(len(interpreter.symbols.values()))
        pbar.start()
        for i, symbol in enumerate(interpreter.symbols.values()):
            widgets[0] = FormatLabel("Symbol: {0}".format(symbol.identifier))
            pbar.update(i)
            symbol.compile()
            if args.stdout:
                print(symbol)
        pbar.finish()

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
    font.add_symbols(list(interpreter.symbols.values()))
    font.compile(to_ttf=args.format == "ttf", bitmap=args.bitmap)


if __name__ == "__main__":
    main()
