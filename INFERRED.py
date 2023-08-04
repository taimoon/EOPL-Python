from LET_ast_node import *
from LET_parser import parser
from LET_environment import *
from memory import *

@dataclass
class Var_Type:
    'INFERRED interpreter data structure'
    id_gen:typing.ClassVar[int] = 0
    var:int = None
    def __post_init__(self):
        self.var = Var_Type.id_gen
        Var_Type.id_gen += 1

def assoc(t,lst):
    for u in lst:
        if u[0] == t:
            return u
    return False

def empty_subst():
    return tuple()

def apply_one_subst(t0,tvar:Var_Type,t1):
    '''
    t0[tv = t1]
    
    return the type obtained by substituting t1 for every occurrence of tv in t0
    '''
    if isinstance(t0,Int_Type):
        return Int_Type()
    elif isinstance(t0,Bool_Type):
        return Bool_Type()
    elif isinstance(t0, Proc_Type):
        return Proc_Type(
            tuple(apply_one_subst(arg_t,tvar,t1) for arg_t in t0.arg_type),
            apply_one_subst(t0.res_type,tvar,t1),
        )
    elif isinstance(t0,Var_Type):
        return t1 if t0 == tvar else t0
    else:
        raise Exception(f"unknown type expression {t0}")

def apply_subst_to_type(t,subst):
    if isinstance(t,Int_Type):
        return Int_Type()
    elif isinstance(t,Bool_Type):
        return Bool_Type()
    elif isinstance(t, Proc_Type):
        return Proc_Type(
            tuple(apply_subst_to_type(arg_t,subst) for arg_t in t.arg_type),
            apply_subst_to_type(t.res_type,subst),
        )
    elif isinstance(t,Var_Type):
        res = assoc(t,subst)
        if res is not False:
            return res[1]
        else:
            return t

def extend_subst(subst,tvar:Var_Type,t):
    def fn(p):
        return p[0], apply_one_subst(p[1],tvar,t)
    
    return ((tvar,t),) + tuple(map(fn,subst))

def no_occurrence(tvar:Var_Type,t) -> bool:
    if isinstance(t,Int_Type|Bool_Type):
        return True
    elif isinstance(t,Proc_Type):
        f = lambda arg_t: no_occurrence(tvar,arg_t)
        return all(map(f,t.arg_type)) and no_occurrence(tvar,t.res_type)
    elif isinstance(t,Var_Type):
        return t != tvar
    else:
        raise Exception(f"no_occurrence undefined arguments {tvar} {t}")
    
def unifier(t1,t2,subst,expr):
    t1 = apply_subst_to_type(t1,subst)
    t2 = apply_subst_to_type(t2,subst)
    if t1 == t2:
        return subst
    elif isinstance(t1,Var_Type):
        if no_occurrence(t1,t2):
            return extend_subst(subst,t1,t2)
        raise Exception(f"no occurrence violation {t1} {t2} {expr}")
    elif isinstance(t2,Var_Type):
        if no_occurrence(t2,t1):
            return extend_subst(subst,t2,t1)
        raise Exception(f"no occurrence violation {t2} {t1} {expr}")
    elif isinstance(t1,Proc_Type)\
        and isinstance(t2,Proc_Type):
        for arg_t1,arg_t2 in zip(t1.arg_type,t2.arg_type):
            subst = unifier(arg_t1,arg_t2,subst,expr)
        subst = unifier(t1.res_type,t2.res_type,subst,expr)
        return subst
    else:
        raise Exception(f"Unification failure {t1} {t2} {expr}")

def opt_type_2_type(t):
    if isinstance(t,No_Type):
        return Var_Type()
    else:
        return t

def check_equal_type(t1,t2,exp):
    t1 = type(t1)
    t2 = type(t2)
    if t1 != t2:
        raise Exception(f"Type didn't match {t1} {t2} {exp}")

def lambda_alpha_subst(t_exp1,t_exp2,sym_tbl=None):
    """
    return answer whose
    1. substituion that convert t_exp1 that\'s alpha equivalence to t_exp2
    2. type is same as t_exp1 if t_exp1 is alpha equivalent to t_exp2,
        otherwise, type is not same as t_exp1 (allow easy alpha equivalent test)
    """
    sym_tbl = dict() if sym_tbl is None else sym_tbl
    if isinstance(t_exp1,Proc_Type) \
        and isinstance(t_exp2,Proc_Type):
        arg_ts = []
        for arg_t1, arg_t2 in zip(t_exp1.arg_type, t_exp2.arg_type):
            ans = lambda_alpha_subst(arg_t1,arg_t2,sym_tbl)
            arg_ts.append(ans.type)
            sym_tbl = ans.subst
        arg_ts = tuple(arg_ts)
        ans = lambda_alpha_subst(t_exp1.res_type,t_exp2.res_type,sym_tbl)
        return Answer(Proc_Type(arg_ts,ans.type),ans.subst)
    elif isinstance(t_exp1,Var_Type) and isinstance(t_exp2,Var_Type):
        if t_exp1.var not in sym_tbl:
            sym_tbl[t_exp1.var] = t_exp2.var
            return Answer(t_exp1,sym_tbl)
        elif sym_tbl[t_exp1.var] != t_exp2.var:
            return Answer(t_exp2,sym_tbl)
        else:
            return Answer(t_exp1,sym_tbl)
    elif isinstance(t_exp1,Int_Type|Bool_Type) and type(t_exp1) == type(t_exp2):
        return Answer(t_exp1,sym_tbl)
    else:
        raise Exception(f"Unknown parameter {t_exp1} {t_exp2}")

