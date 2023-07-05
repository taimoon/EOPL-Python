from LET_parser import *
from LET_environment import *
from memory import *

def value_of_prog(prog, env = init_env(), parse = parser.parse):
    init_store()
    return value_of(parse(prog), env)

def apply_proc(proc:Proc_Val|Primitve_Implementation,args,env):
    if isinstance(proc,Primitve_Implementation):
        return proc.op(*args)
    for param,arg in zip(proc.params,args):
        env = extend_env(param,arg,env)
    if isinstance(proc,Proc_Val):
        return value_of(proc.body, env)
    
def value_of(expr, env):
    if isinstance(expr, Const_Exp):
        return expr.val
    elif isinstance(expr, Var_Exp):
        return apply_env(env, expr.var)
    elif isinstance(expr, Diff_Exp):
        left_val = value_of(expr.left,env)
        right_val = value_of(expr.right,env)
        return left_val - right_val
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
            args = value_of(expr.operand[0].list_expr,env)
        else:
            args = map(lambda o : value_of(o, env), expr.operand)
        # return apply_proc(proc,args,env) # dynamic scoping
        return apply_proc(proc,args,proc.env) # lexical scoping
    elif isinstance(expr, Rec_Proc):
        return value_of(expr.expr, extend_env_rec_multi(expr.var,expr.params,expr.body,env))
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
    elif isinstance(expr,Let_Exp):
        # return value_of(expr.body, extend_env(expr.var, value_of(expr.exp,env), env))
        # as derived form
        return value_of(App_Exp(Proc_Exp(expr.vars, expr.body), expr.exps), env)
    elif isinstance(expr,Let_Star_Exp):
        def expand(vars,exprs):
            if vars == ():
                return expr.body
            else:
                return Let_Exp([vars[0]],[exprs[0]],expand(vars[1:],exprs[1:]))
        return value_of(expand(expr.vars,expr.exps),env)
    else:
        raise Exception("Uknown LET expression type", expr)