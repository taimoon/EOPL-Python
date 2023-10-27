from dataclasses import dataclass
import typing
from typing import Callable

@dataclass
class Expr:...
@dataclass
class Type:...

@dataclass
class Branch(Expr):
    pred:Expr
    conseq:Expr
    alter:Expr

@dataclass
class Clause:
    pred:Expr
    conseq:Expr

@dataclass
class Conditional(Expr):
    clauses:tuple[Clause]
    otherwise:Expr

@dataclass
class Diff_Exp(Expr):
    'Deprecated : As derived form using Primitive_Exp; see LET_parser'
    left:Expr
    right:Expr

@dataclass
class Zero_Test(Expr):
    'Deprecated : As derived form using Primitive_Exp; see LET_parser'
    exp:Expr

@dataclass
class Primitve_Implementation:
    'interpreter data struct'
    op:typing.Any
    env:typing.Any = None

@dataclass
class Primitive(Expr):
    op:Expr
    exps:Expr

@dataclass
class Bi_Op:
    op:Callable

@dataclass
class Unary_Op:
    op:Callable

@dataclass
class Var(Expr):
    var:str

@dataclass
class Let(Expr):
    vars:str
    exps:tuple[Expr]
    body:Expr

@dataclass
class Let_Star(Expr):
    vars:str
    exps:tuple[Expr]
    body:Expr

@dataclass
class Const(Expr):
    val:int|bool|float|str

@dataclass
class Proc_Exp(Expr):
    params:tuple[str]
    body:Expr
    types:tuple[Type] = None

@dataclass
class Proc_Val:
    'interpreter data struct'
    params:tuple[str]
    body:Expr
    env:typing.Any
    types:tuple[Type] = None

@dataclass
class Rec_Proc(Expr):
    var:tuple[str]
    params:tuple[tuple[str]]
    body:tuple[Expr]
    expr:Expr
    res_types:tuple[Type] = None
    arg_types:tuple[Type] = None

@dataclass
class Apply(Expr):
    operator:Expr
    operand:tuple[Expr]

@dataclass
class Pair:
    '''Pair is a recursive data structure that form list and tree.
    The __iter__ yield its data that's similiar to __iter__(list)
    This allows the original interpreter's procedure application can use the same "for in" statements to unload the arguments for both tuple and List. 
    '''
    car: typing.Any
    cdr: typing.Any
    def __iter__(self):
        if isinstance(self.cdr,NULL):
            yield self.car
        else:
            yield self.car
            yield from self.cdr

    def __str__(self,start=True) -> str:
        if isinstance(self.cdr, NULL):
            if start:
                return f'({self.car})'
            else:
                return f'{self.car})'
        
        if not isinstance(self.cdr, Pair):
            x = f'({self.car} . {self.cdr})'
            if start:
                return x
            else:
                return x + ')'
        
        x = str(self.car)
        if start:
            x = '(' + x
        return x + ' ' + self.cdr.__str__(False)

    @staticmethod
    def list_to_pair(*args):
        if args == ():
            return NULL()
        else:
            return Pair(args[0], Pair.list_to_pair(*args[1:]))
    
@dataclass
class Pair_Exp(Expr):
    left:None
    right:None
    homogeneous:bool = False

@dataclass
class Unpair_Exp(Expr):
    left:None
    right:None
    pair_exp:None
    expr:None


@dataclass(init=False)
class Mutable_Pair:
    _car: typing.Any
    _cdr: typing.Any
    
    def __init__(self,left,right):
        from memory import newref,setref,deref
        self.newref = newref
        self.setref = setref
        self.deref = deref
        self._car = self.newref(left)
        self._cdr = self.newref(right)
        
    def setcar(self,v):
        self.setref(self._car,v)
    
    def setcdr(self,v):
        self.setref(self._cdr,v)
    
    @property
    def car(self):
        return self.deref(self._car)
    
    @property
    def cdr(self):
        return self.deref(self._cdr)

    @staticmethod
    def list_to_pair(*args):
        if args == ():
            return NULL()
        else:
            return Mutable_Pair(args[0], Mutable_Pair.list_to_pair(*args[1:]))
    
    def __iter__(self):
        if isinstance(self.cdr,NULL):
            yield self.car
        else:
            yield self.car
            yield from self.cdr
    
    def __str__(self,start=True) -> str:
        if isinstance(self.cdr, NULL):
            if start:
                return f'({self.car})'
            else:
                return f'{self.car})'
        
        if not isinstance(self.cdr, Mutable_Pair):
            x = f'({self.car} . {self.cdr})'
            if start:
                return x
            else:
                return x + ')'
        
        x = str(self.car)
        if start:
            x = '(' + x
        return x + ' ' + self.cdr.__str__(False)

        
@dataclass
class List(Expr):
    exps:tuple[Expr]

@dataclass
class NULL(Expr):
    t:Type = None
    def __str__(self) -> None:
        return '()'
    def __post_init__(self):
        self.t = No_Type() if self.t is None else self.t

@dataclass
class Null_Exp(Expr):
    expr:Expr

