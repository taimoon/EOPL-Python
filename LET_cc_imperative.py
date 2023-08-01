from typing import Any
from LET_parser import *
from LET_environment import *

registers = {
    'expr': None,
    'proc' : None,
    'cc' : None,
    'val' : None,
    'env': None,
}

def end_cc(val):
    print('end of computation')
    return val

def apply_cont():
    'return bounce = lambda: cc()'
    # incorrect : lambda: cc(val) if cc is not end_cc else lambda: val
    cc = registers['cc']
    val = registers['val']
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
    # return trampoline(value_of_k(parse(prog),env,end_cc))
    registers['expr'] = parse(prog)
    registers['env'] = env
    registers['cc'] = end_cc
    bounce = value_of_k()
    return trampoline(bounce)


def apply_proc_k():
    proc:Proc_Val|Primitve_Implementation = registers['proc']
    args = registers['val']
    
    if isinstance(proc,Primitve_Implementation):
        registers['val'] = proc.op(*args)
        return apply_cont()
    
    env = proc.env
    env = extend_env_from_pairs(proc.params,args,env)
    registers['env'] = env
    registers['expr'] = proc.body
    return value_of_k()

def value_of_k():
    expr = registers['expr']
    env = registers['env']
    cc = registers['cc']
    if isinstance(expr, Const_Exp):
        registers['val'] = expr.val
        return apply_cont()
    elif isinstance(expr, Var_Exp):
        registers['val'] = apply_env(env, expr.var)
        return apply_cont()
    elif isinstance(expr, Diff_Exp):
        def diff_cc1(left_val):
            def diff_cc2(right_val):
                registers['cc'] = cc
                registers['val'] = left_val - right_val
                return apply_cont()
            registers['env'] = env
            registers['cc'] = diff_cc2
            registers['expr'] = expr.right
            return value_of_k()
        registers['cc'] = diff_cc1
        registers['expr'] = expr.left
        return value_of_k()
    elif isinstance(expr, Zero_Test_Exp):
        def zero_cc(val):
            registers['val'] = val == 0
            registers['cc'] = cc
            return apply_cont()
        registers['expr'] = expr.exp
        registers['cc'] = zero_cc
        return value_of_k()
    elif isinstance(expr, Branch):
        def branch_cc(val):
            if val == True:
                registers['expr'] = expr.conseq
            else:
                registers['expr'] = expr.alter
            registers['env'] = env
            registers['cc'] = cc
            return value_of_k()
        registers['expr'] = expr.pred
        registers['cc']=branch_cc
        return value_of_k()
        # return value_of_k(expr.pred,env,branch_cc)
    elif isinstance(expr, Proc_Exp):
        registers['val'] = Proc_Val(expr.params, expr.body, env)
        return apply_cont()
    elif isinstance(expr, App_Exp):
        def args_builder(exps,acm_vals):
            if exps[1:] == ():
                def last_cc_ctor(cc=cc):
                    def last_cc(val):
                        registers['proc'] = acm_vals[0]
                        registers['val'] = acm_vals[1:] + [val]
                        registers['cc'] = cc
                        return apply_proc_k()
                    return last_cc
                # last_cc = lambda val: apply_proc_k(acm_vals[0],acm_vals[1:]+[val],cc)
                # return value_of_k(exps[0],env,last_cc)
                registers['env'] = env
                registers['cc'] = last_cc_ctor()
                registers['expr'] = exps[0]
                return value_of_k()
            else:
                def nxt_cc(val):
                    return args_builder(exps[1:],acm_vals+[val])
                # nxt_cc = lambda val: args_builder(exps[1:],acm_vals+[val])
                registers['expr'] = exps[0]
                registers['cc'] = nxt_cc
                return value_of_k()
        if expr.operand == ():
            def nxt_cc(op_val):
                registers['cc'] = cc
                registers['proc'] = op_val
                registers['val'] = []
                return apply_proc_k()
            registers['expr'] = expr.operator
            registers['cc'] = nxt_cc
            return value_of_k()
        elif isinstance(expr.operand[0], Unpack_Exp):
            def operand_cc_ctor(op_val,cc=cc):
                # return lambda operand: apply_proc_k(op_val,operand,cc)
                def nxt_cc(operand):
                    registers['proc'] = op_val
                    registers['val'] = operand
                    registers['cc'] = cc
                    return apply_proc_k()
                return nxt_cc
                
            def operator_cc_ctor(list_expr):
                # return lambda op_val: value_of_k(list_expr,env,operand_cc_ctor(op_val))
                def nxt_cc(op_val):
                    registers['env'] = env
                    registers['expr'] = list_expr
                    registers['cc'] = operand_cc_ctor(op_val)
                    return value_of_k()
                return nxt_cc
                
            registers['expr'] = expr.operator
            registers['cc'] = operator_cc_ctor(expr.operand[0].list_expr)
            return value_of_k()
            # return value_of_k(expr.operator,env,operator_cc_ctor(expr.operand[0].list_expr))
        else:
            return args_builder((expr.operator,) + tuple(expr.operand),[])
    elif isinstance(expr, Rec_Proc):
        registers['expr'] = expr.expr
        registers['env'] = extend_env_rec_multi(expr.var, expr.params,expr.body,env)
        return value_of_k()
        # return value_of_k(expr.expr,extend_env_rec_multi(expr.var, expr.params,expr.body,env),cc)
    # derived form
    elif isinstance(expr, Primitive_Exp):
        registers['expr'] = App_Exp(Var_Exp(expr.op),expr.exps)
        return value_of_k()
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
        registers['expr'] = expand(expr.clauses)
        # return value_of_k(expand(expr.clauses),env,cc)
        return value_of_k()
    elif isinstance(expr,List):
        registers['expr'] = Primitive_Exp('list',tuple(expr.exps))
        return value_of_k()
        # return value_of_k(Primitive_Exp('list',tuple(expr.exps)),env,cc)
    elif isinstance(expr,Pair_Exp):
        registers['expr'] = App_Exp(Var_Exp('cons'),(expr.left,expr.right))
        return value_of_k()
    elif isinstance(expr,Let_Star_Exp):
        def recur(vars,exprs):
            if vars == ():
                return expr.body
            else:
                return Let_Exp([vars[0]],[exprs[0]],recur(vars[1:],exprs[1:]))
        registers['expr'] = recur(expr.vars,expr.exps)
        return value_of_k()
        # return value_of_k(recur(expr.vars,expr.exps),env,cc)
    elif isinstance(expr,Let_Exp):
        # return value_of(expr.body, extend_env(expr.var, value_of(expr.exp,env), env))
        # as derived form
        # return value_of(App_Exp(Proc_Exp([expr.var], expr.body), [expr.exp]), env)
        registers['expr'] = App_Exp(Proc_Exp(expr.vars,expr.body),expr.exps)
        return value_of_k()
        # return value_of_k(App_Exp(Proc_Exp(expr.vars,expr.body),expr.exps),env,cc)
    elif isinstance(expr,Unpack_Exp):
        if expr.vars is None or expr.expr is None:
            raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
        registers['expr'] = App_Exp(Proc_Exp(expr.vars,expr.expr),
                                  (Unpack_Exp(None,expr.list_expr,None),))
        return value_of_k()
        # return value_of_k(App_Exp(Proc_Exp(expr.vars,expr.expr),
        #                           (Unpack_Exp(None,expr.list_expr,None),)),
        #                   env,cc)
    else:
        raise Exception("Uknown LET expression type", expr)
