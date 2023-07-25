from LET_ast_node import *
from LET_parser import parser
from LET_environment import *


def value_of_prog(prog, env = init_env(), parse = parser.parse):
    prog = parse(prog)
    if isinstance(prog,Program):
        return value_of(prog.expr,add_modules_to_env(prog.modules,env))
    else:
        return value_of(prog, env)

def apply_proc(proc:Proc_Val|Primitve_Implementation,args,env):
    if isinstance(proc,Primitve_Implementation):
        return apply_primitive(proc,args)
    env = extend_env_from_pairs(tuple(proc.params),tuple(args),env)
    return value_of(proc.body, env)

def apply_primitive(prim:Primitive_Exp,args):
    return prim.op(*args)

def expand_let_star(expr:Let_Star_Exp):
    def recur(vars,exps):
        if vars == ():
            return expr.body
        else:
            return Let_Exp((vars[0],),(exps[0],),recur(vars[1:],exps[1:]))
    return recur(expr.vars,expr.exps)

def value_of(expr, env):    
    if isinstance(expr, Const_Exp):
        return expr.val
    elif isinstance(expr, Var_Exp):
        return apply_env(env, expr.var)
    elif isinstance(expr, Diff_Exp):
        return value_of(expr.left,env) - value_of(expr.right,env)
    elif isinstance(expr, Zero_Test_Exp):
        return value_of(expr.exp,env) == 0
    elif isinstance(expr, Branch):
        if value_of(expr.pred,env) is True:
            return value_of(expr.conseq,env)
        else:
            return value_of(expr.alter,env)
    elif isinstance(expr, Proc_Exp):
        # return Proc_Val(expr.params,expr.body,empty_env()) # dynamic scoping
        return Proc_Val(expr.params,expr.body,env) # lexical scoping
    elif isinstance(expr, App_Exp):
        proc = value_of(expr.operator,env)
        if len(expr.operand) == 1 and isinstance(expr.operand[0],Unpack_Exp):
            args = value_of(expr.operand[0].list_expr,env)
        else:
            args = map(lambda o : value_of(o, env), expr.operand)
        return apply_proc(proc,args,proc.env) # lexical scoping
    elif isinstance(expr, Rec_Proc):
        return value_of(expr.expr, extend_env_rec_multi(expr.var,expr.params,expr.body,env))
    elif isinstance(expr,Pair_Exp):
        return Pair(value_of(expr.left,env),
                    value_of(expr.right,env))
    elif isinstance(expr,Unpair_Exp):
        pair:Pair = value_of(expr.pair_exp,env)
        env = extend_env(expr.left,pair.car,env)
        env = extend_env(expr.right,pair.cdr,env)
        return value_of(expr.expr,env)
    elif isinstance(expr,Qualified_Var_Exp):
        return lookup_qualified_var(expr.module_name,expr.var_name,env)
    # Derived Form
    elif isinstance(expr,Let_Exp):
        # return value_of(expr.body, extend_env(expr.var, value_of(expr.exp,env), env))
        # as derived form
        return value_of(App_Exp(Proc_Exp(expr.vars, expr.body), expr.exps), env)
    elif isinstance(expr,Let_Star_Exp):
        return value_of(expand_let_star(expr),env)
    elif isinstance(expr,Conditional):
        def expand(clauses:tuple[Clause],otherwise=expr.otherwise):
            if clauses[1:] == ():
                otherwise = Zero_Test_Exp(Const_Exp(1)) if otherwise is None else otherwise
                return Branch(clauses[0].pred,clauses[0].conseq,otherwise)
            else:
                return Branch(clauses[0].pred,clauses[0].conseq,expand(clauses[1:]))
        return value_of(expand(expr.clauses),env)
    elif isinstance(expr, Primitive_Exp):
        return value_of(App_Exp(Var_Exp(expr.op),expr.exps),env)
    elif isinstance(expr,List):
        return value_of(App_Exp(Var_Exp('list'),expr.exps),env)
    elif isinstance(expr,Unpack_Exp):
        if expr.vars is None or expr.expr is None:
            raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
        return value_of(App_Exp(operator = Proc_Exp(expr.vars,expr.expr),
                                operand  = (Unpack_Exp(None,expr.list_expr,None),))
                        ,env)
    else:
        raise Exception("Uknown LET expression type", expr)

def add_modules_to_env(modules:tuple[Module_Def],env):
    'accumulate module bindings to env'
    for module in modules:
        local_env = add_modules_to_env(module.modules,env) # TODO : check correctness
        local_env = let_exp_to_env(module.let_block,local_env)
        bindings = value_of_module_body(module.body,local_env)
        env = extend_env_with_module(module.name,bindings,env)
    return env

def let_exp_to_env(exp:Let_Exp|Let_Star_Exp|Rec_Proc,env:Environment):
    if isinstance(exp,Let_Star_Exp):
        return let_exp_to_env(expand_let_star(exp),env)
    elif isinstance(exp,Let_Exp):
        vals = tuple(value_of(exp,env) for exp in exp.exps)
        return extend_env_from_pairs(exp.vars,vals,env)
    elif isinstance(exp,Rec_Proc):
        return extend_env_rec_multi(exp.var,exp.params,exp.body,env)
    else:
        return env

def value_of_module_body(defs:Module_Body_T,env:Environment) -> Environment:
    if isinstance(defs,Var_Module_Body):
        return lookup_module_name(defs.name,env)
    elif isinstance(defs,Proc_Module_Body):
        return Proc_Module(defs.params,defs.body,env)
    elif isinstance(defs,App_Module_Body):
        module_proc:Proc_Module = lookup_module_name(defs.operator,env)
        if not isinstance(module_proc,Proc_Module):
            raise Exception(f"Operator Module is not procedural module {defs.operator}")
        modules = tuple(lookup_module_name(defn,env) for defn in defs.operands)
        new_env = module_proc.env
        for module_name,module in zip(module_proc.params,modules):
            new_env = extend_env_with_module(module_name,module,new_env)
        return value_of_module_body(module_proc.body,new_env)
    elif isinstance(defs[0],Def_Type):
        return definitions_to_env(defs,env)
    else:
        raise NotImplemented()

def definitions_to_env(defs:tuple[Var_Def],env:Environment) -> Environment:
    # must be recursive
    'let* semantic'
    def recur(defs:tuple[Var_Def],env:Environment) -> Environment:
        
        if defs == tuple():
            return empty_env()
        elif isinstance(defs[0],Type_Def):
            return recur(defs[1:],env)
        else:
            var = defs[0].name
            val = value_of(defs[0].expr,env)
            new_env = extend_env(var,val,env)
            return extend_env(var,val,recur(defs[1:],new_env))
    return recur(defs,env)
