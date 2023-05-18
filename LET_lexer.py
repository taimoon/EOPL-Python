# import ply.lex as lex
import ply.ply.lex as lex
# PLS READ THE LINK TO THE DOC BEFORE MODIFYING
'https://www.dabeaz.com/ply/ply.html'

# tokens list

reserved = {
   'if' : 'IF',
   'then' : 'THEN',
   'else' : 'ELSE',
   'let' : 'LET',
   'unpack': 'UNPACK',
   'in' : 'IN',
   'proc': 'PROC',
   'begin': 'BEGIN',
   'letrec' : 'LETREC',
   'let*': 'LET_STAR',
   'emptylist': 'NULL',
   'cond': 'COND',
   'end': 'END',
   
   'zero?': 'ZERO_TEST',
   'minus': 'MINUS',
   'cdr' : 'CDR',
   'car' : 'CAR',
   
   
   'less?': 'LESS_TEST',
   'greater?' : 'GREATER_TEST',
   'equal?': 'EQUAL_TEST',
   'cons' : 'CONS',
   
   'list': 'LIST',
   
   'newref':'NEWREF',
   'deref' : 'DEREF',
   'setref': 'SET',
}
tokens = "NUMBER ID RIGHTARROW".split() + list(reserved.values())

# literals
literals = '-+*/,=();'

# Specification of tokens
# t_LPAREN = r'\('
# t_RPAREN = r'\)'
t_RIGHTARROW = r'\=>'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9\?\*]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

## INFORMATIONAL OPERATIONS
# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
## END OF INFORMATIONAL OPERATIONS
# Build the lexer
lexer = lex.lex()
