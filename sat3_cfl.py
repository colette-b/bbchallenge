from pysat.solvers import Glucose3, Lingeling, Glucose4, Minisat22, Cadical, Mergesat3
from pysat.formula import CNF
from pysat.card import *
from tm_utils import *
from sat2_utils import *
from cfl_dfa import *
from db_utils import get_machine_i, get_indices_from_index_file
import sat2_cfl
import random

class IdxManager:
    def __init__(self):
        self.idx = 0
    
    def get(self):
        self.idx += 1
        return self.idx

def create_instance(n, tm, get_formula=False):
    #chooselol = random.randint(1, 3)
    #if chooselol == 1:
    #    g = Glucose4() #Minisat22() #Mergesat3() #Cadical() #Lingeling() # Minisat22() # Glucose4()
    #    print('gluc')
    #if chooselol == 2:
    #    g = Minisat22()
    #    print('mini')
    #if chooselol == 3:
    #    g = Cadical()
    #    print('cadical')
    im = IdxManager()
    F = CNF()
    symbols = [None, 
        [str(i) for i in range(n)],
        [str(i) for i in range(n, 2*n)]
        ]
    r = dict()
    ############# define variables
    tr = { (i, j, b): im.get() for i in symbols[1] for j in symbols[1] for b in ['0', '1'] }
    tr.update( {(i, j, b): im.get() for i in symbols[2] for j in symbols[2] for b in ['0', '1'] } )
    acc = { (i, j, s): im.get() for i in symbols[1] for j in symbols[2] for s in TM.tm_symbols }
    r[1] = {(i, t): im.get() for i in symbols[1] for t in range(-1, 2*n)}
    r[2] = {(i, t): im.get() for i in symbols[2] for t in range(-1, 2*n)}

    # exactly one transition
    for b in ['0', '1']:
        for i in symbols[1]:
            for cl in CardEnc.equals([tr[i, j, b] for j in symbols[1]], bound=1, encoding=EncType.pairwise):
                F.append(cl)
        for i in symbols[2]:
            for cl in CardEnc.equals([tr[i, j, b] for j in symbols[2]], bound=1, encoding=EncType.pairwise):
                F.append(cl)
    
    # 'a' is accepted
    F.append([acc[symbols[1][0], symbols[2][0], 'a']])
    # 0* in front and back is irrelevant
    F.append([tr[symbols[1][0], symbols[1][0], '0']])
    F.append([tr[symbols[2][0], symbols[2][0], '0']])
    # acc implications
    for s in TM.tm_symbols:
        new_bit, direction, new_tm_symb = tm.get_transition_info(s)
        for p_ in symbols[1]:
            for p in symbols[1]:
                for q_ in symbols[2]:
                    for q in symbols[2]:
                        for b in ['0', '1']:
                            if direction == 'R':
                                F.append([
                                    -tr[q_, q, b],
                                    -acc[p_, q, s],
                                    -tr[p_, p, new_bit],
                                    acc[p, q_, new_tm_symb.lower() if b=='0' else new_tm_symb.upper()]
                                ])
                            if direction == 'L':
                                F.append([
                                    -tr[p_, p, b],
                                    -acc[p, q_, s],
                                    -tr[q_, q, new_bit],
                                    acc[p_, q, new_tm_symb.lower() if b=='0' else new_tm_symb.upper()]
                                ])
    # tm_halt_symb is never reached
    for tm_halt_symb in tm.final_states():
        for i in symbols[1]:
            for j in symbols[2]:
                F.append([-acc[i, j, tm_halt_symb]])

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

    if get_formula:
        return F, symbols[1], symbols[2], tr, acc
    else:
        g = Minisat22()
        g.append_formula(F)
        return g, symbols[1], symbols[2], tr, acc

def model_to_short_description(raw_model, symbols1, symbols2, tr, acc):
    #raw_model = g.get_model()
    model = dict()
    for x in raw_model:
        if x < 0:
            model[-x] = False
        else:
            model[x] = True
    #print(model)
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

if __name__ == '__main__':
    solved = []
    for idx in TM_SKELET_LIST:
        sample_machine_code = get_machine_i(idx)
        tm = TM(sample_machine_code)
        g, symbols1, symbols2, tr, acc = create_instance(8, tm)
        print(idx, '   \t', end='', flush=True)
        result = g.solve()
        print(result)
        if result:
            solved.append(idx)
            dfa1, dfa2, acc = model_to_short_description(g.get_model(), symbols1, symbols2, tr, acc)
            print(dfa1, dfa2, acc)
            sat2_cfl.verify_short_description(dfa1, dfa2, acc, tm)
    print(len(solved))
    print(solved)
