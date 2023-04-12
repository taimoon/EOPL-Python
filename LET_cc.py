from LET_parser import *
from LET_environment import *

def end_cc(val):
    print('end of computation')
    return val

def apply_cont(cc,val):
    return cc(val)

def value_of_prog(prog, env = init_env(), parse = parser.parse):
    return value_of_k(parse(prog), env,end_cc)

def value_of_k(expr, env,cc):
    def apply_proc_k(proc:Proc_Val|Primitve_Implementation,args,cc):
        if isinstance(proc,Primitve_Implementation):
            return apply_cont(cc,proc.op(*args))
        env = proc.env
        for param,arg in zip(proc.params,args):
            env = extend_env(param,arg,env)
        return value_of_k(proc.body, env, cc)
    if isinstance(expr, Const_Exp):
        return apply_cont(cc, expr.val)
    elif isinstance(expr, Var_Exp):
        return apply_cont(cc, apply_env(env, expr.var)) 
    elif isinstance(expr, Diff_Exp):
        def diff_cc1(left_val):
            diff_cc2 = lambda right_val: apply_cont(cc, left_val - right_val)
            return value_of_k(expr.right,env,diff_cc2)
        return value_of_k(expr.left,env,diff_cc1)
    elif isinstance(expr, Zero_Test_Exp):
        zero_cc = lambda val: apply_cont(cc, val == 0)
        return value_of_k(expr.exp, env, zero_cc)
    elif isinstance(expr, Branch):
        expr.pred, expr.conseq,expr.alter
        def branch_cc(val):
            if val == True:
                return value_of_k(expr.conseq,env,cc)
            else:
                return value_of_k(expr.alter,env,cc)
        return value_of_k(expr.pred,env,branch_cc)
    elif isinstance(expr,Let_Exp):
        # return value_of(expr.body, extend_env(expr.var, value_of(expr.exp,env), env))
        # as derived form
        # return value_of(App_Exp(Proc_Exp([expr.var], expr.body), [expr.exp]), env)
        return value_of_k(App_Exp(Proc_Exp(expr.vars,expr.body),expr.exps),env,cc)
    elif isinstance(expr, Proc_Exp):
        return apply_cont(cc, Proc_Val(expr.params, expr.body, env))
    elif isinstance(expr, App_Exp):
        def args_builder(exps,acm_vals):
            if exps[1:] == ():
                last_cc = lambda val: apply_proc_k(acm_vals[0],acm_vals[1:]+[val],cc)
                return value_of_k(exps[0],env,last_cc)
            else:
                nxt_cc = lambda val: args_builder(exps[1:],acm_vals+[val])
                return value_of_k(exps[0],env,nxt_cc)
        if expr.operand == ():
            return value_of_k(expr.operator,env,lambda op_val: apply_proc_k(op_val,[],cc))
        else:
            return args_builder((expr.operator,) + tuple(expr.operand),[])
    elif isinstance(expr, Rec_Proc):
        return value_of_k(expr.expr,extend_env_rec_multi(expr.var, expr.params,expr.body,env),cc)
    elif isinstance(expr, Primitive_Exp):
        return value_of_k(App_Exp(Var_Exp(expr.op),expr.exps),env,cc)
    elif isinstance(expr,List):
        return value_of_k(Primitive_Exp('list',tuple(expr.exps)),env,cc)
    elif isinstance(expr,Let_Star_Exp):
        def recur(vars,exprs):
            if vars == ():
                return expr.body
            else:
                return Let_Exp([vars[0]],[exprs[0]],recur(vars[1:],exprs[1:]))
        return value_of_k(recur(expr.vars,expr.exps),env,cc)
    elif isinstance(expr,Conditional):
        def recur(clauses:tuple[Clause]):
            if clauses[1:] == ():
                if expr.otherwise is not None:
                    return Branch(clauses[0].pred,clauses[0].conseq,expr.otherwise)
                else:
                    false_val = Zero_Test_Exp(Const_Exp(1))
                    return Branch(clauses[0].pred,clauses[0].conseq,false_val)
            else:
                return Branch(clauses[0].pred,clauses[0].conseq,recur(clauses[1:]))
        return value_of_k(recur(expr.clauses),env,cc)
    else:
        raise Exception("Uknown LET expression type", expr)
