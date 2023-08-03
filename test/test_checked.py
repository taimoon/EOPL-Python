from CHECKED import type_of_prog
from LET import value_of_prog
from LET_parser import type_parse as parse
from LET_ast_node import (Pair,NULL,No_Type,Int_Type)
    
def test_simple_type():
    prog = '-123'
    res = type_of_prog(prog)
    ans = 'int'
    assert(str(res) == ans)
    assert(res == parse(ans))
    
    prog = '-(10,8)'
    res = type_of_prog(prog)
    ans = 'int'
    assert(str(res) == ans)
    assert(res == parse(ans))
    

def test_proc_type():
    prog = 'proc () 1'
    res = type_of_prog(prog)
    ans = '(void -> int)'
    assert(str(res) == ans)
    assert(res == parse(ans))
    
    prog = 'proc (x : int) -(x,11)'
    res = type_of_prog(prog)
    ans = '(int -> int)'
    assert(str(res) == ans)
    assert(res == parse(ans))
    
    prog = '''\
    letrec
        int double (x : int) = if zero?(x)
            then 0
            else -((double -(x,1)), -2)
    in double
    '''
    res = type_of_prog(prog)
    ans = '(int -> int)'
    assert(str(res) == ans)
    assert(res == parse(ans))
    
    prog = 'proc (f : (bool -> int)) proc (n : int) (f zero?(n))'
    res = type_of_prog(prog)
    ans = '((bool -> int) -> (int -> int))'
    assert(str(res) == ans)
    assert(res == parse(ans))


def test_multiple_arg_type():
    prog = '''\
    letrec int accumulator 
            (op:(int * int -> int),stepper:(int -> int),f:(int -> int),a:int,b:int,acm:int) 
            =
            if less?(a,b)
            then (accumulator op stepper f (stepper a) b (op acm (f a)))
            else acm
    in accumulator
    '''
    res = type_of_prog(prog)
    ans = '((int * int -> int) * (int -> int) * (int -> int) * int * int * int -> int)' 
    assert(str(res) == ans)
    assert(res == parse(ans))


def test_and_eval():
    prog = '''\
    letrec int accumulator
            (op:(int * int -> int),stepper:(int -> int),f:(int -> int),a:int,b:int,acm:int) 
            =
            if less?(a,b)
            then (accumulator op stepper f (stepper a) b (op acm (f a)))
            else acm
    in let*
        op = proc(x:int,y:int) +(x,y)
        stepper = proc(x:int) +(x,2)
        f = proc(x:int) *(x,x)
        sum = proc(a:int,b:int) (accumulator op stepper f a b 0)
    in (sum 0 10)
    '''
    ans = sum(x*x for x in range(0,10,2))
    assert(value_of_prog(prog) == ans)
    

def test_pairof():
    prog = '''
    let* z = newpair(3,emptylist)
        y = newpair(1,zero?(0))
        xs = newpair(y,z)
    in newpair(car(xs),cdr(cdr(xs)))
    '''
    res = type_of_prog(prog)
    ans = 'pairof pairof int * bool * ?'
    assert(str(res) == ans)
    assert(res == parse(ans))
    assert(value_of_prog(prog) == Pair(Pair(1,True),NULL()))
    
    prog = '''\
    let neg = proc (x:bool) if x then zero?(1) else zero?(0)
    in letrec pairof int * bool f (xs:pairof int * bool) =
        unpair x y = xs
        in if zero?(x) then newpair(x,y) else (f newpair(-(x,1),(neg y)))
    in (f newpair(3,zero?(0)))
    '''
    res = type_of_prog(prog)
    ans = 'pairof int * bool'
    assert(str(res) == ans)
    assert(res == parse(ans))
    assert(value_of_prog(prog) == Pair(0,False))
    assert(str(value_of_prog(prog)) == '(0 . False)')
    

def test_error():
    def f():
        try:
            prog = '''\
            let f = proc(xs:pairof int * int) xs
            in (f newpair(zero?(3),2))
            '''
            res = type_of_prog(prog)
            assert(False)
        except AssertionError:
            raise Exception("Unhandled Exception for unmatch argument type")
        except Exception:
            assert(True)
    f()


def test_list():
    prog = 'list(1,2,3)'
    res = type_of_prog(prog)
    ans = 'listof int'
    assert(str(res) == ans)
    assert(res == parse(ans))
    assert(value_of_prog(prog) == Pair(1,Pair(2,Pair(3,NULL(No_Type())))))
    
    prog = '''
    letrec listof int enumerate (x:int)
        = if zero?(x) then emptylist(int) else cons(x,(enumerate -(x,1)))
        listof int map (xs: listof int, f : (int -> int))
        = if null?(xs) then emptylist(int) else cons((f car(xs)), (map cdr(xs) f))
        int sqr (x:int) = *(x,x)
    in newpair(enumerate,newpair((enumerate 3),(map (enumerate 3) sqr)))
    '''
    ans = 'pairof (int -> listof int) * pairof listof int * listof int'
    res = type_of_prog(prog)
    assert(str(res) == ans)
    assert(res == parse(ans))
    val = Pair(3,Pair(2,Pair(1,NULL(t=Int_Type()))))
    assert(value_of_prog(prog).cdr.car == val)
    val = Pair(9,Pair(4,Pair(1,NULL(t=Int_Type()))))
    assert(value_of_prog(prog).cdr.cdr == val)
    

def test_checked():
    test_simple_type()
    test_proc_type()
    test_multiple_arg_type()
    test_and_eval()
    test_pairof()
    test_error()
    test_list()
    

def test_inference():
    from INFERRED import type_of_prog,lambda_alpha_subst,Var_Type
    from LET_ast_node import Int_Type,Proc_Type,Bool_Type
    
    get_answer = lambda prog: type_of_prog(type_of_prog(prog))
    
    prog = 'proc (f:?) (f 11)'
    prog = get_answer(prog)
    v1 = Var_Type()
    ans = Proc_Type([Proc_Type([Int_Type()],v1)],v1)
    res = lambda_alpha_subst(prog,ans).type == prog
    assert(res is True)
    ans = Proc_Type([Proc_Type([Int_Type()],v1)],Var_Type())
    res = lambda_alpha_subst(prog,ans).type == prog
    assert(res is False)
    
    
    prog = 'proc (x:?) zero?(x)'
    ans = Proc_Type((Int_Type(),),Bool_Type())
    prog = get_answer(prog)
    assert(lambda_alpha_subst(prog,ans).type == prog)
    
    prog = 'proc (f:?) proc (x:?) -((f 3),(f x))'
    proc_t = Proc_Type((Int_Type(),),Int_Type())
    ans = Proc_Type((proc_t,),proc_t)
    prog = get_answer(prog)
    assert(lambda_alpha_subst(prog,ans).type == prog)


def test_all():
    print('test CHECKED.py')
    test_checked()
    print('end of test')
    print('test INFERENCE.py')
    test_inference()
    print('end of test')
