from automata import NFA, DFA, nfa_to_dfa
from automata import automata_union, automata_concatenation, automata_closure, automata_minimization
from cmp.utils import Token
from code import metodo_predictivo_no_recursivo

'''
import zlib, base64
code = zlib.decompress(base64.b64decode('eJzNWN1um0gUvucp6BWwRSjx1SrSrBRt4iR20rRJW9VCCI1hbE+LgTBDGjvKY+1r7DPtmR9gjIm3q+5KexPDzPn9zjdnDuGIEW4xVOF8SawHtMIMc15ZZ2hKNudVVVTWNcJZZm0QZTRnHOcJsQiiObeWKCO5tUIfNyVRojka44wRa4o+VjWxPiOcbyyMtrS0OEckr9ekwhz2tUBZIl6XGbFYEwGvNieWTddlUXG73KQFt8hTQkpuX8k16QckSsyYtaiKtZ2sy6DmNGON1u9FzjHNSXUPmSUZCNrvxqegk5KFHcc0pzyOXUayhQ/pcML8Bc0hbJ9DCIxyWuRM7FQcHXmgZgvRQIki9WMsgpT82ywpW4i76sFr1tcYcu0cNMuPRYLndYarDai0woYget6ePL8sisre2jS3masi8F5AFlbdU3/u+bdiy1AKKCdr5srobQCAACwP7q3vQPqcVHHseL5zlT/ijKZ2UmQZSYSeXSxsZd4Riv1QwtMonEfott3rgg9wmrpzbz+rIKUswVXqOo6nKkBKRrMijw3DRjFkyDpiuSCT7gXSxS5FRLCKN7ZdEV5X+xqhFIxCx4lASjPqzNBwdXTLCpcrGY+M5AJJDgZnBXfB2reUVsi5vnP8Na6WNEdHwbFI+kLkH+dFSlwl/048OpIYjs9WuCTIKTNgJSdPsJLhOcmQ4/jfacpX6MhfEbpcCb55uqyZT3VZG/bs1JQi588/HJsu4Ans2AROnU3FznAoWRNEQqskIxAT32TwOi+yVJrJWleKt8oiFE0EJCKyx0LiVnp/xcn475yMDzrRVkm6bKyei8fMH2u8qPoFRskuhEZeh31fq8W+PaYd6DqsFLMVSZVzTZsL3SQqUlYxe1zGHROGCKbI4gVJRYBdQgFeUpLI4td88avgvGabVJZdS7Wks/GpC23J+4m+pI/Jtbtx4TTUxCeeKJR87jcEuQjs8Uy9JRzZ345kdaGN9FQ8mbTRh76RzUko7URCA179QVeap6JBQYLBP8qs7SBJXVUkb3urhGhdPBJtZbMGUkkQgFbqzc4LPtQsQtNeZNYw33N2UDVUfqLwKOoYM20ZA/dox5Z9s0YiFTBkmdNtkwyvaL7s1LQt3QnsRCYlZdTRX8hMlaiEJFE9wUzLZKkOo3f2LBGJVMc1L9aYF3lTnA7dG3UpdbePFBDeUtSq7SC2jYyzcovSBrR+171FMsGboC5TsOnewpsO+sYyr4kkK1hd7UcpwpuhkMngWBcceHpCz3vLwMbvK5oReybcb9EsKItShjBwHxm5Dd1W26Y0F8L+gERTp4uGk0+qQE/ymrxQ3W4W4LIkuXrXqZuji/vLkyeRyBc45kWcLnAHgsg+Qc+QVYZeRyrs8pD0i8BTFtAUHclfFksqoM+uBKoT1t25hTADvQkKRRVn6ucVLIXGfNdWNwpIDG5Qj3NbX44N9uWBPG48g/iXCssEoKI5zJBq57KBeqK2L0WaS3fiNW8/nOylUpk05bnslUu9i5tLeSrQJKB5Sp4ayUs0CQtB+PYc2Em4hXj8uVxt+m/ejTFwGbx580YOXTunpFNEIiHLvkdyoTuRE5H8tk0PHLxH4moRqfv3ftJx670kk84bx3UOTHXxsY9HJpmAGekxOoa/I4SP9dT7NoWFGuFR+z6yesMnyPZmlCQ8BT0R+vMYHowZ4mVPeTSoPGqUR7vKSZj5MMihUAVYceFHBSeeR5HqWOmTfy+tuyHsw7IvFPTNA+LqKZL+WjzvT3YK9wVBBd6CJTU49qpj7urx3f4iz3gtT0wHYAfdSBTxuX5p6wJ3pDsRpfIzb7dEQPEEdHLMD5Tq6H9dqhbXFnlzltL4HfsDY7m5p7FV0BqFNq+mtqADDkYHHIz2HPw7tWua2PHg6ap7FfupCg2ehzr6T9CvjUJ03nqIHcZp+Kv9jLKvBXwfiY92gaSY8mHkqSlbxcqse+d3V8JUwPJJwnqOytIdunA0PWqBwJ1Ia/bK0FKr8VigcI1cdxYyMeSJyVKoztRnyrsiV/O1XDwXOEyEZ3caplEgvhhgbIPrm9NHIppyKsSmgfhIYj0LcuvaM2rxKZxEzQWjo/H6NREyyIhVYRveySTvhMlP7ZgfSQwlbvEa5u813eouYk4QU2Sg7v7CmLszMIgpC6KYBmtSwSeVcUf2b89hqSF7ElR9VQ9YUXPFdCo5/0PRddlP4XusqEs1fYnVlVj9ER6Ji1aHv/LUN8USpmoEA4Ten8MX3jd4mKLE6kb/nRN/COaDhbDsq505dtojE5Nj17PuptRv/y3CuXslw3tUDlT1NSRj/3oXY5Pwj9HOfxPmaBpeA+P7NBZ7X9GVHm/UnNZejbOQ+uPdgWb/hlRC6Ktlf0AhHUyAap4G7cdknxfg5KGNYro31PaC7iYeNQddef4Hf+Y/eNZffhu9yA=='))
code = code.decode()
print(code)
'''
t=set
s=range
q=hasattr
D=KeyError
L=all
y=isinstance
e=int
g=len
h=TypeError
n=False
K=True
V=any
a=zip
tt=enumerate
KK=True
pp=tuple
ss=range

