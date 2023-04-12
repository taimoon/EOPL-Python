from EXPLICIT_REFS import *

def test_sequence():
    prog = '''\
    let g = let counter = newref(0)
            in proc (dummy)
                begin
                setref(counter, -(deref(counter), -1));
                deref(counter)
                end
        in let a = (g 11)
            in let b = (g 11)
                in -(a,b)
    '''
    assert(value_of_prog(prog) == -1)
    
    prog = '''\
    let x = newref(0)
    in letrec even(dummy)
                = if zero?(deref(x))
                then 1
                else begin
                setref(x, -(deref(x),1));
                (odd 888)
                end
            odd(dummy)
                = if zero?(deref(x))
                then 0
                else begin
                setref(x, -(deref(x),1));
                (even 888)
                end
    in begin setref(x,13); (odd 888) end
    '''
    assert(value_of_prog(prog) == 1)
    
if __name__ == '__main__':
    test_sequence()
    print("pass all test for EXPLICIT_REFS lang")