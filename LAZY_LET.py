from LET_parser import parser
from IMPLICIT_REFS import IMPLICIT_REFS_Interpreter
from LET_ast_node import *
from memory import *
from LET_environment import (
    Environment,
    extend_env,
    apply_env,
    init_env,
)

def value_of_prog(prog, env = init_env(), parse = parser.parse):
    return LAZY_Let_Interpreter().value_of_prog(prog,env,parse)

class LAZY_Let_Interpreter:
    '''
    LAZY_LET extends IMPLICIT_REFS
    '''
    def init_env(self):
        return IMPLICIT_REFS_Interpreter.init_env(self)

    def change_init_env(self,env):
        return IMPLICIT_REFS_Interpreter.change_init_env(self,env)

    def value_of_prog(self,prog, env = None, parse = parser.parse):
        env = init_env() if env is None else env
        return IMPLICIT_REFS_Interpreter.value_of_prog(self,prog,env,parse)

    def apply_proc(self,proc:Proc_Val,args,env:Environment):
        for param,arg in zip(proc.params,args):
            env = extend_env(param,arg,env)
        return self.value_of(proc.body, env)

    def value_of_operand(self,expr, env):
        'implementing pass-by-reference'
        if isinstance(expr,Var_Exp):
            return apply_env(env,expr.var)
        else:
            return newref(Thunk(expr,env))

    def value_of_thunk(self,expr:Thunk):
        return self.value_of(expr.expr,expr.env)

    def value_of(self,expr, env):
        value_of_thunk = self.value_of_thunk
        value_of = self.value_of
        value_of_operand = self.value_of_operand
        apply_proc = self.apply_proc
        if isinstance(expr, Var_Exp):
            res = apply_env(env, expr.var)
            if isinstance(res,Immutable):
                return res.val
            elif isinstance(deref(res),Thunk):
                return value_of_thunk(deref(res))
            else:
                return deref(res)
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
            return apply_proc(proc,args,proc.env)
        else:
            return IMPLICIT_REFS_Interpreter.value_of(self,expr,env)

