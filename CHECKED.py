from LET_ast_node import *
from LET_parser import parser
from LET_environment import *

def check_equal_type(t1,t2,exp):
    if t1 != t2:
        raise Exception(f"Type didn't match [{t1}] [{t2}] [{exp}]")


def type_of_prog(prog, env = init_tenv(), parse = parser.parse):
    prog = parse(prog)
    if isinstance(prog,Program):
        return type_of(prog.expr,add_modules_to_tenv(prog.modules,env))
    else:
        return type_of(prog, env)


def type_of(expr, env):
    if isinstance(expr, Const_Exp) and isinstance(expr.val,NULL):
        '''
        workaround
        the No_Type NULL only acceptable in newpair
        but Typed NULL only acceptable in cons
        '''
        t = expr.val.t
        return t if isinstance(t,No_Type) else List_Type(t)
    elif isinstance(expr, Const_Exp):
        return Int_Type()
    elif isinstance(expr, Var_Exp):
        return apply_env(env, expr.var)  
    elif isinstance(expr, Diff_Exp):
        check_equal_type(type_of(expr.left,env),Int_Type(),expr.left)
        check_equal_type(type_of(expr.right,env),Int_Type(),expr.right)
        return Int_Type()
    elif isinstance(expr, Zero_Test_Exp):
        check_equal_type(type_of(expr.exp,env),Int_Type(),expr.exp)
        return Bool_Type
    elif isinstance(expr, Branch):
        check_equal_type(type_of(expr.pred,env), Bool_Type(),expr.pred)
        t1 = type_of(expr.conseq,env)
        t2 = type_of(expr.alter,env)
        check_equal_type(t1,t2,expr)
        return t1
    elif isinstance(expr, Proc_Exp): # TODO - move expand_types
        ext_env = extend_env_from_pairs(expr.params, expand_types(expr.types,env), env)
        res_t = type_of(expr.body,ext_env)
        return Proc_Type(expand_types(expr.types,env),
                         result_type=res_t)
    elif isinstance(expr, App_Exp):
        proc_t = type_of(expr.operator,env)
        if not isinstance(proc_t,Proc_Type):
            raise Exception(f"Operator is not a procedure type {proc_t} {expr.operator}")
        arg_types = tuple(map(lambda exp: type_of(exp,env),expr.operand))
        for param_t,arg_t in zip(proc_t.arg_type,arg_types):
            check_equal_type(param_t,arg_t,expr)
        
        return proc_t.result_type
    elif isinstance(expr, Rec_Proc):
        return type_of(expr.expr,rec_proc_to_tenv(expr,env))
    elif isinstance(expr,Pair_Exp):
        t0 = type_of(expr.left,env)
        t1 = type_of(expr.right,env)
        if expr.homogeneous is True:
            t0 = t0.t if isinstance(t0,List_Type) else t0
            t1 = t1.t if isinstance(t1,List_Type) else t1
            check_equal_type(t0,t1,expr)
            return List_Type(t0)
        else:
            return Pair_Type(t0,t1)
    elif isinstance(expr,Unpair_Exp):
        t = type_of(expr.pair_exp,env)
        if not isinstance(t,Pair_Type):
            raise Exception(f"the expression is not pair for UNPAIR {expr}")
        env = extend_env(expr.left,expand_type(t.t0,env),env)
        env = extend_env(expr.right,expand_type(t.t1,env),env)
        return type_of(expr.expr,env)
    elif isinstance(expr,List):
        types = tuple(map(lambda exp: type_of(exp,env), expr.exps))
        t0 = types[0]
        for t in types[1:]:
            check_equal_type(t0,t,expr)
        return List_Type(t0)
    elif isinstance(expr,Null_Exp):
        return Bool_Type()
    elif isinstance(expr,Qualified_Var_Exp):
        return lookup_qualified_var(expr.module_name,expr.var_name,env)
    # Statement
    elif isinstance(expr,Sequence):
        t = None
        for exp in expr.exps:
            t = type_of(exp,env)
        return Void_Type() if t is None else t
    elif isinstance(expr,NewRef):
        return Void_Type()
    elif isinstance(expr,DeRef):
        t = type_of(expr.expr,env)
        check_equal_type(t,Int_Type(),expr.expr)
        return No_Type()
    elif isinstance(expr,SetRef):
        ref_t = type_of(expr.loc,env)
        check_equal_type(ref_t,Int_Type(),expr.loc)
        return Void_Type()
    # Derived Form
    elif isinstance(expr,Let_Exp):
        types = tuple(type_of(exp,env) for exp in expr.exps)
        return type_of(App_Exp(Proc_Exp(expr.vars,expr.body,types),expr.exps),env)
    elif isinstance(expr,Let_Star_Exp):
        return type_of(expand_let_star(expr),env)
    elif isinstance(expr,Conditional):
        def expand(clauses:tuple[Clause]):
            if clauses[1:] == ():
                if expr.otherwise is not None:
                    return Branch(clauses[0].pred,clauses[0].conseq,expr.otherwise)
                else:
                    false_val = Zero_Test_Exp(Const_Exp(1))
                    return Branch(clauses[0].pred,clauses[0].conseq,false_val)
            else:
                return Branch(clauses[0].pred,clauses[0].conseq,expand(clauses[1:]))
        return type_of(expand(expr.clauses),env)
    elif isinstance(expr, Primitive_Exp):
        if expr.op == 'car':
            t = type_of(expr.exps[0],env)
            t = t.t if isinstance(t,List_Type) else t
            t = t.t0 if isinstance(t,Pair_Type) else t
            return t
        elif expr.op == 'cdr':
            t = type_of(expr.exps[0],env)
            t = t.t1 if isinstance(t,Pair_Type) else t
            return t
        return type_of(App_Exp(Var_Exp(expr.op),expr.exps),env)
    elif isinstance(expr,Unpack_Exp):
        if expr.vars is None or expr.expr is None:
            raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
        return type_of(App_Exp(operator = Proc_Exp(expr.vars,expr.expr),
                                operand  = (Unpack_Exp(None,expr.list_expr,None),)
                                ),env)
    else:
        raise Exception("Unknown CHECKED expression type", expr)

