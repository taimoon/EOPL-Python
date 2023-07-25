from LET_ast_node import *
from LET_parser import parser
from LET_environment import *

def check_equal_type(t1,t2,exp):
    if t1 != t2:
        raise Exception(f"Type didn't match [{t1}] [{t2}] [{exp}]")


def type_of_prog(prog, env = init_tenv(), parse = parser.parse):
    prog = parse(prog)
    if isinstance(prog,Program):
        return type_of(prog.expr,add_modules_to_tenv(prog.modules,env))
    else:
        return type_of(prog, env)


def type_of(expr, env):
    if isinstance(expr, Const_Exp) and isinstance(expr.val,NULL):
        '''
        workaround
        the No_Type NULL only acceptable in newpair
        but Typed NULL only acceptable in cons
        '''
        t = expr.val.t
        return t if isinstance(t,No_Type) else List_Type(t)
    elif isinstance(expr, Const_Exp):
        return Int_Type()
    elif isinstance(expr, Var_Exp):
        return apply_env(env, expr.var)  
    elif isinstance(expr, Diff_Exp):
        check_equal_type(type_of(expr.left,env),Int_Type(),expr.left)
        check_equal_type(type_of(expr.right,env),Int_Type(),expr.right)
        return Int_Type()
    elif isinstance(expr, Zero_Test_Exp):
        check_equal_type(type_of(expr.exp,env),Int_Type(),expr.exp)
        return Bool_Type
    elif isinstance(expr, Branch):
        check_equal_type(type_of(expr.pred,env), Bool_Type(),expr.pred)
        t1 = type_of(expr.conseq,env)
        t2 = type_of(expr.alter,env)
        check_equal_type(t1,t2,expr)
        return t1
    elif isinstance(expr, Proc_Exp): # TODO - move expand_types
        ext_env = extend_env_from_pairs(expr.params, expand_types(expr.types,env), env)
        res_t = type_of(expr.body,ext_env)
        return Proc_Type(expand_types(expr.types,env),
                         result_type=res_t)
    elif isinstance(expr, App_Exp):
        proc_t = type_of(expr.operator,env)
        if not isinstance(proc_t,Proc_Type):
            raise Exception(f"Operator is not a procedure type {proc_t} {expr.operator}")
        arg_types = tuple(map(lambda exp: type_of(exp,env),expr.operand))
        for param_t,arg_t in zip(proc_t.arg_type,arg_types):
            check_equal_type(param_t,arg_t,expr)
        
        return proc_t.result_type
    elif isinstance(expr, Rec_Proc):
        return type_of(expr.expr,rec_proc_to_tenv(expr,env))
    elif isinstance(expr,Pair_Exp):
        t0 = type_of(expr.left,env)
        t1 = type_of(expr.right,env)
        if expr.homogeneous is True:
            t0 = t0.t if isinstance(t0,List_Type) else t0
            t1 = t1.t if isinstance(t1,List_Type) else t1
            check_equal_type(t0,t1,expr)
            return List_Type(t0)
        else:
            return Pair_Type(t0,t1)
    elif isinstance(expr,Unpair_Exp):
        t = type_of(expr.pair_exp,env)
        if not isinstance(t,Pair_Type):
            raise Exception(f"the expression is not pair for UNPAIR {expr}")
        env = extend_env(expr.left,expand_type(t.t0,env),env)
        env = extend_env(expr.right,expand_type(t.t1,env),env)
        return type_of(expr.expr,env)
    elif isinstance(expr,List):
        types = tuple(map(lambda exp: type_of(exp,env), expr.exps))
        t0 = types[0]
        for t in types[1:]:
            check_equal_type(t0,t,expr)
        return List_Type(t0)
    elif isinstance(expr,Null_Exp):
        return Bool_Type()
    elif isinstance(expr,Qualified_Var_Exp):
        return lookup_qualified_type(expr.module_name,expr.var_name,env)
    # Statement
    elif isinstance(expr,Sequence):
        t = None
        for exp in expr.exps:
            t = type_of(exp,env)
        return Void_Type() if t is None else t
    elif isinstance(expr,NewRef):
        return Void_Type()
    elif isinstance(expr,DeRef):
        t = type_of(expr.expr,env)
        check_equal_type(t,Int_Type(),expr.expr)
        return No_Type()
    elif isinstance(expr,SetRef):
        ref_t = type_of(expr.loc,env)
        check_equal_type(ref_t,Int_Type(),expr.loc)
        return Void_Type()
    # Derived Form
    elif isinstance(expr,Let_Exp):
        types = tuple(type_of(exp,env) for exp in expr.exps)
        return type_of(App_Exp(Proc_Exp(expr.vars,expr.body,types),expr.exps),env)
    elif isinstance(expr,Let_Star_Exp):
        return type_of(expand_let_star(expr),env)
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
        return type_of(expand(expr.clauses),env)
    elif isinstance(expr, Primitive_Exp):
        if expr.op == 'car':
            t = type_of(expr.exps[0],env)
            t = t.t if isinstance(t,List_Type) else t
            t = t.t0 if isinstance(t,Pair_Type) else t
            return t
        elif expr.op == 'cdr':
            t = type_of(expr.exps[0],env)
            t = t.t1 if isinstance(t,Pair_Type) else t
            return t
        return type_of(App_Exp(Var_Exp(expr.op),expr.exps),env)
    elif isinstance(expr,Unpack_Exp):
        if expr.vars is None or expr.expr is None:
            raise Exception("Ill-formed : Isolated Unpack Exp due to not in application expression")
        return type_of(App_Exp(operator = Proc_Exp(expr.vars,expr.expr),
                                operand  = (Unpack_Exp(None,expr.list_expr,None),)
                                ),env)
    else:
        raise Exception("Unknown CHECKED expression type", expr)

