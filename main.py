import argparse
import threading
import queue
import time
import random
from tqdm import tqdm
from db_utils import *
import sat2_utils
from sat3_cfl import *
from glucose_wrapper import *
from paths import TEMPFILE_DIR, UNDECIDED_INDEX
from test2 import analyze

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['database', 'index'], default='database')
parser.add_argument('n', type=int)
parser.add_argument('threads', type=int)
parser.add_argument('timeout', type=int)
parser.add_argument('--idx', type=int)
parser.add_argument('--machine_code')
parser.add_argument('--instance_path')
parser.add_argument('--additional_acc')
parser.add_argument('--prooftype', default='vanilla')
parser.add_argument('--force_symmetric', action='store_true')

args = parser.parse_args()

csat, cunsat, ctimeout = 0, 0, 0
q = queue.Queue()
pbar = None

def check_and_save_result(result, symbols1, symbols2, tr, acc, tm, idx):
    arr1, arr2, acc_arr = model_to_short_description(result, symbols1, symbols2, tr, acc)
    sat2_utils.verify_short_description(arr1, arr2, acc_arr, tm)
    write_to_proof_file(idx, args.n, f'{(arr1, arr2, acc_arr)}')

def worker():
    global csat, cunsat, ctimeout
    while True:
        time1 = time.time()
        idx = q.get()
        tm_code = get_machine_i(idx)
        time1half = time.time()
        tm = TM(tm_code)
        F, symbols1, symbols2, tr, acc = create_instance(args.n, tm, force_symmetric=args.force_symmetric)
        time2 = time.time()
        result = run_glucose(1, F, timeout=args.timeout)
        time3 = time.time()
        if result:
            if result != 'timeout':
                check_and_save_result(result, symbols1, symbols2, tr, acc, tm, idx)
        else:
            write_to_proof_file(idx, args.n, 'unsat')
        pbar.update(1)
        q.task_done()
        time4 = time.time()
        d1 = round(time1half - time1, 3)
        d2 = round(time2 - time1half, 3)
        d3 = round(time3 - time2, 3)
        d4 = round(time4 - time3, 3)
        if result == 'timeout':
            verdict = 'timeout'
            ctimeout += 1
        elif result:
            verdict = '    sat'
            csat += 1
        else:
            verdict = '  unsat'
            cunsat += 1
        print('{:10d}'.format(idx), '\t', '{:5.2f}'.format(d1), '\t', '{:5.2f}'.format(d2), '\t', \
            '{:5.2f}'.format(d3), '\t', '{:5.2f}'.format(d4), '\t', verdict, \
            '{:5d}'.format(csat), \
            '{:5d}'.format(cunsat), \
            '{:5d}'.format(ctimeout)
        )

def mode_database():
    print(f'{args.force_symmetric = }')
    global pbar
    all_unsolved = get_indices_from_index_file(UNDECIDED_INDEX)
    infodict = read_proof_file()
    proof_file_info()
    random.shuffle(all_unsolved)
    for idx in all_unsolved:
        if is_already_solved(idx, infodict):
            continue
        if args.n in infodict[idx]:
            continue
        q.put(idx)
    pbar = tqdm(total=q.qsize(), smoothing=0.0)
    for _ in range(args.threads):
        threading.Thread(target=worker, daemon=True).start()
    q.join()

def mode_idx():
    if args.idx:
        tm_code = get_machine_i(args.idx)
    else:
        tm_code = args.machine_code
    print(tm_code)
    tm = TM(tm_code)
    F, symbols1, symbols2, tr, acc = create_instance(args.n, tm)
    if args.instance_path:
        with open(args.instance_path, 'w') as fil:
            F.to_fp(fil)
        print(f'written instance to file {args.instance_path}')
    result = run_glucose(args.threads, F, timeout=args.timeout)
    if result:
        if result != 'timeout':
            check_and_save_result(result, symbols1, symbols2, tr, acc, tm, args.idx)
    print('unsat' if result is None else result)

if __name__ == '__main__':
    print(args)
    if args.mode == 'database':
        mode_database()
    if args.mode == 'index':
        mode_idx()

