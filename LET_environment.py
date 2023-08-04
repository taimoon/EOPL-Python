from LET_ast_node import (
    Pair,
    NULL,
    Decl_Type,
    Proc_Type,Int_Type,Bool_Type,
    Primitve_Implementation,
)

from LET_env.assoc_environment import (
    Environment,
    Repeated_Binding,
    is_nameless_env,
    empty_nameless_env,
    extend_nameless_env_vals,
    apply_nameless_env,
)

def empty_env():
    return Environment()

def extend_env_from_dict(d:dict,env:Environment):
    return env.extend_from_dict(d)

def extend_from_bindings(pairs:tuple,env:Environment):
    return env.extend_from_bindings(pairs)

def extend_env_from_pairs(vars:tuple,vals:tuple,env:Environment = None):
    return env.extend_from_pairs(vars,vals)

def extend_env_rec(var,params,body,env:Environment):
    return env.extend_rec(var,params,body)

def extend_env_rec_multi(vars,paramss,bodys,env:Environment):      
    return env.extend_env_rec_multi(vars,paramss,bodys)

def extend_env_rec_ref(vars,paramss,bodys,env:Environment):
    return env.extend_env_rec_ref(vars,paramss,bodys)
    
def apply_env(env:Environment,var):
    return env.apply(var)

def init_tenv():
    corspd = {'-'  : Proc_Type((Int_Type(),Int_Type()),Int_Type()),
              '+'  : Proc_Type((Int_Type(),Int_Type()),Int_Type()),
              '*'  : Proc_Type((Int_Type(),Int_Type()),Int_Type()),
              '/'  : Proc_Type((Int_Type(),Int_Type()),Int_Type()),
              'greater?': Proc_Type((Int_Type(),Int_Type()),Bool_Type()),
              'less?'   : Proc_Type((Int_Type(),Int_Type()),Bool_Type()),
              'equal?'  : Proc_Type((Int_Type(),Int_Type()),Bool_Type()),
              'zero?'   : Proc_Type((Int_Type(),),Bool_Type()),
              'minus'   : Proc_Type((Int_Type(),Int_Type()),Int_Type()),
            }
    return empty_env().extend_from_dict(corspd)

def get_all_primitive_implementation():
    # rather than using nameless lambda, because these print names
    def iszero(x): return x == 0
    def minus(x): return -x
    def car(t): return t.car
    def cdr(t): return t.cdr
    
    from operator import sub,add,mul,truediv,gt,lt,eq
    corspd = {'-'  : sub,
              '+'  : add,
              '*'  : mul,
              '/'  : truediv,
              'greater?': gt,
              'less?'   : lt,
              'equal?'  : eq,
              'cons'    : Pair,
              'zero?'   : iszero,
              'minus'   : minus,
              'car'     : car,
              'cdr'     : cdr,
              'list'    : Pair.list_to_pair,
              'print'   : print,
              'null?'   : lambda x: isinstance(x,NULL)
            }
    return corspd

def init_env(corspd=get_all_primitive_implementation()):
    corspd = {name:Primitve_Implementation(f) for name,f in corspd.items()}
    return extend_env_from_dict(corspd,empty_env())

def empty_senv():
    return Environment()

def extend_senv_vars(vars,env:Environment):
    return env.extend_senv_vars(vars)

def apply_senv(env:Environment,src_var):
    return env.apply_senv(src_var)

def apply_tenv(tenv:Environment,var):
    return apply_env(tenv,var)

def extend_tenv_from_pairs(vars,types,tenv:Environment):
    return extend_env_from_pairs(vars,types,tenv)

def extend_env_with_module(module_name,bindings:Environment,env:Environment):
    return env.add_var(module_name,bindings)

def lookup_module_name(name,env:Environment):
    return env.lookup_module(name)

def lookup_qualified_var(name,var,env:Environment):
    return env.lookup_qualified_var(name,var)

def lookup_type_name(var,tenv:Environment):
    return tenv.apply(var)

def lookup_qualified_type(name,type_name,tenv:Environment):
    return lookup_qualified_var_tenv(name,type_name,tenv)

def lookup_module_tenv(module_name,tenv:Environment):
    return tenv.lookup_module_tenv(module_name)

def extend_tenv_with_module(module_name,interface:tuple[Decl_Type],tenv:Environment):
    return tenv.add_var(module_name,interface)

def lookup_qualified_var_tenv(module_name,name,tenv:Environment):
    return tenv.lookup_qualified_var_tenv(module_name,name)
