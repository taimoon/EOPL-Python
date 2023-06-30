from LET_ast_node import *
from LET_parser import parser
from LET_environment import *
from memory import *

def extend_env_from_pairs(vars,vals,env):
    for var,val in zip(vars,vals):
        env = extend_env(var,val,env)
    return env

def check_equal_type(t1,t2,exp):
    if t1 != t2:
        raise Exception(f"Type didn't match [{t1}] [{t2}] [{exp}]")

def type_of_prog(prog, env = init_tenv(), parse = parser.parse):
    # init_store()
    return type_of(parse(prog), env)

def type_of(expr, env):    
    if isinstance(expr, Const_Exp):
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
    elif isinstance(expr, Proc_Exp):
        ext_env = extend_env_from_pairs(expr.params, expr.types, env)
        res_t = type_of(expr.body,ext_env)
        return Proc_Type(expr.types,
                         result_type=res_t)
    elif isinstance(expr, App_Exp):
        # proc = value_of(expr.operator,env)
        proc_t = type_of(expr.operator,env)
        if not isinstance(proc_t,Proc_Type):
            raise Exception(f"Operator is not a procedure type {proc_t} {expr.operator}")
        
        arg_types = tuple(map(lambda exp: type_of(exp,env),expr.operand))
        for param_t,arg_t in zip(proc_t.arg_type,arg_types):
            check_equal_type(param_t,arg_t,expr)
        
        return proc_t.result_type
    elif isinstance(expr, Rec_Proc):
        ext_env = env
        for var,arg_t,res_t in zip(expr.var,expr.arg_types,expr.res_types):
            ext_env = extend_env(var,Proc_Type(arg_t,res_t),ext_env)
        
        for param,arg_t,body,res_t in zip(expr.params,expr.arg_types,expr.body,expr.res_types):
            body_t = type_of(body,extend_env_from_pairs(param,arg_t,ext_env))
            check_equal_type(body_t,res_t,body)
            
        return type_of(expr.expr,ext_env)
    elif isinstance(expr,Pair_Exp):
        t0 = type_of(expr.left,env)
        t1 = type_of(expr.right,env)
        return Pair_Type(t0,t1)
    elif isinstance(expr,Unpair_Exp):
        t = type_of(expr.pair_exp,env)
        if not isinstance(t,Pair_Type):
            raise Exception(f"the expression is not pair for UNPAIR {expr}")
        env = extend_env(expr.left,t.t0,env)
        env = extend_env(expr.right,t.t1,env)
        return type_of(expr.expr,env)
    # Statement
    elif isinstance(expr,Sequence):
        t = None
        for exp in expr.exps:
            t = type_of(exp,env)
        return Void_Type() if t is None else t
    elif isinstance(expr,NewRef):
        # t = type_of(expr.expr,env)
        return Void_Type()
        # return newref(t)
    elif isinstance(expr,DeRef):
        t = type_of(expr.expr,env)
        check_equal_type(t,Int_Type(),expr.expr)
        return No_Type()
        # return deref(value_of(expr.expr,env))
    elif isinstance(expr,SetRef):
        ref_t = type_of(expr.loc,env)
        check_equal_type(ref_t,Int_Type(),expr.loc)
        # val_t = type_of(expr.expr,env)
        return Void_Type()
        # return setref(ref,val)
    # Derived Form
    elif isinstance(expr,Let_Exp):
        # return value_of(expr.body, extend_env(expr.var, value_of(expr.exp,env), env))
        # as derived form
        types = tuple(type_of(exp,env) for exp in expr.exps)
        return type_of(App_Exp(Proc_Exp(expr.vars, expr.body,types), expr.exps), env)
    elif isinstance(expr,Let_Star_Exp):
        def expand(vars,exprs):
            if vars == ():
                return expr.body
            else:
                return Let_Exp([vars[0]],[exprs[0]],expand(vars[1:],exprs[1:]))
        return type_of(expand(expr.vars,expr.exps),env)
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
        # raise NotImplemented
        return type_of(App_Exp(Var_Exp(expr.op),expr.exps),env)
    elif isinstance(expr,Unpack_Exp):
        if expr.vars is None or expr.expr is None:
            raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
        return type_of(App_Exp(operator = Proc_Exp(expr.vars,expr.expr),
                                operand  = (Unpack_Exp(None,expr.list_expr,None),)
                                ),env)
    else:
        raise Exception("Uknown LET expression type", expr)
