from LET_parser import parser
from IMPLICIT_REFS import IMPLICIT_REFS_Interpreter
from LET_ast_node import *
from memory import *
from LET_environment import (
    Environment,
    apply_env,
    init_env,
    extend_env_from_pairs,
)

def value_of_prog(prog, env = init_env(), parse = parser.parse):
    return LAZY_Let_Interpreter().value_of_prog(prog,env,parse)

class LAZY_Let_Interpreter(IMPLICIT_REFS_Interpreter):
    def apply_proc(self,proc:Proc_Val,args,env:Environment):
        env = extend_env_from_pairs(proc.params,args,env)
        return self.value_of(proc.body, env)

    def value_of_operand(self,expr, env):
        'implementing pass-by-reference'
        if isinstance(expr,Var):
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
        match expr:
            case Var(var):
                res = apply_env(env, var)
                if isinstance(res,Immutable):
                    return res.val
                elif isinstance(deref(res),Thunk):
                    return value_of_thunk(deref(res))
                else:
                    return deref(res)
            case Apply(operator,operand):
                proc = value_of(operator,env)
                if len(operand) == 1 and isinstance(operand[0],Unpack_Exp):
                    # unpack doesn't pass variable by reference
                    args = value_of(operand[0].list_expr,env)
                    args = map(lambda o: newref(o),args)
                elif isinstance(proc, Primitve_Implementation):
                    args = map(lambda o : value_of(o, env), operand)
                    return proc.op(*args)
                else:
                    args = map(lambda o : value_of_operand(o, env), operand)
                return apply_proc(proc,args,proc.env)
            case _:
                return IMPLICIT_REFS_Interpreter.value_of(self,expr,env)

