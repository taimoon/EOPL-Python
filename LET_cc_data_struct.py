from LET_parser import parser
from LET_environment import (
    extend_env_from_pairs,
    init_env,
    extend_env_rec_multi,
    apply_env,
)
from LET import expand_conditional,expand_let_star
from LET_ast_node import *
from continuation import *

def apply_cont(cc,val):
    if isinstance(cc,End_Cont):
        return val
    elif isinstance(cc,Diff_Cont1):
        return value_of_k(cc.exp2,cc.env,Diff_Cont2(cc.cc,val))
    elif isinstance(cc,Diff_Cont2):
        return apply_cont(cc.cc,cc.v - val)
    elif isinstance(cc,Zero_Cont):
        return apply_cont(cc.cc,val == 0)
    elif isinstance(cc,Branch_Cont):
        if val is True:
            return value_of_k(cc.conseq,cc.env,cc.cc)
        else:
            return value_of_k(cc.alter,cc.env,cc.cc)
    elif isinstance(cc,Paramless_Cont):
        return apply_proc_k(val,(),cc.cc)
    elif isinstance(cc,Args_Cont):
        env,exps,acm_vals = cc.env,cc.exps,cc.acm_vals
        if exps == ():
            return apply_proc_k(acm_vals[0],acm_vals[1:]+[val],cc.cc)
        else:
            nxt_cc = Args_Cont(cc.cc,env,exps[1:],acm_vals+[val])
            return value_of_k(exps[0],env,nxt_cc)
    elif isinstance(cc,Operator_Cont):
        nxt_cc = Operand_Cont(cc.cc,val)
        return value_of_k(cc.list_expr,cc.env,nxt_cc)
    elif isinstance(cc,Operand_Cont):
        return apply_proc_k(cc.proc,val,cc.cc)
    else:
        print(cc)
        raise NotImplementedError

    
def value_of_prog(prog, env = init_env(), parse = parser.parse):
    return value_of_k(parse(prog),env,End_Cont())


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
        new_cc = branch_cc_ctor(expr.conseq,expr.alter,env,cc)
        return value_of_k(expr.pred,env,new_cc)
    elif isinstance(expr, Proc_Exp):
        return apply_cont(cc, Proc_Val(expr.params,expr.body,env))
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
    return Zero_Cont(cc)

def branch_cc_ctor(conseq,alter,env,cc):
    return Branch_Cont(cc,env,conseq,alter)

def diff_cc1_ctor(exp2,env,cc):
    return Diff_Cont1(cc,env,exp2)

def args_builder(exps,acm_vals,env,cc):
    return Args_Cont(cc,env,exps,acm_vals)

def operator_cc_ctor(list_expr,env,cc):
    return Operator_Cont(cc,env,list_expr)

def paramless_cc_ctor(cc):
    return Paramless_Cont(cc)
