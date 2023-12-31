from dataclasses import dataclass
from typing import Callable
from LET_environment import Environment as Env

@dataclass
class Cont:
    cc:Callable[[int],int]

@dataclass
class End_Cont(Cont):
    cc:Callable[[int],int] = None
    
@dataclass
class Zero_Cont(Cont):
    pass

@dataclass
class Paramless_Cont(Cont):
    pass
    
@dataclass
class Branch_Cont(Cont):
    env:Env
    conseq:None
    alter:None

@dataclass
class Diff_Cont1(Cont):
    env:Env
    exp2:None

@dataclass
class Diff_Cont2(Cont):
    v:int

@dataclass
class Args_Cont(Cont):
    env:Env
    exps:list
    acm_vals:list
    immutability:bool = False
    
@dataclass
class Operand_Cont(Cont):
    proc:None

@dataclass
class Operator_Cont(Cont):
    env:Env
    list_expr:None

@dataclass
class Try_Cont(Cont):
    var:str
    handler:None
    env:Env
    cc:Cont

@dataclass
class Raise_Cont(Cont):
    pass
@dataclass
class Seq_Cont(Cont):
    exps:tuple
    env:Env

@dataclass
class NewRef_Cont(Cont):
    pass

@dataclass
class DeRef_Cont(Cont):
    pass

@dataclass
class SetRef_Cont1(Cont):
    exp:None
    env:Env

@dataclass
class SetRef_Cont2(Cont):
    loc:int

@dataclass
class Assign_Cont(Cont):
    env:Env
    var:str

@dataclass
class Ref_Cont(Cont):
    pass
