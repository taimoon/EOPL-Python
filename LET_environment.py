from LET_ast_node import Proc_Val
from LET_ast_node import *
'''
# structural representation
def empty_env():
    return ('empty')
def extend_env(var,val,env):
    return ('extend', var, val, env)
def extend_env_rec(var,params,body,env):
    return ('rec-extend', var, params, body, env)
def apply_env(env, src_var):
    match env:
        case ('empty'):
            raise Exception("reach empty_env; possible error - unbound variable", src_var) 
        case ('extend',var,val,enclosed_env):
            if var == src_var:
                return val
            else:
                return apply_env(enclosed_env, src_var)
        case ('rec-extend', var, params, body, enclosed_env):
            if var == src_var:
                matryoshka_env = ('rec-extend', var, params, body, env)
                return Proc_Val(params,body, matryoshka_env)
            else:
                return apply_env(enclosed_env, src_var)
        case _:
            raise Exception("Unknown environment type", env)
'''

'''
# procedural representation
def empty_env():
    def fn(var):
        raise Exception("reach empty_env; possible error - unbound variable", var)
    return fn

def extend_env(var,val,env):
    return lambda search_var: val if var == search_var else env(search_var)

def extend_env_rec(var,params,body,env):
    # matryoshka_env = lambda search_var: extend_env_rec(var,params,body,env)(search_var)
    return lambda search_var: Proc_Val(params,body,extend_env_rec(var,params,body,env)) if var == search_var else env(search_var)

def extend_env_rec_multi(vars,paramss,bodys,env):      
    def recur(search_var):
            for var,params,body in zip(vars,paramss,bodys):
                if search_var == var:
                    return Proc_Val(params,body,extend_env_rec_multi(vars,paramss,bodys,env))
            return env(search_var)
    return recur

def apply_env(env,var):
    return env(var)
'''

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
        @property
        def val(self):
            return Proc_Val(self.params,self.body,self.delayed_env())
    
    def __str__(self) -> str:
        return f'(env {str(tuple(p[0] for p in self.env))})'
    
    def extend(self,var,val):
        pair = (var,val)
        return Environment((pair,) + self.env) # the order here is important
    
    def apply(self,src_var):
        for var,val in self.env:
            if var == src_var:
                if isinstance(val,self.Delayed_Rec_Proc):
                    return val.val
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
        def recur(vars,paramss,bodys):
            if vars == ():
                return self
            else:
                val = self.Delayed_Rec_Proc(paramss[0],bodys[0],delayed_fn)
                return recur(vars[1:],paramss[1:],bodys[1:]).extend(vars[0],val)
        return recur(vars,paramss,bodys)

def empty_env():
    return Environment()

def extend_env(var,val,env:Environment):
    return env.extend(var,val)

def extend_env_rec(var,params,body,env:Environment):
    return env.extend_rec(var,params,body)

def extend_env_rec_multi(vars,paramss,bodys,env:Environment):      
    return env.extend_env_rec_multi(vars,paramss,bodys)

def apply_env(env:Environment,var):
    return env.apply(var)

def init_env():
    def recur(*args):
            if args == ():
                return NULL()
            else:
                return Pair(args[0], recur(*args[1:]))
    from operator import sub,add,mul,truediv,gt,lt,eq
    corspd = {'-': sub,
            '+': add,
            '*': mul,
            '/': truediv,
            'greater?':gt,
            'less?':lt,
            'equal?': eq,
            'cons': lambda x,y: Pair(x,y),
            'zero?': lambda x : x == 0,
            'minus' : lambda exp : - exp,
            'car' : lambda t: t.car,
            'cdr' : lambda t: t.cdr,
            'list':recur,}
    env = empty_env()
    for var,val in corspd.items():
        env = extend_env(var,Primitve_Implementation(val),env)
    return env

def empty_senv():
    return Environment()

def extend_senv(var,env:Environment):
    return env.extend(var,None)

def apply_senv(env:Environment,src_var):
    for lexaddr,(var,_) in enumerate(env.env):
        if var == src_var:
            return lexaddr
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
