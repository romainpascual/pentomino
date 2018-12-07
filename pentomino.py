#!usr/bin/env pypy

import sys
from constraint_programming import constraint_program

"""
En gros vous disposez de 12 formes appelés pentominos, composées chacune de 5 cases unitaires,
 que vous devez placer sur une grille composée de 60 cases. Les formes ne doivent pas se superposer,
  mais peuvent être tournées ou retournées.

Votre programme prendra en argument de ligne de commande une chaîne de la forme [m]x[n], indiquant 
les dimensions de la grille à paver. Les seules entrées possibles sont 6x10, 5x12, 4x15, 3x20. 
Puis votre programme devra afficher un pavage possible, sous forme d’un tableau de lettres, 
puis un entier indiquant le nombre de pavages au total, à symmétrie près.

Affichage attendu par votre programme.

./pentomino.py 6x10
IPPYYYYVVV
IPPXYLLLLV
IPXXXFZZLV
ITWXFFFZUU
ITWWNNFZZU
TTTWWNNNUU
2339

# m =6, n =10

Travail:

Comme il n’y a que 4 entrées possibles à votre code vous pourriez être tenté de les 
stocker dans le code et d’afficher la réponse demandée. Mais pour ce devoir maison on 
vous demande de calculer la solution à l’aide de notre solveur de programmation par contrainte.

Pour cela vous devez modéliser le problème de pavage. Décrivez votre modèle précisément 
dans un document qui accompagnera le code. Indiquez également comment vous avez éliminé 
les solutions symmétriques.

"""


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

[m,n] = [int(x) for x in sys.argv[1].split("x")]

F = [[1,2],[2],[1,1]]
F = [[0,1,1], [1,1,0], [0,1,0]]


def cell(i,j):
    """
    Renvoie la variable correspondant à la case i, j dans le tableau
    """
    return i * n + j

def possibles(forme):
    """
    Génère les 5 uplets possibles à partir d'une forme libre donnée comme une matrice

    Par exemple,
    F = [[0,1,1], [1,1,0], [0,1,0]]
    """

    uplets = []    
    rows,cols = len(forme), len(forme[0])

    cases = []

    for i in range(rows):
        for j in range(cols):
            if forme[i][j]:
                cases.append([i,j])

    for i in range(m - rows +1):
        for j in range(n-cols +1):
            uplets.append(set(map(lambda x:cell(x[0]+i,x[1]+j), cases)))
    
    return uplets
            


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

        if n*m != 60:
            print("invalid size")
        
        print(possibles(F))
        
    except:
        print("exception")

if __name__ == "__main__" :
    main(sys.argv)