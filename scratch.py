from LET import *

prog = '''\
    let f = proc(x) proc (y) +(x,y)
    in f'''
prog = parser.parse(prog)
prog = value_of(prog,empty_env())
print('-'*10)
print(prog)
# print(prog.env('f'))
# print(prog.env('x'))