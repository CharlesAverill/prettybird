from lark.lexer import Token
from lark.tree import Tree
from lark.visitors import Interpreter

from .symbol import Symbol
from .function import Function
from .utils.string_utils import get_empty_grid


class PrettyBirdInterpreter(Interpreter):
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
        if type(declaration_tree.children[1]) == Token and declaration_tree.children[1].type == "INT":
            encoding_value = declaration_tree.children[1]
        if encoding_value is None:
            encoding_value = ord(identifier_name)

        # Check if character has already been defined
        if identifier_name in self.symbols:
            raise NameError(f'Identifier "{identifier_name}" already exists')

        self.symbols[identifier_name] = Symbol(
            identifier_name, encoding_value)

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
            "from_char", [self.get_symbol(from_identifier)])

    def function_definition(self, function_def_tree):
        function_name = function_def_tree.children[0].value
        function_parameter_names = self.visit(function_def_tree.children[1])

        self.current_symbol = None
        self.current_function = Function(
            function_name, function_parameter_names, function_def_tree.children[2])
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
                if child.data != "function_call_step":
                    self.prepare_instruction(
                        update_mode, fill_mode is not None)
                self.visit(child)
            else:
                raise TypeError(
                    f"Unexpected type {type(child)} in step_statement")

    def _get_point(self, point_tree_or_token):
        if type(point_tree_or_token) == Tree:
            return (self._get_num(point_tree_or_token.children[0]), self._get_num(point_tree_or_token.children[1]))
        else:
            return str(point_tree_or_token)

    def _get_num(self, num_token):
        if num_token.type == "CNAME":
            return str(num_token)
        else:
            return int(num_token.value)

    def point_step(self, point_tree):
        self.add_instruction(
            "point", [self._get_point(point_tree.children[0])])

    def vector_step(self, vector_tree):
        first_point = self._get_point(vector_tree.children[0])
        second_point = self._get_point(vector_tree.children[1])
        self.add_instruction(
            "vector", [first_point, second_point])

    def circle_step(self, circle_tree):
        center = self._get_point(circle_tree.children[0])
        radius = self._get_num(circle_tree.children[1])
        self.add_instruction("circle", [center, radius])

    def ellipse_step(self, ellipse_tree):
        p1, p2 = None, None
        if type(ellipse_tree.children[1]) == Token:
            center = self._get_point(ellipse_tree.children[0])
            width = self._get_num(ellipse_tree.children[1])
            height = self._get_num(ellipse_tree.children[2])
            p1 = (center[0] - int(width / 2), center[1] - int(height / 2))
            p2 = (center[0] + int(width / 2), center[1] + int(height / 2))
        else:
            p1 = self._get_point(ellipse_tree.children[0])
            p2 = self._get_point(ellipse_tree.children[1])
        self.add_instruction("ellipse", [p1, p2])

    def function_call_step(self, function_call_tree):
        function_name = function_call_tree.children[0].value
        if function_name not in self.functions:
            raise NameError(f"Undeclared function \"{function_name}\"")
        function_parameters = self.function_call_parameters(
            function_call_tree.children[1])
        self.prepare_instruction(False, False)
        self.add_instruction("function_call", [self.functions[function_name], function_parameters])

    def function_call_parameters(self, function_params_tree):
        if type(function_params_tree) == Token:
            return [function_params_tree.value]
        if not len(function_params_tree.children):
            return []
        out = [self.type(function_params_tree.children[0])]
        if len(function_params_tree.children) > 1:
            out += self.visit(function_params_tree.children[1])
        return out

    def type(self, type_tree_or_token):
        if (type(type_tree_or_token) == Tree):
            return self._get_point(type_tree_or_token)
        else:
            if type_tree_or_token.type == "CNAME":
                return type_tree_or_token.value
            return int(type_tree_or_token.value)
