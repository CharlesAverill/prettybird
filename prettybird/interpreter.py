from lark.lexer import Token
from lark.tree import Tree
from lark.visitors import Interpreter

from .symbol import Symbol
from .function import Function
from .utils import get_empty_grid, Array


class PrettyBirdInterpreter(Interpreter):

    comparator_dict = {
        "<": lambda x, y: x < y,
        "<=": lambda x, y: x <= y,
        ">": lambda x, y: x > y,
        ">=": lambda x, y: x >= y,
        "==": lambda x, y: x == y,
        "!=": lambda x, y: x != y,
    }

    def __init__(self):
        """Initialize the Interpreter"""
        self.symbols = {}
        self.functions = {}
        self.current_symbol = None
        self.current_function = None

    def setup_character_declaration(self):
        """Initialize values for character declaration statements"""
        self.current_symbol = None

    def prepare_instruction(self, update_mode, fill_mode):
        if self.current_symbol is not None:
            self.current_symbol.prepare_instruction(update_mode, fill_mode)
        elif self.current_function is not None:
            self.current_function.prepare_instruction(update_mode, fill_mode)

    def add_instruction(self, name, data):
        if self.current_symbol is not None:
            self.current_symbol.add_instruction(name, data)
        elif self.current_function is not None:
            self.current_function.add_instruction(name, data)

    def get_symbol(self, identifier, raise_error=True):
        """Gets a symbol from self.symbols and does error checking

        Args:
            identifier (str): Identifier of Symbol to retrieve
            raise_error (bool, optional): If True, raise an error if the identifier has not been defined. Defaults to True.

        Raises:
            KeyError: If raise_error and identifier has not been defined

        Returns:
            Symbol: None if not raise_error and identifier has not been defined, otherwise the Symbol being searched for
        """
        if identifier not in self.symbols:
            if raise_error:
                raise NameError(f'Symbol "{identifier}" not defined')
            else:
                return None
        return self.symbols[identifier]

    def character(self, declaration_tree):
        """Process character declaration

        Args:
            declaration_tree (lark.tree.Tree): Tree containing character_declaration information

        Raises:
            NameError: If the character has already been defined
        """
        self.setup_character_declaration()

        identifier_token = declaration_tree.children[0]
        identifier_name = identifier_token.value

        encoding_value = None
        if (
            type(declaration_tree.children[1]) == Token
            and declaration_tree.children[1].type == "INT"
        ):
            encoding_value = declaration_tree.children[1]
        if encoding_value is None:
            encoding_value = ord(identifier_name)

        # Check if character has already been defined
        if identifier_name in self.symbols:
            raise NameError(f'Identifier "{identifier_name}" already exists')

        self.symbols[identifier_name] = Symbol(identifier_name, encoding_value)

        self.current_symbol = self.symbols[identifier_name]
        self.current_function = None

        self.visit_children(declaration_tree)

        self.current_symbol = None

    def blank_statement(self, blank_tree):
        """Set a character's base to a blank base

        Args:
            blank_tree (lark.tree.Tree): Tree containing blank_statement information

        Raises:
            SyntaxError: _description_
        """
        # Check if character's base has already been defined
        if self.current_symbol.parsed_base:
            raise SyntaxError(
                f'Character "{self.current_symbol}" already defined a base'
            )

        width_token = blank_tree.children[0]
        height_token = blank_tree.children[1]

        self.current_symbol.grid = get_empty_grid(
            int(width_token.value), int(height_token.value)
        )

    def constant_base_statement(self, constant_tree, root_call=True):
        """Set a character's base to a pre-set value

        Args:
            constant_tree (lark.tree.Tree): Tree containing the pre-set grid information
            root_call (bool): Whether or not this is the root call to this function (used to determine when the tree is not being read anymore)

        Raises:
            TypeError: If the parse tree contains an object that is neither a Token nor a Tree
        """
        for child in constant_tree.children:
            if type(child) == Token:
                self.current_symbol.append_to_grid(child.value)
            elif type(child) == Tree:
                self.current_symbol.append_to_grid("\n")
                self.constant_base_statement(child, False)
            else:
                raise TypeError(
                    f"Unexpected type {type(child)} in constant_base_statement"
                )
        if root_call:
            self.current_symbol.finish_grid()

    def from_character_base_statement(self, character_base_tree):
        """Set a character's base to another character's computed value

        Args:
            character_base_tree (lark.tree.Tree): Tree containing identifier information
        """
        from_identifier = character_base_tree.children[0].value
        self.current_symbol.prepare_instruction("draw", False)
        self.current_symbol.add_instruction(
            "from_char", [self.get_symbol(from_identifier)]
        )

    def function_definition(self, function_def_tree):
        function_name = function_def_tree.children[0].value
        function_parameter_names = self.visit(function_def_tree.children[1])

        self.current_symbol = None
        self.current_function = Function(
            function_name, function_parameter_names, function_def_tree.children[2]
        )
        self.functions[function_name] = self.current_function

        self.visit(function_def_tree.children[2])

        self.current_function = None

    def function_parameter_list(self, function_params_tree):
        return self.visit(function_params_tree.children[0])

    def function_parameters(self, function_params_tree):
        if type(function_params_tree) == Token:
            return [function_params_tree.value]
        if not len(function_params_tree.children):
            return []
        out = [function_params_tree.children[0].value]
        if len(function_params_tree.children) > 1:
            out += self.visit(function_params_tree.children[1])
        return out

    def steps_statements(self, statements_tree):
        """Parse a set of steps statements

        Args:
            statements_tree (lark.tree.Tree): Tree containing step statement informations
        """
        self.visit_children(statements_tree)

    def step_statement(self, statement_tree):
        update_mode = None
        fill_mode = None
        # half_mode = None
        for child in statement_tree.children:
            if type(child) == Token:
                if update_mode is None:
                    # Either "draw" or "erase"
                    update_mode = child.value
                elif fill_mode is None:
                    # Either "filled" or nothing
                    fill_mode = child.value
            elif type(child) == Tree:
                if child.data not in ("function_call_step", "stop_statement"):
                    self.prepare_instruction(
                        update_mode, fill_mode is not None)
                self.visit(child)
            else:
                raise TypeError(
                    f"Unexpected type {type(child)} in step_statement")

    def _get_point(self, point_tree_or_token):
        if type(point_tree_or_token) == Tree:
            if "expr" in point_tree_or_token.data:
                return self.visit(point_tree_or_token)
            if len(point_tree_or_token.children) == 2:
                return (
                    self._get_num(point_tree_or_token.children[0]),
                    self._get_num(point_tree_or_token.children[1]),
                )
            elif len(point_tree_or_token.children) == 1:
                return str(point_tree_or_token.children[0].value)
        else:
            return str(point_tree_or_token)

    def _get_num(self, num_tree):
        num_token = None
        negative = False

        if type(num_tree) == Token:
            num_token = num_tree
        else:
            if "expr" in num_tree.data:
                return self.visit(num_tree)
            num_token = Token("NUMBER", self._get_num(num_tree.children[0]))
            if type(num_token.value) == str:
                num_token = Token("CNAME", num_token.value)
            negative = num_tree.data == "negative_int"

        if num_token.type == "CNAME":
            return ("-" if negative else "") + str(num_token)
        else:
            return (-1 if negative else 1) * float(num_token.value)

    def point_step(self, point_tree):
        self.add_instruction(
            "point", [self._get_point(point_tree.children[0])])

    def vector_step(self, vector_tree):
        first_point = self._get_point(vector_tree.children[0])
        second_point = self._get_point(vector_tree.children[1])
        self.add_instruction("vector", [first_point, second_point])

    def circle_step(self, circle_tree):
        center = self._get_point(circle_tree.children[0])
        radius = self._get_num(circle_tree.children[1])
        self.add_instruction("circle", [center, radius])

    def square_step(self, square_tree):
        left_top = self._get_point(square_tree.children[0])
        side_length = self._get_num(square_tree.children[1])
        self.current_symbol.add_instruction("square", [left_top, side_length])
    
    def rectangle_step(self, rect_tree):
        left_top = self._get_point(rect_tree.children[0])
        right_bottom = self._get_point(rect_tree.children[1])
        self.current_symbol.add_instruction("rectangle", [left_top, right_bottom])

    def ellipse_step(self, ellipse_tree):
        p1, p2 = None, None
        if type(ellipse_tree.children[1]) == Token:
            center = self._get_point(ellipse_tree.children[0])
            width = self._get_num(ellipse_tree.children[1])
            height = self._get_num(ellipse_tree.children[2])
            p1 = (center[0] - width / 2, center[1] - height / 2)
            p2 = (center[0] + width / 2, center[1] + height / 2)
        else:
            p1 = self._get_point(ellipse_tree.children[0])
            p2 = self._get_point(ellipse_tree.children[1])
        self.add_instruction("ellipse", [p1, p2])

    def function_call_step(self, function_call_tree):
        function_name = function_call_tree.children[0].value
        if function_name not in self.functions:
            raise NameError(f'Undeclared function "{function_name}"')
        function_parameters = self.function_call_parameters(
            function_call_tree.children[1]
        )
        self.prepare_instruction(False, False)
        self.add_instruction(
            "function_call", [
                self.functions[function_name], function_parameters]
        )

    def function_call_parameters(self, function_params_tree):
        if type(function_params_tree) == Token:
            return [function_params_tree.value]
        if not len(function_params_tree.children):
            return []
        out = [self.type(function_params_tree.children[0])]
        if len(function_params_tree.children) > 1:
            out += self.visit(function_params_tree.children[1])
        return out

    def stop_statement(self, stop_tree):
        if len(stop_tree.children) == 0:
            self.prepare_instruction(False, False)
            self.add_instruction("stop", [])
        else:
            left = self.type(stop_tree.children[0])
            right = self.type(stop_tree.children[2])
            self.prepare_instruction(False, False)
            self.add_instruction(
                "stop", [
                    self.comparator_dict[stop_tree.children[1].value], left, right]
            )

    def _expr_simplify(self, to_simplify):
        if to_simplify.shape != () and len(to_simplify) > 1:
            return tuple(to_simplify)
        else:
            return float(to_simplify)

    def add_expr(self, add_tree):
        left = self.type(add_tree.children[0])
        right = self.type(add_tree.children[1])
        if type(left) not in (int, float, tuple) or type(right) not in (
            int,
            float,
            tuple,
        ):
            return [lambda x, y: x + y, left, right]
        out = Array(left) + Array(right)
        return self._expr_simplify(out)

    def sub_expr(self, sub_tree):
        left = self.type(sub_tree.children[0])
        right = self.type(sub_tree.children[1])
        if type(left) not in (int, float) or type(right) not in (int, float):
            return [lambda x, y: x - y, left, right]
        out = Array(left) - Array(right)
        return self._expr_simplify(out)

    def mul_expr(self, mul_tree):
        left = self.type(mul_tree.children[0])
        right = self.type(mul_tree.children[1])
        if type(left) not in (int, float) or type(right) not in (int, float):
            return [lambda x, y: x * y, left, right]
        out = Array(left) * Array(right)
        return self._expr_simplify(out)

    def div_expr(self, div_tree):
        left = self.type(div_tree.children[0])
        right = self.type(div_tree.children[1])
        if type(left) not in (int, float) or type(right) not in (int, float):
            return [lambda x, y: x / y, left, right]
        out = Array(left) / Array(right)
        return self._expr_simplify(out)

    def pow_expr(self, pow_tree):
        left = self.type(pow_tree.children[0])
        right = self.type(pow_tree.children[1])
        if type(left) not in (int, float) or type(right) not in (int, float):
            return [lambda x, y: x**y, left, right]
        out = Array(left) ** Array(right)
        return self._expr_simplify(out)

    def mod_expr(self, mod_tree):
        left = self.type(mod_tree.children[0])
        right = self.type(mod_tree.children[1])
        if type(left) not in (int, float) or type(right) not in (int, float):
            return [lambda x, y: x % y, right, left]
        out = Array(left) % Array(right)
        return self._expr_simplify(out)

    def and_expr(self, and_tree):
        left = self.type(and_tree.children[0])
        right = self.type(and_tree.children[1])
        if type(left) not in (int, float) or type(right) not in (int, float):
            return [lambda x, y: x & y, right, left]
        out = Array(left) % Array(right)
        return self._expr_simplify(out)

    def xor_expr(self, xor_tree):
        left = self.type(xor_tree.children[0])
        right = self.type(xor_tree.children[1])
        if type(left) not in (int, float) or type(right) not in (int, float):
            return [lambda x, y: x ^ y, right, left]
        out = Array(left) % Array(right)
        return self._expr_simplify(out)

    def or_expr(self, or_tree):
        left = self.type(or_tree.children[0])
        right = self.type(or_tree.children[1])
        if type(left) not in (int, float) or type(right) not in (int, float):
            return [lambda x, y: x | y, right, left]
        out = Array(left) % Array(right)
        return self._expr_simplify(out)

    def type(self, type_tree_or_token):
        if type(type_tree_or_token) == Tree:
            if "expr" in type_tree_or_token.data:
                return self.visit(type_tree_or_token)
            elif len(type_tree_or_token.children) > 1:
                return self._get_point(type_tree_or_token)
            else:
                return self.type(type_tree_or_token.children[0])
        else:
            if type(type_tree_or_token) == Token and type_tree_or_token.type == "CNAME":
                return type_tree_or_token.value
            return self._get_num(type_tree_or_token)

    # TODO: draw generalized bezier curve
    def bezier_step(self, bezier_tree):
        p0 = self._get_point(bezier_tree.children[0])
        p1 = self._get_point(bezier_tree.children[1])
        p2 = self._get_point(bezier_tree.children[2])
        self.add_instruction("bezier", [p0, p1, p2])