@dataclass
class Unpack_Exp(Expr):
    'interpreter data struct'
    'but also AST'
    vars:typing.Any
    list_expr:typing.Any
    expr:typing.Any

@dataclass
class Nameless_Var_Exp:
    'nameless LET data structure'
    id:int|tuple[int,int]

@dataclass
class Nameless_Proc_Exp:
    'nameless LET data structure'
    body:typing.Any

@dataclass
class Nameless_Let_Exp:
    'nameless LET data structure'
    exps:tuple[typing.Any]
    body:typing.Any

@dataclass
class Nameless_Rec_Exp:
    'nameless LET data structure'
    exps:tuple[typing.Any]
    body:typing.Any

@dataclass
class Sequence(Expr):
    exps:tuple[Expr]
    
@dataclass
class NewRef(Expr):
    expr:Expr
    
@dataclass
class DeRef(Expr):
    expr:Expr

@dataclass
class SetRef(Expr):
    loc:Expr
    expr:Expr
    
@dataclass
class Ref(Expr):
    var:Expr

@dataclass
class Assign(Expr):
    var:str
    expr:Expr

@dataclass
class Letmutable(Expr):
    vars:tuple[Expr]
    exps:tuple[Expr]
    body:Expr

@dataclass
class Thunk:
    'lazy interpreter data structure'
    expr:typing.Any
    env:typing.Any

# CONTINUATION
@dataclass
class Try(Expr):
    exp:Expr
    var:str
    handler:None

@dataclass
class Raise(Expr):
    exp:Expr

# TYPE
@dataclass
class Int_Type(Type):
    def __str__(self) -> str:
        return 'int'

@dataclass
class Bool_Type(Type):
    def __str__(self) -> str:
        return 'bool'

@dataclass
class Proc_Type(Type):
    arg_type:tuple
    res_type:typing.Any
    def __str__(self) -> str:
        res_t_str = self.res_type.__str__()
        arg_t_str = ' * '.join(str(t) for t in self.arg_type)
        out = f'({arg_t_str} -> {res_t_str})'
        return out
    @property
    def result_type(self): 
        raise DeprecationWarning

@dataclass
class Void_Type(Type):
    def __str__(self) -> str:
        return 'void'

@dataclass
class No_Type(Type):
    def __str__(self) -> str:
        return '?'

@dataclass
class Pair_Type(Type):
    t0:Type
    t1:Type
    def __str__(self) -> str:
        return f'pairof {self.t0} * {self.t1}'

@dataclass
class List_Type(Type):
    t:Type
    def __str__(self) -> str:
        return f'listof {self.t}'
    
@dataclass
class Qualified_Type(Type):
    module_name:str
    type_name:str

@dataclass
class Named_Type(Type):
    name:str


# MODULE
@dataclass
class Var_Def:
    name:str
    expr:Expr

@dataclass
class Type_Def:
    name:str
    type:Type

@dataclass
class Var_Decl:
    name:str
    type:Type

@dataclass
class Opaque_Type_Decl:
    name:str

@dataclass
class Transparent_Type_Decl:
    name:str
    type:Type

Decl_Type = Var_Decl|Opaque_Type_Decl|Transparent_Type_Decl
Def_Type = Var_Def|Type_Def

@dataclass
class Module_Def:
    name:str
    interface: tuple[Decl_Type]
    modules:tuple
    let_block:Let|Let_Star|Letmutable|Rec_Proc
    body: tuple[Def_Type]

@dataclass
class Qualified_Var_Exp:
    module_name:str
    var_name:str

@dataclass
class Proc_Interface:
    params:tuple[str]
    interfaces:tuple[tuple[Decl_Type]]
    res_interface:tuple[Decl_Type]

@dataclass
class Proc_Module:
    'interpreter data structure'
    params:tuple[str]
    body:tuple[Def_Type]
    env:None

@dataclass
class Proc_Module_Body:
    params:tuple
    interfaces:tuple[tuple[Decl_Type]]
    body:tuple[Def_Type]

@dataclass
class Var_Module_Body:
    name:str

@dataclass
class App_Module_Body:
    operator:None
    operands:tuple

Module_Body_T  = tuple[Var_Def|Type_Def]|Proc_Module_Body|Var_Module_Body|App_Module_Body

# CLASS
@dataclass
class Method_Decl:
    name:str
    vars:tuple
    body:None

@dataclass
class Class_Decl:
    name:str
    parent:str
    fields:tuple[str]
    methods:tuple[Method_Decl]

@dataclass
class Program:
    classes:tuple[Class_Decl]
    modules:tuple[Module_Def]
    expr:typing.Any

@dataclass
class New_Obj_Exp:
    cls_name:str
    operands:tuple

@dataclass
class Method_Call_Exp:
    obj_exp:None
    method_name:str
    operands:tuple

@dataclass
class Super_Call_Exp:
    method_name:str
    operands:tuple

@dataclass
class Self_Exp:
    pass

@dataclass
class Instance_Exp:
    exp:None
    cls_name:str
    
@dataclass
class Field_Ref:
    obj_exp:None
    field_name:str

@dataclass
class Field_Set:
    obj_exp:None
    field_name:str
    exp:None
