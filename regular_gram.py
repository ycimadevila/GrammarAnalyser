from cmp.pycompiler import Grammar
from automata import DFA ,NFA, nfa_to_dfa

def is_regular(G):
    for prod in G.Productions:
        left,right = prod
        if right == G.Epsilon and left != G.startSymbol:
            return False
        l=len(right)
        if right!=G.Epsilon and right._symbols[0].IsNonTerminal or (l>2 and right._symbols[1].IsTerminal):
           return False
    return True

def build_automaton_regular_grammar(G):
    no_state = 0
    states = {}   
    finals_states = []
    transitions = {} 
    state_name = {}
    for non_term in G.nonTerminals:
        for prod in non_term.productions:
            left,right=prod
            try:
                state_left = states[left]
            except KeyError:
                state_left = states[left] = no_state 
                state_name[no_state] = str(left)
                no_state+=1
            l = len(right)
            if l == 1 or right == G.Epsilon:
                new_state = no_state
                state_name[no_state] = ' '
                no_state+=1
                finals_states.append(new_state)
                try:
                    transitions[(state_left,str(right))].append(new_state)
                except KeyError:
                    transitions[(state_left,str(right))] = [new_state]
            elif l == 2:
                nt = right._symbols[1]
                try:
                    right_state = states[nt]
                except KeyError:
                    right_state =states[nt] = no_state
                    state_name[no_state] = str(nt)
                    no_state+=1 
                try:
                    transitions[(state_left,str(right._symbols[0]))].append(right_state)
                except KeyError:
                    transitions[(state_left,str(right._symbols[0]))] = [right_state]
    nfa = NFA(no_state ,finals_states,transitions,state_name, states[G.startSymbol])
    dfa = nfa_to_dfa(nfa)
    return dfa

def dfa_to_regex(G,dfa):
    transitions = dfa.transitions
    new_start,new_final,transitions = add_epsilon_transitions(G,transitions,dfa.start,dfa.states,dfa.finals)
    finals = [new_final]
    new_dict = {}#dict[orig,dest] = symbol_transition
    self_transitions = {}#dict[state] = reg_exp
    for key,value in transitions.items(): #build_new dict
        try:
            new_dict[(key[0],value[0])].append(key[1])
        except KeyError:
            new_dict[(key[0],value[0])] = [key[1]]
    for key,value in new_dict.items():
        origen_state = key[0]
        dest_state = key[1]
        reg_exp = str(value[0])
        #transiciones con mas de un simbolo entre dos estados[orig,dest]
        reg_exp = '+'.join([str(i) for i in value]) 
        if(len(value))>1: 
            reg_exp = '('+ reg_exp +')'
        new_dict[key] = reg_exp
        if origen_state == dest_state:
            self_transitions[origen_state] = reg_exp
    
    for state in range(0,dfa.states):
        if state not in finals: 
            _in,_out=build_path(state,new_dict)
            #in = [(orig_state,symbol_transition)]
            #out = [(dest_state,symbol_transition)]
            for in_t in _in:
                in_orig,in_symbol = in_t
                for out_t in _out:
                    #orig-state-dest
                    out_dest,out_symbol = out_t
                    regex = in_symbol
                    if regex == str(G.Epsilon):
                        regex =''
                    if state in self_transitions.keys():
                        regex+= self_transitions[state] + '*'
                    if str(out_symbol) != str(G.Epsilon):
                        regex+= out_symbol
                    if (in_orig,out_dest) in new_dict.keys():
                        if regex!='':
                            new_dict[(in_orig,out_dest)] = '('+regex +'+'+ new_dict[(in_orig,out_dest)]+')'
                    else:
                        if regex!='':
                            new_dict[(in_orig,out_dest)] = regex
                            if in_orig == out_dest:
                                self_transitions[in_orig] = regex
            for i in _in:
                try:
                    new_dict.pop((i[0],state))
                except:
                    pass
            for o in _out:
                try:
                    new_dict.pop((state,o[0]))
                except:
                    pass
    return new_dict[(new_start,new_final)]

def build_path(state,new_dict):
    in_transitions = []
    out_transitions = []
    for key,value in new_dict.items():
        orig_state = key[0]
        dest_state = key[1]
        symbol_transition = value
        if dest_state == state:
            in_transitions.append((orig_state,symbol_transition))
        elif orig_state == state:
            out_transitions.append((dest_state,symbol_transition))
    return in_transitions,out_transitions

def add_epsilon_transitions(G,transitions,init_state,states,finals):
    new_start = states 
    new_final = new_start + 1
    new_transitions={}
    new_transitions[(new_start,str(G.Epsilon))] = [init_state]
    for state in finals:
        try:
            new_transitions[(state,str(G.Epsilon))].append(new_final)
        except:
            new_transitions[(state,str(G.Epsilon))] = [new_final]
    for state_orig,dict_t in transitions.items():
        for symbol,state_dest in dict_t.items():
            new_transitions[(state_orig,symbol)] = state_dest
    return new_start,new_final,new_transitions


def build_new_grammar(G,non_terminals,terminals,productions):
    G.non_terminals = non_terminals
    G.terminals = terminals
    for prod in productions:
        G.AddProductions(prod)

################################################################### 
def parser_terminal(terminals):
    _t = terminals.split('\n')
    temp = ''
    for t in _t:
        t = t.split()
        temp += str(t[0]) + ' '
    result = ''
    for t in range(0, len(temp)- 1):
        result += temp[t]
    return result

def get_inst(term, non_term, gramm):
    inst = []
    _non_term = non_term

    inst.append(f'{non_term[0]} = G.NonTerminal(\'{non_term[0]}\', True)')

    _non_term.remove(_non_term[0])
    __nt = ' '.join(_non_term)
    _nt = ', '.join(_non_term)
    _t = ', '.join(term.split())
    
    if len(__nt) == 1:
        inst.append(f'{_nt} = G.NonTerminal(\'{__nt}\')')
    elif len(__nt) > 1:
        inst.append(f'{_nt} = G.NonTerminals(\'{__nt}\')')

    inst.append(f'{_t} = G.Terminals(\'{term}\')')

    
    inst.append(f'{gramm}')

    return inst

#####################################################################
