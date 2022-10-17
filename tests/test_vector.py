import pathlib

from lark import Lark
from prettybird.interpreter import PrettyBirdInterpreter

parser = Lark(open(pathlib.Path(__file__).parent /
              "../prettybird/grammar.lark", encoding="utf-8"))
interpreter = PrettyBirdInterpreter()


def test_vector():
    input_pbd = r"""
char a {
    base {
        blank(8, 6)
    }

    steps {
        draw vector((5, 1), (5, 5))
        draw filled vector((2, 5), (5, 5))
    }
}
    """
    parse_tree = parser.parse(input_pbd)
    interpreter.visit(parse_tree)
    expected = """........
.....0..
.....0..
.....0..
.....0..
..0000.."""
    compiled_symbols = []
    for symbol in interpreter.symbols_dict.values():
        symbol.compile()
        compiled_symbols.append(str(symbol))
        print(str(symbol))
    achieved = "".join(compiled_symbols)
    assert expected == achieved
