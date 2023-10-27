# LET
```bnf
<prog> ::= <expr>
<expr> ::= <number>
         | -(<expr>,<expr>)
         | zero?(<expr>)
         | if <expr> then <expr> else <expr>
         | <ID>
         | let <ID> = <expr> in <expr>

<expr> ::= <unary_op>(<expr>)
         | <binary_op>(<expr>,<expr>)
         | list(<expr>,...)
         | cond {<expr> ==> <expr>}* end
         | if <bool-expr> then <expr> else <expr>
         | let {<ID> = <expr>}* in <expr>
         | let* {<ID> = <expr>}* in <expr>
         | unpack <ID>* = <expr> in <expr>
<unary_op> ::= minus | -
<binary_op> ::= - | add | mul | div 
              | equal? | greater? | less? 
              | cons
```
# PROC
```bnf
<expr> ::= proc (<ID>) <expr>
         | (<expr> <expr>)
         | proc (<ID>, ...)
         | proc (<ID>, ...) <expr>
         | (<expr> <expr> ...)
         | letproc <ID> (<ID>, ...) = <expr> in <expr>
```
# LETREC
```bnf
<expr> ::= letrec <ID> (<ID>, ...) = <expr> in <expr>
         | letrec {<ID> (<ID>, ...) = <expr>}* in <expr>
```

