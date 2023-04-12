import typing
from dataclasses import dataclass
def draw_obj(obj):
    from itertools import count
    from graphviz import Digraph
    def id_ctor():
        id = count()
        while True: yield str(next(id))
    id_ctor = id_ctor()
    g = Digraph(node_attr={'shape': 'rectangle'})
    def recur(node:object, parent_id:str, edging = lambda x : x):
        # object initialized by __init__; native python object don't has
        is_python_native = lambda t : '__dict__' not in t.__dir__()
        if not is_python_native(node):
            parent = node.__class__.__name__
            new_id = next(id_ctor)
            g.node(new_id, parent)
            edging(new_id)
            for field, val in node.__dict__.items():
                recur(val, new_id, lambda id: g.edge(new_id, id, field))
        elif type(node) in [tuple, list, set]:
            for n in node: recur(n, parent_id, edging)                
        elif is_python_native(node): 
            new_id = next(id_ctor)
            g.node(new_id, str(node))
            edging(new_id)
        else:
            raise Exception("Unknown object type", type(node), node)
    recur(obj, None)
    return g

@dataclass
class Atom:
    val:typing.Any

def tokenize(chars: str) -> list:
    "Convert a string of characters into a list of tokens."
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program: str):
    "Read a Scheme expression from a string."
    def read_from_tokens(tokens: list):
        "Read an expression from a sequence of tokens."
        if len(tokens) == 0:
            raise SyntaxError('unexpected EOF')
        token = tokens.pop(0)
        if token == '(':
            L = ()
            while tokens[0] != ')':
                L += (read_from_tokens(tokens),)
            tokens.pop(0) # pop off ')'
            return L
        elif token == ')':
            raise SyntaxError('unexpected )')
        else:
            return atomize(token)
    return read_from_tokens(tokenize(program))

def atomize(token: str):
    if token.isnumeric():
        return Atom(float(token))
    elif token[0] == '"':
        if token[-1] == '"':
            return Atom(token[1:-1])
        raise Exception(f'Unterminated string {token}')
    else:
        return token
