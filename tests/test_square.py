import pathlib

from lark import Lark
from prettybird.interpreter import PrettyBirdInterpreter

parser = Lark(open(pathlib.Path(__file__).parent /
              "../prettybird/grammar.lark", encoding="utf-8"))
interpreter = PrettyBirdInterpreter()


def test_square():
    input_pbd = r"""
char square {
    base {
        blank(8, 8)
    }

    steps {
        draw square((0, 0), 8)
    }
}
"""

    parse_tree = parser.parse(input_pbd)
    interpreter.visit(parse_tree)
    expected = """00000000
0......0
0......0
0......0
0......0
0......0
0......0
0000000000"""
    compiled_symbols = []
    for symbol in interpreter.symbols_dict.values():
        symbol.compile()
        compiled_symbols.append(str(symbol))
        print(str(symbol))
    achieved = "".join(compiled_symbols)
    assert expected == achieved
