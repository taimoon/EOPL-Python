# from self_repr_ import Self_Repr
from list_parser import *
@dataclass
class Var_Exp:
    var:str

@dataclass
class Lambda:
    bound_var: typing.Any
    body: typing.Any
            
@dataclass
class App_Exp:
    rator:typing.Any
    rand:typing.Any

def parse_lambda_lang(prog:str):
    'https://peps.python.org/pep-0636/'
    prog = parse(prog)
    def recur(prog):
        match prog:
            case x if isinstance(x,Atom):
                return x
            case x if isinstance(x,str):
                return Var_Exp(x)
            case ('lambda', params, body):
                return Lambda(params, recur(body))
            case (op, *args):
                return App_Exp(recur(op), tuple(map(recur, args)))
            case _:
                raise Exception('Unknown Lambda expr', prog)
    return recur(prog)

def occur_free(var, expr):
    if isinstance(expr, Var_Exp):
        return var == expr.var
    elif isinstance(expr, Lambda):
        return all(map(lambda v: v != var, expr.bound_var)) and occur_free(var, expr.body)
    elif isinstance(expr,App_Exp):
        return occur_free(var, expr.rator) or any(map(lambda rand: occur_free(var, rand), expr.rand))
    else:
        raise Exception("Uknown lambda type", expr)

def unparse(ast):
    if isinstance(ast, Lambda):
        return f'(lambda ({" ".join(map(unparse, ast.bound_var))}) {unparse(ast.body)})'
    elif isinstance(ast, Var_Exp):
        return ast.var
    elif isinstance(ast, App_Exp):
        return f'({unparse(ast.rator)} {" ".join(map(unparse, ast.rand))})'
    else:
        return ast
    

prog = '(lambda (x y) (z x y))'
prog = parse_lambda_lang(prog)
assert(occur_free('x', prog) is False)
assert(occur_free('y', prog) is False)
assert(occur_free('z', prog) is True)


prog = '(lambda (x) (f (f x)))'
prog = parse_lambda_lang(prog)
assert(occur_free('f', prog) is True)
assert(occur_free('x', prog) is False)
# draw_obj(prog).view('temp2', cleanup=True)

prog = parse_lambda_lang('((lambda (a) (a b)) c)')
# draw_obj(prog).view('temp1', cleanup=True)

prog = '''(lambda (x) (lambda (y) ((lambda (x) (x y)) x)))'''
prog = parse_lambda_lang(prog)
assert(prog == parse_lambda_lang(unparse(prog)))
assert(occur_free('x', prog) is False)
assert(occur_free('y', prog) is False)
# draw_obj(prog).view('temp2', cleanup=True)