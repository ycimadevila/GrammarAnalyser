import streamlit as st
import pandas as pn
from code import compute_firsts, compute_follows, build_parsing_table, metodo_predictivo_no_recursivo
from cmp.pycompiler import Grammar
from parser import LL1Parser, SLR1Parser, LR1Parser, LALR1Parser
from parser_utils import DerivationTree
from regular_gram import is_regular,build_automaton_regular_grammar,dfa_to_regex
from common_preffixs import left_recursion,eliminate_common_prefix
from simplify_grammar import simplify_grammar
#####################
###  Gramatica 1  ###
#####################

non_terminals1 = 'E T F X Y'

terminals1 = 'plus +\n\
minus -\n\
div /\n\
star *\n\
opar (\n\
cpar )\n\
num num'

grammar1 = 'E %= T + X\n\
X %= plus + T + X | minus + T + X | G.Epsilon\n\
T %= F + Y\n\
Y %= star + F + Y | div + F + Y | G.Epsilon\n\
F %= num | opar + E + cpar'

string11 = 'num star num star num plus num star num plus num plus num'

#####################
###  Gramatica 2  ###
#####################

non_terminals2 = 'E A'

terminals2 = 'plus +\n\
equal =\n\
num num'

grammar2 = 'E %= A + equal + A | num\n\
A %= num + plus + A | num'

string21 = 'num equal num'
string22 = 'num plus num equal num plus num'

#####################
###  Gramatica 3  ###
#####################

non_terminals3 = 'S A B'

terminals3 = '\
a a\n\
b b'

grammar3 = '\
S %= A + B\n\
A %= a + A | G.Epsilon\n\
B %= b + B | A'

#####################
###  Gramatica 4  ###
#####################

non_terminals4 = 'E T F'

terminals4 = '\
plus +\n\
minus -\n\
star *\n\
div /\n\
opar (\n\
cpar )\n\
num num'

grammar4 = '\
E %= E + plus + T | T | E + minus + T\n\
T %= T + star + F | F | T + div + F\n\
F %= num | opar + E + cpar'

string4 = 'num plus num star num'

#####################
###  Gramatica 5  ###
#####################

non_terminals5 = 'S A B'

terminals5 = 'a a\n\
b b'

grammar5 = 'S %= a + A | G.Epsilon\n\
A %= b'

#####################
###     FIN       ### 
#####################

#####################
###  Gramatica 6 ###
#####################

non_terminals6 = 'S A B'

terminals6 = 'a a\n\
b b'

grammar6 = 'S %= a + A | b + A\n\
A %= a + B | b \n\
B %= a + A| b + A'

#####################
###     FIN       ### 
#####################

#####################
###  Gramatica 7  ###
#####################

non_terminals7 = 'S A B'

terminals7 = 'a a\n\
b b\n\
c c'

grammar7 = 'S %= S + A|c\n\
A %= B + a | B + b'

#####################
###     FIN       ### 
#####################

################
##   METODOS  ##
################

def LL1_error(M):
    for item in M:
        if len(M[item]) > 1:
            return True
    return False


def execute_instructions(*inst):
    for i in inst:
        exec(i)

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


############
#  VISUAL  #
############

st.sidebar.title('Proyecto de Compilación')
st.sidebar.subheader('Yasmin Cisneros Cimadevila')
st.sidebar.subheader('Jessy Gigato Izquierdo')
st.sidebar.subheader('C-311') 

parser = st.sidebar.selectbox('Escoja el parser que desea utilizar', ('LL(1)','SLR(1)','LR(1)', 'LALR(1)'))
first_follow = st.sidebar.selectbox('Mostrar firsts y follows', ('Firsts y Follows','Firsts','Follows', 'Ninguno'))
automaton = st.sidebar.selectbox('Mostrar Automata', ('Si', 'No'))
derivation_tree = st.sidebar.selectbox('Mostrar arbol de derivacion', ('Si','No'))
simplify = st.sidebar.selectbox('Simplificar la gramatica',('No','Si'))
rec_izq =  st.sidebar.selectbox('Eliminar recursion izquierda ',('No','Si'))
fact =st.sidebar.selectbox('Eliminar prefijos comunes ',('No','Si'))
non_terminals = st.text_area("Introduzca los no terminales (poniendo de primero al no terminal inicial)", value=non_terminals6)
terminals = st.text_area("Introduzca los terminales", value=terminals6)
grammar = st.text_area("Gramatica", value=grammar6)

