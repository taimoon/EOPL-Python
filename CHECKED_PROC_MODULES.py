from LET_ast_node import *
from LET_parser import parser
from LET import expand_let_star
from LET_environment import (
    Environment,
    init_tenv,
    extend_tenv_with_module,
    lookup_module_tenv,
)
from CHECKED_OPAQUE import CHECKED as CHECKED_OPAQUE


def type_of_prog(prog,env = init_tenv(),parse = parser.parse):
    return CHECKED().type_of_prog(prog,env,parse)

def type_of(prog,env):
    return CHECKED().type_of(prog,env)


def fresh_name():
    from itertools import product
    from string import ascii_lowercase
    for c in product(ascii_lowercase,repeat = 3):
        yield ''.join(c)
        

class CHECKED:
    fresh_name = fresh_name()
    def type_of_prog(self,prog,env = init_tenv(),parse = parser.parse):
        return CHECKED_OPAQUE.type_of_prog(self,prog,env,parse)
    
    def check_equal_type(self,t1,t2,exp):
        return CHECKED_OPAQUE.check_equal_type(self,t1,t2,exp)
        
    def type_of(self,expr,tenv):
        return CHECKED_OPAQUE.type_of(self,expr,tenv)

    def rec_proc_to_tenv(self,exp:Rec_Proc,tenv:Environment) -> Environment:
        return CHECKED_OPAQUE.rec_proc_to_tenv(self,exp,tenv)

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
                raise Exception(f"Does not satisfy interface\nresult\t\t: {interface}\nexpected\t: {module.interface}")
            
            if isinstance(module.interface,Proc_Interface):
                decls = module.interface
            else:
                decls = expand_interface(module.name,module.interface,tenv)
            tenv = extend_tenv_with_module(module.name,decls,tenv)
        
        return tenv

    def let_exp_to_tenv(self,exp:Let_Exp|Let_Star_Exp|Rec_Proc,tenv:Environment):
        return CHECKED_OPAQUE.let_exp_to_tenv(self,exp,tenv)

    def interface_of(self,body:Module_Body_T,tenv:Environment) -> tuple[Decl_Type]:
        interface_of = self.interface_of
        interface_comp = self.interface_comp
        rename_interface = self.rename_interface
        defs_to_decls = self.defs_to_decls
        expand_interface = self.expand_interface
        if isinstance(body,Var_Module_Body):
            return lookup_module_tenv(body.name)
        elif isinstance(body,Proc_Module_Body):
            new_env = tenv
            
            params = body.params
            interfaces = body.interfaces
            body = body.body
            
            for param,iface in zip(params,interfaces):
                iface = expand_interface(param,iface,new_env)
                new_env = extend_tenv_with_module(param,iface,new_env)
            
            body_iface = interface_of(body,new_env)
            return Proc_Interface(params,interfaces,body_iface)
        elif isinstance(body,App_Module_Body):
            proc_iface = lookup_module_tenv(body.operator,tenv)
            if not isinstance(proc_iface,Proc_Interface):
                raise Exception(f"Operator Module is not procedural module {body.operator} {proc_iface}")
            
            modules = tuple(lookup_module_tenv(defn,tenv) for defn in body.operands)
            for actual,expected in zip(modules,proc_iface.interfaces):
                if not interface_comp(actual,expected,tenv):
                    raise Exception(f"Does not satisfy interface {actual} {expected}")
            
            res_interface = proc_iface.res_interface
            for param,name in zip(proc_iface.params, body.operands):
                res_interface = rename_interface(res_interface,param,name)
            return res_interface
        elif isinstance(body[0],Def_Type):
            return defs_to_decls(body,tenv)
        else:
            print(body)
            raise NotImplementedError

    def fresh_name_module(self,name):
        fresh_name = CHECKED.fresh_name
        return f'%fresh_name_{name}_{next(fresh_name)}'

    def interface_comp(self,actual,expected,tenv) -> bool:
        fresh_name_module = self.fresh_name_module
        interface_comp = self.interface_comp
        rename_interface = self.rename_interface
        expand_interface = self.expand_interface
        decls_comp = self.decls_comp
        def is_simple_interface(t):
            return isinstance(t,tuple) and isinstance(t[0],Decl_Type)
        areinstance = lambda type,*args: all(isinstance(arg,type) for arg in args)
        # if isinstance(actual,Proc_Interface) and isinstance(expected,Proc_Interface):
        if areinstance(Proc_Interface,actual,expected):
            new_tenv = tenv
            res_iface1 = actual.res_interface
            res_iface2 = expected.res_interface
            it = zip(actual.params,expected.params,actual.interfaces,expected.interfaces)
            for param1,param2,iface1,iface2 in it:
                new_name = fresh_name_module(param1)
                res_iface1 = rename_interface(res_iface1,param1,new_name)
                res_iface2 = rename_interface(res_iface2,param2,new_name)
                if not interface_comp(iface2,iface1,new_tenv):
                    return False
                iface1 = expand_interface(new_name,iface1,tenv)
                new_tenv = extend_tenv_with_module(new_name,iface1,new_tenv)
            
            return interface_comp(res_iface1,res_iface2,new_tenv)
        elif is_simple_interface(actual) and is_simple_interface(expected):
            return decls_comp(actual,expected,tenv)
        else:
            print(type(actual),type(expected))
            raise NotImplementedError

    def rename_type(self,type,name,new_name):
        rename_type = self.rename_type
        if isinstance(type,Proc_Type):
            arg_type = tuple(rename_type(arg_t,name,new_name) for arg_t in type.arg_type)
            res_type = rename_type(type.res_type,name,new_name)
            return Proc_Type(arg_type,res_type)
        elif isinstance(type,Qualified_Type):
            new_name = new_name if type.module_name == name else name
            return Qualified_Type(new_name,type.type_name)
        else:
            return type

    def rename_interface(self,interface:tuple[Decl_Type],name,new_name):
        rename_type = self.rename_type
        def rename(decl:Decl_Type,name=name,new_name=new_name):
            if isinstance(decl,Var_Decl|Transparent_Type_Decl):
                new_type = rename_type(decl.type,name,new_name)
                return decl.__class__(decl.name,new_type)
            elif isinstance(decl,Opaque_Type_Decl):
                new_name = name if decl.name == name else new_name
                return Opaque_Type_Decl(new_name)
            else:
                raise NotImplementedError
        return tuple(rename(decl) for decl in interface)
            


    def defs_to_decls(self,defs:tuple[Def_Type],tenv:Environment) -> tuple[Decl_Type]:
        return CHECKED_OPAQUE.defs_to_decls(self,defs,tenv)


    def subset_interface(self,actual:tuple[Var_Decl],expected:tuple[Var_Decl]):
        return CHECKED_OPAQUE.subset_interface(self,actual,expected)


    def expand_type(self,type,tenv:Environment):
        return CHECKED_OPAQUE.expand_type(self,type,tenv)


    def expand_types(self,types,tenv:Environment):
        return CHECKED_OPAQUE.expand_types(self,types,tenv)


    def is_equiv_type(self,t1,t2,tenv):
        return CHECKED_OPAQUE.is_equiv_type(self,t1,t2,tenv)


    def decls_comp(self,actual:tuple[Decl_Type],expected:tuple[Decl_Type],tenv:Environment):
        return CHECKED_OPAQUE.decls_comp(self,actual,expected,tenv)


    def decl_satisfy(self,left:Decl_Type,right:Decl_Type,tenv):
        return CHECKED_OPAQUE.decl_satisfy(self,left,right,tenv)

    def expand_interface(self,module_name,decls:tuple[Decl_Type],tenv:Environment) -> tuple[Decl_Type]:
        return CHECKED_OPAQUE.expand_interface(self,module_name,decls,tenv)


    def extend_tenv_with_decl(self,decl,tenv) -> Environment:
        return CHECKED_OPAQUE.extend_tenv_with_decl(self,decl,tenv)

