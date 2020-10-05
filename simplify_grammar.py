from cmp.pycompiler import Sentence

def __print(nonTerminals, terminals, Productions, text):
    print(f'===================== {text} =====================')
    print('non terminals', '\n', nonTerminals)
    print('terminals', '\n', terminals)
    print('productions', '\n', Productions)

def delete_epsilon_from_grammar(G):
    # primero marca como nulleable los posibles no terminales
    # los cuales pueden ser alcanzados por derivaciones de epsilon
    # (en uno o mas pasos) 

    nullable_non_term = {}
    
    for nt in G.nonTerminals:
        prod = nt.productions
        for p in prod:
            if p.IsEpsilon:
                nullable_non_term[p.Left] = True

    augment = True
    while augment:
        len_null = len(nullable_non_term)

        for prod in G.Productions:
            left, right = prod

            if left in nullable_non_term:
                continue
            
            if len(right) == 0:
                nullable_non_term[left] = True
            
            else:
                null = True
                for item in right:
                    if item not in nullable_non_term:
                        null = False
                        break
                if left not in nullable_non_term:
                    nullable_non_term[left] = null
                else:
                    if not nullable_non_term[left] and null:
                        nullable_non_term[left] = True

        augment = len_null != len(nullable_non_term)

    # se encarga de eliminar las producciones sobrantes
    # y tambien de agregar las nuevas producciones luego de la sustitucion

    for nt in G.nonTerminals:
        prod = nt.productions
        mask = {}

        counter = 0 
        while counter < len(prod):
            pr = prod[counter]

            if len(pr.Right) == 0:
                G.Productions.remove(pr)
                nt.productions.remove(pr)
            else:
                for pos, elem in enumerate(pr.Right):
                    try:
                        if nullable_non_term[elem]:
                            temp = [item for i, item in enumerate(pr.Right) if i != pos]
                            sent = Sentence(*temp)
                            if sent not in mask:
                                mask[sent] = True
                                if len(sent):
                                    pr.Left %= sent
                                prod.append(pr.Left.productions[-1])
                    except KeyError:
                        pass
                counter += 1

    return G

def delete_unique_productions(G):
    
    # por todo elemento que comparta el lado derecho con el izquierdo de una produccion y este sea unitario
    # entonces compartiran el mismo lado derecho

    cont = True
    while cont:
        cont = False

        for prod in G.Productions:
            left, right = prod
            if len(right) == 1 and right[0] in G.nonTerminals:
                G.Productions.remove(prod)
                left.productions.remove(prod)
                for p in right[0].productions:
                    prod.Left %= p.Right
                cont = True
    
    return G

def eliminate_non_terminal_variables(G): 
    der_to_term = {}
    
    change = True
    while change:
        change = False
        for nt in G.nonTerminals:
            for prod in nt.productions:
                for elem in prod.Right:
                    if elem not in G.terminals:
                        try:
                            der_to_term[elem]
                        except KeyError:
                            break
                else:
                    try:
                        der_to_term[nt]
                    except KeyError:
                        der_to_term[nt] = True
                        change = True

    # busca las produccines a eliminar
    prod_to_eliminate = []
    for prod in G.Productions:
        try:
            der_to_term[prod.Left]
            for elem in prod.Right:
                if elem not in G.terminals:
                    try:
                        der_to_term[elem]
                    except KeyError:
                        prod_to_eliminate.append(prod)
        except KeyError:
            prod_to_eliminate.append(prod)

    # eliminar producciones innecesarias
    for p in prod_to_eliminate:
        G.Productions.remove(p)
        p.Left.productions.remove(p)

    for nt in G.nonTerminals:
        if len(nt.productions) == 0:
            G.nonTerminals.remove(nt)

    return G

def eliminate_variables_not_reached_for_start_symbol(G):

    temp = [G.startSymbol]
    reachable_nts = set([G.startSymbol])
    reachable_ts = set()

    # agregar los terminales y no terminales alcanzables desde el simbolo inicial
    while len(temp) > 0:
        elem = temp.pop()

        for p in elem.productions:
            for item in p.Right:
                if item.IsNonTerminal:
                    if item not in reachable_nts:
                        reachable_nts.add(item)
                        temp.append(item)
                else:
                    reachable_ts.add(item)

    # eliminar las producciones sobrantes
    delete_non_neccessary_productions = []

    for prod in G.Productions:
        if prod.Left not in reachable_nts:
            delete_non_neccessary_productions.append(prod)
    
    for prod in delete_non_neccessary_productions:
        G.Productions.remove(prod)


    # eliminar los terminales
    delete_non_neccessary_non_terminal = []
    for non_term in G.nonTerminals:
        if non_term not in reachable_nts:
            delete_non_neccessary_non_terminal.append(non_term)
    for non_term in delete_non_neccessary_non_terminal:
        G.nonTerminals.remove(non_term)
    

    # eliminar los no terminales
    delete_non_neccessary_terminal = []
    for term in G.terminals:
        if term not in reachable_ts:
            delete_non_neccessary_terminal.append(term)
    for term in delete_non_neccessary_terminal:
        G.terminals.remove(term)

    return G

def simplify_grammar(G):
    G = delete_epsilon_from_grammar(G)
    #__print(G.nonTerminals, G.terminals, G.Productions, 'epsilon')

    G = delete_unique_productions(G)
    #__print(G.nonTerminals, G.terminals, G.Productions, 'eliminacionde producciones unicas')

    G = eliminate_non_terminal_variables(G)
    #__print(G.nonTerminals, G.terminals, G.Productions, 'eliminacion de variables no terminales')

    G = eliminate_variables_not_reached_for_start_symbol(G)
    #__print(G.nonTerminals, G.terminals, G.Productions, 'eliminacion de variables no alcanzables')
    
    return G


'''
from cmp.pycompiler import Symbol, NonTerminal, Terminal, EOF, Sentence, SentenceList, Epsilon, Production, Grammar

from cmp.utils import pprint, inspect
from parser_utils import get_shortest_terminals_derivation, terminals_string, get_ll1_conflict_productions


G = Grammar()
S = G.NonTerminal('S', True)
A, B, C, D, E = G.NonTerminals('A B C D E')
a, b, d, c = G.Terminals('a b d c')

S %= A + B + C
A %= a + A | G.Epsilon
B %= b + B | G.Epsilon
C %= G.Epsilon
D %= d + D | c
E %= c


G = Grammar()
E = G.NonTerminal('E', True)
T,F,X,Y = G.NonTerminals('T F X Y')
plus, minus, star, div, opar, cpar, num = G.Terminals('+ - * / ( ) num')

E %= T + X
X %= plus + T + X | minus + T + X | G.Epsilon
T %= F + Y
Y %= star + F + Y | div + F + Y | G.Epsilon
F %= num | opar + E + cpar


G = simplify_grammar(G)
print('non terminals', '\n', G.nonTerminals)
print('terminals', '\n', G.terminals)
print('productions', '\n', G.Productions)
'''