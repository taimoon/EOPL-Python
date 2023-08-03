from LET_parser import parser
from CLASSES import value_of_prog
import LET_ast_node as ast
List = ast.Pair.list_to_pair
parse = parser.parse

def test_simple_class():
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

def test_leaf_class():
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

def test_color_class():
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

def test_class_scope1():
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

def test_class_scope2():
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
    
def test_super():
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
    
def test_queue_class():
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
        setref(res_ptr,cons(instanceof q Queue,deref(res_ptr)));
        setref(res_ptr,cons(instanceof 1 Queue,deref(res_ptr)));
        deref(res_ptr)
    end
    '''
    res = value_of_prog(prog)
    expected = List(False,True,5,3,2)
    assert(str(res) == str(expected))


def test_all():
    test_simple_class()
    test_leaf_class()
    test_color_class()
    test_class_scope1()
    test_class_scope2()
    test_super()
    test_queue_class()