* Closed Tape Language solver

* Dependencies: z3-solver, automata-lib (actually unused in the solver, just for doublechecking and non-essential stuff)

Based on `https://github.com/UncombedCoconut/bbchallenge/blob/main/dumb_dfa_decider.py` idea,
except we search for the right DFAs & 'acceptance table' using a SAT solver.
The main algorithm is in the file `sat2_cfl.py`.

* Sample usage: `python3 sat2_cfl.py`.

* Performance: tested on random 1000 machines from the 3.5 million undecided index: 969 solved & 31 unsolved in about 15 minutes.

* Todos:
- add more conditions for 'desymmetrizing' the constraints for SAT solver,
- move from python to another language. The z3<->python interface is highly inefficient,
and currently more time is spent 'writing down' the constraints than actually solving.
