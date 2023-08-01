from dataclasses import dataclass
from LET_ast_node import (
    Decl_Type,
    Proc_Val,
    Proc_Module,Proc_Interface,
)

class Repeated_Binding(Exception): pass
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
    
    def __iter__(self):
        # so that it is compatible with ribcage
        return iter((self.env,))
    
    def memory_mapping(self):
        return {k:(v if isinstance(v,int) else type(v).__name__) for k,v in self.env}

    def extend(self,var,val):
        pair = (var,val)
        return Environment((pair,) + self.env) # the order here is important
    
    def add_var(self,var,val):
        for _var,_ in self.env:
            if var == _var:
                raise Repeated_Binding
        return self.extend(var,val) 
    
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
    
    def extend_from_dict(self,d:dict):
        return self.extend_from_bindings(tuple(d.items()))
    
    def extend_from_pairs(self,vars,vals):
        return self.extend_from_bindings(tuple(zip(vars,vals)))
    
    def extend_from_bindings(self,pairs:tuple):
        recur = self.extend_from_bindings
        if pairs == ():
            return self
        else:
            var,val = pairs[0]
            return recur(pairs[1:]).extend(var,val)
    
    def extend_senv_vars(self,vars):
        return self.extend_from_pairs(vars,tuple(None for _ in vars))
    
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
        val = self.apply(name)
        res = isinstance(val,Environment|Proc_Module)
        assert(res)
        return val
    
    def lookup_qualified_var(self,name,var):
        env = self.lookup_module(name)
        return env.apply(var)
    
    def lookup_module_tenv(self,name):
        val = self.apply(name)
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

def is_nameless_env(env):
    return isinstance(env,tuple)

def empty_nameless_env():
    return tuple()

def extend_nameless_env_vals(vals:tuple,env:tuple):
    return vals + env

def apply_nameless_env(env,addr):
    return env[addr]