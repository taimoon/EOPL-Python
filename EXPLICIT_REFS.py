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
        return Let_Interpreter.value_of_prog(self,prog,env,parse)
    
    def apply_proc(self,proc:Proc_Val|Primitve_Implementation,args):
        return Let_Interpreter.apply_proc(self,proc,args)
    
    def value_of(self,expr,env):
        value_of = self.value_of
        match expr:
            case Sequence(exps):
                val = None
                for exp in exps:
                    val = value_of(exp,env)
                return val
            case NewRef(exp):
                return newref(value_of(exp,env))
            case DeRef(exp):
                return deref(value_of(exp,env))
            case SetRef(loc,exp):
                ref = value_of(loc,env)
                val = value_of(exp,env)
                return setref(ref,val)
            case _:
                return Let_Interpreter.value_of(self,expr,env)
    
