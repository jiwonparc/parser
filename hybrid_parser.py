# Parser for hybrid program expressions in KeYmaera X using ply
# advanced material(predicate symbol) of formula expression has to be added
import ply.lex as lex
import ply.yacc as yacc
import sys

tokens = (
    'TRUE', 'FALSE',
    'OR', 'AND', 'NOT',
    'ID', 'NUM',
    'PLUS', 'MINUS', 'STAR', 'DIVIDE', 'POWER',
    'LPAREN', 'RPAREN', 'LBOX', 'RBOX', 'LDIA', 'LCURL', 'RCURL',
    'EQ', 'NEQ', 'GREATER', 'GEQ', 'LESS', 'LEQ',
    'FORALL', 'EXISTS',
    'LIMPLY', 'RIMPLY', 'BIMPLY',
    'PRIME',
    'COMMA', 'SEMICOLON', 'DEFINE', 'TEST', 'CHOICE',
    'IF', 'ELSE'
)

t_TRUE = r'True'
t_FALSE = r'False'
t_OR = r'[|]'
t_AND = r'&'
t_NOT = r'!'
t_ID = r'[a-zA-Z_]\w*'
t_PLUS = r'\+'
t_MINUS = r'-'
t_STAR = r'\*'
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
t_LCURL = r'{'
t_RCURL = r'}'
t_FORALL = r'\\forall'
t_EXISTS = r'\\exists'
t_LIMPLY = r'->'
t_RIMPLY = r'<-'
t_BIMPLY = r'<->'
t_PRIME = r'\''
t_COMMA = r','
t_SEMICOLON = r';'
t_DEFINE = r':='
t_TEST = r'\?'
t_CHOICE = r'\+{2}'
t_IF = r'if'
t_ELSE = r'else'

t_ignore = r' '

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

def t_error(t):
    print("illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

precedence = (
    ('right', 'COMMA'),
    ('right', 'CHOICE'),
    ('right', 'SEMICOLON'),
    ('right', 'REPET'),
    ('left', 'BIMPLY'),
    ('right', 'LIMPLY'), ('left', 'RIMPLY'),
    ('right', 'OR'),
    ('right', 'AND'),
    ('right', 'NOT'),
    ('right', 'FORALL', 'EXISTS', 'LBOX', 'RBOX', 'LDIA'),
    ('left', 'EQ', 'NEQ', 'GREATER', 'GEQ', 'LESS', 'LEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('right', 'UMINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'POWER')
)

def p_differential_programs(p):
    """
    d_programs : d_program
               | d_program COMMA d_program
    """
    if p[2] == ',': p[0] = (p[1], p[3])

def p_differential_program(p):
    """
    d_program : NUM
              | ID PRIME EQ terms
    """
    if p[2] == "'": p[0] = ('differential', p[1], p[4])
    else:   p[0] = p[1]

def p_programs(p):
    """
    programs : program
    """
    p[0] = p[1]
    # uncomment to test
    print(p[0])


def p_program(p):
    """
    program : TEST program SEMICOLON
            | LCURL d_programs AND formulas RCURL
            | LCURL program RCURL STAR
            | program CHOICE program
    """
    if p[1] == '?': p[0] = (p[1], p[2])
    elif p[3] == '&': p[0] = ('continuous_ev', p[2], p[4])
    elif p[4] == '*': p[0] = ('repetition', p[2])
    elif p[2] == '++': p[0] = ('choice', p[1], p[3])

def p_program_form(p):
    """
    program : program program
            | LCURL program RCURL
    """
    if p[1] == '{': p[0] = p[2]
    else: p[0] = (p[1], p[2])

def p_program_conditional(p):
    """
    program : IF LPAREN formulas RPAREN LCURL program RCURL ELSE LCURL program RCURL
            | if LPAREN formulas RPAREN LCURL program RCURL
    """


# ambiguity on the documentation P ::= a;
# not sure what 'a' is
# put 'a' as a variable name for now
def p_program_assigntment(p):
    """
    program : ID SEMICOLON
            | ID DEFINE term SEMICOLON
            | ID PRIME DEFINE term SEMICOLON
    """
    if p[2] == ';': p[0] = p[1]
    elif p[2] == ':': p[0] = ('define', p[1], p[3])
    else:   p[0] = ('differential', p[1], p[4])


def p_formulas(p):
    """
    formulas : formula
    """
    p[0] = p[1]

def p_formula(p):
    """
    formula : arithmetic_formula
            | LPAREN formula RPAREN
    """
    if p[1] == '(': p[0] = p[2]
    else:   p[0] = p[1]

def p_formula_arithmetic(p):
    """
    arithmetic_formula : terms EQ terms
                       | terms NEQ terms
                       | terms GEQ terms
                       | terms GREATER terms
                       | terms LEQ terms
                       | terms LESS terms
    """
    p[0] = (p[2], p[1], p[3])

def p_formula_logic(p):
    """
    formula : formula OR formula
            | formula AND formula
            | NOT formula
    """
    if p[1] == '!': p[0] = ('!', p[2])
    else:   p[0] = (p[2], p[1], p[3])

def p_formula_quantifier(p):
    """
    formula : FORALL terms formula
            | EXISTS terms formula
    """
    p[0] = (p[1], p[2], p[3])

def p_formula_modality(p):
    """
    formula : LBOX programs RBOX formula
            | LDIA programs GREATER formula
    """
    if p[2] == '[': p[0] = ('box', p[2], p[4])
    else:   p[0] = ('dia', p[2], p[4])

def p_formula_implication(p):
    """
    formula : formula BIMPLY formula
            | formula RIMPLY formula
            | formula LIMPLY formula
    """
    if p[2] == '->': p[0] = ('imply', p[1], p[3])
    elif p[2] == '<-':  p[0] = ('imply', p[3], p[1])
    else:   ('iff', p[1], p[3])

def p_formula_differential(p):
    """
    formula : LPAREN formula RPAREN PRIME
    """
    p[0] = ('differential', p[2])

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
    if p[3] == ',':   p[0] = (p[2], p[4])
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
    formula : TRUE
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
