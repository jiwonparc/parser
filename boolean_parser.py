# Simple parser for a boolean expression using ply
# Return total numbers of values presented and the number of each True of False values

import ply.lex as lex
import ply.yacc as yacc
import sys

tokens = (
    'TRUE',
    'FALSE'
)

t_TRUE = r'True'

t_FALSE = r'False'

t_ignore = r' '

def t_error(t):
    raise TypeError("unknown text '%s', boolean expression expected" % (t.value,))

lex.lex()
'''
class Count(object):
    def __init__(self, value, count):
        self.value = value
        self.count = count
    def __repr__(self):
        return "Count(%r, %r)" % (self.value, self.count)
'''

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
    print("p_string ",p[0])

def p_expression(p):
    """
    expression : values_list value
    """
    p[0] = p[1] + [p[2]]
    print("p_expression {}".format(p[0]))

def p_values(p):
    "values_list : value"
    p[0] = [p[1]]
    print("p_values {}".format(p[0]))

def p_single_value(p):
    """
    value : TRUE
          | FALSE
    """
    p[0] = p[1]
    print("p_single_value {}".format(p[0]))


def p_error(p):
    print("p_error {}".format(p))
    raise TypeError("unknown text at %r" % (p.value))

parser = yacc.yacc()

while True:
    try:
        s = input('')
    except EOFError:
        break
    parser.parse(s)

import collections

def value_counts(s):
    """calculates the total number of values in the expression
    >>> value_counts('True True False')
    3
    """
    counts = collections.defaultdict(int)
    for value in yacc.parse(s):
        if value == 'True':
            counts['True'] += 1
        elif value == 'False':
            counts['False'] += 1
    return counts

def assert_raises(exc, f, *args):
    try:
        f(*args)
    except exc:
        pass
    else:
        raise AssertionError("Expected %r" % (exc,))

def test():
    assert value_counts("True True True") == {"True": 3}
    assert value_counts("True False False False") == {"True": 1, "False": 3}
    assert value_counts("") == {}
    assert value_counts("False False False False") == {"False": 4}
    assert_raises(TypeError, value_counts, "Blah")
    assert_raises(TypeError, value_counts, "10")
    assert_raises(TypeError, value_counts, "1C")

if __name__ == "__main__":
    test()
    print ("All tests passed.")
