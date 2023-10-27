from LET_parser import parser
from LET_environment import (
    init_env,
    apply_env,
    extend_env_rec_multi,
    extend_env_from_pairs,
)
from memory import *
from dataclasses import dataclass
from LET_ast_node import *

@dataclass
class Store:
    store:list = None
    def __post_init__(self):
        self.store = [] if self.store is None else self.store
    def newref(self,v):
        new_store = Store(self.store + [v])
        return new_store
    def deref(self,i):
        return self.store[i]
    def setref(self,i,v):
        new_store = self.copy()
        new_store.store[i] = v
        return new_store
    def copy(self):
        return Store(list(tuple(self.store)))
    def __len__(self):
        return len(self.store)

@dataclass
class Answer:
    val:None
    store:Store = None
    def __iter__(self):
        return iter((self.val,self.store.copy()))
        

def value_of_prog(prog, env = init_env(), parse = parser.parse):
    ans,_ = value_of(parse(prog),env,Store())
    return ans

def apply_proc(proc:Proc_Val|Primitve_Implementation,args,env,store:Store) -> Answer:
    if isinstance(proc,Primitve_Implementation):
        return Answer(proc.op(*args),store)
    env = extend_env_from_pairs(proc.params,args,env)
    if isinstance(proc,Proc_Val):
        return value_of(proc.body, env, store)
    
def value_of(expr, env, store:Store) -> Answer:
    if isinstance(expr, Const):
        return Answer(expr.val,store)
    elif isinstance(expr, Var):
        return Answer(apply_env(env, expr.var),store)
    elif isinstance(expr, Diff_Exp):
        left_val,store = value_of(expr.left,env,store)
        right_val,store = value_of(expr.right,env,store)
        return Answer(left_val - right_val,store)
    elif isinstance(expr, Zero_Test):
        val,store = value_of(expr.exp,env,store)
        return Answer(val == 0,store)
    elif isinstance(expr, Branch):
        val,store = value_of(expr.pred,env,store)
        if val:
            return value_of(expr.conseq,env,store)
        else:
            return value_of(expr.alter,env,store)
    elif isinstance(expr, Proc_Exp):
        return Answer(Proc_Val(expr.params,expr.body,env),store)
    elif isinstance(expr, Apply):
        proc,store = value_of(expr.operator,env,store)
        if len(expr.operand) == 1 and isinstance(expr.operand[0],Unpack_Exp):
            args,store = value_of(expr.operand[0].list_expr,env,store)
        else:
            args = ()
            for o in expr.operand:
                arg,store = value_of(o,env,store)
                args += (arg,)
        return apply_proc(proc,args,proc.env,store)
    elif isinstance(expr, Rec_Proc):
        return value_of(expr.expr, extend_env_rec_multi(expr.var,expr.params,expr.body,env),store)
    elif isinstance(expr,Sequence):
        val = None
        for exp in expr.exps:
            val,store = value_of(exp,env,store)
        return Answer(val,store)
    elif isinstance(expr,NewRef):
        val,store  = value_of(expr.expr,env,store)
        store = store.newref(val)
        return Answer(len(store) - 1,store)
    elif isinstance(expr,DeRef):
        pos,store = value_of(expr.expr,env,store)
        val = store.deref(pos)
        return Answer(val,store)
    elif isinstance(expr,SetRef):
        ref,store = value_of(expr.loc,env,store)
        val,store = value_of(expr.expr,env,store)
        store = store.setref(ref,val)
        return Answer(Pair(ref,val),store)
    # derived form
    elif isinstance(expr, Primitive):
        return value_of(Apply(Var(expr.op),expr.exps),env,store)
    elif isinstance(expr,Conditional):
        def expand(clauses:tuple[Clause]):
            if clauses[1:] == ():
                if expr.otherwise is not None:
                    return Branch(clauses[0].pred,clauses[0].conseq,expr.otherwise)
                else:
                    false_val = Zero_Test(Const(1))
                    return Branch(clauses[0].pred,clauses[0].conseq,false_val)
            else:
                return Branch(clauses[0].pred,clauses[0].conseq,expand(clauses[1:]))
        return value_of(expand(expr.clauses),env,store)
    elif isinstance(expr,List):
        return value_of(Apply(Var('list'),tuple(expr.exps)),env,store)
    elif isinstance(expr,Pair_Exp):
        return value_of(Apply(Var('cons'),(expr.left,expr.right)),env,store)
    elif isinstance(expr,Unpack_Exp):
        if expr.vars is None or expr.expr is None:
            raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
        return value_of(Apply(operator = Proc_Exp(expr.vars,expr.expr),
                                operand  = (Unpack_Exp(None,expr.list_expr,None),)
                                ),env,store)
    elif isinstance(expr,Let):
        return value_of(Apply(Proc_Exp(expr.vars, expr.body), expr.exps),env,store)
    elif isinstance(expr,Let_Star):
        def expand(vars,exprs):
            if vars == ():
                return expr.body
            else:
                return Let([vars[0]],[exprs[0]],expand(vars[1:],exprs[1:]))
        return value_of(expand(expr.vars,expr.exps),env,store)
    else:
        raise Exception("Uknown LET expression type",expr)