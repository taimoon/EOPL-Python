from LET_parser import parser

import LET_ast_node as ast
List = ast.Pair.list_to_pair
parse = parser.parse

def test_queue_class(value_of_prog):
    List = ast.Pair.list_to_pair
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
