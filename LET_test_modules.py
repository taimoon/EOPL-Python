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
    is-red? : (color -> bool)]
    body
    [type color = int
    red = 0
    green = 1
    is-red? = proc (c : color) zero?(c)]
    newpair(colors.red,newpair(colors.green,colors.is-red?))
    '''
    ans = 'type pairof colors.color * pairof colors.color * (colors.color -> bool)'
    assert(type_of_prog(prog) == parse(ans))
    
    prog_ints1 = '''
    module ints1
    interface
    [opaque t
    zero : t
    succ : (t -> t)
    pred : (t -> t)
    is-zero : (t -> bool)]
    body
    [type t = int
    zero = 0
    succ = proc(x : t) -(x,-5)
    pred = proc(x : t) -(x,5)
    is-zero = proc (x : t) zero?(x)]
    '''
    
    prog = f'''{prog_ints1}
    let z = ints1.zero
    in let s = ints1.succ
        p = ints1.pred
        z? = ints1.is-zero
    in letrec int to-int (x : ints1.t) =
    if (z? x)
    then 0
    else -((to-int (p x)), -1)
    in newpair((s (s z)),(to-int (s (s z))))
    '''
    assert(type_of_prog(prog) == parse('type pairof ints1.t * int'))
    assert(value_of_prog(prog) == ast.Pair(10,2))
    
    prog_ints2 = '''
    module ints2
    interface
    [opaque t
    zero : t
    succ : (t -> t)
    pred : (t -> t)
    is-zero : (t -> bool)]
    body
    [type t = int
    zero = 0
    succ = proc(x : t) -(x,3)
    pred = proc(x : t) -(x,-3)
    is-zero = proc (x : t) zero?(x)]
    '''
    
    prog = f'''{prog_ints2}
    let z = ints2.zero
    s = ints2.succ
    p = ints2.pred
    z? = ints2.is-zero
    in letrec int to-int (x : ints2.t)
    = if (z? x)
    then 0
    else -((to-int (p x)), -1)
    in newpair((to-int (s (s z))),(s (s z)))
    '''
    assert(type_of_prog(prog) == parse('type pairof int * ints2.t'))
    assert(value_of_prog(prog) == ast.Pair(2,-6))
    
    prog_to_int_maker = '''
    module to-int-maker
        interface
            ((ints : [opaque t
            zero : t
            succ : (t -> t)
            pred : (t -> t)
            is-zero : (t -> bool)])
            => [to-int : (ints.t -> int)])
        body
            module-proc (ints : [opaque t
            zero : t
            succ : (t -> t)
            pred : (t -> t)
            is-zero : (t -> bool)])
            [to-int
            = let z? = ints.is-zero
            in let p = ints.pred
            in letrec int to-int (x : ints.t)
            = if (z? x)
            then 0
            else -((to-int (p x)), -1)
            in to-int]
    '''
    
    prog = f'''{prog_to_int_maker} {prog_ints1} {prog_ints2}
    module ints1-to-int
    interface [to-int : (ints1.t -> int)]
    body (to-int-maker ints1)
    module ints2-to-int
    interface [to-int : (ints2.t -> int)]
    body (to-int-maker ints2)
    let* 
        s1 = ints1.succ
        z1 = ints1.zero
        to-ints1 = ints1-to-int.to-int
        s2 = ints2.succ
        z2 = ints2.zero
        to-ints2 = ints2-to-int.to-int
        two1 = (s1 (s1 z1))
        two2 = (s2 (s2 z2))
    in newpair((to-ints1 two1), (to-ints2 two2))
    '''
    assert(value_of_prog(prog) == ast.Pair(2,2))
    assert(type_of_prog(prog) == parse('type pairof int * int'))
    print('end of test typed modules')
    
if __name__ == '__main__':
    test_modules()
    test_typed_modules()
    