try:
 import pydot
except ImportError:
 pass
from cmp.utils import ContainerSet
class NFA:
 def __init__(self,states,finals,transitions,start=0):
  self.states=states
  self.start=start
  self.finals=t(finals)
  self.map=transitions
  self.vocabulary=t()
  self.transitions={z:{}for z in s(states)}
  for(A,b),O in transitions.items():
   assert q(O,'__iter__'),'Invalid collection of states'
   self.transitions[A][b]=O
   self.vocabulary.add(b)
  self.vocabulary.discard('')
 def epsilon_transitions(self,state):
  assert state in self.transitions,'Invalid state'
  try:
   return self.transitions[state]['']
  except D:
   return()
 def graph(self):
  G=pydot.Dot(rankdir='LR',margin=0.1)
  G.add_node(pydot.Node('start',shape='plaintext',label='',width=0,height=0))
  for(l,i),O in self.map.items():
   i='ε' if i=='' else i
   G.add_node(pydot.Node(l,shape='circle',style='bold' if l in self.finals else ''))
   for F in O:
    G.add_node(pydot.Node(F,shape='circle',style='bold' if F in self.finals else ''))
    G.add_edge(pydot.Edge(l,F,label=i,labeldistance=2))
  G.add_edge(pydot.Edge('start',self.start,label='',style='dashed'))
  return G
 def _repr_svg_(self):
  try:
   return self.graph().create_svg().decode('utf8')
  except:
   pass
class DFA(NFA):
 def __init__(self,states,finals,transitions,start=0):
  assert L(y(value,e)for value in transitions.values())
  assert L(g(b)>0 for A,b in transitions)
  transitions={key:[value]for key,value in transitions.items()}
  NFA.__init__(self,states,finals,transitions,start)
  self.current=start
 def _move(self,symbol):
  if symbol not in self.transitions[self.current]:
   return n
  self.current=self.transitions[self.current][symbol][0]
  return K
 def _reset(self):
  self.current=self.start
 def recognize(self,string):
  self._reset()
  for c in string:
   if not self._move(c):
    return n
  return self.current in self.finals
def move(automaton,states,symbol):
 M=t()
 for z in states:
  d=automaton.transitions[z]
  try:
   O=d[symbol]
  except D:
   O=()
  M.update(O)
 return M
