from LET_parser import parser
from LET_cc_data_struct import Let_Interpreter
from LET_environment import init_env
from memory import (init_store,setref,newref,deref)
from LET_ast_node import *
from continuation import *

def value_of_prog(prog,env = init_env(),parse = parser.parse):
    return EXPLICIT_REFS_Interpreter().value_of_prog(prog,env,parse)

class EXPLICIT_REFS_Interpreter(Let_Interpreter):
    def value_of_prog(self,prog,env = init_env(),parse = parser.parse):
        init_store()
        return super().value_of_prog(prog,env,parse)
    
    def apply_proc(self,proc:Proc_Val|Primitve_Implementation,args):
        return super().apply_proc_k(self,proc,args)
    
    def apply_cont(self,cc,val):
        value_of_k = self.value_of_k
        apply_cont = self.apply_cont
        if isinstance(cc,Seq_Cont):
            if cc.exps == ():
                return apply_cont(cc.cc,val)
            else:
                return value_of_k(cc.exps[0],cc.env,Seq_Cont(cc.cc,cc.exps[1:],cc.env))
        elif isinstance(cc,NewRef_Cont):
            return apply_cont(cc.cc,newref(val))
        elif isinstance(cc,DeRef_Cont):
            return apply_cont(cc.cc,deref(val))
        elif isinstance(cc,SetRef_Cont1):
            return value_of_k(cc.exp,cc.env,SetRef_Cont2(cc.cc,val))
        elif isinstance(cc,SetRef_Cont2):
            return apply_cont(cc.cc,setref(cc.loc,val))
        else:
            return super().apply_cont(cc,val)
    
    def value_of_k(self,expr,env,cc):
        value_of_k = self.value_of_k
        if isinstance(expr,Sequence):
            sequence_cc_ctor = self.sequence_cc_ctor
            return value_of_k(expr.exps[0],env,sequence_cc_ctor(expr.exps[1:],env,cc))
        elif isinstance(expr,NewRef):
            newref_cc_ctor = self.newref_cc_ctor
            return value_of_k(expr.expr,env,newref_cc_ctor(cc))
        elif isinstance(expr,DeRef):
            deref_cc_ctor = self.deref_cc_ctor
            return value_of_k(expr.expr,env,deref_cc_ctor(cc))
        elif isinstance(expr,SetRef):
            setret_cc_ctor1 = self.setret_cc_ctor1
            return value_of_k(expr.loc,env,setret_cc_ctor1(expr.expr,env,cc))
        else:
            return super().value_of_k(expr,env,cc)

    def sequence_cc_ctor(self,exps,env,cc):
        return Seq_Cont(cc,exps,env)
    
    def newref_cc_ctor(self,cc):
        return NewRef_Cont(cc)
    
    def deref_cc_ctor(self,cc):
        return DeRef_Cont(cc)
    
    def setret_cc_ctor1(self,exp,env,cc):
        return SetRef_Cont1(cc,exp,env)
