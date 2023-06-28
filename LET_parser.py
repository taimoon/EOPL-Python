# import ply.yacc as yacc
import ply.yacc as yacc
# Get the token map from the lexer.  This is required.
from LET_lexer import tokens, reserved
from LET_ast_node import *

def p_application(p):
    "expr : '(' expr_list ')'"
    expr_list = p[2]
    p[0] = App_Exp(expr_list[0],expr_list[1:])

def p_expr_list(p):
    '''expr_list : expr
                 | expr expr_list'''
    p[0] = (p[1],)
    if len(p) > 2:
        p[0] += p[2]

def p_proc(p):
    "expr : PROC '(' params_opt ')' expr"
    params = p[3]
    if len(params[0]) > 1 and\
        isinstance(params[0][1], Int_Type|Bool_Type|Proc_Type):
        types = tuple(map(lambda p: p[1], params))
        params = tuple(map(lambda p: p[0], params))
        p[0] = Proc_Exp(params,p[5],types)
    else:
        p[0] = Proc_Exp(p[3],p[5])

def p_params_opt(p):
    '''params_opt : 
            | typed_params
            | params'''
    p[0] = tuple()
    if len(p) > 1:
        p[0] = p[1]

def p_typed_params(p):
    '''typed_params : ID ':' type
        | ID ':' type ',' typed_params '''
    p[0] = ((p[1],p[3]),)
    if len(p[1:]) > 3:
        p[0] += p[5]

  
def p_params(p):
    '''params : ID
              | ID ',' params'''
    p[0] = (p[1],)
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

def p_neg_exp(p):
    """expr : '-' '(' expr ',' expr ')'
            | '-' expr"""
    match tuple(p[1:]): 
        case (op,'(',left ,',' ,right,')'):
            p[0] = Diff_Exp(left,right)
        case (op, expr):
            p[0] = Diff_Exp(Const_Exp(0), expr)

def p_primitive_exp(p):
    """expr : unary_op '(' expr ')'
            | bi_op '(' expr ',' expr ')'
            | LIST '(' list_opt ')'"""
    match tuple(p[1:]):
        case (op,'(',left ,',' ,right,')'):
            assert(isinstance(op,Bi_Op))
            p[0] = Primitive_Exp(op.op,(left,right))
        case (op,'(', expr ,')'):
            if isinstance(op,Unary_Op):
                p[0] = Primitive_Exp(op.op,(expr,))
            else:
                p[0] = Primitive_Exp(op,expr)

def p_unary_op(p):
    """unary_op : ZERO_TEST
                | MINUS
                | CAR
                | CDR
                | PRINT"""
    p[0] = Unary_Op(p[1])

def p_bi_op(p):
    """bi_op : '+'
             | '*'
             | '/'
             | GREATER_TEST
             | LESS_TEST
             | EQUAL_TEST
             | CONS
             | SETCAR
             | SETCDR"""
    p[0] = Bi_Op(p[1])

def p_list_opt(p):
    '''list_opt : 
              | list_vals'''
    p[0] = tuple()
    if len(p) > 1:
        p[0] = p[1]
        
def p_list_vals(p):
    '''list_vals : expr
                 | expr ',' list_vals'''
    p[0] = (p[1],)
    if len(p) > 2:
        p[0] += p[3]

def p_branch(p):
    'expr : IF expr THEN expr ELSE expr'
    p[0] =  Branch(p[2],p[4],p[6])

def p_unpack_exp(p):
    """expr : UNPACK vars '=' expr IN expr
            | UNPACK '(' expr ')'
            """
    match tuple(p):
        case (None,UNPACK,vars,'=',list_expr,_,expr):
            p[0] =  Unpack_Exp(vars,list_expr,expr)
        case (None,UNPACK,'(',expr,')'):
            p[0] = Unpack_Exp(None,expr,None)

def p_unpack_vars(p):
    '''vars : ID
            | ID vars'''
    p[0] = (p[1],)
    if len(p) > 2:
        p[0] += p[2]

def p_sequence(p):
    """expr : BEGIN expr_seq"""
    begin,expr_seq = p[1:]
    p[0] = Sequence(expr_seq)