def expand_let_star(exp:Let_Star_Exp):
    def recur(vars,exps):
        if vars == ():
            return exp.body
        else:
            return Let_Exp((vars[0],),(exps[0],),recur(vars[1:],exps[1:]))
    return recur(exp.vars,exp.exps)

def rec_proc_to_tenv(exp:Rec_Proc,tenv:Environment) -> Environment:
    ext_env = tenv
    for var,arg_t,res_t in zip(exp.var,exp.arg_types,exp.res_types):
        ext_env = extend_env(var,Proc_Type(arg_t,res_t),ext_env)
    
    for params,arg_t,body,res_t in zip(exp.params,exp.arg_types,exp.body,exp.res_types):
        body_t = type_of(body,extend_env_from_pairs(params,arg_t,ext_env))
        check_equal_type(body_t,res_t,body)
    
    return ext_env

def add_modules_to_tenv(modules:tuple[Module_Def],tenv):
    for module in modules:
        local_tenv = add_modules_to_tenv(module.modules,tenv) 
        local_tenv = let_exp_to_tenv(module.let_block,local_tenv)
        interface = defs_to_decls(module.body,local_tenv)
        if not decl_subset(interface,module.interface,tenv):
            raise Exception(f"Does not satisfy interface {module.interface} {interface}")
        
        module_tenv = decls_to_tenv(expand_interface(module.name,module.interface,tenv))
        tenv = extend_env_with_module(module.name,module_tenv,tenv)
    
    return tenv

def let_exp_to_tenv(exp:Let_Exp|Let_Star_Exp|Rec_Proc,tenv):
    if isinstance(exp,Let_Exp):
        vals = tuple(type_of(exp,tenv) for exp in exp.exps)
        return extend_env_from_pairs(exp.vars,vals,tenv)
    elif isinstance(exp,Let_Star_Exp):
        return let_exp_to_tenv(expand_let_star(exp),tenv)
    elif isinstance(exp,Rec_Proc):
        return rec_proc_to_tenv(exp,tenv)
    else:
        return tenv

Decl_Type = Var_Decl|Opaque_Type_Decl|Transparent_Type_Decl
Def_Type = Var_Def|Type_Def

def decls_to_tenv(decls:tuple[Decl_Type]) -> Environment:
    if decls == tuple():
        return empty_env()
    else:
        return extend_env(decls[0].name,decls[0].type,decls_to_tenv(decls[1:]))


def defs_to_decls(defs:tuple[Def_Type],tenv:Environment) -> tuple[Decl_Type]:
    if defs == tuple():
        return tuple()
    elif isinstance(defs[0],Var_Def):
        name = defs[0].name
        type = type_of(defs[0].expr,tenv)
        new_tenv = extend_env(name,type,tenv)
        decl = Var_Decl(name,type)
        return (decl,) + defs_to_decls(defs[1:],new_tenv)
    elif isinstance(defs[0],Type_Def):
        name,type = defs[0].name,defs[0].type
        new_tenv = extend_env(name,expand_type(type,tenv),tenv)
        decl = Transparent_Type_Decl(name,type)
        return (decl,) + defs_to_decls(defs[1:],new_tenv)
    else:
        raise Exception(defs,tenv)


def subset_interface(actual:tuple[Var_Decl],expected:tuple[Var_Decl]):
    '''
    Used for untyped modules
    Assumption : order must be same for actual and expected
    
    actual < expected
    
    interface that satisfies actual also satisfy expected.
    
    decl satisfy decls_1 implies decl can satisfy decls_2
    '''
    def recur(decls_1:tuple[Var_Decl],decls_2:tuple[Var_Decl]):
        
        if decls_2 == tuple():
            return True
        elif decls_1 == tuple():
            return False
        elif decls_1[0].name != decls_2[0].name:
            return recur(decls_1[1:],decls_2)
        elif decls_1[0].type != decls_2[0].type:
            return False
        else:
            return recur(decls_1[1:],decls_2[1:])
        
    return recur(actual,expected)


