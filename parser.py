from code import compute_firsts, compute_follows, build_parsing_table, compute_local_first, metodo_predictivo_no_recursivo
from cmp.pycompiler import Item
from cmp.utils import ContainerSet
from cmp.automata import State, multiline_formatter
from parser_utils import build_LR0_automaton, expand, compress, closure_lr1, goto_lr1, build_LR1_automaton,\
     build_LALR1_automaton, get_ll1_conflict_productions, get_shortest_terminals_derivation, terminals_string,\
         get_travel
import streamlit as st

class Parser:
    def __init__(self, G):
        self._G = G
        self._firsts = compute_firsts(G)
        self._follows = compute_follows(G, self._firsts)
        self._parse_table = self._build_parsing_table()
    
    @property
    def Firsts(self):
        return self._firsts

    @property
    def Follows(self):
        return self._follows

    @property
    def Table(self):
        return self._parse_table

    def _build_parsing_table(self):
        return NotImplementedError()

    def _get_conflict_string(self):
        pass

class LL1Parser(Parser):
    def _build_parsing_table(self):
        G = self._G
        firsts = self._firsts
        follows = self._follows
        
        # init parsing table
        M = {}
        
        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right
    
            term = [item for item in G.terminals]
            term.append(G.EOF)

            for item in term:
                if item in firsts[alpha]:
                    if (tuple([X, item]) in M and M[tuple([X, item])] == [production,]) or tuple([X, item]) not in M:
                        M[tuple([X, item])] = [production,]
                    else:
                        M[tuple([X, item])].append(production)
                        
                if firsts[alpha].contains_epsilon and (item in follows[X]):
                    if (tuple([X, item]) in M and M[tuple([X, item])] == [production,]) or tuple([X, item]) not in M:
                        temp_container = ContainerSet()
                        temp_container.set_epsilon()
                        M[tuple([X, item])] = [production,]
                    else:
                        M[tuple([X, item])].append(production)

        # parsing table is ready!!!
        return M   

    def _get_conflict_string(self):
       
        G = self._G
        res = get_travel(G, get_ll1_conflict_productions(self.Table)[0])
        dic, eps = get_shortest_terminals_derivation(G)
        conflict_string = [G.startSymbol, ]
        
        while not terminals_string(conflict_string):
            new_confl_string = []
            if len(res) > 0:
                temp = [i for i in conflict_string]
                for item in temp:
                    if item in res:
                        index = (res[item])
                        product = G.nonTerminals[G.nonTerminals.index(item)].productions
                        for i in product[index].Right:
                            new_confl_string.append(i)
                        del res[item]
                    else:
                        new_confl_string.append(item)
                conflict_string = new_confl_string
            else:
                for item in conflict_string:
                    if item.IsTerminal:
                        new_confl_string.append(item)
                    elif item in eps:
                        continue
                    else:
                        try:
                            for i in dic[item]:
                                new_confl_string.append(i)
                        except KeyError:
                            for pr in G.nonTerminals[G.nonTerminals.index(item)].productions:
                                left, right = pr
                                if left not in right:
                                    for r in right:
                                        new_confl_string.append(r)
                conflict_string = new_confl_string
        return conflict_string




    def __call__(self, w): 
        return metodo_predictivo_no_recursivo(self._G, self.Table, self.Firsts, self.Follows)(w)

class ShiftReduceParser(Parser):
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'
    
    def __init__(self, G, verbose=False):
        self.G = G
        self._augmented_grammar = G.AugmentedGrammar(True)
        self._firsts = compute_firsts(self._augmented_grammar)
        self._follows = compute_follows(G, self._firsts)
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()
    
    def _build_parsing_table(self):
        raise NotImplementedError()
    
    def Table(self):
        pass
    def automaton(self):
        pass

 
class SLR1Parser(ShiftReduceParser):
    
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        #firsts = self.Firsts
        follows = self.Follows
        
        automaton = build_LR0_automaton(G).to_deterministic()
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for state in node.state:
                item = state.state
                left, _ = item.production
                
                symbol = item.NextSymbol
                if item.IsReduceItem:
                    if left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), (self.OK, 0))
                    else: 
                        for symb in follows[left]:
                            self._register(self.action, (idx, symb), (self.REDUCE, item))
                else:
                    next_trans = node[symbol.Name][0]
                    if symbol.IsTerminal:
                        self._register(self.action, (idx, symbol), (self.SHIFT, next_trans.idx))
                       
                    elif symbol.IsNonTerminal:
                        self._register(self.goto, (idx, symbol), next_trans.idx)
    
    def __call__(self, w):
        stack = [ 0 ]
        cursor = 0
        output = []
        
        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, '<---||--->', w[cursor:])
                
            # Your code here!!! (Detect error)
            #assert state, lookahead in self.action
            
            action, tag = self.action[state, lookahead]

            # Your code here!!! (Shift case)
            if action == self.SHIFT:
                cursor += 1
                stack.append(tag)

            # Your code here!!! (Reduce case)
            elif action == self.REDUCE:
                for _ in range(len(tag.production.Right)):
                    stack.pop()
                h = stack[-1]
                #assert h, tag.production.Left in self.goto
                stack.append(self.goto[h, tag.production.Left])
                output.append(tag.production)

            # Your code here!!! (OK case)
            elif action == self.OK:
                return output

            # Your code here!!! (Invalid case)
            else:
                assert False, 'patapum'

    def automaton(self):
        return build_LR0_automaton(self.G).graph()
    
    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value

