# Term parser for terms in KeYmaera's differential dynamic logic using ply
import ply.lex as lex
import ply.yacc as yacc
import sys

tokens = (
    'ID', 'NUM',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'POWER',
    'LPAREN', 'RPAREN',
    'PRIME',
    'COMMA'
)

t_ID = r'[a-zA-Z][a-zA-Z0-9]*\_?\_?[0-9]*'
t_NUM = r'[0-9]+\.?[0-9]*'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_POWER = r'\^'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_PRIME = r'\''
t_COMMA = r','




t_ignore = r' '

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

def t_error(t):
    print("illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('right', 'UMINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'POWER')
)

def p_terms(p):
    """
    terms :
           | term
           | function
    """
    #when empty
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]
    #uncomment to test on terminal
    print(p[0])

# interpreted functions have to be added
def p_function(p):
    """
    function : ID LPAREN RPAREN
             | ID LPAREN term RPAREN
    """
    if p[3] == ')': p[0] = ('Constant Symbol', p[1]+'()')
    else:   p[0] = ('function', p[1]+p[2]+str(p[3])+p[4])

def p_term(p):
    """
    term : term PLUS term
         | term MINUS term
         | term MULTIPLY term
         | term DIVIDE term
         | term POWER term
    """
    if p[2] == '/':
        if p[3] != 0:   p[0] = (p[2], p[1], p[3])
        else:
            raise  ZeroDivisionError("cannot divide by zero")
    else:   p[0] = (p[2], p[1], p[3])


# unary minus
# probably better way to write
def p_term_uminus(p):
    """
    term : MINUS term %prec UMINUS
    """
    p[0] = ('*', p[2], '-1')

def p_term_group(p):
    """
    term : LPAREN term RPAREN
         | LPAREN term COMMA term RPAREN
    """
    if p[3] == ',':   p[0] = '('+str(p[2]) +','+ str(p[4])+')'
    else:   p[0] = p[2]

def p_differential(p):
    """
    term : term PRIME
         | LPAREN term RPAREN PRIME
    """
    if p[1] == '(': p[0] = ('differential', p[2])
    else:   p[0] = ('differential', p[1])

def p_numeric_value(p):
    """
    term : NUM
    """
    p[0] = p[1]

def p_value(p):
    """
    term : ID
    """
    p[0] = ('IDENTIFIER', p[1])


def p_error(p):
    print("p_error {}".format(p))
    raise TypeError("unknown text at %r" % (p.value))

parser = yacc.yacc()

#uncomment below to test on the terminal
while True:
    try:
        s = input('')
    except EOFError:
        break
    parser.parse(s)
