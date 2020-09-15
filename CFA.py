# when there is a node connecting two edges
# i being the index of the inital node and j being the index of the destination node
# transition map, tm[i][j] is the list provide all the different
# actions that connects the initial and the destination node
# default [0] for not connected nodes
# when there is a connection without any action required then have [1]
class CFA(object):
    # representation of CFA
    def __init__(self, end, transistions, transition_map, start = 0, error_states = []):
        self.start = start
        self.end = end
        self.transistions = transistions
        self.transition_map = transition_map
        self.error_states = error_states

    def add_transition(self, initial_node, transition, destination_node):
        self.transistions[initial_node][destination_node].append(transition)

    def del_transition(self, initial_node, transition, destination_node):
        if transition in self.transistions[initial_node][destination_node]:
            self.transistions[initial_node][destination_node].remove(transition)

    def add_transition_map(self, tm):
        end2 = tm.shape[0]
        tmap = np.zeros((self.end+end2, self.end+end2, 1),'U20')
        tmap[:self.end+1,:self.end+1,0] = self.transition_map
        tmap[self.end+1:,self.end+1:,0] = tm
        tmap[sef.end, self.end+1, 0] = '1'
        self.transition_map = tm
