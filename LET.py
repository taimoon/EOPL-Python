from LET_ast_node import *
from LET_parser import parser
from LET_environment import (
        init_env,
        apply_env,
        extend_env_from_pairs,
        extend_env_rec_multi,
    )

def value_of_prog(prog,env = init_env(),parse = parser.parse):
    return Let_Interpreter().value_of_prog(prog,env,parse)

def expand_let_star(expr:Let_Star):
    def recur(vars,exps):
        if vars == ():
            return expr.body
        else:
            return Let((vars[0],),(exps[0],),recur(vars[1:],exps[1:]))
    return recur(expr.vars,expr.exps)

def expand_conditional(expr:Conditional):

    def expand(clauses:tuple[Clause],otherwise):
        if clauses[1:] == ():
            otherwise = Zero_Test(Const(1)) if otherwise is None else otherwise
            return Branch(clauses[0].pred,clauses[0].conseq,otherwise)
        else:
            return Branch(clauses[0].pred,clauses[0].conseq,expand(clauses[1:],otherwise))
    
    return expand(expr.clauses,expr.otherwise)
                
class Let_Interpreter:
    def value_of_prog(self,prog,env = init_env(),parse = parser.parse):
        value_of = self.value_of
        prog = parse(prog)
        return value_of(prog,env)
    
    def apply_primitive(self,prim:Primitive,args):
        return prim.op(*args)
    
    def apply_proc(self,proc:Proc_Val|Primitve_Implementation,args):
        if isinstance(proc,Primitve_Implementation):
            return Let_Interpreter.apply_primitive(self,proc,args)
        else:
            env = extend_env_from_pairs(tuple(proc.params),tuple(args),proc.env)
            return self.value_of(proc.body, env)
    
    def value_of(self,expr,env):
        value_of = self.value_of
        apply_proc = self.apply_proc
        match expr:
            case Const(val):
                return val
            case Var(var):
                return apply_env(env,expr.var)
            case Diff_Exp(left,right):
                return value_of(left,env) - value_of(right,env) 
            case Zero_Test(exp):
                return value_of(exp,env) == 0
            case Branch(pred,conseq,alter):
                if value_of(pred,env) is True:
                    return value_of(conseq,env)
                else:
                    return value_of(alter,env)
            case Proc_Exp(params,body):
                return Proc_Val(params,body,env)
            case Apply(operator,operand):
                proc = value_of(operator,env)
                if len(operand) == 1 and isinstance(operand[0],Unpack_Exp):
                    args = value_of(operand[0].list_expr,env)
                else:
                    args = map(lambda o : value_of(o, env), operand)
                return apply_proc(proc,args)
            case Rec_Proc(var,params,body,exp):
                return value_of(exp, extend_env_rec_multi(var,params,body,env))
            case Pair_Exp(left,right):
                return value_of(Apply(Var('cons'),(left,right)),env)
            case Unpair_Exp(left,right,pair_exp,exp):
                pair:Pair = value_of(pair_exp,env)
                vars = left,right
                vals = pair.car,pair.cdr
                env = extend_env_from_pairs(vars,vals,env)
                return value_of(expr.expr,env)
            # Derived Form
            case Let(vars,exps,body):
                return value_of(Apply(Proc_Exp(vars,body),exps),env)
            case Let_Star(vars,exps,body):
                return value_of(expand_let_star(expr),env)
            case Conditional():
                return value_of(expand_conditional(expr),env)
            case Primitive(op,exps):
                return value_of(Apply(Var(op),exps),env)
            case List(exps):
                return value_of(Apply(Var('list'),exps),env)
            case Unpack_Exp(vars,list_expr,exp):
                if vars is None or expr is None:
                    raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
                return value_of(Apply(operator = Proc_Exp(vars,exp),
                                        operand  = (Unpack_Exp(None,list_expr,None),))
                                ,env)
            case Null_Exp(exp):
                return value_of(Apply(Var('null?'),(exp,)),env)
            case _:
                raise Exception("Uknown LET expression type", expr)

