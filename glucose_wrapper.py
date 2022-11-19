import subprocess
import os
import threading
from sat3_cfl import *
from paths import GLUCOSE_PATH, TEMPFILE_DIR

def run_glucose(glucose_path, nthreads, formula, timeout=1e9):
    temp_file_path = f'{TEMPFILE_DIR}temp{random.randint(0, 10**20)}.txt'
    os.mkfifo(temp_file_path)
    result = []
    def thread1():
        with open(temp_file_path, 'w') as fil:
            formula.to_fp(fil)
    def thread2():
        try:
            cp = subprocess.run([GLUCOSE_PATH, f'-nthreads={nthreads}', '-model', temp_file_path], capture_output=True, timeout=timeout)
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
