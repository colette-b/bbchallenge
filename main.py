from db_utils import *
from sat2_cfl import *
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('n', type=int)
args = parser.parse_args()

if __name__ == '__main__':
    all_unsolved = get_indices_from_index_file('./datafiles/bb5_undecided_index')
    infodict = read_proof_file()
    proof_file_info()
    for idx in tqdm(all_unsolved):
        if is_already_solved(idx, infodict):
            continue
        if args.n in infodict[idx]:
            continue
        # print(f'{idx=}...')
        tm_code = get_machine_i(idx)
        result = try_tm_via_binary(args.n, TM(tm_code))
        if result:
            arr1, arr2, acc_arr = result
            write_to_proof_file(idx, args.n, f'{(arr1, arr2, acc_arr)}')
        else:
            write_to_proof_file(idx, args.n, 'unsat')
