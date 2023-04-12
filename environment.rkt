#lang racket
(define (println e) (display e) (newline))
(define (first-implementation)
  (eval '(begin
    (define (empty-env)
      (lambda (var) (error "it is empty-env; possible error the var is not in env" var)))
    (define (apply-env env var) (env var))
    (define (extend-env var val env)
      (lambda (app-var)
        (if (eq? app-var var)
            val
            (env app-var))))
  )))
(define (assoc-list-implementation)
  (eval '(begin
    (define (empty-env) '())
    (define (extend-env var val env)
      (cons (cons var val) env))
    (define (apply-env env var)
      (if (list? env)
          (let ((res (assoc var env)))
            (if res (cdr res) (error "variable is not found" var env)))
          (error "invalid environment type" env)))
    (define (has-binding? env var)
      (if (assoc var env) #t))
    
  )))

(define (empty-env) 
  (list 'empty-env)) ; self-representing
(define (empty-env? env)
  (eq? (car env) 'empty-env))
(define (extend-env var val env)
  (list 'extend-env var val env))
(define (apply-env env var)
 (cond
    ((empty-env? env) 
     (error "variable is not found:" var))
    ((eqv? (car env) 'extend-env)
     (if (eqv? (cadr env) var)
         (caddr env)
         (apply-env (cadddr env) var)))
    (else (error "invalid environment type" env))))

(define (test)
  (define e
  (extend-env 'd 6
  (extend-env 'y 8
  (extend-env 'x 7
  (extend-env 'y 14
  (empty-env))))))
  (for-each (lambda (var) (println (apply-env e var))) '(d y x y z))
)
(test)
(first-implementation)
(test)
(assoc-list-implementation)
(test)