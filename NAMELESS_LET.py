from LET_parser import *
from LET_environment import *
from LET_ast_node import *
# TODO : handling letrec
# TODO : recursion

def value_of_prog(prog:str, env = init_env(), parse = parser.parse):
    # workaround
    # so that it can use the same test cases used by other LET variants.
    # the test cases use ordinary environment
    # the code below is to translate that env to static env and nameless env accordingly
    senv = empty_senv()
    nameless_env = empty_nameless_env()
    if isinstance(env,Environment):
        for var,val in env.env:
            senv = extend_senv(var,senv)
            nameless_env = extend_nameless_env(val,nameless_env)
    nameless_prog = translation_of(parse(prog),senv)
    return value_of(nameless_prog, nameless_env)

def apply_proc(proc:Proc_Val|Primitve_Implementation,args):
    if isinstance(proc,Primitve_Implementation):
        return proc.op(*args)
    new_env = proc.env
    for arg in args:
        new_env = extend_nameless_env(arg,new_env)
    return value_of(proc.body, new_env)

def translation_of(expr,static_env):
    if isinstance(expr, Const_Exp):
        return expr
    elif isinstance(expr, Var_Exp):
        return Nameless_Var_Exp(apply_senv(static_env, expr.var))
    elif isinstance(expr, Primitive_Exp):
            return translation_of(App_Exp(Var_Exp(expr.op),expr.exps),static_env)
    elif isinstance(expr, Diff_Exp):
        return Diff_Exp(translation_of(expr.left,static_env),translation_of(expr.right,static_env))
    elif isinstance(expr, Zero_Test_Exp):
        return Zero_Test_Exp(translation_of(expr.exp,static_env))
    elif isinstance(expr, Branch):
        return Branch(
            translation_of(expr.pred,static_env),
            translation_of(expr.conseq,static_env),
            translation_of(expr.alter,static_env)
        )   
    elif isinstance(expr, Proc_Exp):
        new_senv = static_env
        for param in expr.params:
            new_senv = extend_senv(param,new_senv)
        return Nameless_Proc_Exp(translation_of(expr.body,new_senv))
    elif isinstance(expr, App_Exp):
        proc = translation_of(expr.operator,static_env)
        if expr.operand != () and isinstance(expr.operand[0],Unpack_Exp):
            args = translation_of(expr.operand[0].list_expr,static_env)
            args = (Unpack_Exp(None,args,None),)
        else:
            args = map(lambda o : translation_of(o, static_env), expr.operand)
            args = tuple(args)
        return App_Exp(proc,args)
    elif isinstance(expr, Rec_Proc):
        raise NotImplemented
    elif isinstance(expr,List):
        return translation_of(App_Exp(Var_Exp('list'),tuple(expr.exps)),static_env)
    elif isinstance(expr,Pair_Exp):
        return translation_of(App_Exp(Var_Exp('cons'),(expr.left,expr.right)),static_env)
    elif isinstance(expr,Let_Exp):
        # derived form
        # return translation_of(App_Exp(Proc_Exp(expr.vars, expr.body), expr.exps), static_env)
        new_senv = static_env
        exps = ()
        for var in expr.vars: 
            new_senv = extend_senv(var,new_senv)
        exps = tuple(translation_of(exp,static_env) for exp in expr.exps)
        return Nameless_Let_Exp(exps,translation_of(expr.body,new_senv))
    elif isinstance(expr,Let_Star_Exp):
        def expand(vars,exprs):
            if vars == ():
                return expr.body
            else:
                return Let_Exp([vars[0]],[exprs[0]],expand(vars[1:],exprs[1:]))
        return translation_of(expand(expr.vars,expr.exps),static_env)
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
        return translation_of(expand(expr.clauses),static_env)
    elif isinstance(expr,Unpack_Exp):
        return translation_of(App_Exp(Proc_Exp(expr.vars,expr.expr),
                                      (Unpack_Exp(None,expr.list_expr,None),)),
                              static_env)
    else:
        raise Exception("Uknown LET expression type", expr)

def value_of(expr, nameless_env):
    if isinstance(expr, Const_Exp):
        return expr.val
    elif isinstance(expr, Nameless_Var_Exp):
        return apply_nameless_env(nameless_env, expr.id)
    elif isinstance(expr, Primitive_Exp):
        args = map(lambda exp: value_of(exp, nameless_env), expr.exps)
        return expr.op(*args)
    elif isinstance(expr, Diff_Exp):
        return value_of(expr.left,nameless_env) - value_of(expr.right,nameless_env)
    elif isinstance(expr, Zero_Test_Exp):
        return value_of(expr.exp,nameless_env) == 0
    elif isinstance(expr, Branch):
        if value_of(expr.pred,nameless_env):
            return value_of(expr.conseq,nameless_env)
        else:
            return value_of(expr.alter,nameless_env)
    elif isinstance(expr, Nameless_Proc_Exp):
        return Proc_Val(None,expr.body,nameless_env)
    elif isinstance(expr,Nameless_Let_Exp):
        new_env = nameless_env
        for exp in expr.exps:
            new_env = extend_nameless_env(value_of(exp,nameless_env),new_env)
        return value_of(expr.body,new_env)
    elif isinstance(expr, App_Exp):
        proc = value_of(expr.operator,nameless_env)
        if len(expr.operand) == 1 and isinstance(expr.operand[0],Unpack_Exp):
            args = value_of(expr.operand[0].list_expr,nameless_env)
        else:
            args = map(lambda o : value_of(o, nameless_env), expr.operand)
        return apply_proc(proc,args)
    else:
        raise Exception("Uknown LET expression type", expr)
