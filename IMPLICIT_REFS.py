from LET_parser import parser
from EXPLICIT_REFS import EXPLICIT_REFS_Interpreter
from LET_environment import (
    Environment,
    extend_env_rec_ref,
    apply_env,
    extend_env_from_pairs,
)
from LET_ast_node import *
from memory import *
from object import *

'''
newref(expr)
setref(expr,expr)
deref(expr)
ref(var) % &ptr similiar to C's pointer and address
letmutable {id = expr}+ in expr
# all variables are mutable unless introduced by let
'''

def value_of_prog(prog, env = None, parse = parser.parse):
    if env is None:
        env = IMPLICIT_REFS_Interpreter().init_env()
    return IMPLICIT_REFS_Interpreter().value_of_prog(prog,env,parse)

class IMPLICIT_REFS_Interpreter:
    def init_env(self):
        from LET_environment import init_env
        from LET_environment import get_all_primitive_implementation
        corspd = get_all_primitive_implementation()
        corspd['cons'] = Mutable_Pair
        corspd['setcar'] = lambda p,v: p.setcar(v)
        corspd['setcdr'] = lambda p,v: p.setcdr(v)
        corspd['list'] = Mutable_Pair.list_to_pair

        return init_env(corspd)

    def change_init_env(self,env:Environment):
        from LET_environment import empty_env
        new_env = empty_env()
        for e in env:
            e = {var:newref(val) for var,val in e}
            new_env = new_env.extend_from_dict(e)
        return new_env
        

    def value_of_prog(self,prog, env = None, parse = parser.parse):
        prog = parse(prog)
        init_store()
        return self.value_of(prog, self.change_init_env(env))

    def apply_proc(self,proc:Proc_Val,args):
        if isinstance(proc, Primitve_Implementation):
            return proc.op(*args)
        vals = tuple(newref(arg) for arg in args)
        env = extend_env_from_pairs(proc.params,vals,proc.env)
        return self.value_of(proc.body, env)

    def value_of(self,expr, env):
        value_of = self.value_of
        if isinstance(expr, Var_Exp):
            res = apply_env(env, expr.var)
            if isinstance(res,Immutable):
                return res.val
            else:
                return deref(res)
        elif isinstance(expr, Rec_Proc):
            return value_of(expr.expr, extend_env_rec_ref(expr.var,expr.params,expr.body,env))
        elif isinstance(expr,Let_Exp):
            # introduce immutability
            vals = tuple(Immutable(value_of(exp,env)) for exp in expr.exps)
            env = extend_env_from_pairs(expr.vars,vals,env)
            return value_of(expr.body,env)
        # Statement
        elif isinstance(expr,Ref):
            if not isinstance(expr.var,Var_Exp):
                raise Exception("The argument passed to ref is not a variable")
            var = expr.var.var
            loc = apply_env(env,var)
            return loc
        elif isinstance(expr,Assign_Exp):
            res = apply_env(env,expr.var)
            if isinstance(res,Immutable):
                raise Exception(f"error : attempt to modify immutable variable {expr.var}")
            setref(res,value_of(expr.expr,env))
        # derived form
        elif isinstance(expr,Letmutable_Exp):
            return value_of(App_Exp(Proc_Exp(expr.vars, expr.body), expr.exps), env)
        else:
            return EXPLICIT_REFS_Interpreter.value_of(self,expr,env)
