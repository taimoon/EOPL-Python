from LET_ast_node import *
from LET_parser import parser
from LET import expand_let_star
from LET_environment import (
    Environment,
    init_tenv,
    extend_tenv_from_pairs,
    extend_tenv_with_module,
    lookup_qualified_type,
)
from CHECKED import CHECKED as BASE_CHECKED

def type_of_prog(prog,env = init_tenv(),parse = parser.parse):
    return CHECKED().type_of_prog(prog,env,parse)


class CHECKED:
    'CHECKED SIMPLE MODULES version, check neither user-defined type nor procedural type'
    def type_of_prog(self,prog,env = init_tenv(),parse = parser.parse):
        add_modules_to_tenv = self.add_modules_to_tenv
        type_of = self.type_of
        prog = parse(prog)
        if isinstance(prog,Program):
            return type_of(prog.expr,add_modules_to_tenv(prog.modules,env))
        else:
            return type_of(prog,env)
    
    def check_equal_type(self,t1,t2,exp):
        return BASE_CHECKED.check_equal_type(self,t1,t2,exp)
        
    def type_of(self,expr,tenv):
        if isinstance(expr,Qualified_Var_Exp):
            return lookup_qualified_type(expr.module_name,expr.var_name,tenv)
        else:
            return BASE_CHECKED.type_of(self,expr,tenv)

    def rec_proc_to_tenv(self,exp:Rec_Proc,tenv:Environment) -> Environment:
        return BASE_CHECKED.rec_proc_to_tenv(self,exp,tenv)

    
    def report_unsatisfy_interface(self,actual,expected):
        print("Does not satisfy interface")
        print(f"result\t\t: {actual}")
        print(f"expected\t: {expected}")
        raise Exception
    
    def add_modules_to_tenv(self,modules:tuple[Module_Def],tenv):
        add_modules_to_tenv = self.add_modules_to_tenv
        let_exp_to_tenv = self.let_exp_to_tenv
        interface_of = self.interface_of
        interface_comp = self.interface_comp
        for module in modules:
            local_tenv = add_modules_to_tenv(module.modules,tenv) 
            local_tenv = let_exp_to_tenv(module.let_block,local_tenv)
            interface = interface_of(module.body,local_tenv)
            
            if not interface_comp(interface,module.interface,tenv):
                self.report_unsatisfy_interface(interface,module.interface)
            
            decls = module.interface
            
            tenv = extend_tenv_with_module(module.name,decls,tenv)
        
        return tenv

    def let_exp_to_tenv(self,exp:Let|Let_Star|Rec_Proc,tenv:Environment):
        let_exp_to_tenv = self.let_exp_to_tenv
        type_of = self.type_of
        if isinstance(exp,Let):
            vals = tuple(type_of(exp,tenv) for exp in exp.exps)
            return extend_tenv_from_pairs(exp.vars,vals,tenv)
        elif isinstance(exp,Let_Star):
            return let_exp_to_tenv(expand_let_star(exp),tenv)
        elif isinstance(exp,Rec_Proc):
            rec_proc_to_tenv = self.rec_proc_to_tenv
            return rec_proc_to_tenv(exp,tenv)
        else:
            return tenv


    def interface_of(self,body:Module_Body_T,tenv:Environment) -> tuple[Decl_Type]:
        if isinstance(body[0],Def_Type):
            return self.defs_to_decls(body,tenv)
        else:
            print(body)
            raise NotImplementedError
    
    def defs_to_decls(self,defs:tuple[Def_Type],tenv:Environment) -> tuple[Decl_Type]:
        defs_to_decls = self.defs_to_decls
        type_of = self.type_of
        if defs == tuple():
            return tuple()
        elif isinstance(defs[0],Var_Def):
            name = defs[0].name
            type = type_of(defs[0].expr,tenv)
            
            new_tenv = extend_tenv_from_pairs((name,),(type,),tenv)
            decls = defs_to_decls(defs[1:],new_tenv)
            decl = Var_Decl(name,type)
            
            return (decl,) + decls
        else:
            raise Exception(defs,tenv)
    
    def interface_comp(self,actual,expected,tenv) -> bool:
        decls_comp = self.decls_comp
        def is_simple_interface(t):
            return isinstance(t,tuple) and isinstance(t[0],Decl_Type)
        if is_simple_interface(actual) and is_simple_interface(expected):
            return decls_comp(actual,expected,tenv)
        else:
            print(type(actual),type(expected))
            raise NotImplementedError
    
    def decls_comp(self,actual:tuple[Var_Decl],expected:tuple[Var_Decl],tenv:Environment):
        '''
        Used for untyped modules
        Assumption : order must be same for actual and expected
        
        actual < expected
        
        interface that satisfies actual also satisfy expected.
        
        decl satisfy decls_1 implies decl can satisfy decls_2
        '''
        def recur(decls_1:tuple[Var_Decl],decls_2:tuple[Var_Decl]):
            if decls_2 == tuple():
                return True
            elif decls_1 == tuple():
                return False
            elif decls_1[0].name != decls_2[0].name:
                return recur(decls_1[1:],decls_2)
            elif decls_1[0].type != decls_2[0].type:
                return False
            else:
                return recur(decls_1[1:],decls_2[1:])
            
        return recur(actual,expected)

    def extend_tenv_with_decl(self,decl,tenv) -> Environment:
        if isinstance(decl,Var_Decl):
            return tenv
        else:
            raise NotImplementedError
    

    def is_equiv_type(self,t1,t2,tenv = None):
        return t1 == t2

    def decl_satisfy(self,left:Decl_Type,right:Decl_Type,tenv):
        is_equiv_type = self.is_equiv_type
        return ((isinstance(left,Var_Decl) 
                and isinstance(right,Var_Decl) 
                and is_equiv_type(left.type,right.type,tenv)))

