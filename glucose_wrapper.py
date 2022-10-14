import subprocess
import os
import threading
from sat3_cfl import *

GLUCOSE_PATH = '/home/konrad/Desktop/coding/solvers/glucose-4.2.1/sources/parallel/glucose-syrup_static'

def run_glucose(glucose_path, nthreads, F, temp_file_path='./dupabiskupa'):
    os.mkfifo(temp_file_path)
    result = []
    def thread1():
        with open(temp_file_path, 'w') as fil:
            F.to_fp(fil)
    def thread2():
        cp = subprocess.run([GLUCOSE_PATH, f'-nthreads={nthreads}', '-model', temp_file_path], capture_output=True)
        if 'UNSATISFIABLE' in str(cp.stdout):
            result.append(None)
        else:
            raw_string = str(cp.stdout).split('\\n')[-2][2:-2]
            result.append( [int(x) for x in raw_string.split(' ')] )
    thr1 = threading.Thread(target=thread1, daemon=True)
    thr2 = threading.Thread(target=thread2, daemon=True)
    thr1.start()
    thr2.start()
    thr1.join()
    thr2.join()
    os.unlink(temp_file_path)
    return result[0]

if __name__ == '__main__':
    #sample_machine_code = get_machine_i(9909955)
    #tm = TM(sample_machine_code)
    #F, symbols1, symbols2, tr, acc = create_instance(10, tm, get_formula=True)
    #result = run_glucose(GLUCOSE_PATH, 1, F)
    #print(result)

    solved = []
    for idx in TM_SKELET_LIST:
        sample_machine_code = get_machine_i(idx)
        tm = TM(sample_machine_code)
        F, symbols1, symbols2, tr, acc = create_instance(10, tm, get_formula=True)
        print(idx, '   \t', end='', flush=True)
        result = run_glucose(GLUCOSE_PATH, 3, F)
        print("1" if result else "0")
        if result:
            solved.append(idx)
            dfa1, dfa2, acc = model_to_short_description(result, symbols1, symbols2, tr, acc)
            print(dfa1, dfa2, acc)
            sat2_cfl.verify_short_description(dfa1, dfa2, acc, tm)
    print(len(solved))
    print(solved)
