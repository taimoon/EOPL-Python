from LET_ast_node import *
from LET_parser import parser
from LET_environment import (
        Environment,
        empty_env,
        init_env,
        apply_env,
        extend_env_from_pairs,
        extend_env_rec_multi,
        lookup_qualified_var,
        lookup_module_name,
        extend_env_with_module,
    )

def value_of_prog(prog,env = init_env(),parse = parser.parse):
    return Let_Interpreter().value_of_prog(prog,env,parse)

def expand_let_star(expr:Let_Star_Exp):
    def recur(vars,exps):
        if vars == ():
            return expr.body
        else:
            return Let_Exp((vars[0],),(exps[0],),recur(vars[1:],exps[1:]))
    return recur(expr.vars,expr.exps)

def expand_conditional(expr:Conditional):

    def expand(clauses:tuple[Clause],otherwise):
        if clauses[1:] == ():
            otherwise = Zero_Test_Exp(Const_Exp(1)) if otherwise is None else otherwise
            return Branch(clauses[0].pred,clauses[0].conseq,otherwise)
        else:
            return Branch(clauses[0].pred,clauses[0].conseq,expand(clauses[1:],otherwise))
    
    return expand(expr.clauses,expr.otherwise)
                
class Let_Interpreter:
    def value_of_prog(self,prog,env = init_env(),parse = parser.parse):
        value_of = self.value_of
        add_modules_to_env = self.add_modules_to_env
        prog = parse(prog)
        if isinstance(prog,Program):
            return value_of(prog.expr,add_modules_to_env(prog.modules,env))
        else:
            return value_of(prog,env)
    
    def apply_primitive(self,prim:Primitive_Exp,args):
        return prim.op(*args)
    
    def apply_proc(self,proc:Proc_Val|Primitve_Implementation,args,env):
        if isinstance(proc,Primitve_Implementation):
            return Let_Interpreter.apply_primitive(self,proc,args)
        else:
            env = extend_env_from_pairs(tuple(proc.params),tuple(args),env)
            return self.value_of(proc.body, env)
    
    def value_of(self,expr,env):
        value_of = self.value_of
        apply_proc = self.apply_proc
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
            return value_of(App_Exp(Var_Exp('cons'),(expr.left,expr.right)),env)
        elif isinstance(expr,Unpair_Exp):
            pair:Pair = value_of(expr.pair_exp,env)
            vars = expr.left,expr.right
            vals = pair.car,pair.cdr
            env = extend_env_from_pairs(vars,vals,env)
            return value_of(expr.expr,env)
        elif isinstance(expr,Qualified_Var_Exp):
            return lookup_qualified_var(expr.module_name,expr.var_name,env)
        # Derived Form
        elif isinstance(expr,Let_Exp):
            # return value_of(expr.body, extend_env(expr.var, value_of(expr.exp,env), env))
            # as derived form
            return value_of(App_Exp(Proc_Exp(expr.vars,expr.body),expr.exps),env)
        elif isinstance(expr,Let_Star_Exp):
            return value_of(expand_let_star(expr),env)
        elif isinstance(expr,Conditional):
            return value_of(expand_conditional(expr),env)
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
        elif isinstance(expr,Null_Exp):
            return value_of(App_Exp(Var_Exp('null?'),(expr.expr,)),env)
        else:
            raise Exception("Uknown LET expression type", expr)

    def add_modules_to_env(self,modules:tuple[Module_Def],env):
        'accumulate module bindings to env'
        for module in modules:
            local_env = self.add_modules_to_env(module.modules,env) # TODO : check correctness
            local_env = self.let_exp_to_env(module.let_block,local_env)
            bindings = self.value_of_module_body(module.body,local_env)
            env = extend_env_with_module(module.name,bindings,env)
        return env

    def let_exp_to_env(self,exp:Let_Exp|Let_Star_Exp|Rec_Proc,env:Environment):
        value_of = self.value_of
        if isinstance(exp,Let_Star_Exp):
            return self.let_exp_to_env(expand_let_star(exp),env)
        elif isinstance(exp,Let_Exp):
            vals = tuple(value_of(exp,env) for exp in exp.exps)
            return extend_env_from_pairs(exp.vars,vals,env)
        elif isinstance(exp,Rec_Proc):
            return extend_env_rec_multi(exp.var,exp.params,exp.body,env)
        else:
            return env

    def value_of_module_body(self,defs:Module_Body_T,env:Environment) -> Environment:
        value_of_module_body = self.value_of_module_body
        definitions_to_env = self.definitions_to_env
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

    def definitions_to_env(self,defs:tuple[Var_Def],env:Environment) -> Environment:
        # must be recursive
        'let* semantic'
        value_of = self.value_of
        recur = self.definitions_to_env
        if defs == tuple():
            return empty_env()
        elif isinstance(defs[0],Type_Def):
            return recur(defs[1:],env)
        else:
            var = defs[0].name
            val = value_of(defs[0].expr,env)
            new_env = extend_env_from_pairs((var,),(val,),env)
            return extend_env_from_pairs((var,),(val,),recur(defs[1:],new_env))

