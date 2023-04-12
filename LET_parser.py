import ply.yacc as yacc
# Get the token map from the lexer.  This is required.
from LET_lexer import tokens, reserved
from LET_ast_node import *

def p_application(p):
    "expr : '(' expr_list ')'"
    p[0] = App_Exp(p[2][0], tuple(p[2][1:]))

def p_expr_list(p):
    '''expr_list : expr
                 | expr expr_list'''
    p[0] = [p[1]]
    if len(p) > 2:
        p[0] += p[2]

def p_proc(p):
    "expr : PROC '(' params_opt ')' expr"
    p[0] = Proc_Exp(p[3],p[5])

def p_params_opt(p):
    '''params_opt : 
            | params'''
    p[0] = []
    if len(p) > 1:
        p[0] = p[1]
    
def p_params(p):
    '''params : ID
              | ID ',' params'''
    p[0] = [p[1]]
    if len(p) > 2:
        p[0] += p[3]
    
def p_number(p):
    "expr : NUMBER"
    p[0] = Const_Exp(p[1])

def p_var(p):
    "expr : ID"
    p[0] =  Var_Exp(p[1])

def p_null(p):
    "expr : NULL"
    p[0] = Const_Exp(NULL())

def p_unary_exp(p):
    """
    expr : ZERO_TEST '(' expr ')'
         | MINUS '(' expr ')'
         | CAR '(' expr ')'
         | CDR '(' expr ')'
    """
    from operator import sub
    corspd = {
        'ZERO_TEST': Zero_Test_Exp,
        'MINUS' : lambda exp : Primitive_Exp(sub,(Const_Exp(0),exp)),
        'CAR' : lambda exp : Primitive_Exp(lambda t: t.car,(exp,)),
        'CDR' : lambda exp : Primitive_Exp(lambda t: t.cdr,(exp,)),
    }
    p[0] =  corspd[reserved[p[1]]](p[3])

def p_bi_exp(p):
    """expr : '-' '(' expr ',' expr ')'
            | '+' '(' expr ',' expr ')'
            | '*' '(' expr ',' expr ')'
            | '/' '(' expr ',' expr ')'
            | GREATER_TEST '(' expr ',' expr ')'
            | LESS_TEST '(' expr ',' expr ')'
            | EQUAL_TEST '(' expr ',' expr ')'
            | CONS '(' expr ',' expr ')' 
            | '-' expr
        """
    from operator import add,sub,mul,truediv,gt,lt,eq,mod
    match tuple(p): 
        case (None, op,'(',left ,',' ,right,')'):
            # if op == '-':
            #     p[0] = Diff_Exp(left,right)
            #     return
            corspd = {'-': sub,
                      '+': add,
                      '*': mul,
                      '/': truediv,
                      'GREATER_TEST':gt,
                      'LESS_TEST':lt,
                      'EQUAL_TEST': eq,
                      'CONS': lambda x,y: Pair(x,y),}
            op = reserved.get(op, op)
            p[0] =  Primitive_Exp(corspd[op], (left,right))
        case (None, '-', expr): # as derived form
            p[0] = Diff_Exp(Const_Exp(0), expr)
            # p[0] = Primitive_Exp(sub,(Const_Exp(0), expr))

def p_list_exp(p):
    """
    expr : LIST '(' list_opt ')'
    """
    exps = p[3]
    p[0] = List(exps)

def p_list_opt(p):
    '''list_opt : 
              | list_vals'''
    p[0] = []
    if len(p) > 1:
        p[0] = p[1]
        
def p_list_vals(p):
    ''' list_vals : expr
                | expr ',' list_vals'''
    p[0] = [p[1]]
    if len(p) > 2:
        p[0] += p[3]

def p_branch(p):
    'expr : IF expr THEN expr ELSE expr'
    p[0] =  Branch(p[2],p[4],p[6])

def p_unpack_exp(p):
    "expr : UNPACK vars '=' expr IN expr"
    p[0],_unpack,vars,_assign,list_expr,_in,expr = p

    p[0] =  Unpack_Exp(vars,list_expr,expr)

def p_unpack_vars(p):
    '''vars : ID
              | ID vars'''
    p[0] = [p[1]]
    if len(p) > 2:
        p[0] += p[2]

