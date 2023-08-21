from LET_parser import parser

import LET_ast_node as ast
List = ast.Pair.list_to_pair
parse = parser.parse

def test_leaf_class(value_of_prog):
    prog = '''
    class interior-node extends object
        field left
        field right
        method initialize (l, r) begin
            set left = l;
            set right = r
        end
    method sum () +(send left sum(),send right sum())
        class leaf-node extends object
        field value
        method initialize (v) set value = v
        method sum () value
    let o1 = new interior-node(
    new interior-node(
    new leaf-node(3),
    new leaf-node(4)),
    new leaf-node(5))
    in send o1 sum()
    '''
    assert(value_of_prog(prog) == 12)
