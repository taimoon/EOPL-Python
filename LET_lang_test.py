import sys
sys.setrecursionlimit(2000) # this is necessary for LET_cc testing
IS_DYNAMIC = False
from LET_environment import *
def test_env():
    env = extend_env_from_pairs(('x','v','i','x'),
                                (10,5,1,7),
                                init_env())
    assert(apply_env(env,'i') == 1)
    assert(apply_env(env,'v') == 5)
    assert(apply_env(env,'x') == 10)

def test_diff_exp(value_of_prog):
    env = extend_env_from_pairs(('i','v','x'),
                                (1,5,10),
                                init_env())
    prog = '-(x,3)'
    assert(value_of_prog(prog,env) == 7)
    prog = '-(-(x,3),-(v,i))'
    assert(value_of_prog(prog,env) == 3.0)

def test_bi_exp(value_of_prog):
    prog = "-(7,2)"
    assert(value_of_prog(prog) == 5)
    prog = '''--(-5,9)'''
    assert(value_of_prog(prog) == 14)
    prog = '''minus(-(minus(5),9))'''
    assert(value_of_prog(prog) == 14)
    prog = '+(*(/(9,5),32),32)'
    assert(value_of_prog(prog) == 9/5*32+32)
    prog = 'less?(1,2)'
    assert(value_of_prog(prog) is True)
    prog = 'less?(0,-2)'
    assert(value_of_prog(prog) is False)
    prog = 'equal?(2,2)'
    assert(value_of_prog(prog) is True)
    prog = 'equal?(1,2)'
    assert(value_of_prog(prog) is False)
    prog = 'greater?(1,2)'
    assert(value_of_prog(prog) is False)
    prog = 'greater?(0,-2)'
    assert(value_of_prog(prog) is True)

def test_if(value_of_prog):
    env = extend_env_from_pairs(('x','y'),(33,22),init_env())
    prog = 'if zero?(-(x,11)) then -(y,2)  else -(y,4)'
    assert(value_of_prog(prog,env) == 18)

def test_cond(value_of_prog):
    prog = lambda x :f'''\
        let abs = proc(x) 
            cond 
                zero?(x) => 0
                less?(x,0) => -(0,x)
                else x
            end
        in (abs {x})
    '''
    assert(value_of_prog(prog(-10)) == 10)
    assert(value_of_prog(prog(0)) == 0)
    assert(value_of_prog(prog(10)) == 10)
    
    prog = lambda x : f'''\
        let le = proc(x)
            cond 
                zero?(x) => zero?(0)
                less?(x,0) => zero?(0)
            end
        in (le {x})
    '''
    assert(value_of_prog(prog(-10)) is True)
    assert(value_of_prog(prog(0)) is True)
    assert(value_of_prog(prog(10)) is False)

def test_let(value_of_prog):
    prog = 'let x=5 in -(x,3)'
    assert(value_of_prog(prog) == 2)

    prog = '''\
        let z = 5
          in let x = 3
            in let y = -(x,1)
              in let x = 4
                in -(z,-(x,y))
    '''
    assert(value_of_prog(prog) == 3)  

def test_proc_1(value_of_prog):
    prog = 'let f = proc () 13 in (f)'
    assert(value_of_prog(prog) == 13)
    prog = '''\
        let f = proc (x) -(x,11)
        in (f (f 77))'''
    assert(value_of_prog(prog) == 55)
    
    prog = '''\
        (proc (f) (f (f 77))
         proc (x) -(x,11))'''
    assert(value_of_prog(prog) == 55)
    
    prog = '''\
        let x = 200
        in let f = proc (z) -(z,x)
            in let x = 100
                in let g = proc (z) -(z,x)
                    in -((f 1),(g 1))'''
    # dynamic scope
    # -((f 1),(g 1))
    # (f 1) -> -(1,x) -> -(1,100)
    # (g 1) -> -(1,x) -> -(1,100)
    if IS_DYNAMIC:
        assert(value_of_prog(prog) == 0) 
    else:
        assert(value_of_prog(prog) == -100) # lexical scope
    
