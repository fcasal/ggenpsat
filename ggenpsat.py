
# import sys
from parser import *
import argparse

def main():
    parser = argparse.ArgumentParser(description = "Classical Generalized Probabilistic SAT solver")
    parser.add_argument("--input", "-i", dest = "inp")
    parser.add_argument("--output", "-o", dest = "out")

    args = parser.parse_args()
    ggenpsat(args.inp, args.out)

if __name__ == "__main__":
    main()
