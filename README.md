# Closed Tape Language solver

A meet-in-the-middle CTL solver for Busy Beaver problem.
See here for a comprehensive description and another implementation:
`https://github.com/UncombedCoconut/bbchallenge-deciders/tree/finite-automata-reduction/decider-finite-automata-reduction`

The main algorithm is in the file `sat3_cfl.py`.
### Dependencies: 
- z3-solver
- automata-lib (actually unused in the solver, just for doublechecking and non-essential stuff)
- glucose SAT solver

### Sample usage: 
Fill out the paths in `paths.py` file. 

Then run the solver. There are two work modes.

- to try a single machine: `python3 main.py index DFA_size threads timeout_in_seconds --idx=idx_of_machine`. Example: 
`python3 main.py index 10 3 999 --idx=5884059` 

- To run on a set of machines: `python3 main.py database 10 3 999` - this will try to solve all machines using DFAs of size 10, again 3 is number of threads, and 999 is timeout in seconds. The script tries to avoid unnecessary work, i.e. if solution database already contains a proof, then the particular machine is skipped.
