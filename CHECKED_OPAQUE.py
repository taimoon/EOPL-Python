from LET_ast_node import *
from LET_parser import parser
from LET_environment import (
    Environment,
    init_tenv,
    extend_tenv_from_pairs,
    lookup_qualified_type,
    extend_tenv_with_module,
    lookup_type_name,
)
from CHECKED_MODULES import CHECKED as CHECKED_MODULES

def type_of_prog(prog,env = init_tenv(),parse = parser.parse):
    return CHECKED().type_of_prog(prog,env,parse)

class CHECKED:
    def type_of_prog(self,prog,env = init_tenv(),parse = parser.parse):
        return CHECKED_MODULES.type_of_prog(self,prog,env,parse)
    
    def check_equal_type(self,t1,t2,exp):
        return CHECKED_MODULES.check_equal_type(self,t1,t2,exp)
        
    def type_of(self,expr,tenv):
        type_of = self.type_of
        expand_types = self.expand_types
        
        # TODO - move expand_types
        if isinstance(expr, Proc_Exp): 
            ext_env = extend_tenv_from_pairs(expr.params, expand_types(expr.types,tenv), tenv)
            arg_type = expand_types(expr.types,tenv)
            res_type = type_of(expr.body,ext_env)
            return Proc_Type(arg_type,res_type)
        elif isinstance(expr,Unpair_Exp):
            t = type_of(expr.pair_exp,tenv)
            if not isinstance(t,Pair_Type):
                raise Exception(f"the expression is not pair for UNPAIR {expr}")
            ts = expand_types((t.t0,t.t1),tenv)
            vars = expr.left,expr.right
            tenv = extend_tenv_from_pairs(vars,ts,tenv)
            return type_of(expr.expr,tenv)
        else:
            return CHECKED_MODULES.type_of(self,expr,tenv)

    def rec_proc_to_tenv(self,exp:Rec_Proc,tenv:Environment) -> Environment:
        return CHECKED_MODULES.rec_proc_to_tenv(self,exp,tenv)

    def report_unsatisfy_interface(self,actual,expected):
        CHECKED_MODULES.report_unsatisfy_interface(self,actual,expected)
    
    def add_modules_to_tenv(self,modules:tuple[Module_Def],tenv):
        add_modules_to_tenv = self.add_modules_to_tenv
        let_exp_to_tenv = self.let_exp_to_tenv
        interface_of = self.interface_of
        interface_comp = self.interface_comp
        expand_interface = self.expand_interface
        
        for module in modules:
            local_tenv = add_modules_to_tenv(module.modules,tenv) 
            local_tenv = let_exp_to_tenv(module.let_block,local_tenv)
            interface = interface_of(module.body,local_tenv)
            if not interface_comp(interface,module.interface,tenv):
                self.report_unsatisfy_interface(interface,module.interface)

            decls = expand_interface(module.name,module.interface,tenv)
            tenv = extend_tenv_with_module(module.name,decls,tenv)
        
        return tenv

    def let_exp_to_tenv(self,exp:Let_Exp|Let_Star_Exp|Rec_Proc,tenv:Environment):
        return CHECKED_MODULES.let_exp_to_tenv(self,exp,tenv)

    def interface_of(self,body:Module_Body_T,tenv:Environment) -> tuple[Decl_Type]:
        return CHECKED_MODULES.interface_of(self,body,tenv)

    def interface_comp(self,actual,expected,tenv) -> bool:
        return CHECKED_MODULES.interface_comp(self,actual,expected,tenv)

    def defs_to_decls(self,defs:tuple[Def_Type],tenv:Environment) -> tuple[Decl_Type]:
        defs_to_decls = self.defs_to_decls
        expand_type = self.expand_type
        if defs == tuple():
            return tuple()
        elif isinstance(defs[0],Type_Def):
            name,type = defs[0].name,defs[0].type
            invariant_ty = expand_type(type,tenv)
            new_tenv = extend_tenv_from_pairs((name,),(invariant_ty,),tenv)
            decl = Transparent_Type_Decl(name,type)
            return (decl,) + defs_to_decls(defs[1:],new_tenv)
        else:
            return CHECKED_MODULES.defs_to_decls(self,defs,tenv)

    def expand_type(self,type,tenv:Environment):
        expand_type = self.expand_type
        if isinstance(type,Int_Type|Bool_Type|Void_Type|No_Type):
            return type.__class__()
        elif isinstance(type,Pair_Type):
            return Pair_Type(
                expand_type(type.t0,tenv),
                expand_type(type.t1,tenv)
            )
        elif isinstance(type,List_Type):
            return List_Type(expand_type(type.t,tenv))
        elif isinstance(type,Proc_Type):
            return Proc_Type(
                tuple(expand_type(arg_t,tenv) for arg_t in type.arg_type),
                expand_type(type.res_type,tenv)
            )
        elif isinstance(type,Named_Type):
            return lookup_type_name(type.name,tenv)
        elif isinstance(type,Qualified_Type):
            return lookup_qualified_type(type.module_name,type.type_name,tenv)
        else:
            print(type)
            raise Exception()


    def expand_types(self,types,tenv:Environment):
        expand_type = self.expand_type
        return tuple(expand_type(t,tenv) for t in types)


    def is_equiv_type(self,t1,t2,tenv):
        expand_type = self.expand_type
        return expand_type(t1,tenv) == expand_type(t2,tenv)


    def decls_comp(self,actual:tuple[Decl_Type],expected:tuple[Decl_Type],tenv:Environment):
        '''
        Used for typed modules
        Assumption : order must be same for actual and expected
        
        actual < expected
        
        interface that satisfies actual also satisfy expected.
        
        decl satisfy decls_1 implies decl can satisfy decls_2
        '''
        decl_satisfy = self.decl_satisfy
        extend_tenv_with_decl = self.extend_tenv_with_decl
        def recur(decls_1:tuple[Decl_Type],decls_2:tuple[Decl_Type],tenv:Environment):
            if decls_2 == tuple():
                return True
            elif decls_1 == tuple():
                return False
            elif decls_1[0].name != decls_2[0].name:
                ext_tenv = extend_tenv_with_decl(decls_1[0],tenv)
                return recur(decls_1[1:],decls_2,ext_tenv)
            else:
                ext_tenv = extend_tenv_with_decl(decls_1[0],tenv)
                return (decl_satisfy(decls_1[0],decls_2[0],ext_tenv) 
                        and recur(decls_1[1:],decls_2[1:],ext_tenv))
            
        return recur(actual,expected,tenv)


    def decl_satisfy(self,left:Decl_Type,right:Decl_Type,tenv) -> bool:
        is_equiv_type = self.is_equiv_type
        return ((isinstance(left,Var_Decl) 
                and isinstance(right,Var_Decl) 
                and is_equiv_type(left.type,right.type,tenv))
                or (isinstance(left,Transparent_Type_Decl) 
                    and isinstance(right,Transparent_Type_Decl) 
                    and is_equiv_type(left.type,right.type,tenv))
                or (isinstance(left,Transparent_Type_Decl|Opaque_Type_Decl) 
                    and isinstance(right,Opaque_Type_Decl)))

    def expand_interface(self,module_name,decls:tuple[Decl_Type],tenv:Environment) -> tuple[Decl_Type]:
        expand_interface = self.expand_interface
        expand_type = self.expand_type
        
        if decls == tuple(): 
            return tuple()
        elif isinstance(decls[0],Var_Decl):
            decl = Var_Decl(decls[0].name,expand_type(decls[0].type,tenv))
            return (decl,) + expand_interface(module_name,decls[1:],tenv) 
        elif isinstance(decls[0],Opaque_Type_Decl):
            expanded_type = Qualified_Type(module_name,decls[0].name)
            new_tenv = extend_tenv_from_pairs((decls[0].name,),(expanded_type,),tenv)
            decl = Transparent_Type_Decl(decls[0].name,expanded_type)
            return (decl,) + expand_interface(module_name,decls[1:],new_tenv)
        elif isinstance(decls[0],Transparent_Type_Decl):
            expanded_type = expand_type(decls[0].type,tenv)
            new_tenv = extend_tenv_from_pairs((decls[0].name,),(expanded_type,),tenv)
            decl = Transparent_Type_Decl(decls[0].name,expanded_type)
            return (decl,) + expand_interface(module_name,decls[1:],new_tenv)
        else:
            raise Exception(module_name,decls,tenv)


    def extend_tenv_with_decl(self,decl,tenv) -> Environment:
        expand_type = self.expand_type
        extend_tenv_with_type = lambda name,ty,tenv: extend_tenv_from_pairs((name,),(ty,),tenv)
        if isinstance(decl,Var_Decl):
            return tenv
        elif isinstance(decl,Transparent_Type_Decl):
            expanded_type = expand_type(decl.type,tenv)
            return extend_tenv_with_type(decl.name,expanded_type,tenv)
        elif isinstance(decl,Opaque_Type_Decl):
            expanded_type = Qualified_Type("%unknown",decl.name)
            return extend_tenv_with_type(decl.name,expanded_type,tenv)
            

