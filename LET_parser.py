import ply.yacc as yacc
# Get the token map from the lexer.  This is required.
from LET_lexer import tokens, reserved
from LET_ast_node import *

def p_prog(p):
    '''
    prog : TYPE type
        | modules expr
        | expr
    '''
    match tuple(p[1:]):
        case ('type',type):
            # workaround so that it can parse type expression too
            p[0] = type
        case (modules,expr) if isinstance(modules[0],Module_Def):
            p[0] = Program(tuple(),modules,expr)
        case (x,):
            p[0] = x

def p_prog_cls(p):
    'prog : class_decls expr'
    decls,expr = p[1:]
    p[0] = Program(decls,(),expr)

# Expression
def p_application(p):
    '''
    expr : '(' expr_list ')'
    expr_list : expr
            | expr expr_list
    '''
    match tuple(p[1:]):
        case ('(',expr_list,')'):
            p[0] = App_Exp(expr_list[0],expr_list[1:])
        case (x,xs):
            p[0] = (x,) + xs
        case x:
            p[0] = x

def p_proc(p):
    '''expr : PROC '(' params_opt ')' expr'''
    match tuple(p[1:]):
        case (_,'(',(),')',expr):
            p[0] = Proc_Exp(tuple(),expr,(Void_Type(),))
        case (_,'(',params,')',expr):
            type = Int_Type|Bool_Type|Proc_Type|No_Type|Void_Type|Pair_Type|Named_Type|Qualified_Type|List_Type
            if len(params[0]) > 1 and isinstance(params[0][1], type):
                types = tuple(map(lambda p: p[1], params))
                params = tuple(map(lambda p: p[0], params))
                p[0] = Proc_Exp(params,expr,types)
            else:
                p[0] = Proc_Exp(params,expr)

def p_params_opt(p):
    '''
        typed_params : ID ':' type
            | ID ':' type ',' typed_params
        params : ID
              | ID ',' params
        params_opt : 
            | typed_params
            | params
    '''
    match tuple(p[1:]):
        case (var,':',params):
            p[0] = ((var,params),)
        case (var,':',params,',',typed_param):
            p[0] = ((var,params),) + typed_param
        case (var,',',params):
            p[0] = (var,) + params
        case (var,) if isinstance(var,str):
            p[0] = (var,)
        case ():
            p[0] = tuple()
        case (params,):
            p[0] = params
        case _:
            raise Exception()
        
def p_number(p):
    "expr : NUMBER"
    p[0] = Const_Exp(p[1])

def p_str(p):
    "expr : STRING"
    p[0] = Const_Exp(p[1])

def p_var_exp(p):
    '''expr : FROM ID TAKE ID
        | ID '.' ID
        | ID
    '''
    match tuple(p[1:]):
        case ('from',name,'take',var):
            p[0] = Qualified_Var_Exp(name,var)
        case (name,'.',var):
            p[0] = Qualified_Var_Exp(name,var)
        case (name,):
            p[0] = Var_Exp(name)

def p_null(p):
    # TODO : ambiguous grammar
    '''
        expr : NULL '(' type ')'
            | NULL
    '''
    match tuple(p[1:]):
        case (x,'(',t,')'):
            p[0] = Const_Exp(NULL(t))
        case (x,):
            p[0] = Const_Exp(NULL(No_Type()))

def p_neg_exp(p):
    # neg_exp allows different interpretation of '-' for the purpose of testing
    '''expr : '-' '(' expr ',' expr ')'
            | '-' expr'''
    match tuple(p[1:]): 
        case (op,'(',left ,',' ,right,')'):
            p[0] = Diff_Exp(left,right)
        case (op, expr):
            p[0] = Diff_Exp(Const_Exp(0), expr)

def p_pair_exp(p):
    '''
    expr : NEWPAIR '(' expr ',' expr ')'
        | UNPAIR ID ID '=' expr IN expr
    '''
    p[1] = reserved[p[1]]
    match tuple(p[1:]):
        case ('NEWPAIR','(',left,',',right,')'):
            p[0] = Pair_Exp(left,right)
        case ('UNPAIR',left,right,'=',pair_exp,'in',expr):
            p[0] = Unpair_Exp(left,right,pair_exp,expr)