def test_proc_multi(value_of_prog):
    prog = '''
        let add = proc(x) proc(y) -(x,-(0,y))
        in ((add 3) 7)
    '''
    assert(value_of_prog(prog) == 10)
    
    prog = '''
        let add = proc(x,y) -(x,-y)
        in (add 3 7)
    '''
    assert(value_of_prog(prog) == 10)
    
    prog = '''
        let add = proc(x,y) -(x,-y)
        in let add_3 = proc(x,y,z) (add x (add y z))
            in (add_3 3 7 11)
    '''
    assert(value_of_prog(prog) == 21)

def test_let_multi(value_of_prog):
    prog = '''\
        let x = 30
        in let x = -(x,1)
                y = -(x,2)
            in -(x,y)'''
    assert(value_of_prog(prog) == 1)
    
    prog = '''\
        let x = 30
        in let x = -(x,1)
                y = -(x,2)
                z = -(x,3)
        in -(-(x,y),z)'''
    assert(value_of_prog(prog) == -26)

def test_proc_dynamic(value_of_prog):
    # TODO : Implement dynamic
    prog = '''\
        let a = 3
        in let 
            p = proc (x) -(x,a)
            a = 5
        in -(a,(p 2))'''
    if IS_DYNAMIC:
        assert(value_of_prog(prog) == 8) # for dynamic binding
    else:
        assert(value_of_prog(prog) == 6) # for lexical binding
    prog = '''\
    let a = 3
    in let p = proc (z) a
        in let f = proc (a) (p 0)
            in let a = 5
            in (f 2)
    '''
    if IS_DYNAMIC:
        assert(value_of_prog(prog) == 2) # for dynamic binding
    else:
        assert(value_of_prog(prog) == 3) # for lexical binding
    
def test_let_star(value_of_prog):
    prog = '''\
        let x = 30
        in let* x = -(x,1) y = -(x,2)
            in -(x,y)'''
    assert(value_of_prog(prog) == 2)

def test_dat_struct(value_of_prog):
    prog = 'cons(1,cons(2,3))'

    assert(str(value_of_prog(prog)) == '(1 (2 . 3))')
    
    prog = 'cons(1,cons(2,cons(3,emptylist)))'
    assert(str(value_of_prog(prog)) == '(1 2 3)')
    
    prog ='car(cons(1,2))'
    assert(value_of_prog(prog) == 1)
    prog ='cdr(cons(1,2))'
    assert(value_of_prog(prog) == 2)
    prog = '''\
        let x = 4 
        in cons(x,cons(cons(-(x,1),emptylist),emptylist))'''
    assert(str(value_of_prog(prog)) == '(4 (3))')
    
    prog = 'list(1,2,3,4)'
    assert(str(value_of_prog(prog)) == '(1 2 3 4)')
    
    prog = 'list(list(1,2),list(3,4))'
    assert(str(value_of_prog(prog)) == '((1 2) (3 4))')
    prog = 'list(cons(1,2),cons(3,4))'
    assert(str(value_of_prog(prog)) == '((1 . 2) (3 . 4))')
    prog = '''\
        let x = 4
        in list(x,-(x,1), -(x,3))'''
    assert(str(value_of_prog(prog)) == '(4 3 1)')
    
    prog = 'list()'
    assert(str(value_of_prog(prog)) == '()')

def test_unpack_op(value_of_prog):
    prog = '''\
        let u = 7
        in unpack x y = cons(u,cons(3,emptylist))
            in -(x,y)'''
    assert(value_of_prog(prog) == 4)
    prog = '''\
        let add = proc(x,y) -(x,-y)
        in (add unpack(list(3,4)))
        '''
    assert(value_of_prog(prog) == 7)

