from tm_utils import *
from automata_utils import *
import random
import string
import sys

# machine_pair_list['B'] contains pairs (F, G) of DFAs.
# Each such pair means that we assume that uBv is in L,
# provided that F accepts u and G accepts reverse(v).
# machines process words starting from the infinite-zero-side-of-tape.
# for some later stuff, they should never accept empty word.

# main method: examine any entry in machine_pair_list,
# 'run' a single step of turing machine,
# describe the inference in terms of new DFAs,
# check whether the result is already in L,
# if not then add entries to machine_pair_list.
def is_already_covered(symbol, F, G, machine_pair_list, bonus_info=False):
    small = concatenate(concatenate(F, dfa_from_regex(symbol)), reverse(G))
    big = add_null_symbol(empty_language_machine(), symbol)
    for Fi, Gi in machine_pair_list[symbol]:
        machine_part = concatenate(concatenate(Fi, dfa_from_regex(symbol)), reverse(Gi))
        big = big.union(machine_part)
    if bonus_info:
        return small.issubset(big), to_regex(small.difference(big))
    else:
        return small.issubset(big)

def expand(symbol, F, G, tm):
    b, direction, s = tm.get_transition_info(symbol)
    if direction == 'R':
        G0 = cutoff_last(G, '0')
        G1 = cutoff_last(G, '1')
        F_ = concatenate(F, dfa_from_regex(b))
        return [(s.lower(), F_, G0), (s.upper(), F_, G1)]
    if direction == 'L':
        F0 = cutoff_last(F, '0')
        F1 = cutoff_last(F, '1')
        G_ = concatenate(G, dfa_from_regex(b))
        return [(s.lower(), F0, G_), (s.upper(), F1, G_)]

def check_if_solution(machine_pair_list, tm, verbose=True):
    for s in machine_pair_list:
        if tm.is_final(s) and len(machine_pair_list[s]) > 0:
            print(f'{s} is final symbol for this TM, but machine pair list contains entry for {s}')
            return False
        for F, G in machine_pair_list[s]:
            for s_, F_, G_ in expand(s, F, G, tm):
                contained, error_regex = is_already_covered(s_, F_, G_, machine_pair_list, bonus_info=True)
                if not contained:
                    if verbose:
                        print('the following is in machine_pair_list:')
                        print(s, dfa_info(F), dfa_info(G))
                        print('thus the following should be, but is not covered:')
                        print(s_, dfa_info(F_), dfa_info(G_))
                        print('difference regex:', error_regex)
                        return False, (s_, F_, G_)
    return True, None

def mpl_info(machine_pair_list):
    for s in machine_pair_list:
        for F, G in machine_pair_list[s]:
            print('  - ', s, dfa_info(F), dfa_info(G))

def mpl_to_machine(mpl):
    big_regex = ''
    for s in mpl:
        for F, G in mpl[s]:
            big_regex += '((' + to_regex(F) + ')' + s + '(' + to_regex(reverse(G)) + '))' + '|'
    return NFA.from_regex(big_regex[:-1])


def check_if_solution2(mpl, tm):
    return
    bigmachine = DFA.from_nfa(mpl_to_machine(mpl))
    # if w in L, then w0 in L
    assert concatenate(bigmachine, dfa_from_regex('0')).issubset(bigmachine)
    # if w in L, then 0w in L
    assert concatenate(dfa_from_regex('0'), bigmachine).issubset(bigmachine)
    # 'a' in L
    assert bigmachine.accepts_input('a')
    # no final symbols appear
    for tm_halt_symb in tm.final_states():
        assert intersection(dfa_from_regex(f'.*{tm_halt_symb}.*'), bigmachine).isempty()
    # respecting TM transitions
    for tm_symb in TM.tm_symbols:
        if tm.is_final(tm_symb):
            continue
        new_bit, direction, new_tm_symb = tm.get_transition_info(tm_symb)
        for b in ['0', '1']:
            if direction == 'R':
                old = intersection(dfa_from_regex(f'.*{tm_symb}{b}.*'), bigmachine)
                new = intersection(dfa_from_regex(f'.*{new_bit}{new_tm_symb.upper() if b=="1" else new_tm_symb.lower()}.*'), bigmachine)
                assert old.issubset(new)
            if direction == 'L':
                old = intersection(dfa_from_regex(f'.*{b}{tm_symb}.*'), bigmachine)
                new = intersection(dfa_from_regex(f'.*{new_tm_symb.upper() if b=="1" else new_tm_symb.lower()}{new_bit}.*'), bigmachine)
                assert old.issubset(new)


if __name__ == '__main__':
    # example 1
    sample_machine_code1 = '1RB0LD_1LC1RC_1LA0RC_---0LE_0RB1LD'
    tm1 = TM(sample_machine_code1)
    cased_tm_symbols = 'aAbBcCdDeE'
    # (0|11)* (a1 | 1A | 0b | 1B | c | C | D | e0 | 1E) .*
    machine_pair_list1 = {s: [] for s in cased_tm_symbols}
    machine_pair_list1['a'].append((dfa_from_regex('0*(0|11)*'),       dfa_from_regex('0*(0|1)*1')))
    machine_pair_list1['A'].append((dfa_from_regex('0*(0|11)*1'),      dfa_from_regex('0*(0|1)*')))
    machine_pair_list1['b'].append((dfa_from_regex('0*(0|11)*0'),      dfa_from_regex('0*(0|1)*')))
    machine_pair_list1['B'].append((dfa_from_regex('0*(0|11)*1'),      dfa_from_regex('0*(0|1)*')))
    machine_pair_list1['c'].append((dfa_from_regex('0*(0|11)*'),       dfa_from_regex('0*(0|1)*')))
    machine_pair_list1['C'].append((dfa_from_regex('0*(0|11)*'),       dfa_from_regex('0*(0|1)*')))
    machine_pair_list1['D'].append((dfa_from_regex('0*(0|11)*'),       dfa_from_regex('0*(0|1)*')))
    machine_pair_list1['e'].append((dfa_from_regex('0*(0|11)*'),       dfa_from_regex('0*(0|1)*0')))
    machine_pair_list1['E'].append((dfa_from_regex('0*(0|11)*1'),      dfa_from_regex('0*(0|1)*')))
    print(check_if_solution(machine_pair_list1, tm1))

    # example 2
    sample_machine_code2 = '1RB1RC_1LB1RA_1LD1LD_0RE0RD_1LB---'
    tm2 = TM(sample_machine_code2)
    machine_pair_list2 = {s: [] for s in cased_tm_symbols}
    machine_pair_list2['a'].append((dfa_from_regex('0*'),       dfa_from_regex('0*')))
    machine_pair_list2['A'].append((dfa_from_regex('0*1'),      dfa_from_regex('0*1*')))
    machine_pair_list2['b'].append((dfa_from_regex('0*10*'),    dfa_from_regex('0*1*')))
    machine_pair_list2['B'].append((dfa_from_regex('0*'),       dfa_from_regex('0*11*')))
    machine_pair_list2['c'].append((dfa_from_regex('0*11'),     dfa_from_regex('0*')))
    machine_pair_list2['C'].append((dfa_from_regex('0*11'),     dfa_from_regex('0*1*')))
    machine_pair_list2['D'].append((dfa_from_regex('0*10*'),    dfa_from_regex('0*1*')))
    machine_pair_list2['d'].append((dfa_from_regex('0*10*'),    dfa_from_regex('0*')))
    machine_pair_list2['e'].append((dfa_from_regex('0*10*'),   dfa_from_regex('0*'))) 
    print(check_if_solution(machine_pair_list2, tm2))
