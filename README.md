# this repository is a huge mess

# Closed Tape Language solver

Based on `https://github.com/UncombedCoconut/bbchallenge/blob/main/dumb_dfa_decider.py` idea,
except we search for the right DFAs & 'acceptance table' using a SAT solver.
The main algorithm is in the file `sat2_cfl.py`.
### Dependencies: 
z3-solver, automata-lib (actually unused in the solver, just for doublechecking and non-essential stuff)

### Sample usage: 
The code assumes you had:
- compiled filegen.cpp by `g++ filegen.cpp -o filegen`
- made a `./datafiles/` directory with the files `all_5_states_undecided_machines_with_global_header` and `bb5_undecided_index`
Then you can run `python3 main.py n threads`, where `n` is the size of DFAs to be searched.

### Performance: 
with `n=4` and machines from the 1.5 million undecided index: 25 machines / second processed, around 66% of machines are proven to not halt.
