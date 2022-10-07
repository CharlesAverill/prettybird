from lark.visitors import Interpreter

class PrettyBirdInterpreter(Interpreter):
    def __init__(self):
        """Initialize the Interpreter
        """
        self.characters_dict = {}
        self.current_character = None
    
    def character_declaration(self, ident):
        """Process character declaration

        Args:
            ident (lark.tree.Tree): Tree containing information regarding character declaration

        Raises:
            NameError: If the character has already been defined
        """
        identifier_token = ident.children[0]
        identifier_name = identifier_token.value

        if(identifier_name in self.characters_dict):
            raise NameError(f"Identifier \"{identifier_name}\" already exists")
        
        self.characters_dict[identifier_name] = ""

        print(f"Declared character {identifier_name}")
