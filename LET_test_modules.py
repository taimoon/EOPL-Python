def test_modules():
    from LET import value_of_prog
    from CHECKED import type_of_prog
    import LET_ast_node as ast
    from LET_parser import parser
    parse = parser.parse
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
    
    from CHECKED import Repeated_Module_Error
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
    except Repeated_Module_Error:
        print("Test Pass: Error is detected")
        assert(True)
    except:
        assert(False)
    
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
    
    prog = '''
    module m1
    interface
        [x : int]
    body
        let 
            x = 2
        in  [y = x]
    m1.y
    '''
    assert(value_of_prog(prog) == 2)
    
    prog = '''
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
    (odd_even.even 6)
    '''
    assert(type_of_prog(prog) == ast.Bool_Type())
    assert(value_of_prog(prog) is True)
    
    
if __name__ == '__main__':
    test_modules()