def p_primitive_exp(p):
    '''
    expr : CONS '(' expr ',' expr ')'
        | LIST '(' list_opt ')'
        | NULL_TEST '(' expr ')'
        | unary_op '(' expr ')'
        | bi_op '(' expr ',' expr ')'
    '''
    match tuple(p[1:]):
        case ('cons','(',left ,',' ,right,')'):
            p[0] = Pair_Exp(left,right,True)
        case ('list','(',params,')'):
            p[0] = List(params)
        case ('null?','(',expr,')'):
            p[0] = Null_Exp(expr)
        case (op,'(',left ,',' ,right,')'):
            assert(isinstance(op,Bi_Op))
            p[0] = Primitive_Exp(op.op,(left,right))
        case (op,'(', expr ,')') if isinstance(op,Unary_Op):
            p[0] = Primitive_Exp(op.op,(expr,))
        case (op,'(', expr ,')'):
            p[0] = Primitive_Exp(op,expr)

def p_unary_op(p):
    """unary_op : ZERO_TEST
                | MINUS
                | CAR
                | CDR
                | PRINT
                | SQRT"""
    p[0] = Unary_Op(p[1])

def p_bi_op(p):
    """bi_op : '+'
             | '*'
             | '/'
             | GREATER_TEST
             | LESS_TEST
             | EQUAL_TEST
             | SETCAR
             | SETCDR"""
    p[0] = Bi_Op(p[1])

def p_list_opt(p):
    '''
        list_vals : expr
                    | expr ',' list_vals
        list_opt : 
              | list_vals
    '''
    match tuple(p[1:]):
        case (x,',',xs):
            p[0] = (x,) + xs
        case (x,) if not isinstance(x,tuple):
            p[0] = (x,)
        case ():
            p[0] = tuple()
        case (x,):
            p[0] = x

def p_branch(p):
    'expr : IF expr THEN expr ELSE expr'
    p[0] =  Branch(p[2],p[4],p[6])

def p_unpack_exp(p):
    '''
        expr : UNPACK vars '=' expr IN expr
            | UNPACK '(' expr ')'
        vars : ID
            | ID vars
    '''
    match tuple(p[1:]):
        case (UNPACK,vars,'=',list_expr,_,expr):
            p[0] =  Unpack_Exp(vars,list_expr,expr)
        case (UNPACK,'(',expr,')'):
            p[0] = Unpack_Exp(None,expr,None)
        case (name,):
            p[0] = (name,)
        case (name,names):
            p[0] = (name,) + names

def p_sequence(p):
    '''
    expr_seq : expr END
                | expr ';' expr_seq
    
    expr : BEGIN expr_seq
    '''
    match tuple(p[1:]):
        case (expr,';',expr_seq):
            p[0] = (expr,) + expr_seq
        case (expr,'end'):
            p[0] = (expr,)
        case (_,expr_seq):
            p[0] = Sequence(expr_seq)
        case _:
            raise Exception()

def p_let_exp(p):
    """
        expr : LET_HEADER IN expr
    """
    p[0]:Let_Exp|Let_Star_Exp|Letmutable_Exp = p[1]
    p[0].body = p[3]

def p_let_header(p):
    # workaround with let-blocks in modules
    """
    LET_HEADER : LET let_pairs
            | LETMUT let_pairs
            | LET_STAR let_pairs
    """
    let_token,pairs = p[1:]
    let_token = reserved[let_token]
    vars = tuple(map(lambda t:t[0], pairs))
    vals = tuple(map(lambda t:t[1], pairs))
    if let_token == 'LET':
        p[0] =  Let_Exp(vars,vals,None)
    elif let_token == 'LET_STAR':
        p[0] =  Let_Star_Exp(vars,vals,None)
    else:
        p[0] =  Letmutable_Exp(vars,vals,None)

def p_let_pairs(p):
    '''
    let_pairs : let_pair
                | let_pair let_pairs
    let_pair : ID '=' expr 
    '''
    match tuple(p[1:]):
        case (let_pair,let_pairs):
            p[0] = (let_pair,) + let_pairs
        case (let_pair,):
            p[0] = (let_pair,)
        case (var,'=',expr):
            p[0] = (var,expr)

