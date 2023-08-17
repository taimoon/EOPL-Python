from LET_parser import parser

import LET_ast_node as ast
List = ast.Pair.list_to_pair
parse = parser.parse

def test_color_class(value_of_prog):
    cls_prog = '''
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
    '''
    
    prog = f'''{cls_prog}
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