def expand_let_star(exp:Let_Star_Exp):
    def recur(vars,exps):
        if vars == ():
            return exp.body
        else:
            return Let_Exp((vars[0],),(exps[0],),recur(vars[1:],exps[1:]))
    return recur(exp.vars,exp.exps)

def rec_proc_to_tenv(exp:Rec_Proc,tenv:Environment) -> Environment:
    for var,arg_t,res_t in zip(exp.var,exp.arg_types,exp.res_types):
        tenv = extend_env(var,Proc_Type(arg_t,res_t),tenv)
    
    for params,arg_t,body,res_t in zip(exp.params,exp.arg_types,exp.body,exp.res_types):
        body_t = type_of(body,extend_env_from_pairs(params,arg_t,tenv))
        check_equal_type(body_t,res_t,body)
    
    return tenv

def add_modules_to_tenv(modules:tuple[Module_Def],tenv):
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

def let_exp_to_tenv(exp:Let_Exp|Let_Star_Exp|Rec_Proc,tenv:Environment):
    if isinstance(exp,Let_Exp):
        vals = tuple(type_of(exp,tenv) for exp in exp.exps)
        return extend_env_from_pairs(exp.vars,vals,tenv)
    elif isinstance(exp,Let_Star_Exp):
        return let_exp_to_tenv(expand_let_star(exp),tenv)
    elif isinstance(exp,Rec_Proc):
        return rec_proc_to_tenv(exp,tenv)
    else:
        return tenv


def decls_to_tenv(decls:tuple[Decl_Type]|Proc_Interface) -> Environment:
    raise DeprecationWarning


def interface_of(body:Module_Body_T,tenv:Environment) -> tuple[Decl_Type]:
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


def fresh_name():
    from itertools import product
    from string import ascii_lowercase
    for c in product(ascii_lowercase,repeat = 3):
        yield ''.join(c)
        
fresh_name = fresh_name()

def fresh_name_module(name):
    return f'%fresh_name_{name}_{next(fresh_name)}'

def interface_comp(actual,expected,tenv) -> bool:
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
            new_tenv = extend_env_with_module(new_name,iface1,new_tenv)
        
        return interface_comp(res_iface1,res_iface2,new_tenv)
    elif is_simple_interface(actual) and is_simple_interface(expected):
        return decl_subset(actual,expected,tenv)
    else:
        print(type(actual),type(expected))
        raise NotImplementedError

def rename_type(type,name,new_name):
    if isinstance(type,Proc_Type):
        arg_type = tuple(rename_type(arg_t,name,new_name) for arg_t in type.arg_type)
        res_type = rename_type(type.result_type,name,new_name)
        return Proc_Type(arg_type,res_type)
    elif isinstance(type,Qualified_Type):
        new_name = new_name if type.module_name == name else name
        return Qualified_Type(new_name,type.type_name)
    else:
        return type

