from LET_parser import parser
from LET_ast_node import *
from LET_environment import (
    Environment,
    init_env,
    empty_senv,
    empty_nameless_env,
    apply_senv,
    apply_nameless_env,
    extend_nameless_env_vals,
    extend_senv_vars
)

from LET import (
    Let_Interpreter,
    expand_let_star,
    expand_conditional,
)

def value_of_prog(prog:str, env = init_env(), parse = parser.parse):
    return Nameless_Let_Interpreter().value_of_prog(prog,env,parse)

def translation_of(expr,static_env):
    match expr:
        case Const():
            return expr
        case Var(var):
            return Nameless_Var_Exp(apply_senv(static_env, var))
        case Diff_Exp(left,right):
            return Diff_Exp(translation_of(left,static_env),translation_of(right,static_env))
        case Zero_Test(e):
            return Zero_Test(translation_of(e,static_env))
        case Branch(pred,conseq,alter):
            return Branch(
                translation_of(pred,static_env),
                translation_of(conseq,static_env),
                translation_of(alter,static_env)
            )
        case Proc_Exp(params,body,types):
            new_senv = extend_senv_vars(params,static_env)
            return Nameless_Proc_Exp(translation_of(body,new_senv))
        case Apply(operator,operand):
            proc = translation_of(operator,static_env)
            if operand != () and isinstance(operand[0],Unpack_Exp):
                args = translation_of(operand[0].list_expr,static_env)
                args = (Unpack_Exp(None,args,None),)
            else:
                args = map(lambda o : translation_of(o, static_env), operand)
                args = tuple(args)
            return Apply(proc,args)
        case Rec_Proc(var,params,body,expr,res_types,arg_types):
            new_senv = extend_senv_vars(var,static_env)
            translate = lambda params,body: translation_of(Proc_Exp(params,body),new_senv)
            exps = tuple(translate(*args) for args in zip(params,body))
            return Nameless_Rec_Exp(exps,translation_of(expr,new_senv))
        case Let(vars,exps,body):
            new_senv = extend_senv_vars(vars,static_env)
            exps = tuple(translation_of(exp,static_env) for exp in exps)
            return Nameless_Let_Exp(exps,translation_of(body,new_senv))
        case Primitive(op,exps):
            return translation_of(Apply(Var(op),exps),static_env)
        case List(exps):
            return translation_of(Apply(Var('list'),tuple(exps)),static_env)
        case Pair_Exp(left,right):
            return translation_of(Apply(Var('cons'),(left,right)),static_env)
        case Let_Star():
            return translation_of(expand_let_star(expr),static_env)
        case Conditional():
            return translation_of(expand_conditional(expr),static_env)
        case Unpack_Exp(vars,list_expr,expr):
            return translation_of(Apply(Proc_Exp(vars,expr),
                                        (Unpack_Exp(None,list_expr,None),)),
                                static_env)
        case _:
            raise Exception("Uknown NAMELESS-LET TRANSLATION expression type", expr)

class Nameless_Let_Interpreter:
    def value_of_prog(self,prog:str, env = init_env(), parse = parser.parse):
        # workaround
        # so that it can use the same test cases used by other LET variants.
        # the test cases use ordinary environment
        # the code below is to translate that env to static env and nameless env accordingly
        senv = empty_senv()
        nameless_env = empty_nameless_env()
        assert(isinstance(env,Environment))
        for e in env:
            vars = tuple(p[0] for p in e)
            vals = tuple(p[1] for p in e)
            senv = extend_senv_vars(vars,senv)
            nameless_env = extend_nameless_env_vals(vals,nameless_env)
        nameless_prog = translation_of(parse(prog),senv)
        return self.value_of(nameless_prog, nameless_env)
    
    def apply_proc(self,proc:Proc_Val|Primitve_Implementation,args):
        if isinstance(proc,Primitve_Implementation):
            return Let_Interpreter.apply_primitive(self,proc,args)
        env = extend_nameless_env_vals(args,proc.env)
        return self.value_of(proc.body,env)

    def value_of(self,expr, nameless_env):
        value_of = self.value_of
        apply_proc = self.apply_proc
        match expr:
            case Nameless_Var_Exp(id):
                return apply_nameless_env(nameless_env,id)
            case Nameless_Rec_Exp(exps,body):  
                vals = tuple(value_of(exp,nameless_env) for exp in exps)
                new_env =  extend_nameless_env_vals(vals,nameless_env)
                for val in vals: 
                    val.env = new_env
                return value_of(body,new_env)
            case Nameless_Proc_Exp(body):
                return Proc_Val(None,body,nameless_env)
            case Nameless_Let_Exp(exps,body):
                'deprecated as let expression can be derived'
                vals = tuple(value_of(exp,nameless_env) for exp in exps)
                new_env = extend_nameless_env_vals(vals,nameless_env)
                return value_of(body,new_env)
            case Apply(operator,operand):
                proc = value_of(operator,nameless_env)
                if len(operand) == 1 and isinstance(operand[0],Unpack_Exp):
                    args = value_of(operand[0].list_expr,nameless_env)
                else:
                    args = map(lambda o : value_of(o, nameless_env), operand)
                args = tuple(args)
                return apply_proc(proc,args)
            case _:
                return Let_Interpreter.value_of(self,expr,nameless_env)
    
