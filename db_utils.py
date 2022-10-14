import os
from collections import defaultdict
import fcntl
from sat2_utils import verify_short_description
from tm_utils import *
from tqdm import tqdm

def get_machine_i(i, db_has_header=True):
    machine_db_path = './datafiles/all_5_states_undecided_machines_with_global_header'
    with open(machine_db_path, "rb") as f:
        c = 1 if db_has_header else 0
        f.seek(30*(i+c))
        b = f.read(30)
    s = ''
    for j in range(10):
        part = chr(ord('0') + b[3*j + 0]) + \
             ('L' if b[3*j + 1] else 'R') + \
             chr(ord('A')-1 + b[3*j + 2])
        if b[3*j + 2]==0:
            part = '---'
        s += part + ('_' if j in [1, 3, 5, 7] else '')
    return s             

def get_indices_from_index_file(index_file_path):
    index_file_size = os.path.getsize(index_file_path)
    machines_indices = []
    with open(index_file_path, "rb") as f:
        for i in range(index_file_size//4):
            chunk = f.read(4)
            machines_indices.append(int.from_bytes(chunk, byteorder="big"))
    return machines_indices

def read_proof_file(path='./datafiles/cfl_proofs.txt', verify=False):
    ''' proof file format:
        each line is of the form
        idx;n;unsat, which means an attempt with parameter n has failed, or
        idx;n;(arr1, arr2, acc), which means a successful solution was produced. '''
    infodict = defaultdict(dict)
    with open(path, 'r') as f:
        for line in tqdm(f):
            idx, n, result = line[:-1].split(';')
            idx = int(idx)
            n = int(n)
            infodict[idx][n] = result
            if result!='unsat' and verify:
                arr1, arr2, acc_arr = eval(result)
                tm_code = get_machine_i(idx)
                verify_short_description(arr1, arr2, acc_arr, TM(tm_code))
    return infodict

def is_already_solved(idx, infodict):
    return idx in infodict and set(infodict[idx].values()) != {'unsat'}

def write_to_proof_file(idx, n, data, path='./datafiles/cfl_proofs.txt'):
    with open(path, 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(f'{idx};{n};{data}\n')
        fcntl.flock(f, fcntl.LOCK_UN)

def proof_file_info(path='./datafiles/cfl_proofs.txt'):
    infodict = read_proof_file(path)
    solved = defaultdict(int)
    unsolved = defaultdict(int)
    for idx in infodict:
        for n in infodict[idx]:
            if infodict[idx][n] != 'unsat':
                solved[n] += 1
                break
            else:
                unsolved[n] += 1
    print('proof info:')
    print('length of index file: ', len(get_indices_from_index_file('./datafiles/bb5_undecided_index')))
    print('total idxs considered:', len(infodict))
    counts = list(solved.items())
    counts.sort()
    for n, count in counts:
        print(f'solved with param {n=}: {count}\tleft: {unsolved[n]}\t{round(100 * count / (count + unsolved[n]), 1)} percent success rate')
    print('left unsolved:        ', len(infodict) - sum(solved.values()))