def rename_interface(interface:tuple[Decl_Type],name,new_name):
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
            


def defs_to_decls(defs:tuple[Def_Type],tenv:Environment) -> tuple[Decl_Type]:
    if defs == tuple():
        return tuple()
    elif isinstance(defs[0],Var_Def):
        name = defs[0].name
        type = type_of(defs[0].expr,tenv)
        new_tenv = extend_env(name,type,tenv)
        decl = Var_Decl(name,type)
        return (decl,) + defs_to_decls(defs[1:],new_tenv)
    elif isinstance(defs[0],Type_Def):
        name,type = defs[0].name,defs[0].type
        new_tenv = extend_env(name,expand_type(type,tenv),tenv)
        decl = Transparent_Type_Decl(name,type)
        return (decl,) + defs_to_decls(defs[1:],new_tenv)
    else:
        raise Exception(defs,tenv)


def subset_interface(actual:tuple[Var_Decl],expected:tuple[Var_Decl]):
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


def expand_type(type,tenv:Environment):
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
            expand_type(type.result_type,tenv)
        )
    elif isinstance(type,Named_Type):
        return lookup_type_name(type.name,tenv)
    elif isinstance(type,Qualified_Type):
        return lookup_qualified_type(type.module_name,type.type_name,tenv)
    else:
        print(type)
        raise Exception()


def expand_types(types,tenv:Environment):
    return tuple(expand_type(t,tenv) for t in types)


def is_equiv_type(t1,t2,tenv):
    return expand_type(t1,tenv) == expand_type(t2,tenv)


def decl_subset(actual:tuple[Decl_Type],expected:tuple[Decl_Type],tenv:Environment):
    '''
    Used for typed modules
    Assumption : order must be same for actual and expected
    
    actual < expected
    
    interface that satisfies actual also satisfy expected.
    
    decl satisfy decls_1 implies decl can satisfy decls_2
    '''
    def recur(decls_1:tuple[Var_Decl],decls_2:tuple[Var_Decl],tenv:Environment):
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


def decl_satisfy(left:Decl_Type,right:Decl_Type,tenv):
    return ((isinstance(left,Var_Decl) 
            and isinstance(right,Var_Decl) 
            and is_equiv_type(left.type,right.type,tenv))
            or (isinstance(left,Transparent_Type_Decl) 
                and isinstance(right,Transparent_Type_Decl) 
                and is_equiv_type(left.type,right.type,tenv))
            or (isinstance(left,Transparent_Type_Decl|Opaque_Type_Decl) 
                and isinstance(right,Opaque_Type_Decl)))


def expand_declarations(module_name,decls:tuple[Decl_Type],tenv):
    return expand_interface(module_name,decls,tenv)


def expand_interface(module_name,decls:tuple[Decl_Type],tenv:Environment) -> tuple[Decl_Type]:
    if decls == tuple(): 
        return tuple()
    elif isinstance(decls[0],Var_Decl):
        decl = Var_Decl(decls[0].name,expand_type(decls[0].type,tenv))
        return (decl,) + expand_interface(module_name,decls[1:],tenv) 
    elif isinstance(decls[0],Opaque_Type_Decl):
        expanded_type = Qualified_Type(module_name,decls[0].name)
        new_tenv = extend_env(decls[0].name,expanded_type,tenv)
        decl = Transparent_Type_Decl(decls[0].name,expanded_type)
        return (decl,) + expand_interface(module_name,decls[1:],new_tenv)
    elif isinstance(decls[0],Transparent_Type_Decl):
        expanded_type = expand_type(decls[0].type,tenv)
        new_tenv = extend_env(decls[0].name,expanded_type,tenv)
        decl = Transparent_Type_Decl(decls[0].name,expanded_type)
        return (decl,) + expand_interface(module_name,decls[1:],new_tenv)
    else:
        raise Exception(module_name,decls,tenv)


def extend_tenv_with_decl(decl,tenv) -> Environment:
    if isinstance(decl,Var_Decl):
        return tenv
    elif isinstance(decl,Transparent_Type_Decl):
        expanded_type = expand_type(decl.type,tenv)
        return extend_env(decl.name,expanded_type,tenv)
    elif isinstance(decl,Opaque_Type_Decl):
        expanded_type = Qualified_Type("%uninitialized",decl.name)
        return extend_env(decl.name,expanded_type,tenv)

