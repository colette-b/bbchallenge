import argparse
import threading
import queue
import time
import random
from db_utils import *
import sat2_cfl
from sat3_cfl import *
from tqdm import tqdm
from glucose_wrapper import *

parser = argparse.ArgumentParser()
parser.add_argument('n', type=int)
parser.add_argument('threads', type=int)
args = parser.parse_args()

q = queue.Queue()
pbar = None

def worker():
    while True:
        time1 = time.time()
        idx = q.get()
        # print(f'{idx=}...')
        tm_code = get_machine_i(idx)
        time1half = time.time()
        #print(f'init\t{round(time1half - time1, 3)} s...')
        tm = TM(tm_code)
        #g, symbols1, symbols2, tr, acc = create_instance(args.n, tm)
        F, symbols1, symbols2, tr, acc = create_instance(args.n, tm, get_formula=True)
        time2 = time.time()
        #print(f'setup\t{round(time2 - time1half, 3)} s...')
        #_result = g.solve()
        result = run_glucose(GLUCOSE_PATH, 1, F, temp_file_path=f'./tempfiles/tempfile{threading.get_ident()}')
        time3 = time.time()
        #print(f'solve\t{round(time3 - time2, 3)} s...')
        # result = try_tm_via_binary(args.n, TM(tm_code), verbose=False, ctx=thread_ctx)
        if result:
            #assert _result
            arr1, arr2, acc_arr = model_to_short_description(result, symbols1, symbols2, tr, acc)
            sat2_cfl.verify_short_description(arr1, arr2, acc_arr, tm)
            write_to_proof_file(idx, args.n, f'{(arr1, arr2, acc_arr)}')
        else:
            #assert not _result
            write_to_proof_file(idx, args.n, 'unsat')
        #g.delete()
        pbar.update(1)
        q.task_done()
        time4 = time.time()
        #print(f'post\t{round(time4 - time3, 3)} s...')
        d1 = round(time1half - time1, 3)
        d2 = round(time2 - time1half, 3)
        d3 = round(time3 - time2, 3)
        d4 = round(time4 - time3, 3)
        print(d1, '\t', d2, '\t', d3, '\t', d4, '\t', 'sat' if result else 'unsat')

if __name__ == '__main__':
    all_unsolved = get_indices_from_index_file('./datafiles/bb5_undecided_index')
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
