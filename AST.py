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

    def __eq__(self, object):
        return self.value == object.value and self.type == object.type

class Operator(object):
    """ representation of an operator node of the AST """
    def __init__(self, type, syntax_info, left = None, right = None):
        self.type = type
        self.syntax_info = syntax_info
        self.left = left
        self.right = right

    def __str__(self):
        if self.right:
            return "Operator({},{},{},{})".format(self.type, self.syntax_info, self.left, self.right)
        else:
            return "Operator({},{},{})".format(self.type, self.syntax_info, self.left)

    def __eq__(self, object):
        if self.type == object.type:
            if self.left == object.left:
                if self.right:
                    if self.right == object.right:
                        return True
        return False

class Function(object):
    """ representation of a function node of the AST """
    def __init__(self, name, type, variable, syntax_info):
        self.name = name
        self.type = type
        self.variable = variable
        self.syntax_info = syntax_info

    def __str__(self):
        return "Function({},{},{},{})".format(self.name, self.type, self.variable, self.syntax_info)

    def __eq__(self, object):
        if self.name == object.name:
            if self.type == object.type:
                if self.variable == object.variable:
                    return True
        return False


class Assignment(object):
    """ representation of an assignment node of the AST """
    def __init__(self, name, value, syntax_info):
        self.name = name
        self.value = value
        self.syntax_info = syntax_info

    def __str__(self):
        return "Assignment({},{},{})".format(self.name, self.value, self.syntax_info)

    def __eq__(self, object):
        return self.name == object.name and self.value == object.value


class Bracket(object):
    """ representation of brackets around the node """
    def __init__(self, type, expression, syntax_info):
        self.type = type
        self.expression = expression
        self.syntax_info = syntax_info

    def __str__(self):
        return "Bracket({},{})".format(self.type, self.expression)

    def __eq__(self,object):
        return self.type == object.type and self.expression == object.expression

class Modality(object):
    """ representation of an Modality node of the AST """
    def __init__(self, type, program, formula, syntax_info):
        self.type = type
        self.program = program
        self.formula = formula
        self.syntax_info = syntax_info

    def __str__(self):
        return "Modality({},{},{})".format(self.type, self.program, self.formula)

    def __eq__(self, object):
        if self.type == object.type:
            if self.program == object.program:
                if self.formula == object.formula:
                    return True
        return False

class Quantifier(object):
    """ representation of a quantifier node of the AST """
    def __init__(self, type, variable, formula, syntax_info):
        self.type = type
        self.variable = variable
        self.formula = formula
        self.syntax_info = syntax_info

    def __str__(self):
        return "Quantifier({},{},{})".format(self.name, self.value, self.syntax_info)

    def __eq__(self):
        if self.type == object.type:
            if self.variable == object.variable:
                if self.formula == object.formula:
                    return True
        return False

class DifferentialProgram(object):
    """ representation of a differential program node of the AST """
    def __init__(self, programs):
        self.programs = programs

    def __str__(self):
        return "DifferentialProgram({})".format(self.programs)

    def __eq__(self, object):
        res = True
        for i in range(len(self.programs)):
            res = res and (self.programs[i] == object.programs[i])
        return res

class Tree(object):
    def __init__(self, programs):
        self.programs = programs

    def __str__(self):
        return "Tree({})".format(self.programs)

    def __eq__(self, object):
        res = True
        for i in range(len(self.programs)):
            res = res and (self.programs[i] == object.programs[i])
        return res

# visitor pattern for the tree
class Visitor(object):
    def visit(self, node):
        if type(node) is Tree:
            tree = map(self.visit, node.programs)
            return(' '.join(tree))
        elif type(node) is DifferentialProgram:
            dp = map(self.visit, node.programs)
            return(', '.join(dp))
        elif type(node) is Quantifier:
            return("{} {} {}".format(node.type, node.variable, self.visit(node.formula)))
        elif type(node) is Modality:
            if node.type is 'BOX':
                return("[{}] {}".format(node.program, self.visit(node.formula)))
            else:
                return("<{}> {}".format(node.program, self.visit(node.formula)))
        elif type(node) is Bracket:
            if node.type is 'PAREN':
                return("({})".format(self.visit(node.expression)))
            else:
                return("{"+self.visit(node.expression)+"}")
        elif type(node) is Assignment:
            if node.value is 'NONDASSIGNMENT':
                return("{} := *;".format(node.name))
            else:
                return("{} := {};".format(node.name, self.visit(node.value)))
        elif type(node) is Function:
            if node.type is 'CST_SYM':
                return(node.name + "()")
            else:
                return("{}({})".format(node.name, self.visit(node.variable)))
        elif type(node) is Operator:
            if node.type is 'REPETITION':
                return("{"+self.visit(node.left)+"}*")
            elif node.type is 'C_EVOLOUTION':
                return("{"+ self.visit(node.left) + " & "+ self.visit(node.right)+"}")
            elif node.type is 'CHOICE':
                return("{} ++ {}".format(self.visit(node.left), self.visit(node.right)))
            elif node.type is 'TEST':
                return("?{};".format(self.visit(node.left)))
            elif node.type is 'DIFFERENTIAL':
                if node.right:
                    return("{} '= {}".format(self.visit(node.left), self.visit(node.right)))
                else:
                    return(self.visit(node.left)+"'")
            elif node.type is 'DIFF_ASSIGN':
                return("{} := {};".format(self.visit(node.left), self.visit(node.right)))
            elif node.type is '!':
                return("!{}".format(self.visit(node.left)))
            else:
                return("{} {} {}".format(self.visit(node.left), node.type, self.visit(node.right)))
        elif type(node) is Variable:
            return node.value
        else:
            return node
