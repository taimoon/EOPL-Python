def test_exception(value_of_prog):
    prog = '"reimu"'
    assert(value_of_prog(prog) == "reimu")
    
    prog = '''
    let index
        = proc (n)
        letrec inner (lst)
        = if null?(lst)
        then raise 99
        else if zero?(-(car(lst),n))
        then 0
        else -((inner cdr(lst)), -1)
        in proc (lst)
            try (inner lst)
            catch (x) -1
        in ((index 5) list(2, 3))
    '''
    assert(value_of_prog(prog) == -1)
    
    prog = lambda x : f'''
    letrec list-ref (xs,n) =
    cond 
    null?(xs) => raise "null list"
    zero?(n) => car(xs)
    else (list-ref cdr(xs) -(n,1))
    end
    in try (list-ref list(0,1,2,3) {x}) catch (s) s
    '''
    assert(value_of_prog(prog(0)) == 0)
    assert(value_of_prog(prog(10)) == "null list")
    
    

def test_all():
    from LET_cc_data_struct import value_of_prog
    test_exception(value_of_prog)
    from LET_cc import value_of_prog
    test_exception(value_of_prog)
    from LET_cc_imperative import value_of_prog
    test_exception(value_of_prog)