from LET_ast_node import *
from LET_parser import parser
from LET import (
    Let_Interpreter,
    expand_let_star)

from LET_environment import (
        Environment,
        empty_env,
        init_env,
        extend_env_from_pairs,
        extend_env_rec_multi,
        lookup_qualified_var,
        lookup_module_name,
        extend_env_with_module,
    )

def value_of_prog(prog,env = init_env(),parse = parser.parse):
    return Modules_Interpreter().value_of_prog(prog,env,parse)
               
class Modules_Interpreter:
    def value_of_prog(self,prog,env = init_env(),parse = parser.parse):
        value_of = self.value_of
        add_modules_to_env = self.add_modules_to_env
        prog = parse(prog)
        if isinstance(prog,Program):
            return value_of(prog.expr,add_modules_to_env(prog.modules,env))
        else:
            return value_of(prog,env)
    
    def apply_primitive(self,prim:Primitive_Exp,args):
        return Let_Interpreter.apply_primitive(self,prim,args)
    
    def apply_proc(self,proc:Proc_Val|Primitve_Implementation,args):
        return Let_Interpreter.apply_proc(self,proc,args)
    
    def value_of(self,expr,env):
        if isinstance(expr,Qualified_Var_Exp):
            return lookup_qualified_var(expr.module_name,expr.var_name,env)
        else:
            return Let_Interpreter.value_of(self,expr,env)

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

