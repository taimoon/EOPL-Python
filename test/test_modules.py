from MODULES import value_of_prog

import LET_ast_node as ast
from LET_environment import Repeated_Binding

def test_simple_module(type_of_prog):
    prog = '''\
    module m1
        interface [
            a : int
            b : int
            c : int]
        body
        [a = 33
        x = -(a,1) % = 32
        b = -(a,x) % = 1
        c = -(x,b)] % = 31
    let a = 10
    in -(-(m1.a, m1.b),a)
    '''
    assert(type_of_prog(prog) == ast.Int_Type())
    assert(value_of_prog(prog) == 22)


def test_multiple_modules(type_of_prog):
    prog = '''
    module m1
        interface
            [a : int
            b : int
            c : int]
        body
            [a = 33
            b = 44
            c = 55]
    module m2
        interface
            [a : int
            b : int]
        body
            [a = 66
            b = 77]
    let z = 99
    in -(z, -(m1.a, m2.a))
    '''
    assert(type_of_prog(prog) == ast.Int_Type())
    assert(value_of_prog(prog) == 132)


def test_repeated_binding(type_of_prog):
    try:
        prog = '''\
        module m1
        interface [a : int] body [a = 33]
        module m1
        interface [b : int] body [b = 101]
        10
        '''
        type_of_prog(prog)
        assert(False)
    except Repeated_Binding:
        print("Test Pass: Error is detected", Repeated_Binding)
        assert(True)
    except Exception as e:
        print(e)
        assert(False)


def test_module_in_module(type_of_prog):
    prog = '''\
    module m1
    interface
        [u : int
        v : int]
    body
        module m2
        interface [v : int]
        body [v = 33]
        [u = 44
         v = -(m2.v, 1)]
    m1.v
    '''
    assert(type_of_prog(prog) == ast.Int_Type())
    assert(value_of_prog(prog) == 32)
   

def test_let_module(type_of_prog):
    prog = '''
    module m1
    interface
        [x : int]
    body
        let 
            x = 2
        in  [x = *(x,x)]
    m1.x
    '''
    assert(type_of_prog(prog) == ast.Int_Type())
    assert(value_of_prog(prog) == 4)


def test_letrec_module(type_of_prog):
    prog = lambda x: f'''
    module odd_even
    interface
        [even : (int -> bool)
         odd : (int -> bool)]
    body
        letrec
            int local_even(x:int) = if zero?(x) then 1 else (local_odd -(x,1))
            int local_odd(x:int) = if zero?(x) then 0 else (local_even -(x,1))
        in [
        even = proc(x:int) equal?((local_even x), 1)
        odd = proc(x:int) zero?((local_odd x))
        ]
    (odd_even.even {x})
    '''
    assert(type_of_prog(prog(6)) == ast.Bool_Type())
    assert(value_of_prog(prog(6)) is True)
    

def test_by_variant(type_of_prog):
    test_simple_module(type_of_prog)
    test_multiple_modules(type_of_prog)
    test_repeated_binding(type_of_prog)
    test_module_in_module(type_of_prog)
    test_let_module(type_of_prog)
    test_letrec_module(type_of_prog)

def test_all():
    from CHECKED_MODULES import type_of_prog
    test_by_variant(type_of_prog)
    print('end of test modules')
    from CHECKED_OPAQUE import type_of_prog
    test_by_variant(type_of_prog)
    print('end of test modules')
    from CHECKED_PROC_MODULES import type_of_prog
    test_by_variant(type_of_prog)
    print('end of test modules')


if __name__ == '__main__':
    test_all()
