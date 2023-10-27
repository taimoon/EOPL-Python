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
        match expr:
            case Const(val=NULL(t=No_Type())):
                return No_Type()
            case Const(val=NULL(t=t)):
                return List_Type(t)
            case Const():
                return Int_Type()
            case Var(var):
                return apply_tenv(tenv,var)
            case Diff_Exp(left,right):
                check_equal_type(type_of(left,tenv),Int_Type(),left)
                check_equal_type(type_of(right,tenv),Int_Type(),right)
                return Int_Type()
            case Zero_Test(exp):
                check_equal_type(type_of(exp,tenv),Int_Type(),exp)
                return Bool_Type()
            case Branch(pred,conseq,alter):
                check_equal_type(type_of(pred,tenv), Bool_Type(),pred)
                t1 = type_of(conseq,tenv)
                t2 = type_of(alter,tenv)
                check_equal_type(t1,t2,expr)
                return t1
            case Proc_Exp(params,body,types): # TODO - move expand_types
                ext_env = extend_tenv_from_pairs(params, types, tenv)
                arg_type = types
                res_type = type_of(body,ext_env)
                return Proc_Type(arg_type,res_type)
            case Apply(operator,operand):
                proc_t = type_of(operator,tenv)
                if not isinstance(proc_t,Proc_Type):
                    raise Exception(f"Operator is not a procedure type {proc_t} {operator}")
                
                arg_types = tuple(type_of(exp,tenv) for exp in operand)
                for param_t,arg_t in zip(proc_t.arg_type,arg_types):
                    check_equal_type(param_t,arg_t,expr)
                
                return proc_t.res_type
            case Rec_Proc(expr=exp):
                return type_of(exp,rec_proc_to_tenv(expr,tenv))
            case Pair_Exp(left,right,homogeneous):
                t0 = type_of(left,tenv)
                t1 = type_of(right,tenv)
                if homogeneous is True:
                    t0 = t0.t if isinstance(t0,List_Type) else t0
                    t1 = t1.t if isinstance(t1,List_Type) else t1
                    check_equal_type(t0,t1,expr)
                    return List_Type(t0)
                else:
                    return Pair_Type(t0,t1)
            case Unpair_Exp(left,right,pair_exp,exp):
                t = type_of(pair_exp,tenv)
                if not isinstance(t,Pair_Type):
                    raise Exception(f"the expression is not pair for UNPAIR {expr}")
                ts = t.t0,t.t1
                vars = left,right
                tenv = extend_tenv_from_pairs(vars,ts,tenv)
                return type_of(exp,tenv)
            case List(exps):
                types = tuple(type_of(exp,tenv) for exp in exps)
                t0 = types[0]
                for t in types[1:]:
                    check_equal_type(t0,t,expr)
                return List_Type(t0)
            case Null_Exp():
                return Bool_Type()
            # Statement
            case Sequence(exps):
                t = None
                for exp in exps:
                    t = type_of(exp,tenv)
                return Void_Type() if t is None else t
            case NewRef():
                return Void_Type()
            case DeRef():
                raise NotImplementedError
            case SetRef(loc):
                ref_t = type_of(loc,tenv)
                check_equal_type(ref_t,Int_Type(),loc)
                return Void_Type()
            # Derived Form
            case Let(vars,exps,body):
                types = tuple(type_of(exp,tenv) for exp in exps)
                return type_of(Apply(Proc_Exp(vars,body,types),exps),tenv)
            case Let_Star():
                return type_of(expand_let_star(expr),tenv)
            case Conditional():
                return type_of(expand_conditional(expr),tenv)
            case Primitive('car',(exp,)):
                t = type_of(exp,tenv)
                t = t.t if isinstance(t,List_Type) else t
                t = t.t0 if isinstance(t,Pair_Type) else t
                return t
            case Primitive('cdr',(exp,)):
                t = type_of(exp,tenv)
                t = t.t1 if isinstance(t,Pair_Type) else t
                return t
            case Primitive(op,exps):
                return type_of(Apply(Var(op),exps),tenv)
            case Unpack_Exp(vars,list_expr,exp):
                if vars is None or exp is None:
                    raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
                return type_of(Apply(operator = Proc_Exp(vars,exp),
                                        operand  = (Unpack_Exp(None,list_expr,None),)
                                        ),tenv)
            case _:
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

