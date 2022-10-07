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
        if(identifier_name in self.symbols_dict):
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
            raise SyntaxError(f"Character \"{self.current_symbol}\" already defined a base")
        
        width_token = blank_tree.children[0]
        height_token = blank_tree.children[1]

        self.current_symbol.grid =  get_empty_grid(int(width_token.value), int(height_token.value))
