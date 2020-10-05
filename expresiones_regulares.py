from automata import NFA, DFA, nfa_to_dfa
from automata import automata_union, automata_concatenation, automata_closure, automata_minimization
from cmp.utils import Token
from cmp.automata import State
from cmp.tools.regex import Regex
from code import metodo_predictivo_no_recursivo


#from cmp.ast import get_printer


class Node:
    def evaluate(self):
        raise NotImplementedError()
        
class AtomicNode(Node):
    def __init__(self, lex):
        self.lex = lex

class UnaryNode(Node):
    def __init__(self, node):
        self.node = node
        
    def evaluate(self):
        value = self.node.evaluate() 
        return self.operate(value)
    
    @staticmethod
    def operate(value):
        raise NotImplementedError()
        
class BinaryNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
    def evaluate(self):
        lvalue = self.left.evaluate() 
        rvalue = self.right.evaluate()
        return self.operate(lvalue, rvalue)
    
    @staticmethod
    def operate(lvalue, rvalue):
        raise NotImplementedError()
EPSILON = 'ε'

class EpsilonNode(AtomicNode):
    def evaluate(self):
        return NFA(1, {0}, {}, 0)

class SymbolNode(AtomicNode):
    def evaluate(self):
        s = self.lex
        transitions = {
            (0, s): [1],
        }
        return NFA(2, {1}, transitions, 0)

class ClosureNode(UnaryNode):
    @staticmethod
    def operate(value):
        return automata_closure(value)

class UnionNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return automata_union(lvalue, rvalue)

class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        return automata_concatenation(lvalue, rvalue)



######################################################################################################################
def regex_tokenizer(text, G, skip_whitespaces=True):
    tokens = []
    fixed_tokens = {lex: Token(lex, G[lex]) for lex in '| * ( ) ε'.split() }
    symbol = '' #esto esta puesto para no generar errores
    for char in text:
        if skip_whitespaces and char.isspace():
            continue
        try:
            _token = fixed_tokens[char]
        except KeyError:
            _token = Token(char, symbol) 
            ### revisar ya que hay que ponerlo para el tipo que es en dependencia de los tipajes de los terminales
        
        tokens.append(_token)
            
        
    tokens.append(Token('$', G.EOF))
    return tokens

######################################################################################################################
'''
cp9 - generador de lexer
'''

class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()
    
    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            autom = Regex(regex)
            aut, states = State.from_nfa(autom.automaton, get_states = True)
            for item in states:
                if item.final:
                    item.tag = (n, token_type)
            
            regexs.append(aut)
        return regexs 
    
    
    def _build_automaton(self):
        start = State('start')
        for item in self.regexs:
            start.add_epsilon_transition(item)
        
        return start.to_deterministic()
    
        
    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        final_lex = lex = ''
        
        for symbol in string:
            _curr_state = state[symbol]
            if _curr_state is None:
                break
            lex = lex + symbol
            if _curr_state[0].final:
                final = _curr_state[0]
                final_lex = lex
            state = _curr_state[0]
        return final, final_lex
    
    def _tokenize(self, text):
        while True:
            state, lex = self._walk(text)
            text = text[len(lex):]
            if state and state.final:
                _type = min((s for s in state.state if s.final), key = lambda x :x.tag)
                _type = _type.tag[1]
                yield lex, _type
            else:
                return None
            if text == '':
                break
                
        yield '$', self.eof
    
    def __call__(self, text):
        return [ Token(lex, ttype) for lex, ttype in self._tokenize(text) ]





