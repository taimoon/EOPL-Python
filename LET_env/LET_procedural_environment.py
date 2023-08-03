from LET_ast_node import (Proc_Val)

# procedural representation
def empty_env():
    def fn(var):
        raise Exception("reach empty_env; possible error - unbound variable", var)
    return fn

def extend_env(var,val,env):
    return lambda search_var: val if var == search_var else env(search_var)

def extend_env_rec(var,params,body,env):
    return lambda search_var: Proc_Val(params,body,extend_env_rec(var,params,body,env)) if var == search_var else env(search_var)

def extend_env_rec_multi(vars,paramss,bodys,env):      
    def recur(search_var):
        for var,params,body in zip(vars,paramss,bodys):
            if search_var != var:
                continue
            rec_env = extend_env_rec_multi(vars,paramss,bodys,env)
            return Proc_Val(params,body,rec_env)
        return env(search_var)
    return recur

def apply_env(env,var):
    return env(var)

if __name__ == '__main__':
    env = extend_env('d',6,
            extend_env('y',8,
            extend_env('x',7,
            extend_env('y',14,empty_env()))))
    assert(env('d') == 6)
    assert(env('y') == 8)
    assert(env('x') == 7)
