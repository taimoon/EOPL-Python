from LET_ast_node import *
from LET_parser import parser
from LET import expand_let_star,expand_conditional
from LET_environment import (
    Environment,
    init_tenv,
    apply_tenv,
    extend_tenv_from_pairs,
)

def type_of_prog(prog,env = init_tenv(),parse = parser.parse):
    return CHECKED().type_of_prog(prog,env,parse)

class CHECKED:
    def check_equal_type(self,t1,t2,exp):
        if t1 != t2:
            raise Exception(f"Type didn't match [{t1}] [{t2}] [{exp}]")


    def type_of_prog(self,prog,env = init_tenv(),parse = parser.parse):
        prog = parse(prog)
        return self.type_of(prog,env)


    def type_of(self,expr,tenv):
        check_equal_type = self.check_equal_type
        type_of = self.type_of
        rec_proc_to_tenv = self.rec_proc_to_tenv
        if isinstance(expr, Const_Exp) and isinstance(expr.val,NULL):
            '''
            workaround
            the No_Type NULL only acceptable in newpair
            but Typed NULL only acceptable in cons
            '''
            t = expr.val.t
            return t if isinstance(t,No_Type) else List_Type(t)
        elif isinstance(expr, Const_Exp):
            return Int_Type()
        elif isinstance(expr, Var_Exp):
            return apply_tenv(tenv,expr.var)
        elif isinstance(expr, Diff_Exp):
            check_equal_type(type_of(expr.left,tenv),Int_Type(),expr.left)
            check_equal_type(type_of(expr.right,tenv),Int_Type(),expr.right)
            return Int_Type()
        elif isinstance(expr, Zero_Test_Exp):
            check_equal_type(type_of(expr.exp,tenv),Int_Type(),expr.exp)
            return Bool_Type()
        elif isinstance(expr, Branch):
            check_equal_type(type_of(expr.pred,tenv), Bool_Type(),expr.pred)
            t1 = type_of(expr.conseq,tenv)
            t2 = type_of(expr.alter,tenv)
            check_equal_type(t1,t2,expr)
            return t1
        elif isinstance(expr, Proc_Exp): # TODO - move expand_types
            ext_env = extend_tenv_from_pairs(expr.params, expr.types, tenv)
            arg_type = expr.types
            res_type = type_of(expr.body,ext_env)
            return Proc_Type(arg_type,res_type)
        elif isinstance(expr, App_Exp):
            proc_t = type_of(expr.operator,tenv)
            if not isinstance(proc_t,Proc_Type):
                raise Exception(f"Operator is not a procedure type {proc_t} {expr.operator}")
            
            arg_types = tuple(type_of(exp,tenv) for exp in expr.operand)
            for param_t,arg_t in zip(proc_t.arg_type,arg_types):
                check_equal_type(param_t,arg_t,expr)
            
            return proc_t.res_type
        elif isinstance(expr, Rec_Proc):
            return type_of(expr.expr,rec_proc_to_tenv(expr,tenv))
        elif isinstance(expr,Pair_Exp):
            t0 = type_of(expr.left,tenv)
            t1 = type_of(expr.right,tenv)
            if expr.homogeneous is True:
                t0 = t0.t if isinstance(t0,List_Type) else t0
                t1 = t1.t if isinstance(t1,List_Type) else t1
                check_equal_type(t0,t1,expr)
                return List_Type(t0)
            else:
                return Pair_Type(t0,t1)
        elif isinstance(expr,Unpair_Exp):
            t = type_of(expr.pair_exp,tenv)
            if not isinstance(t,Pair_Type):
                raise Exception(f"the expression is not pair for UNPAIR {expr}")
            ts = t.t0,t.t1
            vars = expr.left,expr.right
            tenv = extend_tenv_from_pairs(vars,ts,tenv)
            return type_of(expr.expr,tenv)
        elif isinstance(expr,List):
            types = tuple(type_of(exp,tenv) for exp in expr.exps)
            t0 = types[0]
            for t in types[1:]:
                check_equal_type(t0,t,expr)
            return List_Type(t0)
        elif isinstance(expr,Null_Exp):
            return Bool_Type()
        # Statement
        elif isinstance(expr,Sequence):
            t = None
            for exp in expr.exps:
                t = type_of(exp,tenv)
            return Void_Type() if t is None else t
        elif isinstance(expr,NewRef):
            return Void_Type()
        elif isinstance(expr,DeRef):
            raise NotImplementedError
        elif isinstance(expr,SetRef):
            ref_t = type_of(expr.loc,tenv)
            check_equal_type(ref_t,Int_Type(),expr.loc)
            return Void_Type()
        # Derived Form
        elif isinstance(expr,Let_Exp):
            types = tuple(type_of(exp,tenv) for exp in expr.exps)
            return type_of(App_Exp(Proc_Exp(expr.vars,expr.body,types),expr.exps),tenv)
        elif isinstance(expr,Let_Star_Exp):
            return type_of(expand_let_star(expr),tenv)
        elif isinstance(expr,Conditional):
            return type_of(expand_conditional(expr.clauses,expr.otherwise),tenv)
        elif isinstance(expr, Primitive_Exp):
            if expr.op == 'car':
                t = type_of(expr.exps[0],tenv)
                t = t.t if isinstance(t,List_Type) else t
                t = t.t0 if isinstance(t,Pair_Type) else t
                return t
            elif expr.op == 'cdr':
                t = type_of(expr.exps[0],tenv)
                t = t.t1 if isinstance(t,Pair_Type) else t
                return t
            return type_of(App_Exp(Var_Exp(expr.op),expr.exps),tenv)
        elif isinstance(expr,Unpack_Exp):
            if expr.vars is None or expr.expr is None:
                raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
            return type_of(App_Exp(operator = Proc_Exp(expr.vars,expr.expr),
                                    operand  = (Unpack_Exp(None,expr.list_expr,None),)
                                    ),tenv)
        else:
            raise Exception("Unknown CHECKED expression type", expr)

    def rec_proc_to_tenv(self,exp:Rec_Proc,tenv:Environment) -> Environment:
        type_of = self.type_of
        check_equal_type = self.check_equal_type
        vals = tuple(Proc_Type(arg_t,res_t) for arg_t,res_t in zip(exp.arg_types,exp.res_types))
        vars = exp.var
        tenv = extend_tenv_from_pairs(vars,vals,tenv)
        
        for params,arg_t,body,res_t in zip(exp.params,exp.arg_types,exp.body,exp.res_types):
            body_t = type_of(body,extend_tenv_from_pairs(params,arg_t,tenv))
            check_equal_type(body_t,res_t,body)
        
        return tenv

