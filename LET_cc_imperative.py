from LET_parser import parser
from LET_environment import (
    extend_env_from_pairs,
    init_env,
    extend_env_rec_multi,
    apply_env,
)
from LET import expand_conditional,expand_let_star
from LET_ast_node import *
from continuation import *

@dataclass
class Registers:
    'Registers.exp is overloaded to store procedure value'
    exp:None = None
    env:Env = None
    val:None = None
    cc:Cont = None
    pc: None = None
    
    @property
    def proc(self):
        return self.exp
    
    @proc.setter
    def proc(self,val):
        self.exp = val

reg = Registers()

def trampoline():
    while reg.pc is not False:
        reg.pc()
    return reg.val

def value_of_prog(prog, env = init_env(), parse = parser.parse):
    reg.exp = parse(prog)
    reg.env = env
    reg.cc = End_Cont()
    reg.pc = value_of_k
    return trampoline()

def apply_cont():
    cc = reg.cc
    val = reg.val
    if isinstance(cc,End_Cont):
        reg.pc = False
    elif isinstance(cc,Diff_Cont1):
        reg.exp = cc.exp2
        reg.env = cc.env
        reg.cc = Diff_Cont2(cc.cc,val)
        reg.pc = value_of_k
    elif isinstance(cc,Diff_Cont2):
        reg.val = cc.v - val
        reg.cc = cc.cc
    elif isinstance(cc,Zero_Cont):
        reg.val = val == 0
        reg.cc = cc.cc
    elif isinstance(cc,Branch_Cont):
        if val is True:
            reg.exp = cc.conseq
        else:
            reg.exp = cc.alter
        reg.env = cc.env
        reg.cc = cc.cc
        reg.pc = value_of_k
    elif isinstance(cc,Paramless_Cont):
        reg.proc = val
        reg.val = ()
        reg.cc = cc.cc
        reg.pc = apply_proc_k
    elif isinstance(cc,Args_Cont):
        exps,acm_vals = cc.exps,cc.acm_vals
        if exps == ():
            reg.cc = cc.cc
            reg.proc = acm_vals[0]
            reg.val = acm_vals[1:] + [val]
            reg.pc = apply_proc_k
        else:
            reg.cc = Args_Cont(cc.cc,cc.env,exps[1:],acm_vals+[val])
            reg.exp = exps[0]
            reg.env = cc.env
            reg.pc = value_of_k
    elif isinstance(cc,Operator_Cont):
        reg.cc = Operand_Cont(cc.cc,val)
        reg.exp = cc.list_expr
        reg.env = cc.env
        reg.pc = value_of_k
    elif isinstance(cc,Operand_Cont):
        reg.proc = cc.proc
        reg.cc = cc.cc
        reg.pc = apply_proc_k
    elif isinstance(cc,Try_Cont):
        reg.cc = cc.cc
    elif isinstance(cc,Raise_Cont):        
        reg.pc = apply_handler
    else:
        print(cc)
        raise NotImplementedError

def apply_proc_k():
    proc,args = reg.proc,reg.val
    if isinstance(proc,Primitve_Implementation):
        reg.val = proc.op(*args)
        reg.pc = apply_cont
    else:
        reg.env = extend_env_from_pairs(proc.params,args,proc.env)
        reg.exp = proc.body 
        reg.pc = value_of_k

def value_of_k():
    expr,env,cc = reg.exp,reg.env,reg.cc
    if isinstance(expr, Const):
        reg.val = expr.val
        reg.pc = apply_cont
    elif isinstance(expr, Var):
        reg.val = apply_env(env,expr.var)
        reg.pc = apply_cont
    elif isinstance(expr, Diff_Exp):
        reg.cc = diff_cc1_ctor(expr.right,env,cc)
        reg.exp = expr.left
    elif isinstance(expr, Zero_Test):
        reg.cc = zero_cc_ctor(cc)
        reg.exp = expr.exp
    elif isinstance(expr, Branch):
        reg.cc = branch_cc_ctor(expr.conseq,expr.alter,env,cc)
        reg.exp = expr.pred
    elif isinstance(expr, Proc_Exp):
        reg.val = Proc_Val(expr.params,expr.body,env)
        reg.pc = apply_cont
    elif isinstance(expr, Apply):
        if expr.operand == ():
            reg.cc = paramless_cc_ctor(cc)
            reg.exp = expr.operator
        elif isinstance(expr.operand[0], Unpack_Exp):
            reg.exp = expr.operator
            reg.cc = operator_cc_ctor(expr.operand[0].list_expr,env,cc)
        else:
            reg.exp = expr.operator
            reg.cc = args_builder(expr.operand,[],env,cc)
    elif isinstance(expr, Rec_Proc):
        reg.exp = expr.expr
        reg.env = extend_env_rec_multi(expr.var,expr.params,expr.body,env)
    # exception
    elif isinstance(expr,Try):
        reg.exp = expr.exp
        reg.cc = try_cont(expr.var,expr.handler,env,cc)
    elif isinstance(expr,Raise):
        reg.exp = expr.exp
        reg.cc = raise_cont1(cc)
    # derived form
    elif isinstance(expr, Primitive):
        reg.exp = Apply(Var(expr.op),expr.exps)
    elif isinstance(expr,Conditional):
        reg.exp = expand_conditional(expr)
    elif isinstance(expr,List):
        reg.exp = Primitive('list',tuple(expr.exps))
    elif isinstance(expr,Pair_Exp):
        reg.exp = Apply(Var('cons'),(expr.left,expr.right))
    elif isinstance(expr,Let_Star):
        reg.exp = expand_let_star(expr)
    elif isinstance(expr,Let):
        reg.exp = Apply(Proc_Exp(expr.vars,expr.body),expr.exps)
    elif isinstance(expr,Unpack_Exp):
        if expr.vars is None or expr.expr is None:
            raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
        reg.exp = Apply(Proc_Exp(expr.vars,expr.expr),
                                  (Unpack_Exp(None,expr.list_expr,None),))
    elif isinstance(expr,Null_Exp):
        reg.exp = Apply(Var('null?'),(expr.expr,))
    else:
        raise Exception("Uknown LET expression type", expr)

def zero_cc_ctor(cc):
    return Zero_Cont(cc)

def branch_cc_ctor(conseq,alter,env,cc):
    return Branch_Cont(cc,env,conseq,alter)

def diff_cc1_ctor(exp2,env,cc):
    return Diff_Cont1(cc,env,exp2)

def args_builder(exps,acm_vals,env,cc):
    return Args_Cont(cc,env,exps,acm_vals)

def operator_cc_ctor(list_expr,env,cc):
    return Operator_Cont(cc,env,list_expr)

def paramless_cc_ctor(cc):
    return Paramless_Cont(cc)

def try_cont(var,handler,env,cc):
    return Try_Cont(cc,var,handler,env)

def raise_cont1(cc):
    return Raise_Cont(cc)

def apply_handler():
    val = reg.val
    cc = reg.cc
    if isinstance(cc,End_Cont):
        raise Exception("uncaught exception",val)
    elif isinstance(cc,Try_Cont):
        reg.env = extend_env_from_pairs((cc.var,),(val,),cc.env)
        reg.exp = cc.handler
        reg.cc = cc.cc
        reg.pc = value_of_k
    else:
        reg.cc = cc.cc
