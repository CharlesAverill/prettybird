import pathlib

from lark import Lark
from prettybird.interpreter import PrettyBirdInterpreter

def test_recursion():
    parser = Lark(open(pathlib.Path(__file__).parents[1] /
                       "prettybird" / "grammar.lark", encoding="utf-8"))
    interpreter = PrettyBirdInterpreter()
    input_pbd = r"""
define draw_square_spiral(start_point, length, iterations, x_dir, y_dir) {
    stop if iterations <= 0
    stop if length <= 0
    draw vector(start_point, 
                start_point + (x_dir * length * (iterations % 2),
                               y_dir * length * ((iterations - 1) % 2))
    )
    draw_square_spiral(
        start_point + (x_dir * length * (iterations % 2),
                        y_dir * length * ((iterations - 1) % 2)),
        length - 1,
        iterations - 1,
        x_dir * (1 - (2 * (iterations % 2))),
        y_dir * (1 - (2 * ((iterations - 1) % 2)))
    )
}

define draw_steps(start_point, iterations) {
    stop if iterations <= 0
    draw vector(start_point, start_point + (5, 0))
    draw vector(start_point + (5, 0), start_point + (5, 5))
    draw_steps(start_point + (5, 5), iterations - 1)
}

char a {
    base {
        blank(15, 15)
    }

    steps {
        draw_square_spiral((1, 1), 13, 13, 1, 1)
    }
}

char b {
    base {
        blank(15, 15)
    }

    steps {
        draw_steps((1, 1), 13)
    }
}
    """
    parse_tree = parser.parse(input_pbd)
    interpreter.visit(parse_tree)
    expected = """...............
.00000000000000
..............0
...0000000000.0
...0........0.0
...0.000000.0.0
...0.0....0.0.0
...0.0.00.0.0.0
...0.0.0..0.0.0
...0.0.0000.0.0
...0.0......0.0
...0.00000000.0
...0..........0
...000000000000
...............
...............
.000000........
......0........
......0........
......0........
......0........
......000000...
...........0...
...........0...
...........0...
...........0...
...........0000
...............
...............
..............."""
    compiled_symbols = []
    for symbol in interpreter.symbols.values():
        symbol.compile()
        compiled_symbols.append(str(symbol))
        print(str(symbol))
    achieved = "\n".join(compiled_symbols)
    assert expected == achieved
