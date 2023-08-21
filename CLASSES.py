from LET_parser import parser
from IMPLICIT_REFS import IMPLICIT_REFS_Interpreter
from LET_environment import (
    Environment as Env,
    apply_env,
    extend_env_from_pairs
)
from memory import init_store,newref,deref
from LET_ast_node import *
from object import (
    Object,Method,
    find_method,
    init_class_env,
    new_object,
    super_name,
    instanceof,
    fieldref,
    fieldset,
)

def value_of_prog(prog, env = None, parse = parser.parse):
    if env is None:
        env = CLASSES_Interpreter().init_env()
    return CLASSES_Interpreter().value_of_prog(prog,env,parse)

class CLASSES_Interpreter(IMPLICIT_REFS_Interpreter):
    'CLASSES extends IMPLICIT_REFS'
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
            res = apply_env(env,"%self")
            assert(isinstance(res,Object))
            return res
        elif isinstance(expr,Method_Call_Exp):
            args = tuple(value_of(exp,env) for exp in expr.operands)
            obj:Object = value_of(expr.obj_exp,env)
            meth = find_method(obj.name,expr.method_name)
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
            meth:Method = find_method(obj.name,'initialize')
            self.apply_method(meth,obj,args)
            return obj
        elif isinstance(expr,Instance_Exp):
            obj = value_of(expr.exp,env)
            return (isinstance(obj,Object) and instanceof(obj.name,expr.cls_name))
        elif isinstance(expr,Field_Ref):
            obj:Object = value_of(expr.obj_exp,env)
            return deref(fieldref(obj,expr.field_name))
        elif isinstance(expr,Field_Set):
            obj:Object = value_of(expr.obj_exp,env)
            val = value_of(expr.exp,env)
            return fieldset(obj,expr.field_name,val)
        else:
            return super().value_of(expr,env)

    def apply_method(self,meth:Method,obj:Object,args:tuple):
        'core of CLASSES lang'
        change_init_env = self.change_init_env
        init_env = self.init_env
        value_of = self.value_of
        
        env = change_init_env(init_env())
        vars = meth.field_names + ('%self','%super')
        vals = obj.fields + (obj,super_name(meth))
        env = extend_env_from_pairs(vars,vals,env)
        env = extend_env_from_pairs(meth.params,tuple(map(newref,args)),env)
        return value_of(meth.body,env)
