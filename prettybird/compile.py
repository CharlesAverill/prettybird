from lark import Transformer

class PrettyBirdTransformer(Transformer):
    def __init__(self):
        self.characters_dict = {}
        self.current_character = None
    
    def character(self, ident):
        print(ident)
        if(self.characters_dict[ident]):
            raise NameError(f"Identifier \"{ident}\" already exists")
        
        self.characters_dict[ident] = ""

def compile_token(token):
    print(token.type)

def compile_tree(node):
    print(node.data)
    for child in node.children:
        compile_token(child)

def compile(AST):
    for node in AST.children:
        compile_tree(node)
