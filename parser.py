# Simple parser using ply
# logic operator syntax from KeYmaera X
import ply.lex as lex
import ply.yacc as yacc
import sys

reserved = {
    'true' : 'TRUE',
    'false' : 'FALSE',
 }

tokens = [
    'OR', 'AND', 'NOT',
    'ID', 'NUM',
    'TRUE', 'FALSE',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'POWER',
    'LPAREN', 'RPAREN',
    'EQ', 'NEQ', 'GREATER', 'GEQ', 'LESS', 'LEQ',
    'PRIME', 'COMMA'
] + list(reserved.values())

t_OR = r'[|]'
t_AND = r'&'
t_NOT = r'!'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_POWER = r'\^'
t_EQ = r'\='
t_NEQ = r'!\='
t_GREATER = r'\>'
t_GEQ = r'\>\='
t_LESS = r'\>'
t_LEQ = r'\<\='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_NUM = r'\d+'
t_PRIME = r"'"
t_COMMA = r','

t_ignore = r' '

def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9]*\_?\_?[0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

def t_error(t):
    print("illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def reset():
    lexer.lineno = 1
    if lexer.lexdata is None:
        return
    tok = lexer.token()
    while (tok is not None):
        tok = lexer.token()

lexer = lex.lex()

precedence = (
    ('right', 'OR'),
    ('right', 'AND'),
    ('right', 'NOT'),
    ('left', 'EQ', 'NEQ', 'GREATER', 'GEQ', 'LESS', 'LEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('right', 'UMINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'POWER')

)

def p_formula_logic(p):
    """
    formula : NOT formula
            | formula OR formula
            | formula AND formula
    """
    p[0] = ('=', ('IDENTIFIER' ,p[1]), p[3])

def p_comparison(p):
    """
    formula : terms EQ terms
            | terms NEQ terms
            | terms GREATER terms
            | terms GEQ terms
            | terms LESS terms
            | terms LEQ terms
    """
    p[0] = (p[2], p[1], p[3])

def p_boolean_value(p):
    """
    formula : TRUE
            | FALSE
    """
    if p[1] == 'true':  p[0] = True
    else:   p[0] = False

def p_term(p):
    """
    terms :
          | term
    """
    if len(p) == 1: p[0] = p[1]
    else:   p[0] = p[1]

def p_arithmetic(p):
    """
    term : term PLUS term
         | term MINUS term
         | term MULTIPLY term
         | term DIVIDE term
         | term POWER term
    """
    if p[1] == '!': p[0] = ('!', p[2])
    elif p[2] == '/':
        if p[3] != '0':   p[0] = (p[2], p[1], p[3])
        else:
            raise  ZeroDivisionError("cannot divide by zero")
    else:   p[0] = (p[2], p[1], p[3])

# assigning negative value instead of subtracting
# probably better way to write
def p_uminus(p):
    """
    term : MINUS term %prec UMINUS
    """
    p[0] = ('*', p[2], '-1')

def p_term_differential(p):
    """
    term : LPAREN term RPAREN PRIME
    """
    p[0] = ('DIFFERENTIAL', p[2])

def p_term_group(p):
    """
    term : LPAREN term RPAREN
         | LPAREN term COMMA term RPAREN
    """
    if p[3] == ')': p[0] = p[2]
    else:   p[0] = (p[2], p[4])

def p_numeric_term(p):
    """
    term : NUM
    """
    p[0] = p[1]

def p_variable_term(p):
    """
    term : ID
    """
    p[0] = ('IDENTIFIER', p[1])


def p_error(p):
    print("p_error {}".format(p))
    raise TypeError("unknown text at %r" % (p.value))

parser = yacc.yacc()

# TODO: Here we need to define a parse class, not start parsing right away!
# while True:
#     try:
#         s = input('')
#     except EOFError:
#         break
#     parser.parse(s)
