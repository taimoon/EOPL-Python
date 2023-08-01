from dataclasses import dataclass
from LET_ast_node import (
    Pair,
    NULL,
    Decl_Type,
    Proc_Type,Int_Type,Bool_Type,
    Proc_Val,
    Proc_Module,Proc_Interface,
    Primitve_Implementation,
)

# Object representation
class Repeated_Binding(Exception): pass
@dataclass
class Environment:
    env:tuple[dict[str]] = ()
    @dataclass
    class Rec_Proc:
        params:None
        body:None
        delayed_env:None    
    
    class Delayed_Rec_Proc(Rec_Proc): pass
    class Referenced_Rec_Proc(Rec_Proc): pass
    class Nameless_Rec_Proc(Rec_Proc): pass
    
    def __str__(self) -> str:
        return f'(env {str(tuple(p.keys() for p in self.env))})'
    
    def memory_mapping(self):
        return tuple({k:(v if isinstance(v,int) else type(v).__name__) for k,v in env.items()} for env in self.env)
    
    def copy(self):
        env = tuple(dict(e.items()) for e in self.env)
        return Environment(env)
    
    def is_empty(self): return self.env == ()
    
    @property
    def current_frame(self): return self.env[0]
    
    @property
    def enclosed_env(self): return Environment(self.env[1:])
    
    def lookup(self,var:str):
        if self.is_empty():
            raise NameError
        elif var not in self.current_frame:
            return self.enclosed_env.lookup(var)
        else:
            return self.current_frame[var]
    
    def add_var(self,var,val):
        env = self.copy()
        if var not in self.current_frame:
            env.current_frame[var] = val
            return env
        else:
            raise Repeated_Binding
    
    def extend_env(self,env:dict):
        return Environment(env.env + self.env)
    
    def extend_from_dict(self,d:dict):
        return self.extend_env(Environment((d,)))
    
    def extend_from_bindings(self,pairs):
        d = {}
        for var,val in pairs:
            if var in d: continue
            d[var] = val
        return self.extend_from_dict(d)
    
    def extend_from_pairs(self,vars,vals):
        return self.extend_from_bindings(zip(vars,vals))
    
    def extend(self,*args,**kwargs):
        raise DeprecationWarning
    
    def map(self,f):
        env = tuple({k:f(v) for k,v in env.items()} for env in self.env)
        return Environment(env)
    
    def __iter__(self): # TODO : WORKAROUND
        return iter(e.items() for e in self.env)
    
    def apply(self,var):
        val = self.lookup(var)
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
    
    def apply_senv(self,src_var,depth=0):
        recur = self.enclosed_env.apply_senv
        if self.is_empty():
            raise NameError
        elif src_var not in self.current_frame:
            return recur(src_var,depth+1)
        else:
            len = self.current_frame[src_var]
            return depth,len
        
    def extend_rec(self,var,params,body):
        delayed_fn = lambda:self.extend_rec(var,params,body)
        val = self.Delayed_Rec_Proc(params,body,delayed_fn)
        return self.extend(var,val)

    def extend_env_rec_multi(self,vars,paramss,bodys):
        # don't nest delayed_fn into recur
        delayed_fn = lambda:self.extend_env_rec_multi(vars,paramss,bodys)
        Rec_Proc_Ctor = lambda params,body:self.Delayed_Rec_Proc(params,body,delayed_fn)
        vals = tuple(Rec_Proc_Ctor(params,body) for params,body in zip(paramss,bodys))
        return self.extend_from_pairs(vars,vals)

    def extend_env_rec_ref(self,vars,paramss,bodys):
        delayed_fn = lambda:self.extend_env_rec_ref(vars,paramss,bodys)
        Rec_Proc_Ctor = lambda params,body:self.Referenced_Rec_Proc(params,body,delayed_fn)
        vals = tuple(Rec_Proc_Ctor(params,body) for params,body in zip(paramss,bodys))
        return self.extend_from_pairs(vars,vals)
    
    def lookup_module(self,name):
        val = self.lookup(name)
        assert(isinstance(val,Environment|Proc_Module))
        return val
    
    def lookup_qualified_var(self,name,var):
        env = self.lookup_module(name)
        return env.apply(var)
    
    def lookup_module_tenv(self,name):
        val = self.lookup(name)
        res = isinstance(val, Proc_Interface) or (isinstance(val,tuple) and isinstance(val[0],Decl_Type))
        assert(res)
        return val
    
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
    return Environment((corspd,))

def empty_senv():
    return Environment()

def extend_senv_vars(vars,env:Environment):
    pairs = tuple((v,i) for i,v in enumerate(vars))
    return env.extend_from_bindings(pairs)

def apply_senv(env:Environment,src_var):
    return env.apply_senv(src_var)

def is_nameless_env(env):
    return isinstance(env,tuple)

def empty_nameless_env():
    return tuple()

def extend_nameless_env_vals(vals:tuple,env:tuple):
    return (vals,) + env

def apply_nameless_env(env,depth,length):
    return env[depth][length]

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
