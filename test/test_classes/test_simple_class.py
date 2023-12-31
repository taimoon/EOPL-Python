from LET_parser import parser

import LET_ast_node as ast
List = ast.Pair.list_to_pair
parse = parser.parse

def test_simple_class(value_of_prog):
    cls_prog = '''
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
    method getstate () list(i,j)'''
    
    prog = f'''{cls_prog}
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
