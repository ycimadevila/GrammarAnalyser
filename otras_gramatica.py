from cmp.pycompiler import Symbol, NonTerminal, Terminal, EOF, Sentence, SentenceList, Epsilon, Production, Grammar

from cmp.utils import pprint, inspect

from cp3 import compute_firsts, ContainerSet, compute_follows, build_parsing_table, metodo_predictivo_no_recursivo
"""
##OTRAS GRAMATICAS
"""


"""
#gramatica 1
"""
G = Grammar()
S = G.NonTerminal('S', True)
A,B = G.NonTerminals('A B')
a,b = G.Terminals('a b')

S %= A + B
A %= a + A | a
B %= b + B | b

print(G)

firsts = compute_firsts(G)
pprint(firsts)

# print(inspect(firsts))
assert firsts == {
   a: ContainerSet(a , contains_epsilon=False),
   b: ContainerSet(b , contains_epsilon=False),
   S: ContainerSet(a , contains_epsilon=False),
   A: ContainerSet(a , contains_epsilon=False),
   B: ContainerSet(b , contains_epsilon=False),
   Sentence(A, B): ContainerSet(a , contains_epsilon=False),
   Sentence(a, A): ContainerSet(a , contains_epsilon=False),
   Sentence(a): ContainerSet(a , contains_epsilon=False),
   Sentence(b, B): ContainerSet(b , contains_epsilon=False),    
   Sentence(b): ContainerSet(b , contains_epsilon=False) 
}
follows = compute_follows(G, firsts)
pprint(follows)

# print(inspect(follows))
assert follows == {
   S: ContainerSet(G.EOF , contains_epsilon=False),
   A: ContainerSet(b , contains_epsilon=False),
   B: ContainerSet(G.EOF , contains_epsilon=False) 
}
M = build_parsing_table(G, firsts, follows)
M


"""
#gramatica 2
"""

G = Grammar()
S = G.NonTerminal('S', True)
A,B,C = G.NonTerminals('A B C')
a,b,c,d,f = G.Terminals('a b c d f')

S %= a + A | B + C | f + B + f
A %= a + A | G.Epsilon
B %= b + B | G.Epsilon
C %= c + C | d

print(G)

firsts = compute_firsts(G)
pprint(firsts)

# print(inspect(firsts))
assert firsts == {
   a: ContainerSet(a , contains_epsilon=False),
   b: ContainerSet(b , contains_epsilon=False),
   c: ContainerSet(c , contains_epsilon=False),
   d: ContainerSet(d , contains_epsilon=False),
   f: ContainerSet(f , contains_epsilon=False),
   S: ContainerSet(d, a, f, c, b , contains_epsilon=False),
   A: ContainerSet(a , contains_epsilon=True),
   B: ContainerSet(b , contains_epsilon=True),
   C: ContainerSet(c, d , contains_epsilon=False),
   Sentence(a, A): ContainerSet(a , contains_epsilon=False),
   Sentence(B, C): ContainerSet(d, c, b , contains_epsilon=False),
   Sentence(f, B, f): ContainerSet(f , contains_epsilon=False),
   G.Epsilon: ContainerSet( contains_epsilon=True),
   Sentence(b, B): ContainerSet(b , contains_epsilon=False),
   Sentence(c, C): ContainerSet(c , contains_epsilon=False),
   Sentence(d): ContainerSet(d , contains_epsilon=False) 
}

follows = compute_follows(G, firsts)
pprint(follows)

# print(inspect(follows))
assert follows == {
   S: ContainerSet(G.EOF , contains_epsilon=False),
   A: ContainerSet(G.EOF , contains_epsilon=False),
   B: ContainerSet(d, f, c , contains_epsilon=False),
   C: ContainerSet(G.EOF , contains_epsilon=False) 
}
M = build_parsing_table(G, firsts, follows)
pprint(M)

# print(inspect(M))
assert M == {
   ( S, a, ): [ Production(S, Sentence(a, A)), ],
   ( S, c, ): [ Production(S, Sentence(B, C)), ],
   ( S, b, ): [ Production(S, Sentence(B, C)), ],
   ( S, d, ): [ Production(S, Sentence(B, C)), ],
   ( S, f, ): [ Production(S, Sentence(f, B, f)), ],
   ( A, a, ): [ Production(A, Sentence(a, A)), ],
   ( A, G.EOF, ): [ Production(A, G.Epsilon), ],
   ( B, b, ): [ Production(B, Sentence(b, B)), ],
   ( B, c, ): [ Production(B, G.Epsilon), ],
   ( B, f, ): [ Production(B, G.Epsilon), ],
   ( B, d, ): [ Production(B, G.Epsilon), ],
   ( C, c, ): [ Production(C, Sentence(c, C)), ],
   ( C, d, ): [ Production(C, Sentence(d)), ] 
}

parser = metodo_predictivo_no_recursivo(G, M)

left_parse = parser([b, b, d, G.EOF])
pprint(left_parse)

# print(inspect(left_parse))
assert left_parse == [ 
   Production(S, Sentence(B, C)),
   Production(B, Sentence(b, B)),
   Production(B, Sentence(b, B)),
   Production(B, G.Epsilon),
   Production(C, Sentence(d)),
]