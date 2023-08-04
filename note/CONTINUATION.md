# Notation
- `<<prog>>` is the ast of the source code `prog`
# How to do continuation?
### Definition
```scheme
(define (apply-cc cc v) (cc v))

(apply-cc (end-cc) val)
  val
```
### zero-expression
```scheme
(val-of-k <<zero?(exp)>> env cc)
(val-of-k exp env (cc-zero cc))
  (apply-cc (cc-zero cc) val)
  (apply-cc cc (= val 0))

(val-of-k <<zero?(0)>> env end-cc)
(apply-cc end-cc #t)
#t
```
### difference-expression
```scheme
(value-of-k <<-(exp1,exp2)>> env cc) ; start
(value-of-k exp1 env (right-cc exp2 env cc))
(apply-cc (right-cc exp2 env cc) val1)
(value-of-k exp2 env (left-cc val1 env cc))
(apply-cc (left-cc val1 env cc) val2)
(apply-cc cc (- val1 val2))
```

```scheme

(value-of-k <<-(-(44,11),3)>> env0 end-cc)
(value-of-k <<-(44,11)>> env0
  (right-cc <<3>> env0 end-cc))
(value-of-k <<44>> env0
  (right-cc <<11>> env0 (right-cc <<3>> env0 end-cc)))
(apply-cc (right-cc <<11>> env0 (right-cc <<3>> env0 end-cc))
          44)
(value-of-k <<11>> env0 
            (left-cc 44 env0 (right-cc <<3>> env0 end-cc)))
(apply-cc (left-cc 44 env0 (right-cc <<3>> env0 end-cc)) 11)
(apply-cc (right-cc <<3>> env0 end-cc) (- 44 11))
(value-of-k <<3>> env0 (left-cc 33 env0 end-cc))
(apply-cc (left-cc 33 env0 end-cc) 3)
(apply-cc end-cc (- 33 3))
(apply-cc end-cc 30)
30
```
### Application-expression
```scheme
(value-of-k <<(exp1 exp2)>> env cc)
(value-of-k exp1 env (operator-cc <<exp2>> env cc))
(apply-cc (operator-cc <<exp2>> env cc) proc1)
(value-of-k <<exp2>> env (operand-cc proc1 cc))
(apply-cc (operand-cc proc1 cc) val2)
(apply-cc cc (proc1 val2))
```
### Multi-argument application expression
#### Version 1
```scheme
(value-of-k <<(exp1 exp2 exp3 exp4)>> env cc)
(value-of-k exp1 env (operator-cc <<exp2 exp3 exp4>> env cc))
(apply-cc (operator-cc <<exp2 exp3 exp4>> env cc) proc1)
(value-of-k exp2 env (operand-cc proc1 <<exp3 exp4>> env cc))
(apply-cc (operand-cc proc1 <<exp3 exp4>> env cc) val2)
(value-of-k exp3 env (operand-cc (proc1 val2) <<exp4>> env cc))
(apply-cc (operand-cc (proc1 val2) <<exp4>> env cc) val3)
(value-of-k exp4 env (operand-cc (proc1 val2 val3) () env cc))
(apply-cc (operand-cc (proc1 val2 val3) () env cc) val4)
(proc1 val2 val3 val4)
```
#### Version 2
```scheme
(value-of-k <<(exp1 exp2 exp3 exp4)>> env cc)
(value-of-k exp1 env (operator-cc <<exp2 exp3 exp4>> env cc))
(apply-cc (operator-cc <<exp2 exp3 exp4>> env cc) proc1)
```