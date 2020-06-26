# Simple parser for a boolean expression using ply
# calculate the boolean value of given boolean expression
# logic operator syntax from KeYmaera X

import ply.lex as lex
import ply.yacc as yacc
import sys

tokens = (
    'TRUE', 'FALSE',
    'OR', 'AND', 'NOT',
)

t_TRUE = r'True'
t_FALSE = r'False'
t_OR = r'[|]'
t_AND = r'&'
t_NOT = r'!'

t_ignore = r' '

def t_error(t):
    raise TypeError("unknown text '%s', boolean expression expected" % (t.value,))

lex.lex()

precedence = (
    ('left','OR'),
    ('left','AND'),
    ('left','NOT')
)

def p_string(p):
    """
    string :
    string : expression
    """
    #when empty
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]
    #uncomment to test on terminal
    print(p[0])

def p_expression(p):
    """
    expression : NOT expression
               | expression OR expression
               | expression AND expression
    """
    if p[1] == '!':  p[0] = ('not', p[2])
    if p[2] == '|': p[0] = ('or', p[1], p[3])
    elif p[2] == '&':   p[0] = ('and', p[1], p[3])

def p_value(p):
    """
    expression : TRUE
               | FALSE
    """
    if p[1] == 'True':  p[0] = True
    else:   p[0] = False


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
