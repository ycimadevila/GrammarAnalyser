from cmp.pycompiler import  Sentence,Grammar,Production,NonTerminal,Terminal


####prefijos comunes##########
def eliminate_common_prefix(G):
    conflict = 1
    new_prods = []
    temp_prods = []
    new_non_terminals = []
    for non_term in G.nonTerminals:
        count = 0
        left = non_term
        productions = left.productions
        common_prefixs = find_common_prefix(G,left,productions)
        for key,prod in common_prefixs.items():
            conflict = len(prod) > 1
            non_term = prod[0].Left
            count+=1
            if not conflict:
                for p in prod:
                    l,r = p
                    l = str(l)
                    if r == G.Epsilon:
                        r = 'G.Epsilon'
                        new_prods.append((p,f'{l} %= {r}'))
                        continue
                    list = []
                    for i in r:
                        list.append(str(i))
                    r = '+'.join(list)
                    new_prods.append((p,f'{l} %= {r}'))
            else:
                while conflict:
                    term_prods= []
                    n_p,t_p,new_non_term = eliminate(G,non_term,key,prod,count)
                    new_non_terminals.append(new_non_term)
                    new_prods = new_prods + n_p
                    c_p_prod = [i[0] for i in t_p]
                    c_p = find_common_prefix(G,left,c_p_prod)
                    temp_prods += t_p
                    conflict = find_conflict(c_p)
                    if conflict:
                        count+=1
                        for p in c_p_prod:
                            if p not in conflict:
                                new_prods.append([t for t in temp_prods if t[0]==p][0])
                        prod = conflict
                        non_term = prod[0].Left
                        key = conflict[0].Right[0]
                    else:
                        new_prods += [p for p in t_p]
                
    _G = create_new_grammar(G,new_non_terminals,new_prods)
    return _G

def find_common_prefix(G,non_term,productions):
    common_prefixs = {} #symbol-->[production](producciones que tienen en comun symbol)
    for prod in productions:
        left,right = prod
        if right == G.Epsilon:
            common_prefixs[G.Epsilon] = [prod]
            continue
        init = right._symbols[0]
        try:
            common_prefixs[init].append(prod)
        except KeyError:
            common_prefixs[init] = [prod]
    return common_prefixs

def eliminate(G,non_term,rep,productions,count):
    new_prods = []
    new_temp_prods = []
    str_left=str(non_term)
    str_rep = str(rep)
    new_non_terminal= str_left[0] + str(count)
    #for i in range(0,count):
    #    new_non_terminal += "'"
    right = str_rep + '+' + new_non_terminal
    new_prods.append((create_productions(G,str_left,str_rep,True,new_non_terminal),f'{str_left} %= {right}'))
    for prod in productions:
        _,right = prod
        _len = len(right)
        if _len == 1:
            new_temp_prods.append((create_productions(G,new_non_terminal,G.Epsilon),f'{new_non_terminal} %= G.Epsilon'))
        else:
            sub = ''
            for s in range(1,len(right._symbols)):
                sub+=str(right._symbols[s])
                sub+=' '
            sub = sub.strip()
            _sub = '+'.join(sub.split())
            new_temp_prods.append((create_productions(G,new_non_terminal,sub.split()), f'{new_non_terminal} %= {_sub} '))
    return new_prods,new_temp_prods,new_non_terminal

def find_conflict(dict):
    list_conflict=[]
    for key,prod in dict.items():
        if len(prod)>1:
            list_conflict += prod
            break
    return list_conflict

def search(G,c):
    for non_term in G.nonTerminals:
        if str(non_term)==c:
            return non_term
    for term in G.nonTerminals:
        if str(term) == c:
            return term
    return None

def create_productions(G,left,right,new = False, new_symbol = None):
    _G = Grammar()
    left = NonTerminal(left,_G)
    list_symbols = []
    if right == G.Epsilon:
        return Production(left,_G.Epsilon)
    for r in right:
        s = search(G,r)
        if not s:
            s= NonTerminal(r,_G)
        list_symbols.append(s)
    if new:
        s = NonTerminal(new_symbol,_G)
        list_symbols.append(s)
    right = Sentence(list_symbols[0])
    for i in range(1,len(list_symbols)):
        right = right + list_symbols[i]
    return Production(left,right)

############### Recusividad izquierda #################################
def left_recursion(G):
    new_prods = []
    new_non_terminals = []
    for non_term in G.nonTerminals:
        left_recursion =  find_common_prefix(G,G.startSymbol,non_term.productions)
        if non_term in left_recursion.keys():
            news,new_nt = eliminate_left_recursion(G,non_term,left_recursion)
            new_prods += news
            if new_nt not in new_non_terminals:
                new_non_terminals.append(new_nt)
        else:
            for p in non_term.productions:
                l,r = p
                if r == G.Epsilon:
                    s = 'G.Epsilon'
                else:
                    s = '+'.join([str(i) for i in r]) 
                new_prods.append((p,f'{l}%={s}'))            
    _G = create_new_grammar(G,new_non_terminals,new_prods)
    return _G

def eliminate_left_recursion(G,left,dict):
    new_prods = []
    new_non_terminal = str(left) + '1'
    ('nnt---->',new_non_terminal)
    conflict_prods = dict[left]
    for prod in left.productions:
        l,r = prod
        nt = NonTerminal(new_non_terminal,G)
        if prod not in conflict_prods:
            ####A ->b1A'|b2A'|...|bnA'####
            s_r = [i for i in r]
            s_r = Sentence(*s_r,nt)
            new_p = Production(left,s_r)
            s = '+'.join([str(i) for i in s_r._symbols])
            new_prods.append((new_p,f'{left}%={s}'))
        else:
            new_r = [i for i in r._symbols]
            new_r.remove(left)
            s_r = Sentence(*new_r,nt)
            new_p = Production(left,s_r)
            s = '+'.join([str(i) for i in s_r._symbols])
            new_prods.append((new_p,f'{new_non_terminal}%={s}'))
    return new_prods,new_non_terminal

##########################AUXILIARES######################################### 
def create_new_grammar(G,new_non_terminals,productions):
    if len(productions) == 0:
        return G
    _G = Grammar()
    inst = []
    inst.append(f'{G.startSymbol} = _G.NonTerminal(\'{G.startSymbol}\', True)')
    non_term = [i for i in G.nonTerminals]
    non_term.remove(G.startSymbol)
    non_terminals = non_term + new_non_terminals

    str_non_terminals = [str(nt) for nt in non_terminals]
    str_terminals = [str(t) for t in G.terminals]
    __nt = ' '.join(str_non_terminals)
    _nt = ', '.join(str_non_terminals)
    __t = ' '.join(str_terminals)
    _t = ', '.join(str_terminals)

    if len(str_non_terminals) == 1:
        inst.append(f'{_nt} = _G.NonTerminal(\'{__nt}\')')
    elif len(str_non_terminals) > 1:
        inst.append(f'{_nt} = _G.NonTerminals(\'{__nt}\')')

    inst.append(f'{_t} = _G.Terminals(\'{__t}\')')
    p = [t[1] for t in productions]
    p = '\n'.join(p)
    inst.append(f'{p}')
    for i in inst:
        exec(i)
    return _G
        
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


