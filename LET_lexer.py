import ply.lex as lex
# PLS READ THE LINK TO THE DOC BEFORE MODIFYING
'https://www.dabeaz.com/ply/ply.html'

# tokens list

reserved = {
   'if'     : 'IF',
   'then'   : 'THEN',
   'else'   : 'ELSE',
   'let'    : 'LET',
   'in'     : 'IN',
   'proc'   : 'PROC',
   'begin'  : 'BEGIN',
   'letrec' : 'LETREC',
   'letmutable' : 'LETMUT',
   'let*'   : 'LET_STAR',
   'cond'   : 'COND',
   'end'    : 'END',
   'emptylist' : 'NULL',
   'unpack' : 'UNPACK',
   'unpair' : 'UNPAIR',
   
   'zero?' : 'ZERO_TEST',
   'minus' : 'MINUS',
   'cdr'   : 'CDR',
   'car'   : 'CAR',
   'null?' : 'NULL_TEST',
   'print' : 'PRINT',
   
   'less?'    : 'LESS_TEST',
   'greater?' : 'GREATER_TEST',
   'equal?'   : 'EQUAL_TEST',
   'cons'     : 'CONS',
   'newpair' : 'NEWPAIR',
   
   'list'   : 'LIST',
   
   'ref'    : 'REF',
   'newref' : 'NEWREF',
   'deref'  : 'DEREF',
   'setref' : 'SETREF',
   'set'    : 'SET',
   'setcar' : 'SETCAR',
   'setcdr' : 'SETCDR',
   
   'void' : 'VOID',
   'int' : 'INT',
   'bool' : 'BOOL',
   'pairof' : 'PAIROF',
   'listof': 'LISTOF',
   
   'module' : 'MODULE',
   'interface': 'INTERFACE',
   'body' : 'BODY',
   'from' : 'FROM',
   'take' : 'TAKE',
   'opaque' : 'OPAQUE',
   'transparent' : 'TRANSPARENT',
   'module-proc' :'MODULE_PROC',
   'type' : 'TYPE',
   
   'class' : 'CLASS',
   'method' : 'METHOD',
   'new' : 'NEW',
   'send' : 'SEND',
   'super' : 'SUPER',
   'self' : 'SELF',
   'extends' : 'EXTENDS',
   'field' : 'FIELD',
   
}

tokens = "NUMBER ID RIGHTARROW TYPEARROW".split() + list(reserved.values())

# literals
literals = r'-+*/,=();{}:?[].'

# Specification of tokens
t_RIGHTARROW = r'\=>'
t_TYPEARROW = r'\->'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9\?\*\-]*'
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

# Define the rule for the percent symbol
def t_PERCENT(t):
    r'%.*'  # Match '%' followed by any characters
    pass   # Discard the token

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
## END OF INFORMATIONAL OPERATIONS
# Build the lexer
lexer = lex.lex()
