# GGenPSAT
GGenPSAT solver
* decides the satisfiability of Boolean combinations of linear inequalities involving probabilities of classical propositional formulas. In other words, it's a satisfiability solver for Fagin et al. probabilistic logic [2]


## Requires
* python
* yices

## Run
Use `python ggenpsat.py -i ifile -o ofile` to run the program on
* input file ifile

and
* output the the smt-lib translation file ofile.

## Input file format
The solver accepts input files in a similar format to standard smt-lib:


One example of this format is the following

```
(define x::Bool)
(define y::Bool)

(assertprop (or (not x) x))

(assert (or (= (pr y) 0) (= (pr y) 1)))
(assert (= (pr (not (<=> (xor x y) y))) (/ 1 2)))
(check)
```

which corresponds to the GGenPSAT problem

![genpsat](https://github.com/fcasal/ggenpsat/blob/master/img/ex1.jpg?raw=true)

## Releases
* v0.1 -- Initial release in December 2016

## References
* C. Caleiro, F. Casal, and A. Mordido. _Classical Generalized probabilistic satisfiability_. [Preprint](http://sqig.math.ist.utl.pt/pub/CaleiroC/16-CCM-ggenpsat.pdf), SQIG - IT and IST - U Lisboa, 1049-001 Lisboa, Portugal, 2016.
* R. Fagin, J. Y. Halpern, and N. Megiddo. _A logic for reasoning about probabilities_. Inf. Comput., 87(1-2):78–128, 1990.