def p_letrec_exp(p):
    "expr : LETREC_HEADER IN expr"
    p[0]:Rec_Proc = p[1]
    p[0].expr = p[3]

def p_letrec_header(p):
    # workaround with let-blocks in modules
    "LETREC_HEADER : LETREC letrec_pairs"
    let_pairs = p[2]
    if len(let_pairs[0]) > 3:
        res_types = tuple(map(lambda t: t[0], let_pairs))
        vars = tuple(map(lambda t: t[1], let_pairs))
        paramss = tuple(map(lambda t: tuple(p[0] for p in t[2]), let_pairs))
        arg_types = tuple(map(lambda t: tuple(p[1] for p in t[2]), let_pairs))
        exps = tuple(map(lambda t: t[3], let_pairs))
        p[0] = Rec_Proc(vars,paramss,exps,None,
                        res_types=res_types,arg_types=arg_types)
    else:
        vars = tuple(map(lambda t: t[0], let_pairs))
        paramss = tuple(map(lambda t: t[1], let_pairs))
        exps = tuple(map(lambda t: t[2], let_pairs))
        p[0] = Rec_Proc(vars,paramss,exps,None)

def p_letrec_pairs(p):
    '''
    letrec_pair : ID '(' params_opt ')' '=' expr
        | type   ID '(' params_opt ')' '=' expr
    
    letrec_pairs : letrec_pair
                | letrec_pair letrec_pairs
    '''
    match tuple(p[1:]):
        case (ID, '(',params,')','=',expr):
            p[0] = (ID,params,expr)
        case (type, ID, '(',params,')','=',expr):
            p[0] = (type,ID,params,expr)
        case (letrec_pair,letrec_pairs):
            p[0] = (letrec_pair,) + letrec_pairs
        case (letrec_pair,):
            p[0] = (letrec_pair,)

def p_cond_exp(p):
    '''
    expr : COND cond_clauses END
    cond_clauses : cond_clause
            | cond_clause ELSE expr
            | cond_clause cond_clauses
    cond_clause : expr RIGHTARROW expr
    '''
    match tuple(p[1:]):
        case ('cond',(*cond_clauses,else_clause),'end') if not isinstance(else_clause, Clause):
            p[0] = Conditional(tuple(cond_clauses),else_clause)
        case ('cond',cond_clauses,'end'):
            p[0] = Conditional(cond_clauses,None)
        case (cond_clause, cond_clauses):
            p[0] = (cond_clause,) + cond_clauses
        case (cond_clause, 'else', expr):
            p[0] = (cond_clause, expr)
        case (cond_clause,):
            p[0] = (cond_clause,)
        case (pred,'=>',conseq):
            p[0] = Clause(pred,conseq)
        case _ :
            print(tuple(p[1:]))
            raise Exception()

# Memory
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

# Exception Handling
def p_exception_exp(p):
    '''
    expr : TRY expr CATCH '(' ID ')' expr
        | RAISE expr
    '''
    match tuple(p)[1:]:
        case ('try',exp,'catch','(',var,')',handler):
            p[0] = Try_Exp(exp,var,handler)
        case ('raise',exp):
            p[0] = Raise_Exp(exp)
        case _:
            raise NotImplementedError(tuple(p)[1:])

# Type
def p_type(p):
    '''
    type : '?'
        | VOID
        | INT
        | BOOL
        | PAIROF type '*' type
        | LISTOF type
        | '(' multi_arg_type TYPEARROW type ')'
    
    multi_arg_type : type
        | type '*' multi_arg_type
    '''
    from typing import Hashable
    p[1] = reserved[p[1]] if isinstance(p[1],Hashable) and p[1] in reserved.keys() else p[1]
    match tuple(p)[1:]:
        case ('?',):
            p[0] = No_Type()
        case ('VOID',):
            p[0] = Void_Type()
        case ('INT',):
            p[0]= Int_Type()
        case ('BOOL',):
            p[0]= Bool_Type()
        case ('PAIROF', t1,'*',t2):
            p[0] = Pair_Type(t1,t2)
        case ('LISTOF', t):
            p[0] = List_Type(t)
        case ('(',arg_type,TYPEARROW,result_type,')'):
            p[0] = Proc_Type(arg_type,result_type)
        case(type,'*',types):
            p[0] = (type,) + types
        case (type,):
            p[0] = (type,)
        case _:
            raise Exception(str(tuple(p[1:])))


