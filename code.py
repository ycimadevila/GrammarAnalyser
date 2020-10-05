from cmp.pycompiler import Symbol, NonTerminal, Terminal, EOF, Sentence, SentenceList, Epsilon, Production, Grammar, Item
from cmp.utils import pprint, inspect, ContainerSet
from pandas import DataFrame
from cmp.automata import State, multiline_formatter
import streamlit as st
from itertools import islice
import pydot


def compute_local_first(firsts, alpha):
    first_alpha = ContainerSet()
    
    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except:
        alpha_is_epsilon = False

    if alpha_is_epsilon:
        first_alpha.set_epsilon()

    else:
        for item in alpha:   
            first_alpha.update(firsts[item])
            if not firsts[item].contains_epsilon:
                break
        else:
            first_alpha.set_epsilon()

    # First(alpha)
    return first_alpha

def compute_firsts(G):
    firsts = {}
    change = True
    
    # init First(Vt)
    for terminal in G.terminals:
        firsts[terminal] = ContainerSet(terminal)
        
    # init First(Vn)
    for nonterminal in G.nonTerminals:
        firsts[nonterminal] = ContainerSet()
    
    while change:
        change = False
        
        # P: X -> alpha
        for production in G.Productions:
            X = production.Left 
            alpha = production.Right
            
            # get current First(X)
            first_X = firsts[X]
                
            # init First(alpha)
            try:
                first_alpha = firsts[alpha]
            except:
                first_alpha = firsts[alpha] = ContainerSet()
            
            # CurrentFirst(alpha)???
            local_first = compute_local_first(firsts, alpha)
            
            # update First(X) and First(alpha) from CurrentFirst(alpha)
            change |= first_alpha.hard_update(local_first)
            change |= first_X.hard_update(local_first)
                    
    # First(Vt) + First(Vt) + First(RightSides)
    return firsts

def compute_follows(G, firsts):
    follows = { }
    change = True
    
    local_firsts = {}
    
    # init Follow(Vn)
    for nonterminal in G.nonTerminals:
        follows[nonterminal] = ContainerSet()
    follows[G.startSymbol] = ContainerSet(G.EOF)
    
    while change:
        change = False
        
        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right
            
            follow_X = follows[X]
            
            # X -> zeta Y beta
            # First(beta) - { epsilon } subset of Follow(Y)
            # beta ->* epsilon or X -> zeta Y ? Follow(X) subset of Follow(Y)
           
            for i, symbol in enumerate(alpha):
                if symbol.IsNonTerminal:
                    follow_Y = follows[symbol]

                    try:
                        first_beta = local_firsts[alpha, i]
                    except KeyError:
                        first_beta = local_firsts[alpha, i] = compute_local_first(firsts, islice(alpha, i + 1, None))

                    change |= follow_Y.update(first_beta)

                    if first_beta.contains_epsilon:
                        change |= follow_Y.update(follow_X)

    # Follow(Vn)
    return follows

def metodo_predictivo_no_recursivo(G, M=None, firsts=None, follows=None):
    '''
    # checking table...
    if M is None:
        if firsts is None:
            firsts = compute_firsts(G)
        if follows is None:
            follows = compute_follows(G, firsts)
        M = build_parsing_table(G, firsts, follows)
    
    
    # parser construction...
    def parser(w):
        
        stack = [G.startSymbol]
        cursor = 0
        output = []
    
        while len(stack) > 0:

            top = stack.pop()
            a = w[cursor]

            if top.IsNonTerminal and (top, a) in M:
                current_value = M[top, a][0]
                print(current_value)
                #left = current_value.Left
                rigth = current_value.Right
                output.append(current_value)

                for item in reversed(rigth):
                    stack.append(item)

            elif a == top:
                cursor += 1

            else: 
                print("ERROR")
        
        
        # left parse is ready!!!
        return output
    
    # parser is ready!!!
    return parser
    '''
    
    # checking table...
    if M is None:
        if firsts is None:
            firsts = compute_firsts(G)
        if follows is None:
            follows = compute_follows(G, firsts)
        M = build_parsing_table(G, firsts, follows)
    
    dict ={}
    for t in G.terminals:
        dict[t.Name] = t
    
    # parser construction...
    def parser(w):
            
        id = 0
        stack = [(id,G.startSymbol)]
        d_tree = pydot.Dot(graph_type='graph', rankdir='TD', margin=0.1)
        d_tree.add_node(pydot.Node(name=id,shape='circle', label=str(G.startSymbol)))
        id+=1
        cursor = 0
        output = []
        while len(stack) > 0:

            id_current,top = stack.pop()
            try:
                a = dict[w[cursor]]
            except IndexError:
                pass

            if top.IsNonTerminal and (top, a) in M:
                current_value = M[top, a][0]
                print(current_value)
                #left = current_value.Left
                rigth = current_value.Right
                output.append(current_value)

                list_nodes = []
                for item in reversed(rigth):
                    stack.append((id,item))
                    list_nodes.append((id,item))
                    id+=1

                for i,item in reversed(list_nodes):
                    d_tree.add_node(pydot.Node(name=i,shape='circle', label=str(item)))
                    d_tree.add_edge(pydot.Edge(id_current,i))

            elif a == top:
                cursor += 1

            else: 
                print("ERROR")
        # left parse is ready!!!
        return output,d_tree

    # parser is ready!!!
    return parser

def build_parsing_table(G, firsts, follows):
    # init parsing table
    M = {}
    
    # P: X -> alpha
    for production in G.Productions:
        X = production.Left
        alpha = production.Right
  
        term = G.terminals
        term.append(G.EOF)

        for item in term:
            if item in firsts[alpha]:
                if (tuple([X, item]) in M and M[tuple([X, item])] == [production,]) or tuple([X, item]) not in M:
                    M[tuple([X, item])] = [production,]
                else:
                    st.error('La gramatica no es LL(1)')
                    return None
                    #raise EnvironmentError("Error de insercion en la tabla, problemas en la produccion: ", production, " Existe conflicto!")
        
            if firsts[alpha].contains_epsilon and (item in follows[X]):
                if (tuple([X, item]) in M and M[tuple([X, item])] == [production,]) or tuple([X, item]) not in M:
                    temp_container = ContainerSet()
                    temp_container.set_epsilon()
                    M[tuple([X, item])] = [production,]
                else:
                    st.error('La gramatica no es LL(1)')
                    return None
                    #raise EnvironmentError("Error de insercion en la tabla, problemas en la produccion: ", production, " Existe conflicto!")
                
      
    # parsing table is ready!!!
    return M  
