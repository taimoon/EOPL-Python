from LET_parser import parser
from LET import Let_Interpreter
from LET_environment import init_env
from memory import (init_store,setref,newref,deref)
from LET_ast_node import *

def value_of_prog(prog,env = init_env(),parse = parser.parse):
    return EXPLICIT_REFS_Interpreter().value_of_prog(prog,env,parse)

class EXPLICIT_REFS_Interpreter:
    def value_of_prog(self,prog,env = init_env(),parse = parser.parse):
        init_store()
        value_of = self.value_of
        return value_of(parse(prog), env)
    
    def apply_proc(self,proc:Proc_Val|Primitve_Implementation,args,env):
        return Let_Interpreter.apply_proc(self,proc,args,env)
    
    def value_of(self,expr, env):
        value_of = self.value_of
        if isinstance(expr,Sequence):
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
        else:
            return Let_Interpreter.value_of(self,expr,env)
