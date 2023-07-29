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
    

def test_class_1():
    from LET_parser import parser
    from CLASSES import value_of_prog
    import LET_ast_node as ast
    
    List = ast.Pair.list_to_pair
    parse = parser.parse
    prog = '''
    class c1 extends object
    field i
    field j
    method initialize (x)
    begin
    set i = x;
    set j = -(0,x)
    end
    method countup (d)
    begin
    set i = +(i,d);
    set j = -(j,d)
    end
    method getstate () list(i,j)
    letmutable 
        t1 = 0
        t2 = 0
        o1 = new c1(3)
    in begin
        set t1 = send o1 getstate();
        send o1 countup(2);
        set t2 = send o1 getstate();
        list(t1,t2)
    end
    '''
    res = value_of_prog(prog)
    expected = List(List(3,-3),List(5,-5))
    assert(str(res) == str(expected))
    prog = '''
    class interior-node extends object
    field left
    field right
    method initialize (l, r)
    begin
    set left = l;
    set right = r
    end
    method sum () +(send left sum(),send right sum())
    class leaf-node extends object
    field value
    method initialize (v) set value = v
    method sum () value
    let o1 = new interior-node(
    new interior-node(
    new leaf-node(3),
    new leaf-node(4)),
    new leaf-node(5))
    in send o1 sum()
    '''
    assert(value_of_prog(prog) == 12)
    prog = '''
    class point extends object
    field x 
    field y
    method initialize (initx, inity)
    begin
    set x = initx;
    set y = inity
    end
    method move (dx, dy)
    begin
    set x = +(x,dx);
    set y = +(y,dy)
    end
    method get-location () list(x,y)
    class colorpoint extends point
    field color
    method set-color (c) set color = c
    method get-color () color
    let p = new point(3,4)
    cp = new colorpoint(10,20)
    in begin
    send p move(3,4);
    send cp set-color(87);
    send cp move(10,20);
    list(send p get-location(), % returns (6 8)
    send cp get-location(), % returns (20 40)
    send cp get-color()) % returns 87
    end
    '''
    res = value_of_prog(prog)
    expected = List(List(6,8),List(20,40),87)
    assert(str(res) == str(expected))
    prog = '''
    class c1 extends object
    field x
    field y
    method initialize () 1
    method setx1 (v) set x = v
    method sety1 (v) set y = v
    method getx1 () x
    method gety1 () y
    class c2 extends c1
    field y
    method sety2 (v) set y = v
    method getx2 () x
    method gety2 () y
    let o2 = new c2()
    in begin
    send o2 setx1(101);
    send o2 sety1(102);
    send o2 sety2(999);
    list(send o2 getx1(), % returns 101
    send o2 gety1(), % returns 102
    send o2 getx2(), % returns 101
    send o2 gety2()) % returns 999
    end
    '''
    res = value_of_prog(prog)
    expected =  List(101,102,101,999)
    assert(str(res) == str(expected))
    
    prog = '''
    class c1 extends object
    method initialize () 1
    method m1 () 11
    method m2 () send self m1()
    class c2 extends c1
    method m1 () 22
    let o1 = new c1() o2 = new c2()
    in list(send o1 m1(), send o2 m1(), send o2 m2())
    '''
    res = value_of_prog(prog)
    expected =  List(11,22,22)
    assert(str(res) == str(expected))
    
    cls = '''
    class c1 extends object
    method initialize () 1
    method m1 () send self m2() % dynamic dispatch
    method m2 () 13 
    class c2 extends c1
    method m1 () 22
    method m2 () 23
    method m3 () super m1() % static dispatch
    method m4 () super m2()
    class c3 extends c2
    method m1 () 32
    method m2 () 33
    method m5 () list(send self m1(), send self m2(), super m1(),super m2())
    '''
    prog = f'{cls} let o3 = new c3() in send o3 m3()'
    assert(value_of_prog(prog) == 33)
    prog = f'{cls} let o3 = new c3() in send o3 m4()'
    assert(value_of_prog(prog) == 13)
    prog = f'{cls} let o3 = new c3() in send o3 m5()'
    res = value_of_prog(prog)
    ans = List(32,33,22,23)
    assert(str(res) == str(ans))
    
def test_class_2():
    from LET_parser import parser
    from CLASSES import value_of_prog
    import LET_ast_node as ast
    
    List = ast.Pair.list_to_pair
    parse = parser.parse
    queue_prog = '''
    class Queue extends object
    field tail
    field xs
    method initialize () begin
        set xs = emptylist;
        set tail = xs
    end
    method enqueue (x)
        if null?(xs)
        then begin
            set xs = cons(x,xs);
            set tail = xs
            end
        else begin
            setcdr(tail,list(x));
            set tail = cdr(tail)
            end
    method dequeue ()
        let res = car(xs)
        in begin
            set xs = cdr(xs);
            res
        end
    '''
    prog = f'''{queue_prog}
    let q = new Queue()
    res_ptr = newref(emptylist)
    in begin
        send q enqueue(2);
        send q enqueue(3);
        send q enqueue(5);
        setref(res_ptr,cons(send q dequeue(),deref(res_ptr)));
        setref(res_ptr,cons(send q dequeue(),deref(res_ptr)));
        setref(res_ptr,cons(send q dequeue(),deref(res_ptr)));
        deref(res_ptr)
    end
    '''
    res = value_of_prog(prog)
    expected = List(5,3,2)
    assert(str(res) == str(expected))

if __name__ == '__main__':
    test_modules()
    test_typed_modules()
    test_class_1()
    test_class_2()
    
