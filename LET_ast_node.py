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
    left:typing.Any
    right:typing.Any

@dataclass
class Primitive_Exp:
    op:typing.Any
    exps:typing.Any
    
@dataclass
class Zero_Test_Exp:
    exp:typing.Any

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

@dataclass
class Proc_Val:
    params:typing.Any
    body:typing.Any
    env:typing.Any

@dataclass
class Rec_Proc:
    var:typing.Any
    params:typing.Any
    body:typing.Any
    expr:typing.Any

@dataclass
class App_Exp:
    operator:typing.Any
    operand:typing.Any

@dataclass
class Pair:
    car: typing.Any
    cdr: typing.Any
    def unpack(self):
        if isinstance(self.cdr,NULL):
            return (self.car,)
        else:
            return  (self.car,) + self.cdr.unpack()
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

@dataclass
class List:
    exps:typing.Any
    
class NULL:
    def __str__(self) -> None:
        return '()'

@dataclass
class Unpack_Exp:
    vars:typing.Any
    list_expr:typing.Any
    expr:typing.Any

@dataclass
class Nameless_Var_Exp:
    id:int

@dataclass
class Nameless_Proc_Exp:
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