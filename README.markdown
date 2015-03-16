# Automated Theorem Prover
A theorem prover for Reasoning at The University of Birmingham.

# Running
The theorem prover was programmed using Python 3. It can be run in the labs'
Linux machines using the command `python3.4 tp.py`. Running the program without
arguments will show the available flags.

# zip
Included in the zip are this README, the source code and the git repository
containing these files.

# Code structure
The imported libraries are `re` for regex, `argparse` and `sys` for parsing
command line arguments.

## Part 1
The program parses the input and converts it into an AST in `parse()` so
implication, equivalence, De Morgan, double negation and distributivity
disjunction can be applied easily with `trav1()`, `trav2()` and `trav3()` in
`cnfize()`. When the AST is in the right format, clauses are added to a set
structure in `clauses()`. The CNF is always shown on screen and can be saved to
file in the DIMACS format using the flag `--save` followed by an optional
filename (defaults to "cnf.cnf"). The parsing process can be shown explicitly
using the flag `-p`. The `--cnf` flag is used to output the CNF and quit,
skipping the resolution process.

## Part 2
The resolution rule is applied repeatedly in `resolve()` until the resolvent is
the empty set, outputting "Unsatisfiable" or no more resolutions can be done,
outputting "Satisfiable".

## Part 3 (option 1)
In `optimise()`, using the `-s` flag, subsumption steps are applied before the
resolution procedure starts. Using the `-o` flag, clauses are ordered by length
so unit literals will always be resolved when possible. Set of Support wasn't
implemented.
