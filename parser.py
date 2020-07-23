# Simple parser using ply
# logic operator syntax from KeYmaera X
# advanced material(predicate symbol) of formula expression has to be added
import ply.lex as lex
import ply.yacc as yacc
import sys
from AST import *

reserved = {
    'true' : 'TRUE',
    'false' : 'FALSE',
 }

tokens = [
    'OR', 'AND', 'NOT',
    'ID', 'NUM',
    'PLUS', 'MINUS', 'STAR', 'DIVIDE', 'POWER',
    'LPAREN', 'RPAREN', 'LBOX', 'RBOX', 'LCURL', 'RCURL',
    'EQ', 'NEQ', 'GREATER', 'GEQ', 'LESS', 'LEQ',
    'FORALL', 'EXISTS',
    'LIMPLY', 'RIMPLY', 'BIMPLY',
    'PRIME',
    'COMMA', 'SEMICOLON', 'DEFINE', 'TEST', 'CHOICE',
] + list(reserved.values())

t_OR = r'[|]'
t_AND = r'&'
t_NOT = r'!'
t_PLUS = r'\+'
t_MINUS = r'-'
t_STAR = r'\*'
t_DIVIDE = r'/'
t_POWER = r'\^'
t_EQ = r'\='
t_NEQ = r'!\='
t_GREATER = r'\>'
t_GEQ = r'\>\='
t_LESS = r'\<'
t_LEQ = r'\<\='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_NUM = r'[0-9]+\.?[0-9]*'
t_LBOX = r'\['
t_RBOX = r'\]'
t_LCURL = r'{'
t_RCURL = r'}'
t_FORALL = r'\\forall'
t_EXISTS = r'\\exists'
t_LIMPLY = r'\-\>'
t_RIMPLY = r'\<\-'
t_BIMPLY = r'\<\-\>'
t_PRIME = r'\''
t_COMMA = r','
t_SEMICOLON = r';'
t_DEFINE = r':='
t_TEST = r'\?'
t_CHOICE = r'\+{2}'

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
    ('right', 'CHOICE'),
    ('right', 'SEMICOLON'),
    ('right', 'REPET'),
    ('left', 'BIMPLY'),
    ('right', 'LIMPLY'), ('left', 'RIMPLY'),
    ('right', 'OR'),
    ('right', 'AND'),
    ('right', 'NOT'),
    ('right', 'FORALL', 'EXISTS', 'BOX', 'DIA'),
    ('left', 'EQ', 'NEQ', 'GREATER', 'GEQ', 'LESS', 'LEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('right', 'UMINUS'),
    ('left', 'STAR', 'DIVIDE'),
    ('right', 'POWER')
)

def p_program_form(p):
    """
    program : program program
            | LCURL program RCURL
    """
    if p[1] == '{':
        syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
        Bracket('CURL', p[2], syntax)
    else:
        if isinstance(p[1],Tree):
            p[1].programs.append(p[2])
        else:
            p[0] = Tree([p[1],p[2]])

def p_program_repet(p):
    """
    program : LCURL program RCURL STAR %prec REPET
    """
    syntax = SyntaxInfo(p.lineno(4), p.lexpos(4))
    p[0] = Operator('REPETITION', syntax, left = p[2])

def p_program(p):
    """
    program : LCURL d_program AND formula RCURL
            | program CHOICE program
    """
    if p[3] == '&':
        syntax = SyntaxInfo(p.lineno(3), p.lexpos(3))
        p[0] = Operator('C_EVOLOUTION', syntax, left = p[2], right = p[4])
    elif p[2] == '++':
        syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
        p[0] = Operator('CHOICE', syntax, left = p[1], right = p[3])

def p_program_test(p):
    """
    program : TEST formula SEMICOLON
    """
    syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
    p[0] = Operator('TEST', syntax, left = p[2])

# ambiguity on the documentation P ::= a;
# not sure what 'a' is
# put 'a' as a variable name for now
def p_program_assigntment(p):
    """
    program : ID SEMICOLON
            | ID DEFINE STAR SEMICOLON
            | ID DEFINE term SEMICOLON
            | ID PRIME DEFINE term SEMICOLON
    """
    if p[2] == ';':
        syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
        p[0] = Variable(p[1], 'IDENTIFIER', syntax)
    elif p[2] == ':=':
        if p[3] == '*':
            syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
            p[0] = Assignment(p[1], 'NONDASSIGNMENT', syntax)
        else:
            syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
            p[0] = Assignment(p[1], p[3], syntax)
    else:
        syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))

def p_differential_program(p):
    """
    d_program : NUM
              | ID PRIME EQ term
              | d_program COMMA d_program
    """
    if p[2] == "'":
        syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
        p[0] = Operator('DIFFERENTIAL', syntax, left = p[1], right = p[4])
    elif p[2] == ",":
        if isinstance(p[1], Tree):
            p[1].programs.append(p[3])
        else:
            p[0] = Tree([p[1], p[3]])
    else:
        syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
        p[0] = Variable(p[1], 'DP_CST', syntax)