def test_y_combinator(value_of_prog):
    # y combinator might be too deep for python
    # don't use values that's too big
    prog = '''\
    let add = proc (x) proc (y) -(x,-y)
    in let makemult = proc (f)
                    proc (x)
                    if zero?(x)
                    then 0
                    else let add4 = (add 4) in (add4 ((f f) -(x,1)))
        in let times4 = proc (x) ((makemult makemult) x)
            in (times4 7)
        '''
    assert(value_of_prog(prog) == 28)
    
    prog = '''\
    let add = proc (x) proc (y) -(x,-y)
    in let makemult = proc (f) proc (x) proc (y)
                    if zero?(x)
                    then 0
                    else let addy = (add y) in (addy (((f f) -(x,1)) y))
        in let mult = proc (x) proc (y) (((makemult makemult) x) y)
            in ((mult 5) 5)
    '''
    assert(value_of_prog(prog) == 5*5) # cannot to big for CPS
    
    x = 3
    prog = f'''\
    let add = proc (x) proc (y) -(x,-y)
    in let makemult = proc (f) proc (x) proc (y)
                    if zero?(x)
                    then 0
                    else let addy = (add y) in (addy (((f f) -(x,1)) y))
    in let mult = proc (x) proc (y) (((makemult makemult) x) y)
    in let makefact = proc (f) proc(n)
                    if zero?(n)
                    then 1
                    else let multn = (mult n) in (multn ((f f) -(n,1)))
    in let fact = proc (n) ((makefact makefact) n)
        in (fact {x})
    '''
    fact = lambda n : 1 if n <= 1 else n*fact(n-1)
    assert(value_of_prog(prog) == fact(x)) 

def test_letrec(value_of_prog):
    prog = '''\
    letrec double (x)
        = if zero? (x) then 0 else -((double -(x,1)), -2)
    in (double 6)'''
    assert(value_of_prog(prog) == 12)
    
    prog = '''\
    letrec mult (x,y)
        = if zero? (x) then 0 else -((mult -(x,1) y), -(0,y))
    in (mult 11 11)'''
    assert(value_of_prog(prog) == 11*11)
    
    prog = '''\
    letrec mult (x,y)
        = if zero? (x) then 0 else -((mult -(x,1) y), -(0,y))
    in (mult 7 23)'''
    assert(value_of_prog(prog) == 7*23)
    
    prog = '''\
        letrec fact (n) = if zero?(n) then 1 else *(n,(fact -(n,1)))
        in (fact 4)
    '''
    from math import factorial
    assert(value_of_prog(prog) == factorial(4))
    
    prog = '''\
        letrec fact_iter (n,acm) = if zero?(n) then acm else (fact_iter -(n,1) *(n,acm))
        in let fact = proc (x) (fact_iter x 1) in
            (fact 4)
    '''
    assert(value_of_prog(prog) == factorial(4))

def test_letrec_multi(value_of_prog):
    prog = '''\
        letrec
            even(x) = if zero?(x) then 1 else (odd -(x,1))
            odd(x) = if zero?(x) then 0 else (even -(x,1))
            in (odd 5)'''
    assert(value_of_prog(prog) == True)
    
    prog = '''\
        letrec
            even(x) = if zero?(x) then 1 else (odd -(x,1))
            odd(x) = if zero?(x) then 0 else (even -(x,1))
            in (even 5)'''
    assert(value_of_prog(prog) == False)
    
    prog = '''\
    letrec
        mod(x,d) = if less?(x,d) then x else (mod -(x,d) d)
        divide(d,x) = zero?((mod x d))
        smallest_divisor(x,d) = if (divide d x) then d else (smallest_divisor x +(d,1))
        is_prime(x) = equal?((smallest_divisor x 2),x)
        dec(x) = -(x,1)
        sum_prime(p,acm) = 
            cond
                less?(p,2) => acm
                (is_prime p) => (sum_prime (dec p) +(p,acm))
                else (sum_prime (dec p) acm)
            end
        in (sum_prime 5 0)'''
    smallest_div = lambda x : min([d for d in range(2,x+1) if x%d == 0])
    is_prime = lambda p: p == smallest_div(p)
    assert(value_of_prog(prog) == sum([i for i in range(2,5+1) if is_prime(i)]))
    
    prog = '''\
        letrec
            add(x,y) = -(x,-(0,y))
            dec(x) = -(x,1)
            even(x) = if zero?(x) then 1 else (odd (dec x))
            odd(x) = if zero?(x) then 0 else (even (dec x))
                in letrec 
                    sum_odd(x,acm) =
                        cond 
                        zero?(x) => acm
                        equal?((odd x),1) => (sum_odd (dec x) (add x acm))
                        else (sum_odd (dec x) acm)
                        end
                    in (sum_odd 6 0)'''
    # value cannot be too big
    ans = sum([i for i in range(6+1) if i % 2 != 0])
    assert(value_of_prog(prog) == ans)
    