class LR1Parser(ShiftReduceParser):

    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        
        automaton = build_LR1_automaton(G, self.Firsts)
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                left, _ = item.production
                symbol = item.NextSymbol
                
                if item.IsReduceItem:
                    if left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), (self.OK, 0))

                        # if (idx, G.EOF) not in self.action or self.action[(idx, G.EOF)] == (self.OK, 0):
                        #     st.error('Shift-Reduce or Reduce-Reduce conflict!!!')
                        #     return
                        # self.action[(idx, G.EOF)] = (self.OK, 0)
                    else: 
                        for symb in item.lookaheads:
                            self._register(self.action, (idx, symb), (self.REDUCE, item.production))

                            # if (idx, symb) not in self.action or self.action[(idx, symb)] == (self.REDUCE, item.production):
                            #     st.error('Shift-Reduce or Reduce-Reduce conflict!!!')
                            #     return
                            # self.action[(idx, symb)] = (self.REDUCE, item.production)
                else:
                    next_trans = node[symbol.Name][0]
                    if symbol.IsTerminal:
                        self._register(self.action, (idx, symbol), (self.SHIFT, next_trans.idx))
                       
                        # if (idx, symb) not in self.action or self.action[(idx, symb)] == (self.SHIFT, next_trans.idx):
                        #     st.error('Shift-Reduce or Reduce-Reduce conflict!!!')
                        #     return
                        # self.action[(idx, symb)] = (self.SHIFT, next_trans.idx)
                    
                    elif symbol.IsNonTerminal:  
                        self._register(self.goto, (idx, symbol), next_trans.idx)

                        # if (idx, symb) not in self.goto or self.goto[(idx, symb)] == next_trans.idx:
                        #     st.error('Shift-Reduce or Reduce-Reduce conflict!!!')
                        #     return
                        # self.goto[(idx, symb)] = next_trans.idx
    
    def __call__(self, w):
        stack = [ 0 ]
        cursor = 0
        output = []
        
        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, '<---||--->', w[cursor:])
                
            # Your code here!!! (Detect error)
            #assert state, lookahead in self.action
            
            action, tag = self.action[state, lookahead]

            # Your code here!!! (Shift case)
            if action == self.SHIFT:
                cursor += 1
                stack.append(tag)

            # Your code here!!! (Reduce case)
            elif action == self.REDUCE:
                for _ in range(len(tag.Right)):
                    stack.pop()
                h = stack[-1]
                #assert h, tag.production.Left in self.goto
                stack.append(self.goto[h, tag.Left])
                output.append(tag)

            # Your code here!!! (OK case)
            elif action == self.OK:
                return output

            # Your code here!!! (Invalid case)
            else:
                assert False, 'patapum'

    def automaton(self):
        return build_LR1_automaton(self.G, self.Firsts).graph()

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value

class LALR1Parser(ShiftReduceParser):
    
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        
        automaton = build_LALR1_automaton(G, self._firsts)
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                left, _ = item.production
                symbol = item.NextSymbol
                
                if item.IsReduceItem:
                    if left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), (self.OK, 0))
                    else: 
                        for symb in item.lookaheads:
                            self._register(self.action, (idx, symb), (self.REDUCE, item.production))
                else:
                    next_trans = node[symbol.Name][0]
                    if symbol.IsTerminal:
                        self._register(self.action, (idx, symbol), (self.SHIFT, next_trans.idx))
                       
                    elif symbol.IsNonTerminal:
                        self._register(self.goto, (idx, symbol), next_trans.idx)
    
    def __call__(self, w):
        stack = [ 0 ]
        cursor = 0
        output = []
        
        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, '<---||--->', w[cursor:])
                
            # Your code here!!! (Detect error)
            #assert state, lookahead in self.action
            
            action, tag = self.action[state, lookahead]

            # Your code here!!! (Shift case)
            if action == self.SHIFT:
                cursor += 1
                stack.append(tag)

            # Your code here!!! (Reduce case)
            elif action == self.REDUCE:
                for _ in range(len(tag.Right)):
                    stack.pop()
                h = stack[-1]
                #assert h, tag.production.Left in self.goto
                stack.append(self.goto[h, tag.Left])
                output.append(tag)

            # Your code here!!! (OK case)
            elif action == self.OK:
                return output

            # Your code here!!! (Invalid case)
            else:
                assert False, 'patapum'

    def automaton(self):
        return build_LALR1_automaton(self.G, self.Firsts).graph()

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value
