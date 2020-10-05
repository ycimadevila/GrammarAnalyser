#from code import ContainerSet
from cmp.utils import ContainerSet

import pydot

###############
#  AUTOMATAS  #
###############

#Automata No Determinista
class NFA:
    def __init__(self, states, finals, transitions,state_name, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = { state: {} for state in range(states) }
        self.state_name = state_name
        
        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)
            
        self.vocabulary.discard('')
        
    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return ()
            
    def graph(self):
        G = pydot.Dot(rankdir='LR', margin=0.1)
        G.add_node(pydot.Node('start', shape='plaintext', label=self.state_name[self.start], width=0, height=0))

        for (start, tran), destinations in self.map.items():
            tran = 'ε' if tran == '' else tran
            G.add_node(pydot.Node(start, shape='circle', style='bold' if start in self.finals else '',label=self.state_name[start]))
            for end in destinations:
                G.add_node(pydot.Node(end, shape='circle', style='bold' if end in self.finals else '',label=self.state_name[end]))
                G.add_edge(pydot.Edge(start, end, label=tran, labeldistance=2))

        G.add_edge(pydot.Edge('start', self.start, label='', style='dashed'))
        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except:
            pass


#Automata Determinista
class DFA(NFA):
    
    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)
        
        transitions = { key: [value] for key, value in transitions.items() }
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start
        
    def _move(self, symbol):
        result = True
        try:
            self.current = self.transitions[self.current][symbol][0]
        except:
            result = False
        return result
    
    def _reset(self):
        self.current = self.start
        
    def recognize(self, string):
        self._reset()
        for st in string:
            if not self._move(st):
                return False
        return self.current in self.finals


def move(automaton, states, symbol):
    moves = set()
    for state in states:
        try:
            value = automaton.transitions[state][symbol]
            for v in value:
                moves.add(v)
        except KeyError:
            pass
    return moves


def epsilon_closure(automaton, states):
    pending = [ s for s in states ] # equivalente a list(states) pero me gusta así :p
    closure = { s for s in states } # equivalente a  set(states) pero me gusta así :p
    
    while pending:
        state = pending.pop()
        eps = automaton.epsilon_transitions(state)
        for var in eps:
            pending.append(var)
            closure.add(var)
                
    return ContainerSet(*closure)


def nfa_to_dfa(automaton):
    transitions = {}
    
    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [ start ]

    pending = [ start ]
    while pending:
        state = pending.pop()
        
        for symbol in automaton.vocabulary:
            sub_state = move(automaton, state, symbol)
            new_state = epsilon_closure(automaton, sub_state)
            try:
                transitions[state.id, symbol]
                assert False, 'Invalid DFA!!!'
            except KeyError:
                if new_state != set():
                    try:
                        s = next(v for v in states if v == new_state)  
                        transitions[state.id, symbol] = s.id
                    except StopIteration:
                        new_state.is_final = any(s in automaton.finals for s in new_state)
                        new_state.id = states[-1].id + 1
                        transitions[state.id, symbol] = new_state.id
                        states.append(new_state)
                        pending.append(new_state)

    finals = [ state.id for state in states if state.is_final ]
    dfa = DFA(len(states), finals, transitions,automaton.state_name)
    return dfa


#############################
# OPERACIONES CON AUTOMATAS #
#############################

def automata_union(a1, a2):
    transitions = {}
    
    start = 0
    d1 = 1
    d2 = a1.states + d1
    final = a2.states + d2
    
    for (origin, symbol), destinations in a1.map.items():
        ## Relocate a1 transitions ...
        transitions[(d1 + origin, symbol)] = [f + d1 for f in destinations]

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        transitions[(d2 + origin, symbol)] = [f + d2 for f in destinations]
    
    ## Add transitions from start state ...
    transitions[(start, '')] = [a1.start + d1, a2.start + d2]
    
    ## Add transitions to final state ...
    for f in a1.finals:
            transitions[(f + d1, '')] = [final]
    for f in a2.finals:
            transitions[(f + d2, '')] = [final]
            
    states = a1.states + a2.states + 2
    finals = { final }
    
    return NFA(states, finals, transitions, start)


def automata_concatenation(a1, a2):
    transitions = {}
    
    start = 0
    d1 = 0
    d2 = a1.states + d1
    final = a2.states + d2
    
    for (origin, symbol), destinations in a1.map.items():
        transitions[(d1 + origin, symbol)] = [f + d1 for f in destinations]

    for (origin, symbol), destinations in a2.map.items():
        transitions[(d2 + origin, symbol)] = [f + d2 for f in destinations]
    
    ## Add transitions to final state ...
    for f in a1.finals:
        transitions[(f + d1, '')] = [a2.start + d2]     
    for f in a2.finals:
        transitions[(f + d2, '')] = [final]        
            
    states = a1.states + a2.states + 1
    finals = { final }
    
    return NFA(states, finals, transitions, start)


def automata_closure(a1):
    transitions = {}
    
    start = 0
    d1 = 1
    final = a1.states + d1
    
    for (origin, symbol), destinations in a1.map.items():
        ## Relocate automaton transitions ...
        transitions[(origin + d1, symbol)] = [item + d1 for item in destinations]
    
    ## Add transitions from start state ...
    transitions[(start, '')] = [a1.start + d1]
    
    ## Add transitions to final state and to start state ...
    for f in a1.finals:
        transitions[(f + d1, '')] = [final, start]
    
    transitions[(final, '')] = [a1.start + d1]
    transitions[(start, '')] = [final] 
    
    states = a1.states +  2
    finals = { final }
    
    return NFA(states, finals, transitions, start)


def distinguish_states(group, automaton, partition):
    split = {}
    
    vocabulary = tuple(automaton.vocabulary)
    
    for item in group:
        
        trans = automaton.transitions[item.value]

        elem = []
        for value in vocabulary:
            if value in trans:
                elem.append(trans[value][0])
            
        part = []
        for value in elem:
            if value in partition.nodes:
                part.append(partition[value].representative)
             
        part = tuple(part)
        
        try:
            split[part].append(item.value)
        except KeyError:
            split[part] = [item.value]
            
    return[val for val in split.values()]


def state_minimization(automaton):
    
    partition = DisjointSet(*range(automaton.states))
    
    #mezclo finales
    partition.merge(s for s in automaton.finals)
    
    #mezclo los no finales
    partition.merge(s for s in range(automaton.states)if s not in automaton.finals)

    while True:
        new_partition = DisjointSet(*range(automaton.states))
        
        for group in partition.groups:
            distinguish = distinguish_states(group, automaton, partition)
            
            for item in distinguish:
                new_partition.merge(item)
               
        if len(new_partition) == len(partition):
            break
            
        partition = new_partition
            
    return partition


def automata_minimization(automaton):
    partition = state_minimization(automaton)
    states = [s for s in partition.representatives]
    
    transitions = {}
    
    for i, state in enumerate(states):
        origin = state.value
        
        for symbol, destinations in automaton.transitions[origin].items():
            value = partition[destinations[0]].representative
            result = states.index(value)
            
            try:
                transitions[i, symbol]
                assert False
            except KeyError:
                transitions[i, symbol] = result
    
    finals = [i for i,state in enumerate(states)if state.value in automaton.finals]
    start = states.index(partition[automaton.start].representative)
    
    return DFA(len(states), finals, transitions, start)