def test_sequence(value_of_prog):
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
    in letrec 
        even() = if zero?(deref(x))
                then 1
                else begin
                    setref(x, -(deref(x),1));
                    (odd)
                    end
        odd() = if zero?(deref(x))
                then 0
                else begin
                    setref(x, -(deref(x),1));
                    (even)
                    end
    in begin setref(x,13); (odd) end
    '''
    assert(value_of_prog(prog) == 1)

def test_swap(value_of_prog):
    'test call-by-reference'
    prog = '''\
    letmutable f = proc (x) set x = 44
    in letmutable g = proc (y) (f y)
        in letmutable z = 55
            in begin (g z); z end
    '''
    assert(value_of_prog(prog) == 44)
    prog = '''\
    let swap = proc (x,y)
        let temp = x
        in begin
            set x = y;
            set y = temp
            end
    in letmutable a = 33
           b = 44
        in begin
            (swap a b);
            -(a,b)
            end
    '''
    assert(value_of_prog(prog) == 11)

def test_ref(value_of_prog):
    prog = '''\
    let swap = proc (x,y)
        let temp = deref(x)
        in begin
            setref(x,deref(y));
            setref(y,temp)
            end
    in letmutable a = 33
           b = 44
        in begin
            (swap ref(a) ref(b));
            -(a,b)
            end
    '''
    assert(value_of_prog(prog) == 11)

def test_laziness(value_of_prog):
    prog ='''\
    letrec infinite_loop (x) = (infinite_loop -(x,-1))
    in let f = proc (z) 11
        in (f (infinite_loop 0))
    '''
    assert(value_of_prog(prog) == 11)
    prog = '''\
    letrec infinite_loop () = (infinite_loop) in
    let
        my_if = proc (pred,conseq,alter) if pred then conseq else alter
        d = 0
    in (my_if zero?(0) 1 (infinite_loop))
    '''
    assert(value_of_prog(prog) == 1)

def test_checked():
    from CHECKED import type_of_prog
    from LET import value_of_prog
    from LET_parser import type_parse as parse
    prog = 'proc (x : int) -(x,1)'
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
    
    prog = '''\
    letrec int accumulator 
            (op:(int * int -> int),stepper:(int -> int),f:(int->int),a:int,b:int,acm:int) =
        if less?(a,b)
        then (accumulator op stepper f (stepper a) b (op acm (f a)))
        else acm
    in accumulator
    '''
    res = type_of_prog(prog)
    ans = '((int * int -> int) * (int -> int) * (int -> int) * int * int * int -> int)' 
    assert(str(res) == ans)
    assert(res == parse(ans))
    
    prog = '''\
    letrec int accumulator 
            (op:(int * int -> int),stepper:(int -> int),f:(int->int),a:int,b:int,acm:int) =
        if less?(a,b)
        then (accumulator op stepper f (stepper a) b (op acm (f a)))
        else acm
    in let*
        op = proc(x:int,y:int) +(x,y)
        stepper = proc(x:int) +(x,2)
        f = proc(x:int) *(x,x)
        sum = proc (a:int,b:int) (accumulator op stepper f a b 0)
    in (sum 0 10)
    '''
    ans = sum(x*x for x in range(0,10,2))
    assert(value_of_prog(prog) == ans)
    
    prog = 'proc () 1'
    res = type_of_prog(prog)
    ans = '(void -> int)'
    assert(str(res) == ans)
    assert(res == parse(ans))
    
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
    in newpair(enumerate,(enumerate 3))
    '''
    ans = 'pairof (int -> listof int) * listof int'
    res = type_of_prog(prog)
    assert(str(res) == ans)
    assert(res == parse(ans))
    val = Pair(3,Pair(2,Pair(1,NULL(t=Int_Type()))))
    assert(value_of_prog(prog).cdr == val)
    
