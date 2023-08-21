from LET_parser import parser

import LET_ast_node as ast
List = ast.Pair.list_to_pair
parse = parser.parse


def test_class_scope1(value_of_prog):
    cls_prog = '''
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
    '''
    prog = f'''{cls_prog}
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

def test_class_scope2(value_of_prog):
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
    
def test_super(value_of_prog):
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
