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
    
@dataclass
class Operand_Cont(Cont):
    proc:None

@dataclass
class Operator_Cont(Cont):
    env:Env
    list_expr:None


