# Simple parser using ply
# quantifiers to be added next week
# logic operator syntax from KeYmaera X
import ply.lex as lex
import ply.yacc as yacc
import sys

tokens = (
    'TRUE', 'FALSE',
    'OR', 'AND', 'NOT',
    'ID', 'NUM',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'POWER',
    'LPAREN', 'RPAREN',
    'EQ', 'NEQ', 'GREATER', 'GEQ', 'LESS', 'LEQ'
)

t_TRUE = r'True'
t_FALSE = r'False'
t_OR = r'[|]'
t_AND = r'&'
t_NOT = r'!'
t_ID = r'[a-zA-Z_]\w*'
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

t_ignore = r' '

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

def t_error(t):
    print("illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

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

def p_string(p):
    """
    string :
           | expression
           | var_assign
    """
    #when empty
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]
    #uncomment to test on terminal
    print(p[0])

def p_var_assign(p):
    """
    var_assign : ID EQ expression
    """
    p[0] = ('=', ('IDENTIFIER' ,p[1]), p[3])

def p_expression(p):
    """
    expression : NOT expression
               | expression OR expression
               | expression AND expression
               | expression PLUS expression
               | expression MINUS expression
               | expression MULTIPLY expression
               | expression DIVIDE expression
               | expression POWER expression
    """
    if p[1] == '!': p[0] = ('!', p[2])
    elif p[2] == '/':
        if p[3] != '0':   p[0] = (p[2], p[1], p[3])
        else:
            raise  ZeroDivisionError("cannot divide by zero")
    else:   p[0] = (p[2], p[1], p[3])

def p_comparison(p):
    """
    expression : expression EQ expression
               | expression NEQ expression
               | expression GREATER expression
               | expression GEQ expression
               | expression LESS expression
               | expression LEQ expression
    """
    p[0] = (p[2], p[1], p[3])

# assigning negative value instead of subtracting
# probably better way to write
def p_expression_uminus(p):
    """
    expression : MINUS expression %prec UMINUS
    """
    p[0] = ('*', p[2], '-1')

def p_expression_group(p):
    """
    expression : LPAREN expression RPAREN
    """
    p[0] = p[2]

def p_numeric_value(p):
    """
    expression : NUM
    """
    p[0] = p[1]

# if value is assigned to boolean value
# then boolean value(True, False) becomes an identifier
# maybe have to fix later
def p_value(p):
    """
    expression : ID
               | TRUE
               | FALSE
    """
    if p[1] == 'True':  p[0] = p[1]
    elif p[1] == 'False': p[0] = p[1]
    else:   p[0] = ('IDENTIFIER', p[1])


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
