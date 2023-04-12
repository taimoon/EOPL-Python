# from LET import *
from LET_cc import *
# from NAMELESS_LET import *
# from EXPLICIT_REFS import *
import sys
sys.setrecursionlimit(2000) # this is necessary for LET_cc testing
IS_DYNAMIC = False

def test_env():
    env = init_env()
    env = extend_env('i', 1, env)
    env = extend_env('v', 5, env)
    env = extend_env('x', 10, env)
    assert(apply_env(env,'i') == 1)
    assert(apply_env(env,'v') == 5)
    assert(apply_env(env,'x') == 10)

def test_diff_exp():
    env = init_env()
    env = extend_env('i', 1, env)
    env = extend_env('v', 5, env)
    env = extend_env('x', 10, env)
    prog = '-(-(x,3),-(v,i))'
    assert(value_of_prog(prog,env) == 3.0)

def test_bi_exp():
    prog = '''--(-5,9)'''
    assert(value_of_prog(prog) == 14)
    
    prog = '''minus(-(minus(5),9))'''
    assert(value_of_prog(prog) == 14)
    
    prog = '+(-2,10)'
    assert(value_of_prog(prog) == 8)
    prog = '*(-7,13)'
    assert(value_of_prog(prog) == -7*13)
    prog = '/(15,3)'
    assert(value_of_prog(prog) == 15/3)
    prog = '''let  celsius_to_fahr = proc (c) +(*(/(9,5),c),32)
    in (celsius_to_fahr 32)
    '''
    assert(value_of_prog(prog) == 9/5*32+32)
    prog = 'less?(1,2)'
    assert(value_of_prog(prog) == True)
    prog = 'less?(0,-2)'
    assert(value_of_prog(prog) == False)
    prog = 'equal?(2,2)'
    assert(value_of_prog(prog) == True)
    prog = 'greater?(1,2)'
    assert(value_of_prog(prog) == False)
    prog = 'greater?(0,-2)'
    assert(value_of_prog(prog) == True)

def test_other_repr():
    prog = '(let (z 5) (let (x 3) (let (y (- x 1)) (let (x 4) (- z (- x y)))))))'
    assert(value_of_prog(prog,parse=parse_LET_lang) == 3)
    prog = '''
    (let (x 7)
    (let (y 2)
    (let (y 
            (let (x (- x 1)) (- x y)))
    (- (- x 8) y)
    )))
    '''
    assert(value_of_prog(prog,parse=parse_LET_lang) == -5)

def test_if():
    env = init_env()
    env = extend_env('x',33, 
                    extend_env('y',22, env))
    prog = 'if zero?(-(x,11)) then -(y,2)  else -(y,4)'
    assert(value_of_prog(prog,env) == 18)

def test_cond():
    prog = lambda x :f'''\
        let abs = proc(x) 
            cond zero?(x) => 0
            less?(x,0) => -(0,x)
            else x
            end
        in (abs {x})
        '''
    assert(value_of_prog(prog(-10)) == 10)
    assert(value_of_prog(prog(0)) == 0)
    assert(value_of_prog(prog(10)) == 10)

def test_let():
    prog = 'let x=5 in -(x,3)'
    assert(value_of_prog(prog) == 2)

    prog = '''\
        let z = 5
          in let x = 3
            in let y = -(x,1)
              in let x = 4
                in -(z,-(x,y))'''
    assert(value_of_prog(prog) == 3)  

def test_proc_1():
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
    
def test_proc_multi():
    print('test_proc_multi')

    prog = '''\
    let add = proc(x) proc(y) -(x,-(0,y))
    in ((add 3) 7)
    '''
    assert(value_of_prog(prog) == 10)
    
    prog = '''\
        let add = proc(x,y) -(x,-y)
        in (add 3 7)
        '''
    assert(value_of_prog(prog) == 10)
    
    prog = '''\
        let add = proc(x,y) -(x,-y)
        in let add_3 = proc(x,y,z) (add x (add y z))
        in (add_3 3 7 11)
        '''
    assert(value_of_prog(prog) == 21)
    print('end_of_testing_proc_multi')

def test_let_multi():
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

def test_proc_dynamic():
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
    
def test_let_star():
    prog = '''\
        let x = 30
            in let* x = -(x,1) y = -(x,2)
            in -(x,y)'''
    assert(value_of_prog(prog) == 2)

def test_dat_struct():
    prog = 'cons(1,cons(2,3))'
    # print(value_of_prog(prog))
    assert(str(value_of_prog(prog)) == '(1 (2 . 3))')
    
    prog = 'cons(1,cons(2,cons(3,emptylist)))'
    assert(str(value_of_prog(prog)) == '(1 2 3)')
    
    prog ='''\
    car(cons(1,2))'''
    assert(value_of_prog(prog) == 1)
    prog ='''\
    cdr(cons(1,2))'''
    assert(value_of_prog(prog) == 2)
    prog = '''\
    let x = 4
    in cons(x,
            cons(cons(-(x,1),
            emptylist),
            emptylist))'''
    assert(str(value_of_prog(prog)) == '(4 (3))')
    
    prog = '''\
        list(1,2,3,4)'''
    assert(str(value_of_prog(prog)) == '(1 2 3 4)')
    
    prog = '''\
        let x = 4
        in list(x,-(x,1), -(x,3))'''
    assert(str(value_of_prog(prog)) == '(4 3 1)')
    
    prog = '''list()'''
    assert(str(value_of_prog(prog)) == '()')

def test_unpack_op():
    prog = '''\
        let u = 7
        in unpack x y = cons(u,cons(3,emptylist))
            in -(x,y)'''
    assert(value_of_prog(prog) == 4)

def test_y_combinator():
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

def test_letrec():
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

def test_letrec_multi():
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
                        (odd x) => (sum_odd (dec x) (add x acm))
                        else (sum_odd (dec x) acm)
                        end
                    in (sum_odd 7 0)'''
    ans = sum([i for i in range(7+1) if i % 2 != 0])
    assert(value_of_prog(prog) == ans)
    

if __name__ == '__main__':
    test_env()
    test_diff_exp()
    test_if()
    test_cond()
    test_let()
    test_let_multi()
    test_let_star()
    test_dat_struct()
    # test_unpack_op()
    test_bi_exp()
    
    test_proc_1()
    test_proc_dynamic()
    test_proc_multi()
    test_y_combinator()
    test_letrec()
    test_letrec_multi()
    
    # test_other_repr()
    print('pass all test')

