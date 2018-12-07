#!usr/bin/env pypy

import sys
from constraint_programming import constraint_program

"""
    
    F:   ##
        ##
         #

    I:  #####    
    
    L:  ####
        #

    N:  ###
          ##

    P:  ###
         ##

    T:  #
        ###
        #

    U:  # #
        ###

    V:  ###
        #
        #

    W:  ##
         ##
          #

    X:   #
        ###
         #

    Z:  #
        ###
          #
"""

# formes possibles
rotation = { "F": [k for k in range(8)],
             "I": [k for k in range(8,10)],
             "L": [k for k in range(10,18)],
             "N": [k for k in range(18,26)],
             "P": [k for k in range(26,34)],
             "T": [k for k in range(34,38)],
             "U": [k for k in range(38,42)],
             "V": [k for k in range(42,46)],
             "W": [k for k in range(46,50)],
             "X": [50],
             "Y": [k for k in range(51,59)],
             "Z": [k for k in range(59,63)],
             }


def main(argv=[]):
    try:
        [m,n] = [int(x) for x in argv[1].split("x")]

        if n*m != 60:
            print("invalid size")
        
    except:
        print("exception")

if __name__ == "__main__" :
    main(sys.argv)