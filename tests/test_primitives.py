import pathlib

from lark import Lark
from prettybird.interpreter import PrettyBirdInterpreter


def test_square():
    parser = Lark(open(pathlib.Path(__file__).parent /
                       "../prettybird/grammar.lark", encoding="utf-8"))
    interpreter = PrettyBirdInterpreter()
    input_pbd = r"""
char s {
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
00000000"""
    compiled_symbols = []
    for symbol in interpreter.symbols_dict.values():
        symbol.compile()
        compiled_symbols.append(str(symbol))
        print(str(symbol))
    achieved = "".join(compiled_symbols)
    assert expected == achieved


def test_filled_squared():
    parser = Lark(open(pathlib.Path(__file__).parent /
                       "../prettybird/grammar.lark", encoding="utf-8"))
    interpreter = PrettyBirdInterpreter()
    input_pbd = r"""
char f {
    base {
        blank(8, 8)
    }

    steps {
        draw filled square((0, 0), 8)
    }
}
"""
    parse_tree = parser.parse(input_pbd)
    interpreter.visit(parse_tree)
    expected = """00000000
00000000
00000000
00000000
00000000
00000000
00000000
00000000"""
    compiled_symbols = []
    for symbol in interpreter.symbols_dict.values():
        symbol.compile()
        compiled_symbols.append(str(symbol))
        print(str(symbol))
    achieved = "".join(compiled_symbols)
    assert expected == achieved


def test_circle():
    parser = Lark(open(pathlib.Path(__file__).parent /
                       "../prettybird/grammar.lark", encoding="utf-8"))
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


def test_vector():
    parser = Lark(open(pathlib.Path(__file__).parent /
                       "../prettybird/grammar.lark", encoding="utf-8"))
    interpreter = PrettyBirdInterpreter()
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
