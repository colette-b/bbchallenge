from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from automata.fa.gnfa import GNFA
import random
import copy

# helper methods 
def empty_language_machine():
    return DFA(
        states={'p'},
        input_symbols={'0', '1'},
        transitions={'p': {'0': 'p', '1': 'p'}},
        initial_state='p',
        final_states=set()
    )

def to_regex(machine):
    if type(machine) == DFA:
        regex_ = GNFA.from_dfa(machine).to_regex()
    if type(machine) == NFA:
        regex_ = GNFA.from_nfa(machine).to_regex()
    return regex_ if regex_ is not None else '<empty>'

def dfa_info(dfa):
    return "[states=" + str(len(dfa.states)) + " regex=" + to_regex(dfa) + "]"

def empty_word_machine():
    return DFA(
        states={'p', 'q'},
        input_symbols={'0', '1'},
        transitions={'p': {'0': 'q', '1': 'q'}, 'q': {'0': 'q', '1': 'q'}},
        initial_state='p',
        final_states={'p'}
    )

def add_null_symbol(dfa, new_symbol):
    assert new_symbol not in dfa.input_symbols
    null_state = str(random.randint(1000, 1e15))
    assert null_state not in dfa.states
    new_transitions = dict()
    for state in dfa.states:
        new_transitions[state] = dfa.transitions[state] | {new_symbol: null_state}
    new_transitions[null_state] = {symbol: null_state for symbol in dfa.input_symbols.union({new_symbol})}
    return DFA(
        states = dfa.states.union({null_state}),
        input_symbols = dfa.input_symbols.union({new_symbol}),
        transitions = new_transitions,
        initial_state = dfa.initial_state,
        final_states = dfa.final_states
    )

def unify_symbol_sets(dfa1, dfa2):
    dfa1_ = dfa1.copy()
    dfa2_ = dfa2.copy()
    for s in dfa2.input_symbols.difference(dfa1.input_symbols):
        dfa1_ = add_null_symbol(dfa1_, s)
    for s in dfa1.input_symbols.difference(dfa2.input_symbols):
        dfa2_ = add_null_symbol(dfa2_, s)
    return dfa1_, dfa2_

def cutoff_last(dfa, b):
    dfa_ = dfa.copy()
    if '0' not in dfa_.input_symbols:
        dfa_ = add_null_symbol(dfa_, '0')
    if '1' not in dfa_.input_symbols:
        dfa_ = add_null_symbol(dfa_, '1')
    
    new_dfa = DFA(
        states=dfa_.states,
        input_symbols=dfa_.input_symbols,
        transitions=dfa_.transitions,
        initial_state=dfa_.initial_state,
        final_states={s for s in dfa_.states if dfa_.transitions[s][b] in dfa_.final_states}
    )
    return new_dfa

def concatenate(dfa1, dfa2):
    dfa1_, dfa2_ = unify_symbol_sets(dfa1, dfa2)
    return DFA.from_nfa(
        NFA.from_dfa(dfa1_) + NFA.from_dfa(dfa2_)
    ).minify(retain_names=False)

def intersection(dfa1, dfa2):
    dfa1_, dfa2_ = unify_symbol_sets(dfa1, dfa2)
    return dfa1_.intersection(dfa2_)

def union(dfa1, dfa2):
    dfa1_, dfa2_ = unify_symbol_sets(dfa1, dfa2)
    return DFA.from_nfa(
        NFA.from_dfa(dfa1_) | NFA.from_dfa(dfa2_)
    ).minify(retain_names=False)

def reverse(dfa):
    reversed_dfa = DFA.from_nfa(NFA.from_dfa(dfa).reverse()).minify(retain_names=False)
    return reversed_dfa

def dfa_from_regex(regex):
    dfa = DFA.from_nfa(NFA.from_regex(regex)).minify(retain_names=False)
    for s in ['0', '1']:
        if s not in dfa.input_symbols:
            dfa = add_null_symbol(dfa, s)
    return dfa

def smallest_word(dfa):
    return dfa.random_word(dfa.minimum_word_length())

def dfa_to_array(dfa):
    def r(x):
        if x == dfa.initial_state:
            return 0
        if x == 0:
            return dfa.initial_state
        return x
    arr = []
    for j in range(len(dfa.states)):
        arr.append(r(dfa.transitions[r(j)]['0']))
        arr.append(r(dfa.transitions[r(j)]['1']))
    return arr

def dfa_from_array(arr):
    assert len(arr) % 2 == 0
    n = len(arr) // 2
    return DFA(
        states = set(i for i in range(n)),
        input_symbols = {'0', '1'},
        transitions = {
            i : {'0': arr[2*i], '1': arr[2*i + 1]}
            for i in range(n)
        },
        initial_state = 0,
        final_states = set()
    )

def dfa_has_sink_state(arr):
    assert len(arr) % 2 == 0
    n = len(arr) // 2
    return any(arr[2*j]==j and arr[2*j+1]==j for j in range(n))
