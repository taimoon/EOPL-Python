def obj_repr():
    class environment:
        def __init__(self):
            self.env = []
        def is_empty(self):
            return self.env == []
        def extend(self, var, val):
            env = environment()
            env.var = var
            env.val = val
            env.env = self.env
            self.env = env
            return env
        def apply(self,var):
            if self.is_empty():
                raise Exception('variable is not found', var)
            elif self.env.var == var:
                return self.env.val
            else:
                return self.env.apply(var)
    env = environment()
    env.extend('d',6)\
        .extend('y', 8).\
            extend('x', 7).\
                extend('y', 14)
    assert(env.apply('d') == 6)
    assert(env.apply('y') == 8)
    assert(env.apply('x') == 7)
    assert(env.apply('y') == 8)
    print(env)

def procedural_repr():
    def empty_env():
        def fn(var):
            raise Exception("reach empty_env; possible error - unbound variable", var)
        return fn

    def extend_env(var,val,env):
        return lambda search_var: val if var == search_var else env(search_var)

    def apply_env(env,var):return env(var)

    env = empty_env()
    env = extend_env('y', 14,env)
    env = extend_env('x', 7,env)
    env = extend_env('y',8,env)
    env = extend_env('d',6,env)

    assert(apply_env(env,'d') == 6)
    assert(apply_env(env,'y') == 8)
    assert(apply_env(env,'x') == 7)
    assert(apply_env(env,'y') == 8)
    print(env)

def data_struct_repr():
    def empty_env():
        return ['empty-env']
    def is_empty(env):
        return env[0] == 'empty-env'

    def extend_env(var,val,env):
        return ['extend-env', var, val, env]

    def apply_env(env,var):
        if is_empty(env):
            raise Exception("Unbound variable", var)
        elif env[0] == 'extend-env':
            if env[1] == var:
                return env[2]
            else:
                return apply_env(env[3],var)
        else:
            raise Exception("Bad environment", env)

    env = empty_env()
    env = extend_env('y',14,env)
    env = extend_env('x', 7,env)
    env = extend_env('y',8,env)
    env = extend_env('d',6,env)

    assert(apply_env(env,'d') == 6)
    assert(apply_env(env,'y') == 8)
    assert(apply_env(env,'x') == 7)
    assert(apply_env(env,'y') == 8)
    print(env)

procedural_repr()
data_struct_repr()
obj_repr()