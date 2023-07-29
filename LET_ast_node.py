from dataclasses import dataclass
import typing

@dataclass
class Branch:
    pred:typing.Any
    conseq:typing.Any
    alter:typing.Any

@dataclass
class Clause:
    pred:typing.Any
    conseq:typing.Any

@dataclass
class Conditional:
    clauses:tuple[Clause]
    otherwise:typing.Any

@dataclass
class Diff_Exp:
    'Deprecated : As derived form using Primitive_Exp; see LET_parser'
    left:typing.Any
    right:typing.Any

@dataclass
class Zero_Test_Exp:
    'Deprecated : As derived form using Primitive_Exp; see LET_parser'
    exp:typing.Any

@dataclass
class Primitve_Implementation:
    'interpreter data struct'
    op:typing.Any
    env:typing.Any = None

@dataclass
class Primitive_Exp:
    op:typing.Any
    exps:typing.Any

@dataclass
class Bi_Op:
    op:typing.Any

@dataclass
class Unary_Op:
    op:typing.Any

@dataclass
class Var_Exp:
    var:str

@dataclass
class Let_Exp:
    vars:str
    exps:typing.Any
    body:typing.Any

@dataclass
class Let_Star_Exp:
    vars:str
    exps:typing.Any
    body:typing.Any

@dataclass
class Const_Exp:
    val:typing.Any

@dataclass
class Proc_Exp:
    params:typing.Any
    body:typing.Any
    types:typing.Any = None

@dataclass
class Proc_Val:
    'interpreter data struct'
    params:typing.Any
    body:typing.Any
    env:typing.Any
    types:typing.Any = None

@dataclass
class Rec_Proc:
    var:typing.Any
    params:typing.Any
    body:typing.Any
    expr:typing.Any
    res_types:typing.Any = None
    arg_types:typing.Any = None

@dataclass
class App_Exp:
    operator:typing.Any
    operand:typing.Any

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
class Pair_Exp:
    left:None
    right:None
    homogeneous:bool = False

@dataclass
class Unpair_Exp:
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
class List:
    exps:typing.Any

@dataclass
class NULL:
    t:typing.Any = None
    def __str__(self) -> None:
        return '()'
    def __post_init__(self):
        self.t = No_Type() if self.t is None else self.t

@dataclass
class Null_Exp:
    expr:typing.Any

@dataclass
class Unpack_Exp:
    'interpreter data struct'
    'but also AST'
    vars:typing.Any
    list_expr:typing.Any
    expr:typing.Any

@dataclass
class Nameless_Var_Exp:
    'nameless LET data structure'
    id:int

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
class Sequence:
    exps:typing.Any
    
@dataclass
class NewRef:
    expr:typing.Any
    
@dataclass
class DeRef:
    expr:typing.Any

@dataclass
class SetRef:
    loc:typing.Any
    expr:typing.Any
    
@dataclass
class Ref:
    var:typing.Any

@dataclass
class Assign_Exp:
    var:None
    expr:None

@dataclass
class Letmutable_Exp:
    vars:str
    exps:typing.Any
    body:typing.Any

@dataclass
class Thunk:
    'lazy interpreter data structure'
    expr:typing.Any
    env:typing.Any


# TYPE
@dataclass
class Int_Type:
    def __str__(self) -> str:
        return 'int'

@dataclass
class Bool_Type:
    def __str__(self) -> str:
        return 'bool'

@dataclass
class Proc_Type:
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
class Void_Type:
    def __str__(self) -> str:
        return 'void'

@dataclass
class No_Type:
    def __str__(self) -> str:
        return '?'

@dataclass
class Pair_Type:
    t0:typing.Any
    t1:typing.Any
    def __str__(self) -> str:
        return f'pairof {self.t0} * {self.t1}'

@dataclass
class List_Type:
    t:typing.Any
    def __str__(self) -> str:
        return f'listof {self.t}'
    
@dataclass
class Qualified_Type:
    module_name:str
    type_name:str

@dataclass
class Named_Type:
    name:str


# MODULE
@dataclass
class Var_Def:
    name:str
    expr:typing.Any

@dataclass
class Type_Def:
    name:str
    type:None

@dataclass
class Var_Decl:
    name:str
    type:None

@dataclass
class Opaque_Type_Decl:
    name:str

@dataclass
class Transparent_Type_Decl:
    name:str
    type:None

Decl_Type = Var_Decl|Opaque_Type_Decl|Transparent_Type_Decl
Def_Type = Var_Def|Type_Def

@dataclass
class Module_Def:
    name:str
    interface: tuple[Decl_Type]
    modules:tuple
    let_block:Let_Exp|Let_Star_Exp|Letmutable_Exp|Rec_Proc
    body: tuple[Def_Type]

@dataclass
class Qualified_Var_Exp:
    module_name:str
    var_name:str

@dataclass
class Proc_Interface:
    params:tuple
    interfaces:tuple[tuple[Decl_Type]]
    res_interface:tuple[Decl_Type]

@dataclass
class Proc_Module:
    'interpreter data structure'
    params:tuple
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
