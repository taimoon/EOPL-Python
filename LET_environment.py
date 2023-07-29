from dataclasses import dataclass
from LET_ast_node import (
    Pair,
    NULL,
    Decl_Type,
    Proc_Type,Int_Type,Bool_Type,
    Proc_Val,
    Proc_Module,Proc_Interface,
    Primitve_Implementation
)

# Object representation
@dataclass
class Environment:
    env:tuple = ()
    @dataclass
    class Rec_Proc:
        params:None
        body:None
        delayed_env:None    
    
    class Delayed_Rec_Proc(Rec_Proc): pass
    class Referenced_Rec_Proc(Rec_Proc): pass
    class Nameless_Rec_Proc(Rec_Proc): pass
    
    def __str__(self) -> str:
        return f'(env {str(tuple(p[0] for p in self.env))})'
    
    def memory_mapping(self):
        return {k:(v if isinstance(v,int) else type(v).__name__) for k,v in self.env}

    def extend(self,var,val):
        pair = (var,val)
        return Environment((pair,) + self.env) # the order here is important
    
    def apply(self,src_var):
        for var,val in self.env:
            if var != src_var:
                continue
            if isinstance(val,self.Delayed_Rec_Proc):
                return Proc_Val(val.params,val.body,val.delayed_env())
            elif isinstance(val,self.Referenced_Rec_Proc):
                from memory import newref
                # also work but not test cases to show it doesn't work
                # newref(Proc_Val(val.params,val.body,self)) 
                # either I must write a test to test the lexical scoping
                # nevertheless, the program still capture the closure.
                return newref(Proc_Val(val.params,val.body,val.delayed_env()))
            else:
                return val
        raise Exception("Unbound variable",src_var,str(self))
    
    def apply_senv(self,src_var):
        for lex_addr,(var,_) in enumerate(self.env):
            if var != src_var: continue
            return lex_addr
        raise Exception("Unbound variable",src_var,f"env - {self.env}")

    def extend_rec(self,var,params,body):
        delayed_fn = lambda:self.extend_rec(var,params,body)
        val = self.Delayed_Rec_Proc(params,body,delayed_fn)
        return self.extend(var,val)

    def extend_env_rec_multi(self,vars,paramss,bodys):
        # don't nest delayed_fn into recur
        delayed_fn = lambda:self.extend_env_rec_multi(vars,paramss,bodys) 
        env = self
        for var,params,body in zip(vars,paramss,bodys):
            val = self.Delayed_Rec_Proc(params,body,delayed_fn)
            env = env.extend(var,val)
        return env

    def extend_env_rec_ref(self,vars,paramss,bodys):
        delayed_fn = lambda:self.extend_env_rec_ref(vars,paramss,bodys)
        env = self
        for var,params,body in zip(vars,paramss,bodys):
            val = self.Referenced_Rec_Proc(params,body,delayed_fn)
            env = env.extend(var,val)
        return env
    
    def lookup_module(self,name):
        for var,val in self.env:
            if var != name:
                continue
            elif not isinstance(val,Environment|Proc_Module):
                continue
            else:
                return val
        raise Exception("Unbound modules",name, self.__str__())
    
    def lookup_qualified_var(self,name,var):
        env = self.lookup_module(name)
        return env.apply(var)
    
    def lookup_module_tenv(self,name):
        for var,val in self.env:
            if var != name:
                continue
            elif not isinstance(val, Proc_Interface) and not (isinstance(val,tuple) and isinstance(val[0],Decl_Type)):
                continue
            else:
                return val
        raise Exception("Unbound modules",name, self.__str__())
    
    def lookup_qualified_var_tenv(self,module_name,name):
        decls = self.lookup_module_tenv(module_name)
        for decl in decls:
            if decl.name != name:
                continue
            else:
                return decl.type
        raise Exception("Unbound modules",name, self.__str__())


def empty_env():
    return Environment()

def extend_env(var,val,env:Environment):
    return env.extend(var,val)

def extend_env_from_pairs(vars:tuple,vals:tuple,env:Environment = None):
    if vars == ():
        return empty_env() if env is None else env
    else:
        return extend_env(vars[0],vals[0],
                          extend_env_from_pairs(vars[1:],vals[1:],env))

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
    env = empty_env()
    for var,val in corspd.items():
        env = extend_env(var,val,env)
    return env

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
    env = empty_env()
    for var,val in corspd.items():
        env = extend_env(var,Primitve_Implementation(val),env)
    return env

def empty_senv():
    return Environment()

def extend_senv(var,env:Environment):
    return env.extend(var,None)

def extend_senv_vars(vars,env:Environment):
    for var in vars: env = extend_senv(var,env)
    return env

def apply_senv(env:Environment,src_var):
    return env.apply_senv(src_var)

def is_nameless_env(env):
    return isinstance(env,tuple)

def empty_nameless_env():
    return tuple()

def extend_nameless_env(val,env):
    return (val,) + env

def apply_nameless_env(env,addr):
    return env[addr]

def extend_tenv(var,type,tenv:Environment):
    return extend_env(var,type,tenv)

def apply_tenv(tenv:Environment,var):
    return apply_env(tenv,var)

def extend_tenv_from_pairs(vars,types,tenv:Environment):
    return extend_env_from_pairs(vars,types,tenv)

class Repeated_Module_Error(Exception): pass

def extend_env_with_module(module_name,bindings:Environment,env:Environment):
    try:
        env.lookup_module(module_name,env)
        raise Repeated_Module_Error
    except Repeated_Module_Error:
        raise Repeated_Module_Error(f"Repeated module name of '{module_name}' in {env}")
    except Exception as e:
        pass
    return extend_env(module_name,bindings,env)

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
    try:
        lookup_module_tenv(module_name,tenv)
        raise Repeated_Module_Error
    except Repeated_Module_Error:
        raise Repeated_Module_Error(f"Repeated module name of '{module_name}' in {tenv}")
    except Exception as e: # TODO : Bad Practice, remove it in future
        pass
    return extend_env(module_name,interface,tenv)

def lookup_qualified_var_tenv(module_name,name,tenv:Environment):
    return tenv.lookup_qualified_var_tenv(module_name,name)