@dataclass
class Answer:
    type:None
    subst:None

def type_of_prog(prog, env = init_tenv(), parse = parser.parse):
    if isinstance(prog,Answer):
        return apply_subst_to_type(prog.type,prog.subst)
    else:
        return type_of(parse(prog),env,empty_subst())

def type_of(expr, env, subst):
    if isinstance(expr, Const_Exp):
        return Answer(Int_Type(),subst)
    elif isinstance(expr, Var_Exp):
        return Answer(apply_env(env,expr.var),subst)
    elif isinstance(expr, Diff_Exp):
        ans:Answer = type_of(expr.left,env,subst)
        subst = unifier(ans.type, Int_Type(), ans.subst, expr.left)
        ans:Answer = type_of(expr.right,env,subst)
        subst = unifier(ans.type, Int_Type(), ans.subst, expr.right)
        return Answer(Int_Type(),subst)
    elif isinstance(expr, Zero_Test_Exp):
        ans:Answer = type_of(expr.exp,env,subst)
        subst = unifier(ans.type,Int_Type(),ans.subst,expr)
        return Answer(Bool_Type(),subst)
    elif isinstance(expr, Branch):
        ans:Answer = type_of(expr.pred,env,subst)
        subst = unifier(ans.type,Bool_Type(),ans.subst,expr.pred)
        ans_conseq:Answer = type_of(expr.conseq,env,subst)
        ans_alter:Answer = type_of(expr.alter,env,ans_conseq.subst)
        subst = unifier(ans_conseq.type,ans_alter.type,ans_alter.subst,expr)
        return Answer(ans_conseq.type,ans_conseq.subst)
    elif isinstance(expr, Proc_Exp):
        var_types = tuple(map(opt_type_2_type,expr.types))
        env = extend_env_from_pairs(expr.params,var_types,env)
        ans:Answer = type_of(expr.body,env,subst)
        return Answer(Proc_Type(var_types,ans.type),ans.subst)
    elif isinstance(expr, App_Exp):
        # proc = value_of(expr.operator,env)
        ans_operator:Answer = type_of(expr.operator,env,subst)
        ans_operands = tuple(
            type_of(arg,env,subst) for  arg in expr.operand
        )
        arg_types = tuple(t.type for t in ans_operands)
        res_t = Var_Type()
        subst = unifier(ans_operator.type,
                        Proc_Type(arg_types,res_t),
                        subst,expr)
        return Answer(res_t,subst)
    elif isinstance(expr, Rec_Proc):
        res_types = tuple(map(opt_type_2_type,expr.res_types))
        
        f = lambda arg_ts: tuple(map(opt_type_2_type,arg_ts))
        arg_types = tuple(map(f,expr.arg_types))
        vars = expr.var
        vals = tuple(Proc_Type(arg_ts,res_t) for arg_ts,res_t in zip(arg_types,res_types))
        env = extend_env_from_pairs(vars,vals,env)
        
        for body,params,arg_ts,res_t in \
            zip(expr.body,expr.params,arg_types,res_types):
            
            ext_env = extend_env_from_pairs(params,arg_ts,env)
            # the subst should accumlate
            ans:Answer = type_of(body,ext_env,subst)
            subst = unifier(ans.type,res_t,ans.subst,body)
        return type_of(expr.expr,env,subst)
    elif isinstance(expr,Pair_Exp):
        raise NotImplementedError
    # Derived Form
    elif isinstance(expr,Let_Exp):
        # return value_of(expr.body, extend_env(expr.var, value_of(expr.exp,env), env))
        # as derived form
        types = tuple(type_of(exp,env,subst) for exp in expr.exps)
        return type_of(App_Exp(Proc_Exp(expr.vars, expr.body,types), expr.exps), env,subst)
    elif isinstance(expr,Let_Star_Exp):
        def expand(vars,exprs):
            if vars == ():
                return expr.body
            else:
                return Let_Exp([vars[0]],[exprs[0]],expand(vars[1:],exprs[1:]))
        return type_of(expand(expr.vars,expr.exps),env,subst)
    elif isinstance(expr,Conditional):
        def expand(clauses:tuple[Clause]):
            if clauses[1:] == ():
                if expr.otherwise is not None:
                    return Branch(clauses[0].pred,clauses[0].conseq,expr.otherwise)
                else:
                    false_val = Zero_Test_Exp(Const_Exp(1))
                    return Branch(clauses[0].pred,clauses[0].conseq,false_val)
            else:
                return Branch(clauses[0].pred,clauses[0].conseq,expand(clauses[1:]))
        return type_of(expand(expr.clauses),env,subst)
    elif isinstance(expr, Primitive_Exp):
        return type_of(App_Exp(Var_Exp(expr.op),expr.exps),env,subst)
    elif isinstance(expr,Unpack_Exp):
        if expr.vars is None or expr.expr is None:
            raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
        return type_of(App_Exp(operator = Proc_Exp(expr.vars,expr.expr),
                                operand  = (Unpack_Exp(None,expr.list_expr,None),)
                                ),env,subst)
    else:
        raise Exception("Uknown LET expression type", expr)
