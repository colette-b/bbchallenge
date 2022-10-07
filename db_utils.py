import os

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