def p_sequence(p):
    """\
    expr : BEGIN expr_seq"""
    begin,expr_seq = p[1:]
    p[0] = Sequence(expr_seq)

def p_expr_seq(p):
    """\
    expr_seq : expr END
            | expr ';' expr_seq
            """
    match tuple(p)[1:]:
        case (expr,';',exprs):
            p[0] = (expr,) + exprs
        case (expr,_):
            p[0] = (expr,)
    
def p_let_exp(p):
    "expr : LET let_pairs IN expr"
    p[0],_,pairs,_,expr = p
    vars = tuple(map(lambda t:t[0], pairs))
    vals = tuple(map(lambda t:t[1], pairs))
    p[0] =  Let_Exp(vars,vals,expr)

def p_let_pairs(p):
    """
    let_pairs : let_pair
                | let_pair let_pairs"""
    match tuple(p):
        case (None,let_pair,let_pairs):
            p[0] = (let_pair,) + let_pairs
        case (None,let_pair):
            p[0] = (let_pair,)

def p_let_pair(p):
    """let_pair : ID '=' expr """
    p[0] = (p[1],p[3])

def p_let_star_exp(p):
    "expr : LET_STAR let_pairs IN expr"
    p[0],_,pairs,_,expr = p
    vars = tuple(map(lambda t:t[0], pairs))
    vals = tuple(map(lambda t:t[1], pairs))
    p[0] =  Let_Star_Exp(vars,vals,expr)

''' Another Way
def p_let_star_expand(p):
    """ 
    let_star_expand : let_pair IN expr
                 | let_pair let_star_expand
    """
    match tuple(p):
        case (None, let_pair, IN, expr):
            p[0] =  Let_Exp((let_pair[0],),(let_pair[1],),expr)
        case (None, let_pair, let_pairs):
            p[0] = Let_Exp((let_pair[0],),(let_pair[1],),let_pairs) 
'''       
def p_letrec_exp(p):
    "expr : LETREC letrec_pairs IN expr"
    let_pairs = p[2]
    vars = tuple(map(lambda t: t[0], let_pairs))
    paramss = tuple(map(lambda t: t[1], let_pairs))
    exprs = tuple(map(lambda t: t[2], let_pairs))

    p[0] = Rec_Proc(vars,paramss,exprs, p[4])

def p_letrec_pairs(p):
    """
    letrec_pairs : letrec_pair
                | letrec_pair letrec_pairs"""
    p[0] = [p[1]]
    if len(p) > 2:
        p[0] += p[2]

def p_letrec_pair(p):
    "letrec_pair : ID '(' params_opt ')' '=' expr"
    p[0] = (p[1],p[3],p[6])

def p_cond_exp(p):
    "expr : COND cond_clauses END"
    p[0] = p[2]
    if not isinstance(p[2][-1],Clause):
        p[0] = Conditional(p[2][0:-1],p[2][-1])
    else:
        p[0] = Conditional(p[2],None)

def p_clauses_expand(p):
    """cond_clauses : cond_clause
                    | cond_clause ELSE expr
                    | cond_clause cond_clauses"""
    match tuple(p):
        case (None,cond_clause, cond_clauses):
            p[0] = (cond_clause,) + cond_clauses
        case (None, cond_clause, 'else', expr):
            p[0] = (cond_clause, expr)
        case (None,cond_clause):
            p[0] = (cond_clause,)

def p_clause_exp(p):
    "cond_clause : expr RIGHTARROW expr"
    p[0] = Clause(p[1],p[3])

def p_memory_exp(p):
    """\
    expr : NEWREF '(' expr ')'
        | DEREF '(' expr ')'
        | SET '(' expr ',' expr ')'
    """
    p[1] = reserved[p[1]]
    match tuple(p)[1:]:
        case ('SET','(', loc, ',', expr,')'):
            p[0] = SetRef(loc,expr)
        case ('DEREF', '(',expr,')'):
            p[0] = DeRef(expr)
        case ('NEWREF', '(',expr,')'):
            p[0] = NewRef(expr)

# Error rule for syntax errors
def p_error(p):
    print(p)
    print("Syntax error in input!")

# Build the parser to make parser.parse available
parser = yacc.yacc()

if __name__ == '__main__':
    while True:
        try:
            s = input('LET > ')
        except EOFError:
            break
        if not s: continue
        result = parser.parse(s)
        print(result)