def p_expr_seq(p):
    """expr_seq : expr END
                | expr ';' expr_seq
    """
    match tuple(p)[1:]:
        case (expr,';',exprs):
            p[0] = (expr,) + exprs
        case (expr,_):
            p[0] = (expr,)
    
def p_let_exp(p):
    """expr : LET let_pairs IN expr
            | LETMUT let_pairs IN expr
            | LET_STAR let_pairs IN expr"""
    let_token,pairs,_,expr = p[1:]
    vars = tuple(map(lambda t:t[0], pairs))
    vals = tuple(map(lambda t:t[1], pairs))
    if reserved[let_token] == 'LET':
        p[0] =  Let_Exp(vars,vals,expr)
    elif reserved[let_token] == 'LET_STAR':
        p[0] =  Let_Star_Exp(vars,vals,expr)
    else:
        p[0] =  Letmutable_Exp(vars,vals,expr)

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

def p_letrec_exp(p):
    "expr : LETREC letrec_pairs IN expr"
    let_pairs = p[2]
    if len(let_pairs[0]) > 3:
        res_types = tuple(map(lambda t: t[0], let_pairs))
        vars = tuple(map(lambda t: t[1], let_pairs))
        paramss = tuple(map(lambda t: tuple(p[0] for p in t[2]), let_pairs))
        arg_types = tuple(map(lambda t: tuple(p[1] for p in t[2]), let_pairs))
        exprs = tuple(map(lambda t: t[3], let_pairs))
        p[0] = Rec_Proc(vars,paramss,exprs,p[4],
                        res_types=res_types,arg_types=arg_types)
    else:
        vars = tuple(map(lambda t: t[0], let_pairs))
        paramss = tuple(map(lambda t: t[1], let_pairs))
        exprs = tuple(map(lambda t: t[2], let_pairs))

        p[0] = Rec_Proc(vars,paramss,exprs, p[4])

def p_letrec_pairs(p):
    """
    letrec_pairs : letrec_pair
                | letrec_pair letrec_pairs"""
    p[0] = (p[1],)
    if len(p) > 2:
        p[0] += p[2]

def p_letrec_pair(p):
    """
    letrec_pair : ID '(' params_opt ')' '=' expr
        | type   ID '(' params_opt ')' '=' expr
    """
    match tuple(p[1:]):
        case (ID, '(',params,')','=',expr):
            p[0] = (ID,params,expr)
        case (type, ID, '(',params,')','=',expr):
            p[0] = (type,ID,params,expr)

def p_cond_exp(p):
    "expr : COND cond_clauses END"
    p[0] = p[2]
    if not isinstance(p[2][-1],Clause): # (else <<expr>>)
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
    """
    expr : REF '(' expr ')'
        | NEWREF '(' expr ')'
        | DEREF '(' expr ')'
        | SETREF '(' expr ',' expr ')'
        | SET ID '=' expr
    """
    p[1] = reserved[p[1]]
    match tuple(p)[1:]:
        case ('SET', var, '=', expr):
            p[0] = Assign_Exp(var,expr)
        case ('SETREF','(', loc, ',', expr,')'):
            p[0] = SetRef(loc,expr)
        case ('DEREF', '(',expr,')'):
            p[0] = DeRef(expr)
        case ('NEWREF', '(',expr,')'):
            p[0] = NewRef(expr)
        case ('REF', '(',expr,')'):
            p[0] = Ref(expr)

def p_type(p):
    """type : '?'
        | INT
        | BOOL
        | '(' type TYPEARROW type ')'
    """
    p[1] = reserved[p[1]] if p[1] in reserved.keys() else p[1]
    match tuple(p)[1:]:
        case ('?'):
            p[0] = No_Type()
        case ('(',arg_type,TYPEARROW,result_type,')'):
            p[0] = Proc_Type((arg_type,),result_type)
        case ('INT',):
            p[0]=Int_Type()
        case ('BOOL',):
            p[0]=Bool_Type()
        case _:
            raise Exception(str(tuple(p[1:])))
           

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