def p_var_type_exp(p):
    '''
    type : FROM ID TAKE ID
        | ID '.' ID
        | ID
    '''
    match tuple(p)[1:]:
        case ('from',module_name,'take',type_name):
            p[0] = Qualified_Type(module_name,type_name)
        case (module_name,'.',type_name):
            p[0] = Qualified_Type(module_name,type_name)
        case (type_name,):
            p[0] = Named_Type(type_name)
        case _:
            raise Exception(str(tuple(p)[1:]))


# Modules
def p_module_def(p):
    '''
    module :  MODULE ID INTERFACE interface BODY module_body
        | MODULE ID INTERFACE interface BODY LET_HEADER IN module_body
        | MODULE ID INTERFACE interface BODY LETREC_HEADER IN module_body
        | MODULE ID INTERFACE interface BODY modules module_body
    
    modules : module
        | module modules
    '''
    modules = ()
    let_exp = None
    match tuple(p[1:]):
        case (kw,name,interface_kw,declarations,body_kw,body):
            p[0] = Module_Def(name,declarations,modules,let_exp,body)
        case (kw,name,interface_kw,declarations,body_kw,let_exp,'in',body):
            p[0] = Module_Def(name,declarations,modules,let_exp,body)
        case (kw,name,interface_kw,declarations,body_kw,modules,body):
            p[0] = Module_Def(name,declarations,modules,let_exp,body)
        case (module,):
            p[0] = (module,)
        case (module,modules):
            p[0] = (module,) + modules
        case _:
            raise NotImplemented

def p_interface(p):
    '''
    interface : '[' decl_opt ']'
        | '(' '(' param_interfaces ')' RIGHTARROW interface ')'
    param_interfaces : ID ':' interface
        | ID ':' interface param_interfaces
    '''
    match tuple(p[1:]):
        case ('[',decls,']'):
            p[0] = decls
        case ('(','(',param_interfaces,')','=>',res_interface,')'):
            params = tuple(p[0] for p in param_interfaces)
            interfaces = tuple(p[1] for p in param_interfaces)
            p[0] = Proc_Interface(params,interfaces,res_interface)
        case (param,':',interface):
            p[0] = ((param,interface),)
        case (param,':',interface,param_interfaces):
            p[0] = ((param,interface),) + param_interfaces
        case _:
            raise Exception()

def p_declarations(p):
    '''
    decl_opt : 
        | declarations
    
    declarations : decl
        | decl declarations
    '''
    match tuple(p[1:]):
        case ():
            p[0] = tuple()
        case (declarations,) if isinstance(declarations,tuple):
            p[0] = declarations
        case (decl,declarations):
            p[0] = (decl,) + declarations
        case (decl,):
            p[0] = (decl,)

def p_decl(p):
    '''
    decl : ID ':' type
        | OPAQUE ID
        | TRANSPARENT ID '=' type
    '''
    match tuple(p[1:]):
        case (var,':',t):
            p[0] = Var_Decl(var,t)
        case ('opaque',var):
            p[0] = Opaque_Type_Decl(var)
        case ('transparent',var,'=',t):
            p[0] = Transparent_Type_Decl(var,t)

def p_module_body(p):
    '''
    module_body : '[' ']'
        | '[' defs ']'
        | MODULE_PROC  '(' param_interfaces ')' module_body
        | '(' vars ')'
        | ID
    '''
    match tuple(p[1:]):
        case ('[',']'):
            p[0] = tuple()
        case ('[',definitons,']') if isinstance(definitons,tuple):
            p[0] = definitons
        case ('module-proc','(',param_interfaces,')',module_body):
            params = tuple(p[0] for p in param_interfaces)
            interfaces = tuple(p[1] for p in param_interfaces)
            p[0] = Proc_Module_Body(params,interfaces,module_body)
        case ('(',vars,')'):
            p[0] = App_Module_Body(vars[0],vars[1:])
        case (var,):
            p[0] = Var_Module_Body(var)
        case _:
            raise Exception()

