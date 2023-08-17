from LET_parser import parser

import LET_ast_node as ast
List = ast.Pair.list_to_pair
parse = parser.parse

def test_class_ref(value_of_prog):
    cls_prog = '''
    class c1 extends object
    field x
    field y
    method initialize () begin
        set x = 3;
        set y = 5
    end
    class c2 extends c1
    field x
    field z
    method initialize () begin
        super initialize();
        set x = 11;
        set z = 7
    end
    method tolist () list(fieldref self x, fieldref self y, fieldref self z)
    '''
    prog = f'''{cls_prog}
    let o2 = new c2 ()
        sqr = proc (x) *(x,x)
    in begin
    fieldset o2 x = (sqr fieldref o2 x);
    fieldset o2 y = (sqr fieldref o2 y);
    fieldset o2 z = (sqr fieldref o2 z);
    list(fieldref o2 x,fieldref o2 y,fieldref o2 z)
    end
    '''
    res = value_of_prog(prog)
    ans = List(11*11,5*5,7*7)
    assert(str(res) == str(ans))
    
    prog = f'''{cls_prog}
    let o2 = new c2 ()
    in send o2 tolist()
    '''
    res = value_of_prog(prog)
    ans = List(11,5,7)
    assert(str(res)==str(ans))