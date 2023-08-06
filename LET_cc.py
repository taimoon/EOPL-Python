from LET_parser import parser
from LET_ast_node import *
from LET_environment import (
    extend_env_from_pairs,
    init_env,
    extend_env_rec_multi,
    apply_env,
)
from LET import expand_conditional,expand_let_star

def end_cc(val):
    return val

def apply_cont(cc,val):
    'return bounce = lambda: cc()'
    bounce = lambda: cc(val)
    bounce.val = val
    bounce.cc = cc
    # workaround
    # so that trampoline can return the value
    # without checking whether the value is ExpVal.
    # This exploits the fact that function python is object.
    return bounce

def trampoline(bounce):
    if bounce.cc is end_cc:
        return bounce.val
    else:
        return trampoline(bounce())
    
def value_of_prog(prog, env = init_env(), parse = parser.parse):
    return trampoline(value_of_k(parse(prog),env,end_cc))


def apply_proc_k(proc:Proc_Val|Primitve_Implementation,args,cc):
    if isinstance(proc,Primitve_Implementation):
        return apply_cont(cc,proc.op(*args))
    env = extend_env_from_pairs(proc.params,args,proc.env)
    return value_of_k(proc.body,env,cc)

def value_of_k(expr,env,cc):
    if isinstance(expr, Const_Exp):
        return apply_cont(cc,expr.val)
    elif isinstance(expr, Var_Exp):
        return apply_cont(cc, apply_env(env, expr.var)) 
    elif isinstance(expr, Diff_Exp):
        return value_of_k(expr.left,env,diff_cc1_ctor(expr.right,env,cc))
    elif isinstance(expr, Zero_Test_Exp):
        return value_of_k(expr.exp,env,zero_cc_ctor(cc))
    elif isinstance(expr, Branch):
        cc = branch_cc_ctor(expr.conseq,expr.alter,env,cc)
        return value_of_k(expr.pred,env,cc)
    elif isinstance(expr, Proc_Exp):
        return apply_cont(cc, Proc_Val(expr.params, expr.body, env))
    elif isinstance(expr, App_Exp):
        if expr.operand == ():
            return value_of_k(expr.operator,env,paramless_cc_ctor(cc))
        elif isinstance(expr.operand[0], Unpack_Exp):
            return value_of_k(expr.operator,env,
                              operator_cc_ctor(expr.operand[0].list_expr,env,cc))
        else:
            return value_of_k(expr.operator,env,args_builder(expr.operand,[],env,cc))
    elif isinstance(expr, Rec_Proc):
        return value_of_k(expr.expr,extend_env_rec_multi(expr.var, expr.params,expr.body,env),cc)
    # derived form
    elif isinstance(expr, Primitive_Exp):
        return value_of_k(App_Exp(Var_Exp(expr.op),expr.exps),env,cc)
    elif isinstance(expr,Conditional):
        return value_of_k(expand_conditional(expr),env,cc)
    elif isinstance(expr,List):
        return value_of_k(Primitive_Exp('list',tuple(expr.exps)),env,cc)
    elif isinstance(expr,Pair_Exp):
        return value_of_k(App_Exp(Var_Exp('cons'),(expr.left,expr.right)),env,cc)
    elif isinstance(expr,Let_Star_Exp):
        return value_of_k(expand_let_star(expr),env,cc)
    elif isinstance(expr,Let_Exp):
        # return value_of(expr.body, extend_env(expr.var, value_of(expr.exp,env), env))
        # as derived form
        # return value_of(App_Exp(Proc_Exp([expr.var], expr.body), [expr.exp]), env)
        return value_of_k(App_Exp(Proc_Exp(expr.vars,expr.body),expr.exps),env,cc)
    elif isinstance(expr,Unpack_Exp):
        if expr.vars is None or expr.expr is None:
            raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
        return value_of_k(App_Exp(Proc_Exp(expr.vars,expr.expr),
                                  (Unpack_Exp(None,expr.list_expr,None),)),
                          env,cc)
    else:
        raise Exception("Uknown LET expression type", expr)

def zero_cc_ctor(cc):
    return lambda val: apply_cont(cc,val == 0)

def branch_cc_ctor(conseq,alter,env,cc):
    def branch_cc(val):
        if val is True:
            return value_of_k(conseq,env,cc)
        else:
            return value_of_k(alter,env,cc)
    return branch_cc

def diff_cc2_ctor(w,cc):
    return lambda v : apply_cont(cc,w-v)

def diff_cc1_ctor(exp2,env,cc):
    return lambda v : value_of_k(exp2,env,diff_cc2_ctor(v,cc))

def args_cc_ctor(exps,acm_vals,env,cc):
    return lambda val: args_builder(exps,acm_vals+[val],env,cc)

def args_builder(exps,acm_vals,env,cc):
    if exps == ():
        return lambda val: apply_proc_k(acm_vals[0],acm_vals[1:]+[val],cc)
    else:
        return lambda val: value_of_k(exps[0],env,args_builder(exps[1:],acm_vals+[val],env,cc))

def paramless_cc_ctor(cc):
    return lambda op_val: apply_proc_k(op_val,[],cc)

def operand_cc_ctor(op_val,cc):
    return lambda operand: apply_proc_k(op_val,operand,cc)

def operator_cc_ctor(list_expr,env,cc):
    return lambda op_val: value_of_k(list_expr,env,operand_cc_ctor(op_val,cc))
