from LET_parser import parser
from LET_environment import *
from memory import *

'''
newref(expr)
setref(expr)
deref(expr)
letmutable {id = expr}+ in expr
# all variables are mutable unless introduced by let
'''

def init_env():
    from LET_environment import init_env
    corspd = get_all_primitive_implementation()
    corspd['cons'] = lambda x,y: Mutable_Pair(x,y)
    corspd['setcar'] = lambda p,v: p.setcar(v)
    corspd['setcdr'] = lambda p,v: p.setcdr(v)

    return init_env(corspd)

def change_init_env(env):
    # another day, another workaround
    new_env = empty_env()
    for var,val in env.env:
        new_env = extend_env(var,newref(val),new_env)
    return new_env

def value_of_prog(prog, env = init_env(), parse = parser.parse):
    init_store()
    return value_of(parse(prog), change_init_env(env))

def apply_proc(proc:Proc_Val,args,env:Environment):
    for param,arg in zip(proc.params,args):
        # env = extend_env(param,newref(arg),env)
        env = extend_env(param,arg,env)
    return value_of(proc.body, env)

def value_of_operand(expr, env):
    'implementing pass-by-reference'
    if isinstance(expr,Var_Exp):
        return apply_env(env,expr.var)
    else:
        return newref(Thunk(expr,env))

def value_of_thunk(expr:Thunk):
    return value_of(expr.expr,expr.env)

def value_of(expr, env):
    if isinstance(expr, Const_Exp):
        return expr.val
    elif isinstance(expr, Var_Exp):
        res = apply_env(env, expr.var)
        if isinstance(res,Immutable):
            return res.val
        elif isinstance(deref(res),Thunk):
            return value_of_thunk(deref(res))
        else:
            return deref(res)
    elif isinstance(expr, Diff_Exp):
        return value_of(expr.left,env) - value_of(expr.right,env)
    elif isinstance(expr, Zero_Test_Exp):
        return value_of(expr.exp,env) == 0
    elif isinstance(expr, Branch):
        if value_of(expr.pred,env):
            return value_of(expr.conseq,env)
        else:
            return value_of(expr.alter,env)
    elif isinstance(expr, Proc_Exp):
        # return Proc_Val(expr.params,expr.body,empty_env()) # dynamic scoping
        return Proc_Val(expr.params,expr.body,env) # lexical scoping
    elif isinstance(expr, App_Exp):
        proc = value_of(expr.operator,env)
        if len(expr.operand) == 1 and isinstance(expr.operand[0],Unpack_Exp):
            # unpack doesn't pass variable by reference
            args = value_of(expr.operand[0].list_expr,env)
            args = map(lambda o: newref(o),args)
        elif isinstance(proc, Primitve_Implementation):
            args = map(lambda o : value_of(o, env), expr.operand)
            return proc.op(*args)
        else:
            args = map(lambda o : value_of_operand(o, env), expr.operand)
        return apply_proc(proc,args,proc.env) # lexical scoping
    elif isinstance(expr, Rec_Proc):
        # extend_env_rec_ref(expr.var,expr.params,expr.body,env)
        return value_of(expr.expr, extend_env_rec_ref(expr.var,expr.params,expr.body,env))
    elif isinstance(expr,Let_Exp):
        # introduce immutability
        new_env = env
        for var,exp in zip(expr.vars,expr.exps):
            val = value_of(exp,env)
            new_env = extend_env(var,Immutable(val),new_env)
        return value_of(expr.body,new_env)
    # Statement
    elif isinstance(expr,Sequence):
        val = None
        for exp in expr.exps:
            val = value_of(exp,env)
        return val
    elif isinstance(expr,NewRef):
        return newref(value_of(expr.expr,env))
    elif isinstance(expr,DeRef):
        return deref(value_of(expr.expr,env))
    elif isinstance(expr,SetRef):
        ref = value_of(expr.loc,env)
        val = value_of(expr.expr,env)
        return setref(ref,val)
    elif isinstance(expr,Ref):
        if not isinstance(expr.var,Var_Exp):
            raise Exception("The argument passed to ref is not a variable")
        var = expr.var.var
        loc = apply_env(env,var)
        return loc
    elif isinstance(expr,Assign_Exp):
        res = apply_env(env,expr.var)
        if not is_reference(res):
            raise Exception(f"error : attempt to modify immutable variable {expr.var}")
        setref(apply_env(env,expr.var),value_of(expr.expr,env))
    # derived form
    elif isinstance(expr, Primitive_Exp):
        return value_of(App_Exp(Var_Exp(expr.op),expr.exps),env)
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
        return value_of(expand(expr.clauses),env)
    elif isinstance(expr,List):
        return value_of(App_Exp(Var_Exp('list'),tuple(expr.exps)),env)
    elif isinstance(expr,Pair_Exp):
        return value_of(App_Exp(Var_Exp('cons'),(expr.left,expr.right)),env)
    elif isinstance(expr,Unpack_Exp):
        if expr.vars is None or expr.expr is None:
            raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
        return value_of(App_Exp(operator = Proc_Exp(expr.vars,expr.expr),
                                operand  = (Unpack_Exp(None,expr.list_expr,None),)
                                ),env)
    elif isinstance(expr,Let_Star_Exp):
        def expand(vars,exprs):
            if vars == ():
                return expr.body
            else:
                return Let_Exp([vars[0]],[exprs[0]],expand(vars[1:],exprs[1:]))
        return value_of(expand(expr.vars,expr.exps),env)
    elif isinstance(expr,Letmutable_Exp):
        return value_of(App_Exp(Proc_Exp(expr.vars, expr.body), expr.exps), env)
    else:
        raise Exception("Uknown LET expression type", expr)