def p_defs(p):
    '''
    defs : def
        | def defs
    '''
    match tuple(p[1:]):
        case (definition,definitons):
            p[0] = (definition,) + definitons
        case (definition,):
            p[0] = (definition,)


def p_module_body_def(p):
    '''
    def : ID '=' expr
        | TYPE ID '=' type
    '''
    match tuple(p[1:]):
        case (var,'=',exp):
            p[0] = Var_Def(var,exp)
        case (type_kw,var,'=',t):
            p[0] = Type_Def(var,t)
        case _:
            print(tuple(p[1:]))
            raise NotImplemented

def p_class_decl(p):
    '''
    class_decl : CLASS ID EXTENDS ID field_decl_opt method_decl_opt
    '''
    match tuple(p[1:]):
        case ('class',cls_name,'extends',parent,fields,methods):
            p[0] = Class_Decl(cls_name,parent,fields,methods)
        case _:
            print(tuple(p[1:]))
            raise NotImplementedError 

def p_cls_decl_opt(p):
    '''
    field_decl_opt : 
        | field_decls
    method_decl_opt :
        | method_decls
    '''
    match tuple(p[1:]):
        case ():
            p[0] = ()
        case (decls,):
            p[0] = decls
        case _:
            print(tuple(p[1:]))
            raise NotImplementedError

def p_field_decls(p):
    '''
    class_decls : class_decl
        | class_decl class_decls
    field_decls : field_decl
        | field_decl field_decls
    field_decl : FIELD ID
    '''
    match tuple(p[1:]):
        case ('field',name):
            p[0] = name
        case (decl,decls):
            p[0] = (decl,) + decls
        case (decl,):
            p[0] = (decl,)
        case _:
            print(tuple(p[1:]))
            raise NotImplementedError

def p_method_decl(p):
    '''
    method_decls : method_decl
        | method_decl method_decls
    
    method_decl : METHOD ID '(' params_opt ')' expr
    '''
    match tuple(p[1:]):
        case ('method',var,'(',params,')',expr):
            p[0] = Method_Decl(var,params,expr)
        case ('method',var,'(',(),')',expr):
            p[0] = Method_Decl(var,(),expr)
        case (decl,decls):
            p[0] = (decl,) + decls
        case (decl,):
            p[0] = (decl,)
        case _:
            print(tuple(p[1:]))
            raise NotImplementedError

def p_class_other(p):
    '''
    expr : NEW ID '(' list_opt ')'
        | SEND expr ID '(' list_opt ')'
        | SUPER ID '(' list_opt ')'
        | INSTANCEOF expr ID 
        | SELF
    '''
    match tuple(p[1:]):
        case ('new',cls_name,'(',exps,')'):
            p[0] = New_Obj_Exp(cls_name,exps)
        case ('send',expr,method_name,'(',exps,')'):
            p[0] = Method_Call_Exp(expr,method_name,exps)
        case ('super',method_name,'(',exps,')'):
            p[0] = Super_Call_Exp(method_name,exps)
        case ('instanceof',expr,cls_name):
            p[0] = Instance_Exp(expr,cls_name)
        case ('self',):
            p[0] = Self_Exp()
        case _:
            print(tuple(p[1:]))
            raise NotImplementedError

def p_field_ref(p):
    '''
    expr : FIELDREF expr ID
        | FIELDSET expr ID '=' expr
    '''
    match tuple(p)[1:]:
        case ('fieldref',obj_exp,field_name):
            p[0] = Field_Ref(obj_exp,field_name)
        case ('fieldset',obj_exp,field_name,'=',exp):
            p[0] = Field_Set(obj_exp,field_name,exp)
        case _:
            raise NotImplementedError(tuple(p)[1:])

# Error rule for syntax errors
def p_error(p):
    print(p)
    print("Syntax error in input!")

# Build the parser to make parser.parse available
parser = yacc.yacc(debug=True)
def type_parse(prog):
    return parser.parse('type ' + prog)

if __name__ == '__main__':
    while True:
        try:
            s = input('LET > ')
        except EOFError:
            break
        if not s: continue
        result = parser.parse(s)
        print(result)