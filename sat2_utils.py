from z3 import *
from tm_utils import *
from pydot import Dot, Edge, Node
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from cfl_dfa import *
import time

def model_to_mpl(model, symbols1, symbols2, tr, acc):
    states1 = set(symbols1)
    states2 = set(symbols2)
    transitions1 = {i: dict() for i in states1}
    transitions2 = {i: dict() for i in states2}
    for i, j, b in tr:
        if model[tr[i, j, b]]:
            if i in states1:
                transitions1[i][b] = j
            if i in states2:
                transitions2[i][b] = j
    machine_pair_list = {s : [] for s in TM.tm_symbols}
    for i, j, s in acc:
        if not model[acc[i, j, s]]:
            continue
        dfa1 = DFA(
            states=states1,
            input_symbols={'0', '1'},
            transitions=transitions1,
            initial_state=symbols1[0],
            final_states={i}
        )
        dfa2 = DFA(
            states=states2,
            input_symbols={'0', '1'},
            transitions=transitions2,
            initial_state=symbols2[0],
            final_states={j}
        )
        if dfa1.isempty() or dfa2.isempty():
            continue
        machine_pair_list[s].append((dfa1, dfa2))
    return machine_pair_list

def sanity_check(mpl, tm):
    assert(check_if_solution(mpl, tm))
    check_if_solution2(mpl, tm)
    print('checker says OK')
    F = DFA.from_nfa(mpl_to_machine(mpl))
    print(f'{len(F.states)=}')
    assert F.accepts_input('a')
    print("'a' in L")
    add_left_zero = concatenate(dfa_from_regex('0'), F)
    assert add_left_zero.issubset(F)
    print("w in L => 0w in L")
    add_right_zero = concatenate(F, dfa_from_regex('0'))
    assert add_right_zero.issubset(F)
    print("w in L => w0 in L")
    w, s, v = '', 'a', ''
    simsize = 10**4
    for _ in range(simsize):
        assert F.accepts_input(w + s + v[::-1])
        w, s, v = tm.simulation_step(w, s, v)
    print(f"first {simsize} steps are in L")

def verify_short_description(arr1, arr2, acc, tm):
    ''' verify that a description of two DFAs and 'acceptance array' gives a CFL 
        for a given TM. This is just a double-check, as sat-solver conditions 
        should imply all the necessary conditions. '''
    assert arr1[0] == 0
    assert arr2[0] == 0
    assert '0-a-0' in acc
    for item in acc:
        l, s, r = item.split('-')
        l, r = int(l), int(r)
        new_bit, direction, new_tm_symb = tm.get_transition_info(s)
        for b in ['0', '1']:
            if direction == 'R':
                for j in range(len(arr2) // 2):
                    if arr2[2*j + int(b)] == r:
                        corr = f'{arr1[2*l + int(new_bit)]}-{new_tm_symb.lower() if b=="0" else new_tm_symb.upper()}-{j}'
                        assert corr in acc
            if direction == 'L':
                for i in range(len(arr1) // 2):
                    if arr1[2*i + int(b)] == l:
                        corr = f'{i}-{new_tm_symb.lower() if b=="0" else new_tm_symb.upper()}-{arr2[2*r + int(new_bit)]}'
                        assert corr in acc

def verify_dfa_pair(arr1, arr2, tm):
    assert arr1[0] == 0
    assert arr2[0] == 0

    def fill_step(acc):
        new_acc = copy.deepcopy(acc)
        for item in acc:
            l, s, r = item.split('-')
            l, r = int(l), int(r)
            if tm.is_final(s):
                return None
            new_bit, direction, new_tm_symb = tm.get_transition_info(s)
            for b in ['0', '1']:
                if direction == 'R':
                    for j in range(len(arr2) // 2):
                        if arr2[2*j + int(b)] == r:
                            corr = f'{arr1[2*l + int(new_bit)]}-{new_tm_symb.lower() if b=="0" else new_tm_symb.upper()}-{j}'
                            new_acc.add(corr)
                if direction == 'L':
                    for i in range(len(arr1) // 2):
                        if arr1[2*i + int(b)] == l:
                            corr = f'{i}-{new_tm_symb.lower() if b=="0" else new_tm_symb.upper()}-{arr2[2*r + int(new_bit)]}'
                            new_acc.add(corr)
        return new_acc
    
    acc = set()
    acc.add('0-a-0')
    while True:
        new_acc = fill_step(acc)
        if new_acc is None:
            return False
        if len(new_acc) == len(acc):
            return True
        acc = new_acc
    
        