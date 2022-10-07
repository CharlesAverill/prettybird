from lark.lexer import Token
from lark.tree import Tree
from lark.visitors import Interpreter

from .symbol import Symbol
from .utils.string_utils import get_empty_grid


class PrettyBirdInterpreter(Interpreter):
    def __init__(self):
        """Initialize the Interpreter
        """
        self.symbols_dict = {}
        self.current_symbol = None

    def setup_character_declaration(self):
        """Initialize values for character declaration statements
        """
        self.current_symbol = None
    
    def get_symbol(self, identifier, raise_error=True):
        """Gets a symbol from self.symbols_dict and does error checking

        Args:
            identifier (str): Identifier of Symbol to retrieve
            raise_error (bool, optional): If True, raise an error if the identifier has not been defined. Defaults to True.

        Raises:
            KeyError: If raise_error and identifier has not been defined

        Returns:
            Symbol: None if not raise_error and identifier has not been defined, otherwise the Symbol being searched for
        """
        if identifier not in self.symbols_dict:
            if raise_error:
                raise KeyError(f"Symbol \"{identifier}\" not defined")
            else:
                return None
        return self.symbols_dict[identifier]

    def character_declaration(self, declaration_tree):
        """Process character declaration

        Args:
            declaration_tree (lark.tree.Tree): Tree containing character_declaration information

        Raises:
            NameError: If the character has already been defined
        """
        self.setup_character_declaration()

        identifier_token = declaration_tree.children[0]
        identifier_name = identifier_token.value

        # Check if character has already been defined
        if (identifier_name in self.symbols_dict):
            raise NameError(f"Identifier \"{identifier_name}\" already exists")

        self.symbols_dict[identifier_name] = Symbol(identifier_name)

        self.current_symbol = self.symbols_dict[identifier_name]

        self.visit_children(declaration_tree)

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
                f"Character \"{self.current_symbol}\" already defined a base")

        width_token = blank_tree.children[0]
        height_token = blank_tree.children[1]

        self.current_symbol.grid = get_empty_grid(
            int(width_token.value), int(height_token.value))

    def constant_base_statement(self, constant_tree):
        """Set a character's base to a pre-set value

        Args:
            constant_tree (lark.tree.Tree): Tree containing the pre-set grid information

        Raises:
            TypeError: If the parse tree contains an object that is neither a Token nor a Tree
        """
        for constant_base_statement_character in constant_tree.children:
            if type(constant_base_statement_character) == Token:
                self.current_symbol.append_to_grid(constant_base_statement_character.value)
            elif type(constant_base_statement_character) == Tree:
                self.current_symbol.append_to_grid("\n")
                self.constant_base_statement(constant_base_statement_character)
            else:
                raise TypeError(f"Unexpected type {type(constant_base_statement_character)} in constant_base_statement")
    
    def from_character_base_statement(self, character_base_tree):
        """Set a character's base to another character's computed value

        Args:
            character_base_tree (_type_): _description_
        """
        from_identifier = character_base_tree.children[0].value
        self.current_symbol.grid = self.get_symbol(from_identifier).grid