def test_inference():
    from INFERRED import type_of_prog,lambda_alpha_subst,Var_Type
    
    get_answer = lambda prog: type_of_prog(type_of_prog(prog))
    
    prog = '''\
    proc (f:?) (f 11)
    '''
    prog = get_answer(prog)
    v1 = Var_Type()
    ans = Proc_Type([Proc_Type([Int_Type()],v1)],v1)
    res = lambda_alpha_subst(prog,ans).type == prog
    assert(res is True)
    ans = Proc_Type([Proc_Type([Int_Type()],v1)],Var_Type())
    res = lambda_alpha_subst(prog,ans).type == prog
    assert(res is False)
    
    
    prog = '''\
    proc (x:?) zero?(x)
    '''
    ans = Proc_Type((Int_Type(),),Bool_Type())
    prog = get_answer(prog)
    assert(lambda_alpha_subst(prog,ans).type == prog)
    
    prog = '''\
    proc (f:?) proc (x:?) -((f 3),(f x))
    '''
    proc_t = Proc_Type((Int_Type(),),Int_Type())
    ans = Proc_Type((proc_t,),proc_t)
    prog = get_answer(prog)
    assert(lambda_alpha_subst(prog,ans).type == prog)

def test_all(value_of_prog):
    test_env()
    test_diff_exp(value_of_prog)
    test_if(value_of_prog)
    test_cond(value_of_prog)
    test_let(value_of_prog)
    test_let_multi(value_of_prog)
    test_let_star(value_of_prog)
    test_dat_struct(value_of_prog)
    test_unpack_op(value_of_prog)
    test_bi_exp(value_of_prog)
    
    test_proc_1(value_of_prog)
    test_proc_multi(value_of_prog)
    test_y_combinator(value_of_prog)
    
    test_letrec(value_of_prog)
    test_letrec_multi(value_of_prog)
    
    print('pass all test')

if __name__ == '__main__':
    from LET import value_of_prog
    print('LET')
    test_all(value_of_prog)
    from NAMELESS_LET import value_of_prog
    print('NAMELESS_LET')
    test_all(value_of_prog)
    from EXPLICIT_REFS import value_of_prog
    print('EXPLICIT_REFS')
    test_all(value_of_prog)
    test_sequence(value_of_prog)
    print('Store_Passing_Refs')
    from STORE_PASSING_LET import value_of_prog
    test_all(value_of_prog)
    test_sequence(value_of_prog)
    from IMPLICIT_REFS import value_of_prog
    print('IMPLICIT_REFS')
    test_all(value_of_prog)
    test_sequence(value_of_prog)
    test_ref(value_of_prog)
    from LAZY_LET import value_of_prog
    print('LAZY_LET')
    test_all(value_of_prog)
    test_sequence(value_of_prog)
    test_ref(value_of_prog)
    test_swap(value_of_prog)
    test_laziness(value_of_prog)
    from LET_cc import value_of_prog 
    print('LET_cc')
    test_all(value_of_prog)
    from LET_cc_imperative import value_of_prog 
    print('LET_cc_imperative')
    test_all(value_of_prog)
    print('test CHECKED.py')
    test_checked()
    print('end of test')
    print('test INFERENCE.py')
    test_inference()
    print('end of test')