def expand_type(type,tenv:Environment):
    if isinstance(type,Int_Type|Bool_Type|Void_Type|No_Type):
        return type.__class__()
    elif isinstance(type,Pair_Type):
        return Pair_Type(
            expand_type(type.t0,tenv),
            expand_type(type.t1,tenv)
        )
    elif isinstance(type,List_Type):
        return List_Type(expand_type(type.t,tenv))
    elif isinstance(type,Proc_Type):
        return Proc_Type(
            tuple(expand_type(arg_t,tenv) for arg_t in type.arg_type),
            expand_type(type.result_type,tenv)
        )
    elif isinstance(type,Named_Type):
        return lookup_type_name(type.name,tenv)
    elif isinstance(type,Qualified_Type):
        return lookup_qualified_type(type.module_name,type.type_name,tenv)
    else:
        print(type)
        raise Exception()


def expand_types(types,tenv:Environment):
    return tuple(expand_type(t,tenv) for t in types)


def is_equiv_type(t1,t2,tenv):
    return expand_type(t1,tenv) == expand_type(t2,tenv)


def decl_subset(actual:tuple[Decl_Type],expected:tuple[Decl_Type],tenv:Environment):
    '''
    Used for typed modules
    Assumption : order must be same for actual and expected
    
    actual < expected
    
    interface that satisfies actual also satisfy expected.
    
    decl satisfy decls_1 implies decl can satisfy decls_2
    '''
    def recur(decls_1:tuple[Var_Decl],decls_2:tuple[Var_Decl],tenv:Environment):
        if decls_2 == tuple():
            return True
        elif decls_1 == tuple():
            return False
        elif decls_1[0].name != decls_2[0].name:
            return recur(decls_1[1:],decls_2,
                         extend_tenv_with_decl(decls_1[0],tenv))
        else:
            return (decl_satisfy(decls_1[0],decls_2[0],
                                 extend_tenv_with_decl(decls_1[0],tenv)) 
                    and 
                    recur(decls_1[1:],decls_2[1:],
                          extend_tenv_with_decl(decls_1[0],tenv)))
        
    return recur(actual,expected,tenv)


def decl_satisfy(left:Decl_Type,right:Decl_Type,tenv):
    return (
    (isinstance(left,Var_Decl) and
    isinstance(right,Var_Decl) and
    is_equiv_type(left.type,right.type,tenv))
     or
    (isinstance(left,Transparent_Type_Decl) and
    isinstance(right,Transparent_Type_Decl) and
    is_equiv_type(left.type,right.type,tenv))
    or
    (isinstance(left,Transparent_Type_Decl) and
    isinstance(right,Opaque_Type_Decl))
    or
    (isinstance(left,Opaque_Type_Decl) and
    isinstance(right,Opaque_Type_Decl)))

def expand_declarations(module_name,decls:tuple[Decl_Type],tenv):
    return expand_interface(module_name,decls,tenv)


def expand_interface(module_name,decls:tuple[Decl_Type],tenv:Environment) -> tuple[Decl_Type]:
    if decls == tuple(): 
        return tuple()
    elif isinstance(decls[0],Var_Decl):
        decl = Var_Decl(decls[0].name,expand_type(decls[0].type,tenv))
        return (decl,) + expand_interface(module_name,decls[1:],tenv) 
    elif isinstance(decls[0],Opaque_Type_Decl):
        expanded_type = Qualified_Type(module_name,decls[0].name)
        new_tenv = extend_env(decls[0].name,expanded_type,tenv)
        decl = Transparent_Type_Decl(decls[0].name,expanded_type)
        return (decl,) + expand_interface(module_name,decls[1:],new_tenv)
    elif isinstance(decls[0],Transparent_Type_Decl):
        expanded_type = expand_type(decls[0].type,tenv)
        new_tenv = extend_env(decls[0].name,expanded_type,tenv)
        decl = Transparent_Type_Decl(decls[0].name,expanded_type)
        return (decl,) + expand_interface(module_name,decls[1:],new_tenv)
    else:
        raise Exception(module_name,decls,tenv)


def extend_tenv_with_decl(decl,tenv) -> Environment:
    if isinstance(decl,Var_Decl):
        return tenv
    elif isinstance(decl,Transparent_Type_Decl):
        expanded_type = expand_type(decl.type,tenv)
        return extend_env(decl.name,expanded_type,tenv)
    elif isinstance(decl,Opaque_Type_Decl):
        expanded_type = Qualified_Type("%uninitialized",decl.name)
        return extend_env(decl.name,expanded_type,tenv)

