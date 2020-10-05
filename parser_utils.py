from cmp.automata import State, multiline_formatter
from cmp.pycompiler import Item
from cmp.utils import ContainerSet
from code import compute_local_first
import pydot




def build_LR0_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0)

    automaton = State(start_item, True)
    pending = [ start_item ]
    visited = { start_item: automaton }
    
    while pending:
        current_item = pending.pop()
        if current_item.IsReduceItem:
            continue
        
        next_item = current_item.NextItem()
        symbol = current_item.NextSymbol
        
           
        try:
            visited[current_item].add_transition(symbol.Name, visited[next_item])
        except:
            visited[next_item] = State(next_item, True)
            visited[current_item].add_transition(symbol.Name, visited[next_item])
            pending.append(next_item)
            
        if symbol.IsNonTerminal:
            prod = symbol.productions
            for p in prod:
                item = Item(p, 0)
                try:
                    visited[current_item].add_epsilon_transition(visited[item])
                except KeyError:
                    visited[item] = State(item, True)
                    visited[current_item].add_epsilon_transition(visited[item])
                    pending.append(item)
                
    return automaton

def expand(item, firsts):
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []
    lookaheads = ContainerSet()
    for prev in item.Preview():
        new_first = compute_local_first(firsts, prev)
        lookaheads.update(new_first)
    
    assert not lookaheads.contains_epsilon
    result = []
    for prod in next_symbol.productions:
        result.append(Item(prod,0,lookaheads))
        
    return result

def compress(items):
    centers = {}

    for item in items:
        center = item.Center()
        try:
            lookaheads = centers[center]
        except KeyError:
            centers[center] = lookaheads = set()
        lookaheads.update(item.lookaheads)
    
    return { Item(x.production, x.pos, set(lookahead)) for x, lookahead in centers.items() }

def closure_lr1(items, firsts):
    closure = ContainerSet(*items)
    changed = True
    while changed:
        changed = False
        new_items = ContainerSet()
        for item in closure:
            exp = expand(item, firsts)
            new_items.extend(exp)
            
        changed = closure.update(new_items)
    return compress(closure)

def goto_lr1(items, symbol, firsts=None, just_kernel=False):
    assert just_kernel or firsts is not None, '`firsts` must be provided if `just_kernel=False`'
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_lr1(items, firsts)

def build_LR1_automaton(G, firsts):
    #assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'
    
    firsts[G.EOF] = ContainerSet(G.EOF)
    
    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])
    
    closure = closure_lr1(start, firsts)
    automaton = State(frozenset(closure), True)
    
    pending = [ start ]
    visited = { start: automaton }
    
    while pending:
        current = pending.pop()
        current_state = visited[current]
        
        for symbol in G.terminals + G.nonTerminals:
            goto = goto_lr1(current_state.state, symbol, just_kernel=True)
            if goto == frozenset():
                continue
            
            try:
                next_state = visited[goto]
            except:
                clos = closure_lr1(goto, firsts)
                next_state = visited[goto] = State(frozenset(clos), True)
                pending.append(goto)
            current_state.add_transition(symbol.Name, next_state)
    
    automaton.set_formatter(multiline_formatter)
    return automaton

def build_LALR1_automaton(G, firsts):
    #assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'
    
    firsts[G.EOF] = ContainerSet(G.EOF)
    
    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])
    
    closure = closure_lr1(start, firsts)
    automaton = State(frozenset(closure), True)
    
    pending = [ start ]
    visited = { start: automaton }
        
    while pending:
        current = pending.pop()
        current_state = visited[current]
        
        for symbol in G.terminals + G.nonTerminals:
            goto = goto_lr1(current_state.state, symbol, just_kernel=True)
            
            closure = closure_lr1(goto, firsts)
            center = frozenset(item.Center() for item in goto)
            
            if center == frozenset():
                continue
            
            try:
                next_state = visited[center]
                centers = {item.Center(): item for item in next_state.state}
                centers = {item.Center(): (centers[item.Center()], item) for item in closure}

                _items = set()
                for c, (itemA, itemB) in centers.items():
                    item = Item(c.production, c.pos, itemA.lookaheads | itemB.lookaheads)
                    _items.add(item)

                _items = frozenset(_items)
                if next_state.state != _items:
                    pending.append(center)
                next_state.state = _items

            except KeyError:
                visited[center] = next_state = State(frozenset(closure), True)
                pending.append(center)

            if current_state[symbol.Name] is None:
                current_state.add_transition(symbol.Name, next_state)
            else:
                assert current_state.get(symbol.Name) is next_state, 'Bad build!!!'
    automaton.set_formatter(multiline_formatter)
    return automaton

