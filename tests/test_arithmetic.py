import pathlib

from lark import Lark
from prettybird.interpreter import PrettyBirdInterpreter

def test_num_num():
    parser = Lark(open(pathlib.Path(__file__).parents[1] /
                       "prettybird" / "grammar.lark", encoding="utf-8"))
    interpreter = PrettyBirdInterpreter()
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
        draw filled circle ((3, 3), (1 + 1) * 2 - 2)
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
    for symbol in interpreter.symbols.values():
        symbol.compile()
        compiled_symbols.append(str(symbol))
        print(str(symbol))
    achieved = "".join(compiled_symbols)
    assert expected == achieved


def test_num_point():
    parser = Lark(open(pathlib.Path(__file__).parents[1] /
                       "prettybird" / "grammar.lark", encoding="utf-8"))
    interpreter = PrettyBirdInterpreter()
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
        draw filled circle (2 + (1, 1), (1 + 1) * 2 - 2)
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
    for symbol in interpreter.symbols.values():
        symbol.compile()
        compiled_symbols.append(str(symbol))
        print(str(symbol))
    achieved = "".join(compiled_symbols)
    assert expected == achieved
