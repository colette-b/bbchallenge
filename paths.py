# path to glucose solver executable
GLUCOSE_PATH = '/usr/bin/glucose-syrup'
# some empty directory
TEMPFILE_DIR = './tempfiles/'
# undecided index
UNDECIDED_INDEX = './datafiles/bb5_undecided_index'
# machines db file
MACHINES_DB_FILE = './datafiles/all_5_states_undecided_machines_with_global_header'
# a file where proofs will be dumped, can be just any initially empty file
CTL_PROOF_FILE = './datafiles/cfl_proofs.txt'

# please end the tempfile directory with a slash
assert TEMPFILE_DIR[-1] == '/'
