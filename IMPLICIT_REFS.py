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

class Immutable_Modify_Error(Exception):
    pass

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
        match expr:
            case Var_Exp(var):
                res = apply_env(env, var)
                if isinstance(res,Immutable):
                    return res.val
                else:
                    return deref(res)
            case Rec_Proc(vars,params,body,exp):
                return value_of(exp, extend_env_rec_ref(vars,params,body,env))
            case Let_Exp(vars,exps,body):
                # introduce immutability
                vals = tuple(Immutable(value_of(exp,env)) for exp in exps)
                env = extend_env_from_pairs(vars,vals,env)
                return value_of(body,env)
            # Statement
            case Ref(var):
                if not isinstance(var,Var_Exp):
                    raise Exception("The argument passed to ref is not a variable")
                var = var.var
                loc = apply_env(env,var)
                return loc
            case Assign_Exp(var,exp):
                res = apply_env(env,var)
                if isinstance(res,Immutable):
                    raise Immutable_Modify_Error(f"error : attempt to modify immutable variable {var}")
                setref(res,value_of(exp,env))
            # derived form
            case Letmutable_Exp(vars,exps,body):
                return value_of(App_Exp(Proc_Exp(vars, body), exps), env)
            case _:
                return EXPLICIT_REFS_Interpreter.value_of(self,expr,env)
