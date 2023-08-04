from MODULES import value_of_prog
import LET_ast_node as ast
from LET_parser import parser
parse = parser.parse

def test_transparent(type_of_prog):
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
    
def test_opaque(type_of_prog):
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
    
def test_color_example(type_of_prog):
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

def ints1_setup():
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
    return prog_ints1

def ints2_setup():
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
    return prog_ints2

def test_ints1(type_of_prog):
    prog_ints1 = ints1_setup()
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
    
def test_ints2(type_of_prog):
    prog_ints2 = ints2_setup()
    
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
    
def test_int_maker(type_of_prog):
    prog_ints1 = ints1_setup()
    prog_ints2 = ints2_setup()
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
    
def test_type_by_variant(type_of_prog):
    # test opaque modules
    test_transparent(type_of_prog)
    test_opaque(type_of_prog)
    test_color_example(type_of_prog)
    test_ints1(type_of_prog)
    test_ints2(type_of_prog)

def test_all():
    from CHECKED_OPAQUE import type_of_prog
    test_type_by_variant(type_of_prog)
    print('end of test typed modules')

    from CHECKED_PROC_MODULES import type_of_prog
    # test opaque modules
    test_type_by_variant(type_of_prog)
    # test proc modules
    test_int_maker(type_of_prog)
    print('end of test typed modules')
    