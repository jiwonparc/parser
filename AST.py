class SyntaxInfo(object):
    """ Store the low level info of the node, like the line number and column """
    def __init__(self, line_number, column):
        self.line_number = line_number
        self.column = column

    def __str__(self):
        return "SyntaxInfo({},{})".format(self.line_number, self.column)

class Variable(object):
    """ representation of a variable node of the AST """
    def __init__(self, value, type, syntax_info):
        self.value = value
        self.type = type
        self.syntax_info = syntax_info

    def __str__(self):
        return "Variable({},{},{})".format(self.value, self.type, self.syntax_info)

class Operator(object):
    """ representation of an operator node of the AST """
    def __init__(self, type, syntax_info, left = None, right = None):
        self.type = type
        self.syntax_info = syntax_info
        self.left = left
        self.right = right

    def __str__(self):
        if self.right != None:
            return "Operator({},{},{},{})".format(self.type, self.syntax_info, self.left, self.right)
        else:
            return "Operator({},{},{})".format(self.type, self.syntax_info, self.left)

class Function(object):
    """ representation of a function node of the AST """
    def __init__(self, name, type, variable, syntax_info):
        self.name = name
        self.type = type
        self.variable = variable
        self.syntax_info = syntax_info

    def __str__(self):
        return "Function({},{},{},{})".format(self.name, self.type, self.variable, self.syntax_info)


class Assignment(object):
    """ representation of an assignment node of the AST """
    def __init__(self, name, value, syntax_info):
        self.name = name
        self.value = value
        self.syntax_info = syntax_info

    def __str__(self):
        return "Assignment({},{},{})".format(self.name, self.value, self.syntax_info)


class HybridModel(object):
    def __init__(self, expressions):
        self.expressions = expressions

    def __str__(self):
        return "HybridModel({})".format(self.expressions)
