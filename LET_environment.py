from LET_ast_node import *
from dataclasses import dataclass
# Object representation
@dataclass
class Environment:
    env:tuple = ()
    @dataclass
    class Delayed_Rec_Proc:
        params:None
        body:None
        delayed_env:None
    
    @dataclass
    class Referenced_Rec_Proc:
        params:None
        body:None
        delayed_env:None
    
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


def empty_env():
    return Environment()

def extend_env(var,val,env:Environment):
    return env.extend(var,val)

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
              'cons'    : Pair,
              'zero?'   : Proc_Type((Int_Type(),),Bool_Type()),
              'minus'   : Proc_Type((Int_Type(),Int_Type()),Int_Type()),
            #   'car'     : car,
            #   'cdr'     : cdr,
            #   'list'    : list_to_pair,
            #   'print'   : print,
            }
    env = empty_env()
    for var,val in corspd.items():
        env = extend_env(var,val,env)
    return env

def get_all_primitive_implementation():
    def list_to_pair(*args):
        if args == ():
            return NULL()
        else:
            return Pair(args[0], list_to_pair(*args[1:]))
    # rather than using nameless lambda, because these print names
    def iszero(x): return x == 0
    def minus(x): return -x
    def car(t): return t.car
    def cdr(t): return t.cdr
    
    # iszero = lambda x : x == 0
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
              'list'    : list_to_pair,
              'print'   : print,
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

def apply_senv(env:Environment,src_var):
    for lex_addr,(var,_) in enumerate(env.env):
        if var == src_var:
            return lex_addr
    raise Exception("Unbound variable",src_var,f"env - {env.env}")

def nameless_env(obj):
    return isinstance(obj,list)

def is_nameless_env(env):
    return isinstance(env,tuple)

def empty_nameless_env():
    return tuple()

def extend_nameless_env(val,env):
    return (val,) + env

def apply_nameless_env(env,addr):
    return env[addr]