def p_formula_form(p):
    """
    formula : LPAREN formula RPAREN
    """
    syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
    p[0] = Bracket('PAREN', p[2], syntax)

def p_formula_implication(p):
    """
    formula : formula BIMPLY formula
            | formula RIMPLY formula
            | formula LIMPLY formula
    """
    syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
    p[0] = Operator(p[2], syntax, left = p[1], right = p[3])

def p_formula_logic(p):
    """
    formula : formula OR formula
            | formula AND formula
            | NOT formula
    """
    if p[1] == '!':
        syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
        p[0] = Operator(p[1], syntax, left = p[1])
    else:
        syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
        p[0] = Operator(p[2], syntax, left = p[1], right = p[3])

def p_formula_quantifier(p):
    """
    formula : FORALL ID formula
            | EXISTS ID formula
    """
    syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
    p[0] = Quantifier(p[1], p[2], p[3], syntax)

def p_formula_modality(p):
    """
    formula : LBOX program RBOX formula %prec BOX
            | LESS program GREATER formula %prec DIA
    """
    if p[1] == '[':
        syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
        p[0] = Modality('BOX', p[2], p[4], syntax)
    else:
        syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
        p[0] = Modality('DIA', p[2], p[4], syntax)

def p_formula_differential(p):
    """
    formula : LPAREN formula RPAREN PRIME
    """
    syntax = SyntaxInfo(p.lineno(4), p.lexpos(4))
    p[0] = Operator('DIFFERENTIAL', syntax, left = p[2])

def p_formula_arithmetic(p):
    """
    formula : term EQ term
            | term NEQ term
            | term GEQ term
            | term GREATER term
            | term LEQ term
            | term LESS term
    """
    syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
    p[0] = Operator(p[1], syntax, left = p[1], right = p[3])

def p_formula_value(p):
    """
    formula : TRUE
            | FALSE
    """
    if p[1] == 'true':
        syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
        p[0] = Variable(p[1], 'BOOLEAN', syntax)
    else:
        syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
        p[0] = Variable(p[1], 'BOOLEAN', syntax)

def p_term(p):
    """
    term :
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
    if p[3] == ')':
        syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
        p[0] = Function(p[1], 'CST_SYM', 'constant', syntax)
    else:
        syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
        p[0] = Function(p[1], 'FUNCTION', p[3].value, syntax)

def p_term_group(p):
    """
    term : LPAREN term RPAREN
         | LPAREN term COMMA term RPAREN
    """
    if p[3] == ',':
        if isinstance(p[2], Tree):
            p[2].programs.append(p[4])
        else:
            p[0] = Tree([p[2], p[4]])
    else:
        syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
        p[0] = Bracket('PAREN', p[2], syntax_info)

def p_differential(p):
    """
    term : term PRIME
         | LPAREN term RPAREN PRIME
    """
    if p[1] == '(':
        syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
        syntax_b = SyntaxInfo(p.lineno(1), p.lexpos(1))
        p[0] = Operator('DIFFERENTIAL', syntax, left = Bracket('PAREN',p[2],syntax_b))
    else:
        syntax = SyntaxInfo(p.lineno(4), p.lexpos(4))
        p[0] = Operator('DIFFERENTIAL', syntax, left = p[2])

def p_term_arithmetic(p):
    """
    term : term PLUS term
         | term MINUS term
         | term STAR term
         | term DIVIDE term
         | term POWER term
    """
    if p[2] == '/':
        if p[3] != 0:
            syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
            p[0] = Operator(p[2], syntax, left = p[1], right = p[3])
        else:
            raise  ZeroDivisionError("cannot divide by zero")
    elif p[2] == '+':
        syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
        p[0] = Operator(p[2], syntax, left = p[1], right = p[3])
    elif p[2] == '-':
        syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
        p[0] = Operator(p[2], syntax, left = p[1], right = p[3])
    elif p[2] == '*':
        syntax = SyntaxInfo(p.lineno(2), p.lexpos(2))
        p[0] = Operator(p[2], syntax, left = p[1], right = p[3])

def p_term_uminus(p):
    """
    term : MINUS term %prec UMINUS
    """
    p[2].value = '-' + p[2].value
    p[0] = p[2]

def p_term_numeric_value(p):
    """
    term : NUM
    """
    syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
    p[0] = Variable(p[1], 'NUMBER', syntax)

def p_term_value(p):
    """
    term : ID
    """
    syntax = SyntaxInfo(p.lineno(1), p.lexpos(1))
    p[0] = Variable(p[1], 'IDENTIFIER', syntax)

def p_error(p):
    print("p_error {}".format(p))
    raise TypeError("unknown text at %r" % (p.value))

parser = yacc.yacc()
