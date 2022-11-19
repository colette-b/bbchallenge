from pysat.solvers import Glucose3, Lingeling, Glucose4, Minisat22, Cadical, Mergesat3
from pysat.formula import CNF
from pysat.card import *
from tm_utils import *
from sat2_utils import *
from cfl_dfa import *
from db_utils import get_machine_i, get_indices_from_index_file
import random
from glucose_wrapper import run_glucose

class IdxManager:
    def __init__(self):
        self.idx = 0
    
    def get(self):
        self.idx += 1
        return self.idx

def op_and(idxmanager, cnf, variables):
    if len(variables) == 2:
        var_and = idxmanager.get()
        var1, var2 = variables
        cnf.append([-var1, -var2, var_and])
        cnf.append([-var_and, var1])
        cnf.append([-var_and, var2])
        return var_and
    else:
        return op_and(idxmanager, cnf, [op_and(idxmanager, cnf, [variables[0], variables[1]])] + variables[2:])


def op_or(idxmanager, cnf, variables):
    if len(variables) == 2:
        var_or = idxmanager.get()
        var1, var2 = variables
        cnf.append([var1, var2, -var_or])
        cnf.append([-var1, var_or])
        cnf.append([-var2, var_or])
        return var_or
    else:
        return op_or(idxmanager, cnf, [op_or(idxmanager, cnf, [variables[0], variables[1]])] + variables[2:])

def create_instance(n, tm, accepted_start_configs=[('', ('A', '0'), '')]):
    ''' mode='vanilla' for the usual CTL,
        mode='coctl' for coCTL '''
    im = IdxManager()
    F = CNF()
    symbols = [None, 
        [str(i) for i in range(n)],
        [str(i) for i in range(n, 2*n)]
        ]
    r = dict()
    # define variables
    tr = { (i, j, b): im.get() for i in symbols[1] for j in symbols[1] for b in tm.tape_symbols }
    tr.update( {(i, j, b): im.get() for i in symbols[2] for j in symbols[2] for b in tm.tape_symbols } )
    acc = { (i, j, s): im.get() for i in symbols[1] for j in symbols[2] for s in tm.combo_symbols }
    r[1] = {(i, t): im.get() for i in symbols[1] for t in range(-1, 2*n)}
    r[2] = {(i, t): im.get() for i in symbols[2] for t in range(-1, 2*n)}

    # exactly one transition
    for b in tm.tape_symbols:
        for i in symbols[1]:
            for cl in CardEnc.equals([tr[i, j, b] for j in symbols[1]], bound=1, encoding=EncType.pairwise):
                F.append(cl)
        for i in symbols[2]:
            for cl in CardEnc.equals([tr[i, j, b] for j in symbols[2]], bound=1, encoding=EncType.pairwise):
                F.append(cl)

    # symmetry removal
    for p in [1, 2]:
        for i in range(n):
            F.append([r[p][symbols[p][i], -1] * (1 if i==0 else -1)])
        for i in range(n-1):
            for t in range(-1, 2*n):
                F.append([
                    -r[p][symbols[p][i + 1], t],
                    r[p][symbols[p][i], t]
                ])
        for i in range(n):
            for t in range(-1, 2*n - 1):
                x, y, z1, z2 = r[p][symbols[p][i], t + 1], r[p][symbols[p][i], t], r[p][symbols[p][t//2], t], tr[symbols[p][t//2], symbols[p][i], str(t%2)]
                # write down "x = y or (z1 and z2)"
                F.append([-y, x])
                F.append([-z1, -z2, x])
                F.append([-x, y, z1])
                F.append([-x, y, z2])

    # there is a transition symbol0 -0-> symbol0 in both machines
    F.append([tr[symbols[1][0], symbols[1][0], '0']])
    F.append([tr[symbols[2][0], symbols[2][0], '0']])

    # 'A0' is accepted
    F.append([acc[symbols[1][0], symbols[2][0], ('A', '0')]])
    # tm_halt_symb is never reached
    for tm_halt_symb in tm.final_states():
        for i in symbols[1]:
            for j in symbols[2]:
                F.append([-acc[i, j, tm_halt_symb]])

    # acc implications
    for s in tm.combo_symbols:
        new_bit, direction, new_tm_symb = tm.get_transition_info(s)
        for p_ in symbols[1]:
            for p in symbols[1]:
                for q_ in symbols[2]:
                    for q in symbols[2]:
                        for b in tm.tape_symbols:
                            if direction == 'R':
                                F.append([
                                    -tr[q_, q, b],
                                    - acc[p_, q, s],
                                    -tr[p_, p, new_bit],
                                    acc[p, q_, (new_tm_symb, b)]
                                ])
                            if direction == 'L':
                                F.append([
                                    -tr[p_, p, b],
                                    - acc[p, q_, s],
                                    -tr[q_, q, new_bit],
                                    acc[p_, q, (new_tm_symb, b)]
                                ])

    # additional_acc
    s_left, s_right = dict(), dict()
    lefts = set(item[0] for item in accepted_start_configs)
    rights = set(item[2] for item in accepted_start_configs)
    def fill_with_prefixes(wordset):
        def search(w):
            if len(w) == 0 or w[:-1] in wordset:
                return
            wordset.add(w[:-1])
            search(w[:-1])
        for w in list(wordset):
            search(w)
    fill_with_prefixes(lefts)
    fill_with_prefixes(rights)
    for s_, allwords_set, vertices in [(s_left, lefts, symbols[1]), (s_right, rights, symbols[2])]:
        allwords = list(allwords_set)
        allwords.sort(key=lambda w: len(w))
        for j in vertices:
            s_['', j] = im.get()
            F.append([s_['', j]] if j==vertices[0] else [-s_['', j]])
        for w in allwords:
            if w == '':
                continue
            wp = w[:-1]
            for j in vertices:
                s_[w, j] = op_or(im, F, [op_and(im, F, [s_[wp, jp], tr[jp, j, w[-1]]]) for jp in vertices])
    for left, combo_symbol, right in accepted_start_configs:
        this_accepted = op_or(im, F, [
            op_and(im, F, 
                [
                    s_left[left, i],
                    s_right[right, j],
                    acc[i, j, combo_symbol]
                ]
            )
            for i in symbols[1] for j in symbols[2]
        ])
        F.append([this_accepted])

    return F, symbols[1], symbols[2], tr, acc

def check_if_solved(n, tm, threads=1, accepted_start_configs=[('', ('A', '0'), '')]):
    F, symbols1, symbols1, tr, acc = create_instance(n, tm, accepted_start_configs=accepted_start_configs)
    ret = run_glucose(threads, F)
    return type(ret) is list

if __name__ == '__main__':
    from db_utils import get_machine_i
    from glucose_wrapper import *
    idx = 3369312
    tm = TM(get_machine_i(idx))
    F, symbols1, symbols1, tr, acc = create_instance(4, tm)
    print('OK')
    #with open('./instance.txt', 'w') as fil:
    #    F.to_fp(fil)
    ret = run_glucose(1, F)

'''
def model_to_short_description(raw_model, symbols1, symbols2, tr, acc):
    model = dict()
    for x in raw_model:
        if x < 0:
            model[-x] = False
        else:
            model[x] = True
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
'''