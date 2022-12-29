import subprocess
import os
import threading
import random
from paths import GLUCOSE_PATH, TEMPFILE_DIR

def run_glucose(nthreads, formula, glucose_path=GLUCOSE_PATH, timeout=2e6):
    ''' runs glucose on given formula, number of threads and timeout given in seconds
        return value is:
        - 'timeout' if timeout happened,
        - None if unsat,
        - array e.g. [-1, 2, 3] if sat, where signs describe the assignment '''
    temp_file_path = f'{TEMPFILE_DIR}temp{random.randint(0, 10**10)}.txt'
    os.mkfifo(temp_file_path)
    result = []
    def thread1():
        with open(temp_file_path, 'w') as fil:
            formula.to_fp(fil)
    def thread2():
        try:
            cp = subprocess.run([glucose_path, f'-nthreads={nthreads}', '-model', temp_file_path], capture_output=True, timeout=timeout)
            if 'UNSATISFIABLE' in str(cp.stdout):
                result.append(None)
            else:
                raw_string = str(cp.stdout).split('\\n')[-2][2:-2]
                result.append( [int(x) for x in raw_string.split(' ')] )
        except:
            result.append('timeout')
    thr1 = threading.Thread(target=thread1, daemon=True)
    thr2 = threading.Thread(target=thread2, daemon=True)
    thr1.start()
    thr2.start()
    thr1.join()
    thr2.join()
    os.unlink(temp_file_path)
    return result[0]
