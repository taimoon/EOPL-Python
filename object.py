from dataclasses import dataclass
import LET_ast_node as ast

@dataclass
class Object:
    'interpreter data struct'
    name:str
    fields:tuple

@dataclass
class Method:
    'interpreter data struct'
    params:tuple[str]
    body:None
    name:str
    field_names:tuple[str]

Method_Env_T = tuple[tuple[str,Method]]

@dataclass
class Class:
    'interpreter data struct'
    super_name:None|str
    field_names:tuple[str]
    method_env:Method_Env_T

@dataclass
class Class_Env:
    env:tuple[tuple[str,Class]]
    def __init__(self) -> None:
        self.env = tuple()
    
    def add_class(self,name:str,cls:Class):
        self.env = ((name,cls),) + self.env
    
    def lookup_class(self,cls_name:str):
        for name,_cls in self.env:
            if name == cls_name:
                return _cls
        raise NameError(f'class name : {cls_name} is not bound in the env {the_class_env}')
    
    def __str__(self) -> str:
        return str([i[0] for i in self.env])

the_class_env = Class_Env()

def add_to_class_env(name:str,cls:Class):
    the_class_env.add_class(name,cls)

def lookup_class(cls_name:str) -> Class:
    return the_class_env.lookup_class(cls_name)


def init_class_env(decls:tuple[ast.Class_Decl]):
    the_class_env.__init__()
    the_class_env.add_class('object',Class(None,(),()))
    for decl in decls: add_class_decl(decl)

def add_class_decl(decl:ast.Class_Decl) -> None:
    parent_cls = lookup_class(decl.parent)
    field_names = append_field_names(parent_cls.field_names,decl.fields)
    method_env = method_decls_to_env(decl.methods,decl.name,field_names)
    cls = Class(decl.parent,field_names,method_env)
    add_to_class_env(decl.name,cls)

from itertools import count
new_id = count()
def fresh_identifier(name):
    return f'{name}%{next(new_id)}'

def append_field_names(supers:tuple[str],fields:tuple[str]) -> tuple[str]:
    f = lambda super: fresh_identifier(super) if super in fields else super
    return tuple(f(super) for super in supers) + fields


def method_decls_to_env(decls:tuple[ast.Method_Decl],name:str,fields:tuple[str])\
    -> Method_Env_T:
    def method_from(decl:ast.Method_Decl):
        return Method(decl.vars,decl.body,name,fields)
    return tuple((decl.name,method_from(decl)) for decl in decls)

def find_method(cls_name:str,name:str) -> Method:
    cls = lookup_class(cls_name)
    for m_name,method in cls.method_env:
        if m_name == name:
            return method
    if cls.super_name is not None:
        return find_method(cls.super_name,name)
    raise NameError(f"{name} field is not found in {cls_name}")

def super_name(meth:Method):
    return lookup_class(meth.name).super_name

def new_object(cls_name:str):
    from memory import newref
    field_names = lookup_class(cls_name).field_names
    # the val passed to newref can be any
    res = Object(cls_name,tuple(newref(['%uninitialized',name]) for name in field_names))
    return res

def fieldref(obj:Object,field_name:str):
    cls = lookup_class(obj.name)
    for name,ref in zip(cls.field_names,obj.fields):
        if name == field_name:
            return ref
    raise NameError(field_name,obj)

def fieldset(obj:Object,field_name:str,val):
    from memory import setref
    ref = fieldref(obj,field_name)
    setref(ref,val)

def instanceof(name,cls_name):
    if name is None:
        return False
    elif name != cls_name:
        name = lookup_class(name).super_name
        return instanceof(name,cls_name)
    else:
        return True
