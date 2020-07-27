# defining a class for AST
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

class Bracket(object):
    """ representation of brackets around the node """
    def __init__(self, type, expression, syntax_info):
        self.type = type
        self.expression = expression
        self.syntax_info = syntax_info

    def __str__(self):
        return "Bracket({},{})".format(self.type, self.expression)

class Modality(object):
    """ representation of an Modality node of the AST """
    def __init__(self, type, program, formula, syntax_info):
        self.type = type
        self.program = program
        self.formula = formula
        self.syntax_info = syntax_info

    def __str__(self):
        return "Modality({},{},{})".format(self.type, self.program, self.formula)

class Quantifier(object):
    """ representation of a quantifier node of the AST """
    def __init__(self, type, variable, formula, syntax_info):
        self.type = type
        self.variable = variable
        self.formula = formula
        self.syntax_info = syntax_info

    def __str__(self):

        return "Quantifier({},{},{})".format(self.name, self.value, self.syntax_info)

class Tree(object):
    def __init__(self, programs):
        self.programs = programs

    def __str__(self):
        return "Tree({})".format(self.programs)

# visitor pattern for the tree
class Visitor(object):
    def visit(self, node):
        if type(node) == Tree:
            tree = map(self.visit, node.programs)
            return (', '.join(tree))
        elif type(node) == Quantifier:
            return("{} {} {}".format(node.type, node.variable, self.visit(node.formula)))
        elif type(node) == Modality:
            if node.type == 'BOX':
                return("[{}] {}".format(node.program, self.visit(node.formula)))
            else:
                return("<{}> {}".format(node.program, self.visit(node.formula)))
        elif type(node) == Bracket:
            if node.type == 'PAREN':
                return("({})".format(self.visit(node.expression)))
            else:
                return("{"+self.visit(node.expression)+"}")
        elif type(node) == Assignment:
            if node.value == 'NONDASSIGNMENT':
                return("{} := *;".format(node.name))
            else:
                return("{} := {};".format(node.name, self.visit(node.value)))
        elif type(node) == Function:
            if node.type == 'CST_SYM':
                return(node.name + "()")
            else:
                return("{}({})".format(node.name, self.visit(node.variable)))
        elif type(node) == Operator:
            if node.type == 'REPETITION':
                return("{"+self.visit(node.left)+"}*")
            elif node.type == 'C_EVOLOUTION':
                return("{"+ self.visit(node.left) + " & "+ self.visit(node.right)+"}")
            elif node.type == 'CHOICE':
                return("{} ++ {}".format(self.visit(node.left), self.visit(node.right)))
            elif node.type == 'TEST':
                return("?{};".format(self.visit(node.left)))
            elif node.type == 'DIFFERENTIAL':
                if node.right != None:
                    return("{} '= {}".format(self.visit(node.left), self.visit(node.right)))
                else:
                    return(self.visit(node.left)+"'")
            elif node.type == '!':
                return("!{}".format(self.visit(node.left)))
            else:
                return("{} {} {}".format(self.visit(node.left), node.type, self.visit(node.right)))
        elif type(node) == Variable:
            return node.value
        else:
            return node
