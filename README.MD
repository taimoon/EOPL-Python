# Note
1. By convention,
   ```
   <token>(...)
   ```
   is implemented outside of the target language.
   ```
   (operator ...)
   ```
   is reserved for user-defined procedure.
2. Derived Form 
   ---
   Expression that expand to other expressions. The idea can be generalized to marco in Scheme. Reference : [The Scheme Programming Language, 4th Edition](https://www.scheme.com/tspl4/further.html#./further:h1).
   
   It allows a smaller implementation. Example usage is that `let` expression is defined in term of `procedure`, then if implemented the semantic of `procedure`, then `let` automatically follow. 
   
   Another example, the `conditional` 
    ```scheme
    (cond ((< x 0) (- x))
          ((= x 0) 0)
          (else x))
    ```
    can be rewritten in form using `branch` to
    ```scheme
    (if (< x 0)
        (- x)
        (if (= x 0)
            0
            x))
    ```
3. Although expansion of derived form can be interleaved to parsing stage, implementer prefers to seperate them into 2 steps. So that parsing only return uninterpreted AST. It is the task of interpreter to give it meaning. 
  
    It might be tempting to seperate expansion process from `value_of` function. The reason of not seperating these is that put all behaviour definition in the same function, even they are derived. This is to document these together.
    
    However, expansion has the problem that we cannot easily to know the expected behaviour of program from the expansions itself. This requires additional documentation.

# TODO
1. add unpack operation to all let variant
   ```
   let u = 7
    in unpack x y = list(u,3)
    in -(x,y) 
    => 4
   ```
   Previously, testing various implementation of unpack operation. There are at least 2 implementations has been tried
   1. Add `unpack` as primitive implementation to env, the proc will first unpack evaluated list expression then apply it
   2. Expand `unpack_exp` to application form, then it is the task of application_exp evaluator to unpack the list arguments. (current implementation)
   
   Additionally, I've overloaded the meaning of `Unpack_Exp`; inspired by Python `*args,**kwargs`; Scheme `(apply <operator> (list ...))`. This allows `unpack` let defined as derived form.

   For example,
   ```
   (add unpack(list(3,4)))
   ```
   should be same as
   ```
   (add 3 4)
   ```
2. Specify and implement multi-arguments PROC_MODULES
