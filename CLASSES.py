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
        match expr:
            case Self_Exp():
                res = apply_env(env,"%self")
                return res
            case Method_Call_Exp(obj_exp,method_name,operands):
                args = tuple(value_of(exp,env) for exp in operands)
                obj:Object = value_of(obj_exp,env)
                meth = find_method(obj.name,method_name)
                apply_method = self.apply_method
                return apply_method(meth,obj,args)
            case Super_Call_Exp(method_name,operands):
                args = tuple(value_of(exp,env) for exp in operands)
                obj:Object = apply_env(env,'%self')
                super_meth:Method = find_method(apply_env(env,'%super'),method_name)
                apply_method = self.apply_method
                return apply_method(super_meth,obj,args)
            case New_Obj_Exp(cls_name,operands):
                args = tuple(value_of(exp,env) for exp in operands)
                obj = new_object(cls_name)
                meth:Method = find_method(obj.name,'initialize')
                self.apply_method(meth,obj,args)
                return obj
            case Instance_Exp(exp,cls_name):
                obj = value_of(exp,env)
                return (isinstance(obj,Object) and instanceof(obj.name,cls_name))
            case Field_Ref(obj_exp,field_name):
                obj:Object = value_of(obj_exp,env)
                return deref(fieldref(obj,field_name))
            case Field_Set(obj_exp,field_name,exp):
                obj:Object = value_of(obj_exp,env)
                val = value_of(exp,env)
                return fieldset(obj,field_name,val)
            case _:
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
