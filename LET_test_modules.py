def test_modules():
    from LET import value_of_prog
    from CHECKED import type_of_prog
    import LET_ast_node as ast
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
    
    from LET_environment import Repeated_Module_Error
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
    print('end of test modules')
    
def test_typed_modules():
    from LET import value_of_prog
    import LET_ast_node as ast
    from CHECKED import type_of_prog
    from LET_parser import parser
    parse = parser.parse
    prog = '''
    module m1
    interface [
        transparent t = int
        z : t
        s : (t -> t)
        is_z? : (t -> bool)
    ] body [
        type t = int
        z = 33
        s = proc (x : t) -(x,-1)
        is_z? = proc (x : t) zero?(-(x,z))
        ]
    proc (x : m1.t) (m1.is_z? -(x,0))
    '''
    ans = parse('type (int -> bool)')
    assert(type_of_prog(prog) == ans)
    value_of_prog(prog)
    
    prog = '''
    module m1
    interface
    [opaque t
    z:t
    s : (t -> t)
    is_z? : (t -> bool)]
    body
    [type t = int
    z = 33
    s = proc (x : t) -(x,-1)
    is_z? = proc (x : t) zero?(-(x,z))]
    proc (x : m1.t)
    (m1.is_z? x)
    '''
    ans = parse('type (m1.t -> bool)')
    assert(type_of_prog(prog) == ans)
    value_of_prog(prog)
    
    prog = '''
    module colors
    interface
    [opaque color
    red : color
    green : color
    is_red? : (color -> bool)]
    body
    [type color = int
    red = 0
    green = 1
    is_red? = proc (c : color) zero?(c)]
    newpair(colors.red,newpair(colors.green,colors.is_red?))
    '''
    ans = 'type pairof colors.color * pairof colors.color * (colors.color -> bool)'
    assert(type_of_prog(prog) == parse(ans))
    
    prog = '''
    module ints1
    interface
    [opaque t
    zero : t
    succ : (t -> t)
    pred : (t -> t)
    is_zero : (t -> bool)]
    body
    [type t = int
    zero = 0
    succ = proc(x : t) -(x,-5)
    pred = proc(x : t) -(x,5)
    is_zero = proc (x : t) zero?(x)]
    let z = from ints1 take zero
    in let s = from ints1 take succ
    in let p = from ints1 take pred
    in let z? = from ints1 take is_zero
    in letrec int to_int (x : from ints1 take t) =
    if (z? x)
    then 0
    else -((to_int (p x)), -1)
    in newpair((s (s z)),(to_int (s (s z))))
    '''
    assert(type_of_prog(prog) == parse('type pairof ints1.t * int'))
    assert(value_of_prog(prog) == ast.Pair(10,2))
    
    prog = '''
    module ints2
    interface
    [opaque t
    zero : t
    succ : (t -> t)
    pred : (t -> t)
    is_zero : (t -> bool)]
    body
    [type t = int
    zero = 0
    succ = proc(x : t) -(x,3)
    pred = proc(x : t) -(x,-3)
    is_zero = proc (x : t) zero?(x)]
    let z = from ints2 take zero
    in let s = from ints2 take succ
    in let p = from ints2 take pred
    in let z? = from ints2 take is_zero
    in letrec int to_int (x : from ints2 take t)
    = if (z? x)
    then 0
    else -((to_int (p x)), -1)
    in newpair((to_int (s (s z))),(s (s z)))
    '''
    assert(type_of_prog(prog) == parse('type pairof int * ints2.t'))
    assert(value_of_prog(prog) == ast.Pair(2,-6))
    
    print('end of test typed modules')
    
if __name__ == '__main__':
    test_modules()
    test_typed_modules()
    
