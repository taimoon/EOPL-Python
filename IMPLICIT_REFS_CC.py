from LET_parser import parser
from EXPLICIT_REFS_CC import EXPLICIT_REFS_Interpreter
from LET_environment import (
    Environment,
    extend_env_rec_ref,
    apply_env,
    extend_env_from_pairs,
)
from LET_ast_node import *
from memory import *
from object import *
from continuation import *


def value_of_prog(prog, env = None, parse = parser.parse):
    if env is None:
        env = IMPLICIT_REFS_Interpreter().init_env()
    return IMPLICIT_REFS_Interpreter().value_of_prog(prog,env,parse)

class IMPLICIT_REFS_Interpreter(EXPLICIT_REFS_Interpreter):
    def value_of_prog(self,prog, env = None, parse = parser.parse):
        prog = parse(prog)
        init_store()
        env = self.change_init_env(env)
        return self.value_of_k(prog,env,End_Cont())
    
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
    
    def apply_proc_k(self,proc:Proc_Val,args,cc):
        if isinstance(proc, Primitve_Implementation):
            apply_cont = self.apply_cont
            return apply_cont(cc,proc.op(*args))
        vals = tuple(newref(arg) for arg in args)
        env = extend_env_from_pairs(proc.params,vals,proc.env)
        return self.value_of_k(proc.body,env,cc)

    def value_of_k(self,expr,env,cc):
        apply_cont = self.apply_cont
        value_of_k = self.value_of_k
        if isinstance(expr,Var):
            res = apply_env(env,expr.var)
            if isinstance(res,Immutable):
                val = res.val
            else:
                val = deref(res)
            return apply_cont(cc,val)
        elif isinstance(expr,Rec_Proc):
            # BUG
            return value_of_k(expr.expr,extend_env_rec_ref(expr.var,expr.params,expr.body,env),cc)
        elif isinstance(expr,Let):
            let_cc_ctor = self.let_cc_ctor
            return value_of_k(Proc_Exp(expr.vars,expr.body),env,let_cc_ctor(expr.exps,env,cc))
        # Statement
        elif isinstance(expr,Ref):
            if not isinstance(expr.var,Var):
                raise Exception("The argument passed to ref is not a variable")
            var = expr.var.var
            loc = apply_env(env,var)
            return apply_cont(cc,loc)
        elif isinstance(expr,Assign):
            assign_cc_ctor = self.assign_cc_ctor
            return value_of_k(expr.expr,env,assign_cc_ctor(expr.var,env,cc))
        # derived form
        elif isinstance(expr,Letmutable):
            return value_of_k(Apply(Proc_Exp(expr.vars,expr.body),expr.exps),env,cc)
        else:
            return super().value_of_k(expr,env,cc)
    
    def apply_cont(self,cc,val):
        value_of_k = self.value_of_k
        if isinstance(cc,Assign_Cont):
            ref = apply_env(cc.env,cc.var)
            if isinstance(ref,Immutable):
                from IMPLICIT_REFS import Immutable_Modify_Error
                raise Immutable_Modify_Error(f"error : attempt to modify immutable variable {cc.var}")
            return setref(ref,val)
        elif isinstance(cc,Args_Cont) and cc.immutability is True:
            env,exps,acm_vals = cc.env,cc.exps,cc.acm_vals
            if exps == ():
                proc:Proc_Val = acm_vals[0]
                vals = acm_vals[1:]+[val]
                vals = tuple(Immutable(val) for val in vals)
                return value_of_k(proc.body,extend_env_from_pairs(proc.params,vals,proc.env),cc.cc)
            else:
                nxt_cc = Args_Cont(cc.cc,env,exps[1:],acm_vals+[val],cc.immutability)
                return value_of_k(exps[0],env,nxt_cc)
        else:
            return super().apply_cont(cc,val)
    
    def assign_cc_ctor(self,var,env,cc):
        return Assign_Cont(cc,env,var)
    
    def let_cc_ctor(self,exps,env,cc):
        return Args_Cont(cc,env,exps,[],True)