def get_ll1_conflict_productions(M):
    return [[item, M[item]] for item in M if len(M[item]) > 1]

def terminals_string(sentense):
    for item in sentense:
        if item.IsNonTerminal:
            return False
    return True

def get_shortest_terminals_derivation(G):
    dic = { }
    non_term_epsilon = []
    
    for prod in G.Productions:
        if terminals_string(prod.Right):
            try:
                p = dic[prod.Left]
                if len(p) > len(prod.Right) and type(G.Epsilon) != type(prod.Right[0]):
                    dic[prod.Left] = prod.Right
                
            except KeyError:
                if not prod.Right.IsEpsilon:
                    dic[prod.Left] = prod.Right
                else:
                    non_term_epsilon.append(prod.Left)
                

    return dic, non_term_epsilon

class DerivationTreeNode:
    def __init__(self, symbol, father=None):
        self.symbol = symbol
        self.father = father
        self.childs = []

    def add_child(self, symbol):
        self.childs.append(DerivationTreeNode(symbol, father=self))
        return self.childs[-1]

    def go_root(self):
        return self if self.father is None else self.father.go_root()

    def __str__(self):
        return str(self.symbol)

class DerivationTree:
    def __init__(self, productions, is_lr=False):
        self.root = self._build_tree(productions, is_lr)

    def _build_tree(self, productions, is_lr):
        p = productions if not is_lr else reversed(productions)
        iter_productions = iter(p)
        if is_lr:
            return self._extreme_right_derivation(iter_productions)
        return self._extreme_left_derivation(productions)

    def _extreme_left_derivation(self, productions, node=None):
        try:
            head, body = next(productions)
        except StopIteration:
            return node.go_root()

        if node is None:
            node = DerivationTreeNode(head)

        assert node.symbol == head

        for symbol in body:
            if symbol.IsTerminal:
                node.add_child(symbol)
            elif symbol.IsNonTerminal:
                next_node = node.add_child(symbol)
                self._extreme_left_derivation(productions, next_node)
        return node

    def _extreme_right_derivation(self, productions, node=None):
        try:
            head, body = next(productions)
        except StopIteration:
            return node.go_root()

        if node is None:
            node = DerivationTreeNode(head)

        assert node.symbol == head

        for symbol in reversed(body):
            if symbol.IsTerminal:
                node.add_child(symbol)
            elif symbol.IsNonTerminal:
                next_node = node.add_child(symbol)
                self._extreme_right_derivation(productions, next_node)
        node.childs.reverse()
        return node

    def graph(self):
        G = pydot.Dot(graph_type='graph', rankdir='TD', margin=0.1)
        stack = [self.root]
        
        while stack:
            current = stack.pop()
            ids = id(current)
            G.add_node(pydot.Node(name=ids, label=str(current), shape='circle'))
            for child in current.childs:
                stack.append(child)
                G.add_node(pydot.Node(name=id(child), label=str(child), shape='circle'))
                G.add_edge(pydot.Edge(ids, id(child)))
        
        return G
    
    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except:
            pass

    def __str__(self):
        return str(self.root)

class Trie:
    def __init__(self, G, equal_or_terminal, value, pos, non_term, term, father=None):
        self._G = G
        self._value = value
        self._father = father 
        self._childs = []
        self._mark = equal_or_terminal
        self._pos = pos
        self._nt = non_term
        self._t = term
        if not self._mark:
            self.add_childs(self._G.nonTerminals[self._G.nonTerminals.index(value)].productions)
        
    
    def add_child(self, mark, new_child, pos):
        self._childs.append(Trie(self._G, mark, new_child, pos, self._nt, self._t, self))
    
    def add_childs(self, new_childs_list):
        for pos, pr in enumerate(new_childs_list):
            for child in pr.Right:
                if child.IsNonTerminal:
                    self.add_child(self._value == child, child, pos)
                else:
                    self.add_child(True, child, pos)
                
    
    def get_travel_to_father(self, _array):
        if self._father == None:
            return _array
        else:
            _array[self._father._value] = self._pos
            self._father.get_travel_to_father(_array)

    def preorden(self, array):
        if self._value == self._nt:
            self.get_travel_to_father(array)
            return array
        for child in range(len(self._childs)):
            self._childs[child].preorden(array)
            if len(array):
                return array

def get_travel(G, conflict_duo):
    trie = Trie(G, False, G.startSymbol, -1, conflict_duo[0][0], conflict_duo[0][1])
    result = {}
    trie.preorden(result)
    return result
