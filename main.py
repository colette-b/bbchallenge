import argparse
import threading
import queue
import time
import random
from db_utils import *
from sat2_cfl import *
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('n', type=int)
parser.add_argument('threads', type=int)
args = parser.parse_args()

q = queue.Queue()
pbar = None

def worker():
    thread_ctx = z3.Context()
    while True:
        idx = q.get()

        # print(f'{idx=}...')
        tm_code = get_machine_i(idx)
        result = try_tm_via_binary(args.n, TM(tm_code), verbose=False, ctx=thread_ctx)
        if result:
            arr1, arr2, acc_arr = result
            write_to_proof_file(idx, args.n, f'{(arr1, arr2, acc_arr)}')
        else:
            write_to_proof_file(idx, args.n, 'unsat')
        pbar.update(1)
        q.task_done()

if __name__ == '__main__':
    all_unsolved = get_indices_from_index_file('./datafiles/bb5_undecided_index')
    infodict = read_proof_file()
    proof_file_info()
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