cadenas = st.text_area('introduzca(s) cadena(s) a parsear', value=string21)

bt_analize = st.button('Analizar gramatica')


###############################
###  INICIALIZAR VARIABLES  ###
###############################

G = Grammar()


if bt_analize:
    
    for item in get_inst(parser_terminal(terminals), non_terminals.split(), grammar):
        exec(item)

    _parser = ''

    if parser == 'LL(1)':
        _parser = LL1Parser(G)


    elif parser == 'SLR(1)':
        _parser = SLR1Parser(G)
        

    elif parser == 'LR(1)':
        _parser = LR1Parser(G)

    else:
        _parser = LALR1Parser(G)
    
    firsts = _parser.Firsts
    follows = _parser.Follows

    error = False
    if parser == 'LL(1)':
        M = _parser.Table
        st.subheader('Tabla')
        st.text('\n'.join(str(f) + ': ' + str(M[f]) for f in M))
        error = LL1_error(M)


    if first_follow == 'Firsts' or first_follow == 'Firsts y Follows':
        st.subheader('Firsts')
        st.text('\n'.join(str(f) + ': ' + str(firsts[f]) for f in firsts)) 

    if first_follow == 'Follows' or first_follow == 'Firsts y Follows':
        st.subheader('Follows')
        st.text('\n'.join(str(f) + ': ' + str(follows[f]) for f in follows))
    if cadenas and not error:
        derivation = ''
        if parser == 'LL(1)':
            exec(f'derivation = _parser({cadenas.split()})')  
        else:
            cadenas = ', '.join(cadenas.split())
            cadenas = cadenas[0: len(cadenas)] + ', G.EOF'
            cadenas = '[' + cadenas + ']'  
            exec(f'derivation = _parser({cadenas})')

        if derivation_tree == 'Si':
            st.subheader('Árbol de Derivacion')
            if parser in ('SLR(1)', 'LR(1)', 'LALR(1)'):
                st.graphviz_chart(str(DerivationTree(derivation, parser in ('SLR(1)', 'LR(1)', 'LALR(1)')).graph()))    
            else:
                st.graphviz_chart(str(derivation[1]))
    
    if automaton == 'Si' and parser != 'LL(1)':
        st.graphviz_chart(str(_parser.automaton()))

    if is_regular(G):
        st.write('La gramatica es regular')
        dfa =build_automaton_regular_grammar(G)
        st.graphviz_chart(str(dfa.graph()))
        regex = dfa_to_regex(G,dfa)
        st.write(regex)
    else :
        st.write('La gramatica no es regular')

    if rec_izq == 'Si':
        G = left_recursion(G)
        st.header('Recursion izquierda eliminada')
        st.write("No Terminales")
        for nt in G.nonTerminals:
            st.text(nt)
        st.write("Terminales")
        for t in G.terminals:
            st.text(t)
        st.write("Producciones")
        for prod in G.Productions:
            st.text(prod)
    
    if fact == 'Si':
        G = eliminate_common_prefix(G)
        st.header('Prefijos comunes eliminados')
        st.write("No Terminales")
        for nt in G.nonTerminals:
            st.text(nt)
        st.write("Terminales")
        for t in G.terminals:
            st.text(t)
        st.write("Producciones")
        for prod in G.Productions:
            st.text(prod)
        
    if simplify == 'Si':
        G = simplify_grammar(G)
        st.write("No Terminales")
        for nt in G.nonTerminals:
            st.write(nt)
        st.write("Terminales")
        for t in G.terminals:
            st.write(t)
        st.write("Producciones")
        for prod in G.Productions:
            st.write(prod)

    elif error:
        if parser == 'LL(1)':
            conflict_string = _parser._get_conflict_string()
            string = ''
            for i in conflict_string:
                string += str(i) + ' '
            st.subheader('Una cadena de conflicto para la gramatica seria:')
            st.text(string)
        
    

