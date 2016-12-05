
# import sys
from parser import *
import parserz3
import argparse

def main():
    parser = argparse.ArgumentParser(description = "Classical Generalized Probabilistic SAT solver")
    parser.add_argument("--input", "-i", dest = "inp")
    parser.add_argument("--output", "-o", dest = "out")
    parser.add_argument("--z3", "-z3", dest = "solver")

    args = parser.parse_args()
    print args.solver
    if args.solver == None:
        ggenpsat(args.inp, args.out)
    else:
        parserz3.ggenpsat(args.inp, args.out)

if __name__ == "__main__":
    main()
