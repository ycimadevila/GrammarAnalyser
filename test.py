from cmp.pycompiler import Symbol, NonTerminal, Terminal, EOF, Sentence, SentenceList, Epsilon, Production, Grammar
from parser import LL1Parser
from cmp.utils import pprint, inspect
from parser_utils import get_shortest_terminals_derivation, terminals_string,\
     get_ll1_conflict_productions, get_ll1_conflict_productions, get_travel, terminals_string
#from simplifier_grammar import simplifier_grammar

'''
G = Grammar()
E = G.NonTerminal('E', True)
A = G.NonTerminal('A')
plus, equal, num = G.Terminals('plus equal num')

E %= A + equal + A | num
A %= num + plus + A | num
'''