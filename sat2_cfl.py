from z3 import *
from tm_utils import *
from sat2_utils import *
from cfl_dfa import *
from db_utils import get_machine_i, get_indices_from_index_file
import time

z3.set_option(verbose=1, timeout=10000)

def create_z3_instance(n, tm):
    Z = Solver()
    symbols1 = [str(i) for i in range(n)]
    symbols2 = [str(i) for i in range(n, 2*n)]
    ############# define two DFAs
    tr = { (i, j, b): Bool(f'tr_{i}_{j}_{b}') for i in symbols1 for j in symbols1 for b in ['0', '1'] }
    tr.update( {(i, j, b): Bool(f'tr_{i}_{j}_{b}') for i in symbols2 for j in symbols2 for b in ['0', '1'] } )
    # exactly one transition
    for b in ['0', '1']:
        for i in symbols1:
            Z.add(PbEq([(tr[i, j, b], 1) for j in symbols1], 1))
        for i in symbols2:
            Z.add(PbEq([(tr[i, j, b], 1) for j in symbols2], 1))

    acc = { (i, j, s): Bool(f'acc_{i}_{j}_{s}') for i in symbols1 for j in symbols2 for s in TM.tm_symbols }
    # 'a' is accepted
    Z.add(acc[symbols1[0], symbols2[0], 'a'] == True)
    # 0* in front and back is irrelevant
    Z.add(tr[symbols1[0], symbols1[0], '0'] == True)
    Z.add(tr[symbols2[0], symbols2[0], '0'] == True)
    # acc implications
    for s in TM.tm_symbols:
        new_bit, direction, new_tm_symb = tm.get_transition_info(s)
        for p_ in symbols1:
            for p in symbols1:
                for q_ in symbols2:
                    for q in symbols2:
                        for b in ['0', '1']:
                            if direction == 'R':
                                Z.add(Implies(
                                    And(
                                        tr[q_, q, b],
                                        acc[p_, q, s],
                                        tr[p_, p, new_bit]
                                    ),
                                    acc[p, q_, new_tm_symb.lower() if b=='0' else new_tm_symb.upper()]
                                ))
                            if direction == 'L':
                                Z.add(Implies(
                                    And(
                                        tr[p_, p, b],
                                        acc[p, q_, s],
                                        tr[q_, q, new_bit]
                                    ),
                                    acc[p_, q, new_tm_symb.lower() if b=='0' else new_tm_symb.upper()]
                                ))
    # tm_halt_symb is never reached
    for tm_halt_symb in tm.final_states():
        for i in symbols1:
            for j in symbols2:
                Z.add(acc[i, j, tm_halt_symb] == False)
    # some symmetry removing conditions
    Z.add(Or(tr[symbols1[0], symbols1[0], '1'], tr[symbols1[0], symbols1[1], '1']))
    Z.add(Or(tr[symbols1[1], symbols1[0], '1'], tr[symbols1[1], symbols1[1], '1'], tr[symbols1[1], symbols1[2], '1']))
    # same for symbols2
    Z.add(Or(tr[symbols2[0], symbols2[0], '1'], tr[symbols2[0], symbols2[1], '1']))
    Z.add(Or(tr[symbols2[1], symbols2[0], '1'], tr[symbols2[1], symbols2[1], '1'], tr[symbols2[1], symbols2[2], '1']))
    return Z, symbols1, symbols2, tr, acc

def model_to_short_description(model, symbols1, symbols2, tr, acc):
    ''' we represent a DFA on n vertices as an array of 2n elements: 
        tr[0][0], tr[0][1], tr[1][0], tr[1][1], ... tr[n-1][0], tr[n-1][1]
        and list of accepted fragments as list x-S-y, where x is a state of first machine,
        S is one of aAbBcCdDeE, and y is a state of second machine '''
    dfa_arr1 = []
    for i in range(len(symbols1)):
        dfa_arr1.append([j for j in range(len(symbols1)) if model[tr[symbols1[i], symbols1[j], '0']]][0])
        dfa_arr1.append([j for j in range(len(symbols1)) if model[tr[symbols1[i], symbols1[j], '1']]][0])
    dfa_arr2 = []
    for i in range(len(symbols2)):
        dfa_arr2.append([j for j in range(len(symbols2)) if model[tr[symbols2[i], symbols2[j], '0']]][0])
        dfa_arr2.append([j for j in range(len(symbols2)) if model[tr[symbols2[i], symbols2[j], '1']]][0])
    acc_arr = []
    for i, j, s in acc:
        if not model[acc[i, j, s]]:
            continue
        acc_arr.append(i + '-' + s + '-' + str(symbols2.index(j)))
    return dfa_arr1, dfa_arr2, acc_arr

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

def try_tm(n, tm, doublecheck=False):
    starttime = time.time()
    Z, symbols1, symbols2, tr, acc = create_z3_instance(n, tm)
    diff = round(time.time() - starttime, 4)
    print(f'solving (n = {n})...')
    print(f'time init=\t {diff} s')
    get_result = Z.check()
    print(f'time spent=\t {Z.statistics().time} s')
    if get_result == z3.sat:
        print('sat')
        model = Z.model()
        arr1, arr2, acc = model_to_short_description(model, symbols1, symbols2, tr, acc)
        print(arr1, arr2, acc)
        verify_short_description(arr1, arr2, acc, tm)
        if doublecheck:
            mpl = model_to_mpl(model, symbols1, symbols2, tr, acc)
            assert(check_if_solution(mpl, tm))
            mpl_info(mpl)
            sanity_check(mpl, tm)
        return True
    else:
        print('unsat')
        return False

if __name__ == '__main__':
    solved = []
    unsolved = []
    all_unsolved = get_indices_from_index_file('./datafiles/bb5_undecided_index')
    print(f'{len(all_unsolved)=}')
    for _ in range(10**3):    
        idx = all_unsolved[random.randint(1, len(all_unsolved) - 1)]
        sample_machine_code = get_machine_i(idx)
        tm = TM(sample_machine_code)
        print('='*40, idx, '='*40)

        if try_tm(3, tm) or try_tm(4, tm) or try_tm(5, tm) or try_tm(6, tm):
            solved.append(idx)
        else:
            unsolved.append(idx)
        print(f'solved = {len(solved)}\tunsolved = {len(unsolved)}')
    print(unsolved)
