from LET_parser import parser
from IMPLICIT_REFS import IMPLICIT_REFS_Interpreter
from LET_environment import (
    Environment as Env,
    extend_env,
    apply_env,
    extend_env_from_pairs
)
from memory import init_store,newref
from LET_ast_node import *
from object import (
    Object,Method,
    find_method,
    init_class_env,
    new_object
)

def value_of_prog(prog, env = None, parse = parser.parse):
    if env is None:
        env = CLASSES_Interpreter().init_env()
    return CLASSES_Interpreter().value_of_prog(prog,env,parse)

class CLASSES_Interpreter:
    'CLASSES extends IMPLICIT_REFS'
    
    def init_env(self):
        return IMPLICIT_REFS_Interpreter.init_env(self)
    
    def change_init_env(self,env:Env):
        return IMPLICIT_REFS_Interpreter.change_init_env(self,env)
    
    def apply_proc(self,proc,args,env:Env):
        return IMPLICIT_REFS_Interpreter.apply_proc(self,proc,args,env)
    
    def value_of_prog(self,prog, env = None, parse = parser.parse):
        prog = parse(prog)
        init_store()
        if isinstance(prog,Program):
            init_class_env(prog.classes)
            prog = prog.expr
        return self.value_of(prog, self.change_init_env(env))
    
    def value_of(self,expr,env):
        value_of = self.value_of
        if isinstance(expr,Self_Exp):
            return apply_env(env,"%self")
        elif isinstance(expr,Method_Call_Exp):
            args = tuple(value_of(exp,env) for exp in expr.operands)
            obj:Object = value_of(expr.obj_exp,env)
            meth = find_method(obj.class_name,expr.method_name)
            apply_method = self.apply_method
            return apply_method(meth,obj,args)
        elif isinstance(expr,Super_Call_Exp):
            args = tuple(value_of(exp,env) for exp in expr.operands)
            obj:Object = apply_env(env,'%self')
            super_meth:Method = find_method(apply_env(env,'%super'),expr.method_name)
            apply_method = self.apply_method
            return apply_method(super_meth,obj,args)
        elif isinstance(expr,New_Obj_Exp):
            args = tuple(value_of(exp,env) for exp in expr.operands)
            obj = new_object(expr.cls_name)
            meth:Method = find_method(obj.class_name,'initialize')
            self.apply_method(meth,obj,args)
            return obj
        else:
            return IMPLICIT_REFS_Interpreter.value_of(self,expr,env)

    def apply_method(self,meth:Method,obj:Object,args:tuple):
        'core of CLASSES lang'
        change_init_env = self.change_init_env
        init_env = self.init_env
        value_of = self.value_of
        
        env = change_init_env(init_env())
        env = extend_env_from_pairs(meth.field_names,obj.fields,env)
        env = extend_env('%self',obj,env)
        env = extend_env('%super',meth.super_name,env)
        env = extend_env_from_pairs(meth.params,tuple(map(newref,args)),env)
        return value_of(meth.body,env)
