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
    if isinstance(expr, Const_Exp):
        return expr
    elif isinstance(expr, Var_Exp):
        return Nameless_Var_Exp(apply_senv(static_env, expr.var))
    elif isinstance(expr, Diff_Exp):
        return Diff_Exp(translation_of(expr.left,static_env),translation_of(expr.right,static_env))
    elif isinstance(expr, Zero_Test_Exp):
        return Zero_Test_Exp(translation_of(expr.exp,static_env))
    elif isinstance(expr, Branch):
        return Branch(
            translation_of(expr.pred,static_env),
            translation_of(expr.conseq,static_env),
            translation_of(expr.alter,static_env)
        )
    elif isinstance(expr, Proc_Exp):
        new_senv = extend_senv_vars(expr.params,static_env)
        return Nameless_Proc_Exp(translation_of(expr.body,new_senv))
    elif isinstance(expr, App_Exp):
        proc = translation_of(expr.operator,static_env)
        if expr.operand != () and isinstance(expr.operand[0],Unpack_Exp):
            args = translation_of(expr.operand[0].list_expr,static_env)
            args = (Unpack_Exp(None,args,None),)
        else:
            args = map(lambda o : translation_of(o, static_env), expr.operand)
            args = tuple(args)
        return App_Exp(proc,args)
    elif isinstance(expr, Rec_Proc):
        new_senv = extend_senv_vars(expr.var,static_env)
        translate = lambda params,body: translation_of(Proc_Exp(params,body),new_senv)
        exps = tuple(translate(*args) for args in zip(expr.params,expr.body))
        return Nameless_Rec_Exp(exps,translation_of(expr.expr,new_senv))
    elif isinstance(expr, Primitive_Exp):
        return translation_of(App_Exp(Var_Exp(expr.op),expr.exps),static_env)
    elif isinstance(expr,List):
        return translation_of(App_Exp(Var_Exp('list'),tuple(expr.exps)),static_env)
    elif isinstance(expr,Pair_Exp):
        return translation_of(App_Exp(Var_Exp('cons'),(expr.left,expr.right)),static_env)
    elif isinstance(expr,Let_Exp):
        # derived form
        # return translation_of(App_Exp(Proc_Exp(expr.vars, expr.body), expr.exps), static_env)
        new_senv = extend_senv_vars(expr.vars,static_env)
        exps = tuple(translation_of(exp,static_env) for exp in expr.exps)
        return Nameless_Let_Exp(exps,translation_of(expr.body,new_senv))
    elif isinstance(expr,Let_Star_Exp):
        return translation_of(expand_let_star(expr),static_env)
    elif isinstance(expr,Conditional):
        return translation_of(expand_conditional(expr),static_env)
    elif isinstance(expr,Unpack_Exp):
        return translation_of(App_Exp(Proc_Exp(expr.vars,expr.expr),
                                      (Unpack_Exp(None,expr.list_expr,None),)),
                              static_env)
    else:
        raise Exception("Uknown NAMELESS-LET TRANSLATION expression type", expr)

class Nameless_Let_Interpreter:
    def value_of_prog(self,prog:str, env = init_env(), parse = parser.parse):
        # workaround
        # so that it can use the same test cases used by other LET variants.
        # the test cases use ordinary environment
        # the code below is to translate that env to static env and nameless env accordingly
        senv = empty_senv()
        nameless_env = empty_nameless_env()
        if isinstance(env,Environment):
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
        env = proc.env
        env = extend_nameless_env_vals(args,env)
        return self.value_of(proc.body,env)

    def value_of(self,expr, nameless_env):
        value_of = self.value_of
        apply_proc = self.apply_proc
        if isinstance(expr, Nameless_Var_Exp):
            return apply_nameless_env(nameless_env,expr.id)
        elif isinstance(expr,Nameless_Rec_Exp):
            vals = tuple(value_of(exp,nameless_env) for exp in expr.exps)
            new_env =  extend_nameless_env_vals(vals,nameless_env)
            for val in vals: 
                val.env = new_env
            return value_of(expr.body,new_env)
        elif isinstance(expr, Nameless_Proc_Exp):
            return Proc_Val(None,expr.body,nameless_env)
        elif isinstance(expr,Nameless_Let_Exp):
            'deprecated as let expression can be derived'
            vals = tuple(value_of(exp,nameless_env) for exp in expr.exps)
            new_env = extend_nameless_env_vals(vals,nameless_env)
            return value_of(expr.body,new_env)
        elif isinstance(expr, App_Exp):
            proc = value_of(expr.operator,nameless_env)
            if len(expr.operand) == 1 and isinstance(expr.operand[0],Unpack_Exp):
                args = value_of(expr.operand[0].list_expr,nameless_env)
            else:
                args = map(lambda o : value_of(o, nameless_env), expr.operand)
            args = tuple(args)
            return apply_proc(proc,args)
        else:
            return Let_Interpreter.value_of(self,expr,nameless_env)
