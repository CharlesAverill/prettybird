import pathlib

from lark import Lark
from prettybird.interpreter import PrettyBirdInterpreter

parser = Lark(open(pathlib.Path(__file__).parent /
              "../prettybird/grammar.lark", encoding="utf-8"))
interpreter = PrettyBirdInterpreter()


def test_circle():
    input_pbd = r"""
char o {
    base {
        ........,
        ........,
        ........,
        ........,
        ........,
        ........
    }

    steps {
        draw filled circle ((3, 3), 2)
    }
}
    """
    parse_tree = parser.parse(input_pbd)
    interpreter.visit(parse_tree)
    expected = """........
..000...
.00000..
.00000..
.00000..
..000..."""
    compiled_symbols = []
    for symbol in interpreter.symbols_dict.values():
        symbol.compile()
        compiled_symbols.append(str(symbol))
        print(str(symbol))
    achieved = "".join(compiled_symbols)
    assert expected == achieved
