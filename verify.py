from tm_utils import *
from sat2_utils import verify_dfa_pair
from db_utils import get_machine_i
from sys import argv

if __name__ == '__main__':
    idx = int(argv[1])
    arr1 = eval(argv[2])
    arr2 = eval(argv[3])
    tm = TM(get_machine_i(324))
    print(verify_dfa_pair(arr1, arr2, tm))