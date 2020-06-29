# Parser for formula expression in KeYmaera X using ply
# advanced material(predicate symbol) of formula expression has to be added
import ply.lex as lex
import ply.yacc as yacc
import sys

tokens = (
    'TRUE', 'FALSE',
    'OR', 'AND', 'NOT',
    'ID', 'NUM',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'POWER',
    'LPAREN', 'RPAREN', 'LBOX', 'RBOX', 'LDIA', 'RDIA',
    'EQ', 'NEQ', 'GREATER', 'GEQ', 'LESS', 'LEQ',
    'FORALL', 'EXISTS',
    'LIMPLY', 'RIMPLY', 'BIMPLY',
    'PRIME',
    'COMMA'
)

t_TRUE = r'True'
t_FALSE = r'False'
t_OR = r'[|]'
t_AND = r'&'
t_NOT = r'!'
t_ID = r'[a-zA-Z][a-zA-Z0-9]*\_?\_?[0-9]*'
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
t_LBOX = r'\['
t_RBOX = r'\]'
t_LDIA = r'\<'
t_RDIA = r'\>'
t_FORALL = r'\\forall'
t_EXISTS = r'\\exists'
t_LIMPLY = r'->'
t_RIMPLY = r'<-'
t_BIMPLY = r'<->'
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
    ('nonassoc', 'BIMPLY'),
    ('right', 'LIMPLY'), ('left', 'RIMPLY'),
    ('right', 'OR'),
    ('right', 'AND'),
    ('right', 'NOT'),
    ('right', 'FORALL', 'EXISTS', 'LBOX', 'RBOX', 'LDIA', 'RDIA'),
    ('left', 'EQ', 'NEQ', 'GREATER', 'GEQ', 'LESS', 'LEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('right', 'UMINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'POWER')
)

def p_formula(p):
    """
    formula :
             | formulas
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]
    # uncomment to test
    print(p[0])
def p_formula_comparison(p):
    """
    formulas : terms EQ terms
             | terms NEQ terms
             | terms GEQ terms
             | terms GREATER terms
             | terms LEQ terms
             | terms LESS terms
    """
    p[0] = (p[2], p[1], p[3])

def p_formula_logic(p):
    """
    formulas : formulas OR formulas
             | formulas AND formulas
             | NOT formulas
    """
    if p[1] == '!': p[0] = ('!', p[2])
    else:   p[0] = (p[2], p[1], p[3])

def p_formula_quantifier(p):
    """
    formulas : FORALL terms formulas
             | EXISTS terms formulas
    """
    p[0] = (p[1], p[2], p[3])

# change ID to programs after writing parsing for HP
# greater sign same as right diamond sign
def p_formula_modality(p):
    """
    formulas : LBOX ID RBOX formulas
             | LDIA ID GREATER formulas
    """
    if p[2] == '[': p[0] = ('box', p[2], p[4])
    else:   p[0] = ('dia', p[2], p[4])

def p_formula_implication(p):
    """
    formulas : formulas BIMPLY formulas
             | formulas RIMPLY formulas
             | formulas LIMPLY formulas
    """
    if p[2] == '->': p[0] = ('imply', p[1], p[3])
    elif p[2] == '<-':  p[0] = ('imply', p[3], p[1])
    else:   ('iff', p[1], p[3])

def p_formula_differential(p):
    """
    formulas : LPAREN formulas RPAREN
             | LPAREN formulas RPAREN PRIME
    """
    if p[4] == "'": p[0] = ('differential', p[2])
    else:   p[0] = (p[2])

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

def p_term_numeric_value(p):
    """
    term : NUM
    """
    p[0] = p[1]

def p_term_value(p):
    """
    term : ID
    """
    p[0] = ('IDENTIFIER', p[1])

def p_formula_value(p):
    """
    formulas : TRUE
             | FALSE
    """
    if p[1] == 'true': p[0] == True
    else:   p[0] == False

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
