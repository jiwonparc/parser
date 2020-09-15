from parser import*
from CFA import*
import numpy as np

# have a look at the Visitor class in AST file to see what kind of classes has to be translated
# when assigning the datatype for the np array 'U20' is used
# to support a string of length up to 20
def translate_operator(op):
    operation = Transition(Visitor().visit(op))
    tm = np.zeros((2,2,1), 'U20')
    tm[0,1,0] = operation
    return CFA(1, [operation], tm)

def translate_assignment(a):
    assignment = Transition(Visitor().visit(a))
    tm = np.zeros((2,2,1), 'U20')
    tm[0,1,0] = assignment
    return CFA(1, [assignment], tm)

def translate_dprograms(dp):
    l = len(dp.programs)
    programs = []
    for dp in dp.programs:
        programs.append(Visitor().visit(dp))
    tm = np.zeros((l+1, l+1, 1), 'U20')
    for i in range(l):
        tm[i, i+1, 0] = programs[i]
    return CFA(l, programs, tm)


# all the translate function from here is assuming that the basic case has been turned into CFA already
def translate_tree(t):
    programs = []
    for prog in t.programs:
        if type(prog) == Tree:
            for p in prog.programs:
                programs.append(p)
        else:
            programs.append(prog)
    l = len(programs)
    for i in range(len(programs)):
        programs[i] = Visitor().visit(programs[i])
    tm = np.zeros((l+1, l+1, 1), 'U20')
    for i in range(l):
        tm[i, i+1, 0] = programs[i]
    return CFA(l, programs, tm)

# dia modality has to be written
def translate_modality(m):
    prog = m.program
    formula = m.formula
    notformula = "!({})".format(Visitor().visit(formula))
    prog = translate_program(prog)
    formula = translate_formula(formula)
    if m.type == 'BOX':
        end1, t1, tm1, err1 = prog.end, prog.transitions, prog.transition_map, prog.error_states
        end2, r2, tm2, err2 = formula.end, formula.transitions, formula.transition_map, formula.error_states
        if err1:
            if err2:
                err = err1 + err2
            err = err1
        elif err2:
            err = err2
        if err:
            err.append(end1+end2+1)
        else:
            err = [end1+end2+1]
        modal = (end1+end2+2, t1+t2+notformula, tm1, err)
        modal.add_transition_map(tm1)
        tm = np.zeros((modal.end+1,modal.end+1,1), 'U20')
        tm[:modal.end+1,:modal.end+1,0] = modal.transition_map
        tm[end1,end1+end2+1,0] = notformula
        modal.transition_map = tm
        return modal
    elif m.type == 'DIA':
        pass

# function has to be written
def translate_quantifier(q):
    pass

# transition map has to be made
def translate_seq(sequential):
    transistions = []
    for p in sequential.programs:
        transistions.append(p)
    end = len(transistions)
    tm = []
    return CFA(end, transistions, tm)

def translate_choice(P1, P2):
    end1, t1, tm1, err1 = P1.end, P1.transitions, P1.transition_map, P1.error_states
    end2, t2, tm2, err2 = P2.end, P2.transitions, P2.transition_map, P2.error_states
    if err1:
        if err2:
            err = err1 + err2
        err = err1
    elif err2:
        err = err2
    choice = CFA(end1+end2, t1+t2, tm1, err)
    choice.add_transition_map(tm2)
    choice.transition_map[0,end1+1,0] = '1'
    return choice


def translate_repetition(r):
    return r.add_transition(r.end, Transition('REPETITION'), r.start)

# continuous evolution is considered as a basic case for now
def translate_c_evolution(c):
    ce = Transition(Visitor().visit(c))
    tm = np.zeros((2,2,1), 'U20')
    tm[0,1,0] = ce
    return CFA(1, [ce], tm)

# for the translate functions, cod has to be modified to be recursive
def translate_term(t):
    if type(t) == Bracket:
        return translate_term(t.expression)
    elif type(t) == Operator:
        return translate_operator(t)
    elif type(t) == Quantifier:
        return translate_quantifier(t)
    elif type(t) == Modality:
        return translate_modality(t)

def translate_program(p):
    while p:
        if type(p) == Tree:
            return translate_tree(p)
        if type(p) == Bracket:
            return translate_program(p.expression)
        if p.type == 'Assignment':
            return translate_assignment(p)
        elif p.type == 'TEST':
            return translate_operator(p)
        elif type(p) == Tree:
            return translate_tree(p)
        elif p.type == 'CHOICE':
            return translate_choice(p)
        elif p.type == 'REPET':
            return translate_repetition(p)
        elif p.type == 'C_EVOLOUTION':
            return translate_c_evolution(p)
