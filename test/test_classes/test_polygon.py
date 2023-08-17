from LET_parser import parser

import LET_ast_node as ast
List = ast.Pair.list_to_pair
parse = parser.parse

def test_polygon(value_of_prog):
    poly_prog = '''
    class Polygon extends object
        field xs
        method initialize (ys) set xs = ys
        method sum(ys)
            if null?(ys) 
            then 0 
            else +(car(ys),send self sum(cdr(ys)))
        method perimeter() send self sum(xs)
        method sideref(n) send self listref(xs,n)
        method listref(ys,n) cond 
            null?(ys) => emptylist
            zero?(n) => car(ys)
            else send self listref(cdr(ys),-(n,1)) 
            end
        method setside(x,n) letrec 
            setlist(xs,n) = cond
            null?(xs) => emptylist
            zero?(n) => setcar(xs,x)
            else (setlist cdr(xs) -(n,1)) end
        in (setlist xs n)
        method copy() letrec copy(xs) =
        if null?(xs) then emptylist else cons(car(xs),(copy cdr(xs)))
        in (copy xs)
    ''' 
    triangle_prog = '''class Triangle extends Polygon
        method initialize(x,y,z)
            super initialize(list(x,y,z))
        method area() 
            let s = /(send self perimeter(), 2)
            in let
                a = -(s,super sideref(0))
                b = -(s,super sideref(1))
                c = -(s,super sideref(2))
            in sqrt(*(s,*(a,*(b,c))))
    '''
    rect_prog = '''class Rect extends Polygon
        method initialize(a,b) super initialize(list(a,b,a,b))
        method setfirst(n) begin
            super setside(n,0);
            super setside(n,2) end
        method setsecond(n) begin
            super setside(n,1);
            super setside(n,3) end
        method area() *(send self sideref(0), send self sideref(1))
    class Square extends Rect
        method initialize(l) super initialize(l,l)
        method setside(n) begin
            send self setfirst(n);
            send self setsecond(n) end
    '''
    cls_prog = f'{poly_prog}{triangle_prog}{rect_prog}'
    prog = f'''{cls_prog} 
    let poly = new Polygon (list(2,3,5,7)) 
    in list(send poly perimeter(), 
        send poly sideref(0),
        send poly sideref(1), 
        send poly sideref(2),
        send poly sideref(3))
    '''
    res = value_of_prog(prog)
    ans = List(17,2,3,5,7)
    assert(str(res) == str(ans))
    
    prog = f'''{cls_prog} 
    let poly = new Triangle (3,4,5) 
    in list(send poly area(), 
        send poly sideref(0),
        send poly sideref(1), 
        send poly sideref(2))'''
    res = value_of_prog(prog)
    ans = List(6.0,3,4,5)
    assert(str(res) == str(ans))
    
    prog = f'''{cls_prog} 
    let rect = new Rect (3,5)
    in list(send rect area(), send rect copy())'''
    res = value_of_prog(prog)
    ans = List(15,List(3,5,3,5))
    assert(str(res) == str(ans))
    
    prog = f'''{cls_prog} 
    let sqr = new Square (13)
    in list(send sqr area(), send sqr copy())'''
    res = value_of_prog(prog)
    ans = List(13*13,List(13,13,13,13))
    assert(str(res) == str(ans))
    
    prog = f'''{cls_prog} 
    let sqr = new Square (13)
    in begin send sqr setside(17);
    list(send sqr area(), send sqr sideref(0), send sqr sideref(1)) end'''
    res = value_of_prog(prog)
    ans = List(17*17,17,17)
    assert(str(res) == str(ans))

    prog = f'''{cls_prog}
    let sqr = new Square (3)
    tri = new Triangle (2,3,5)
    in list(
        instanceof sqr Polygon,
        instanceof sqr Rect,
        instanceof sqr Triangle,
        instanceof tri Polygon,
        instanceof tri Rect
        )
    '''
    res = value_of_prog(prog)
    ans = List(True,True,False,True,False)
    assert(str(res) == str(ans))