def epsilon_closure(automaton,states):
 Y=[s for s in states]
 x={s for s in states}
 while Y:
  z=Y.pop()
  epsilon_transitions=automaton.epsilon_transitions(z)
  for G in epsilon_transitions:
   if G not in x:
    x.add(G)
    Y.append(G)
 return ContainerSet(*x)
def nfa_to_dfa(automaton):
 c={}
 l=epsilon_closure(automaton,[automaton.start])
 l.id=0
 l.is_final=V(s in automaton.finals for s in l)
 J=[l]
 Y=[l]
 while Y:
  z=Y.pop()
  for b in automaton.vocabulary:
   M=move(automaton,z,b)
   H=epsilon_closure(automaton,M)
   if not H:
    continue
   if H not in J:
    H.id=g(J)
    H.is_final=V(s in automaton.finals for s in H)
    J.append(H)
    Y.append(H)
   else:
    o=J.index(H)
    H=J[o]
   try:
    c[z.id,b]
    assert n,'Invalid DFA!!!'
   except D:
    c[z.id,b]=H.id
 S=[z.id for z in J if z.is_final]
 P=DFA(g(J),S,c)
 return P
def automata_union(a1,a2):
 c={}
 l=0
 d1=1
 d2=a1.states+d1
 u=a2.states+d2
 for(A,b),O in a1.map.items():
  c[A+d1,b]={F+d1 for F in O}
 for(A,b),O in a2.map.items():
  c[A+d2,b]={F+d2 for F in O}
 c[l,'']=[a1.start+d1,a2.start+d2]
 for dx,S in a([d1,d2],[a1.finals,a2.finals]):
  for z in S:
   try:
    X=c[z+dx,'']
   except D:
    X=c[z+dx,'']=t()
   X.add(u)
 J=a1.states+a2.states+2
 S={u}
 return NFA(J,S,c,l)
def automata_concatenation(a1,a2):
 c={}
 l=0
 d1=0
 d2=a1.states+d1
 u=a2.states+d2
 for(A,b),O in a1.map.items():
  c[A+d1,b]={F+d1 for F in O}
 for(A,b),O in a2.map.items():
  c[A+d2,b]={F+d2 for F in O}
 for z in a1.finals:
  try:
   X=c[z+d1,'']
  except D:
   X=c[z+d1,'']=t()
  X.add(a2.start+d2)
 for z in a2.finals:
  try:
   X=c[z+d2,'']
  except D:
   X=c[z+d2,'']=t()
  X.add(u)
 J=a1.states+a2.states+2
 S={u}
 return NFA(J,S,c,l)
def automata_closure(a1):
 c={}
 l=0
 d1=1
 u=a1.states+d1
 for(A,b),O in a1.map.items():
  c[A+d1,b]={F+d1 for F in O}
 c[l,'']=[a1.start+d1,u]
 for z in a1.finals:
  try:
   X=c[z+d1,'']
  except D:
   X=c[z+d1,'']=t()
  X.add(u)
  X.add(a1.start+d1)
 J=a1.states+2
 S={u}
 return NFA(J,S,c,l)
from cmp.utils import DisjointSet
def distinguish_states(R,automaton,K):
 U={}
 E=pp(automaton.vocabulary)
 for u in R:
  Y=automaton.transitions[u.value]
  L=((Y[s][0]if s in Y else None)for s in E)
  J=pp((K[d].representative if d in K.nodes else None)for d in L)
  try:
   U[J].append(u.value)
  except D:
   U[J]=[u.value]
 return[R for R in U.values()]
def state_minimization(automaton):
 K=DisjointSet(*ss(automaton.states))
 K.merge(s for s in automaton.finals)
 K.merge(s for s in ss(automaton.states)if s not in automaton.finals)
 while KK:
  c=DisjointSet(*ss(automaton.states))
  for R in K.groups:
   for h in distinguish_states(R,automaton,K):
    c.merge(h)
  if g(c)==g(K):
   break
  K=c
 return K
def automata_minimization(automaton):
 K=state_minimization(automaton)
 I=[s for s in K.representatives]
 Y={}
 for i,state in tt(I):
  v=state.value
  for F,L in automaton.transitions[v].items():
   b=K[L[0]].representative
   j=I.index(b)
   try:
    Y[i,F]
    assert n
   except D:
    Y[i,F]=j
 Q=[i for i,state in tt(I)if state.value in automaton.finals]
 q=I.index(K[automaton.start].representative)
 return DFA(g(I),Q,Y,q)