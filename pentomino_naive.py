#!usr/bin/env pypy

## Description du Problème
    
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

#ici, m =6, n =10

Travail:

Comme il n’y a que 4 entrées possibles à votre code vous pourriez être tenté de les 
stocker dans le code et d’afficher la réponse demandée. Mais pour ce devoir maison on 
vous demande de calculer la solution à l’aide de notre solveur de programmation par contrainte.

Pour cela vous devez modéliser le problème de pavage. Décrivez votre modèle précisément 
dans un document qui accompagnera le code. Indiquez également comment vous avez éliminé 
les solutions symmétriques.

"""


## Imports

import sys, time
from constraint_programming import constraint_program
sys.setrecursionlimit(10000)



## Dessin des différentes formes

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
         
    Y:  #
        ##
        #
        #
         
    Z:  #
        ###
          #
          
"""


## Lecture de l'entrée

# Cette lecture est nécéssaire en dehors du main parce que les variables sont utilisées
# dans d'autres fonctions

try:
    [M, N] = [int(x) for x in sys.argv[1].split("x")]
    if N*M != 60:
        print("Invalid Size")
        sys.exit(1)
except IndexError:
    print("Invalid args.")
    sys.exit(1)


## Fonction d'affichage

def print_sol(sol):
    """
    Cette fonction permet d'afficher une solution dans la forme demandée.
    """
    table_sol = [[None for _ in range(N)] for __ in range(M)]
    for cell in sol:
        if type(cell) is int:
            table_sol[cell//N][cell%N] = sol[cell]
    for line in table_sol:
        print(''.join(line))


## Fonction pour la génération des variables et des contraintes.
        
def cell(i, j):
    """
    Renvoie la variable correspondant à la case i, j dans le tableau.
    """
    return i * N + j


def possibles(forme):
    """
    Génère les 5 uplets possibles à partir d'une forme libre donnée comme une matrice.

    Par exemple,
    F = [[0,1,1], [1,1,0], [0,1,0]]
    """

    uplets = set()
    rows, cols = len(forme), len(forme[0])

    cases = []

    for i in range(rows):
        for j in range(cols):
            if forme[i][j]:
                cases.append([i, j])

    for i in range(M - rows + 1):
        for j in range(N-cols + 1):
            uplets.add(frozenset(map(lambda x: cell(x[0]+i, x[1]+j), cases)))
    return set(map(tuple, map(sorted, map(tuple, uplets))))


def get_all_shapes(shape_matrix):
    """
    Cette fonction prend les formes et retourne les rotations et les symétries
    """
    # Il suffit de construire le symétrique puis de faire tourner les deux possibilités
    
    # Symétrie de l'axe Y
    symmetric_matrix = shape_matrix[::-1] 
    
    # Rotation de la matrice
    for _ in range(4):
        shape_matrix = list(zip(*shape_matrix[::-1]))
        symmetric_matrix = list(zip(*symmetric_matrix[::-1]))
        yield shape_matrix
        yield symmetric_matrix


## Main fonction pour résoudre le problème du pavage par pentomino
def main(argv=[]):
    """
    Fonction principale : créer le CSP, ses variables, ses contraintes et le résout à l'aide du solveur dédié
    """

    ###
    # On génère le domaines des variables de forme
    ###
    
    shapes = {
        'F': [[0, 1, 1], [1, 1, 0], [0, 1, 0]],
        'I': [[1, 1, 1, 1, 1]],
        'L': [[1, 1, 1, 1], [1, 0, 0, 0]],
        'N': [[1, 1, 1, 0], [0, 0, 1, 1]],
        'P': [[1, 1, 1], [0, 1, 1]],
        'T': [[1, 0, 0], [1, 1, 1], [1, 0, 0]],
        'U': [[1, 0, 1], [1, 1, 1]],
        'V': [[1, 1, 1], [1, 0, 0], [1, 0, 0]],
        'W': [[1, 1, 0], [0, 1, 1], [0, 0, 1]],
        'X': [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
        'Y': [[1, 0], [1, 1], [1, 0], [1, 0]],
        'Z': [[1, 0, 0], [1, 1, 1], [0, 0, 1]]}
    
    # Dictionnaire auxiliaire, clé = forme (F, I, L, etc), valeur = configurations (sous la forme d'une matrice
    all_shapes = dict()
    
    # Dictionnaire clé = formes, valeurs = quintuplets de cases possibles (sous la forme de tuples)
    SHAPES = dict()
    
    # formes possibles
    FREE_PENTOMINOS = ["F","I","L","N","P","T","U","V","W","X","Y","Z"]

    # Génère tous les pentominos possibles (rotations, symétries)
    # Les divers changements de types sont nécessaires car un tuple n'est pas mutable et un set n'est pas hashable
    for shape_name, shape_matrix in shapes.items():
        shape_set = set()
        for modified_shape in get_all_shapes(shape_matrix[:]):
            shape_set.add(tuple(modified_shape))
        all_shapes[shape_name] = list(map(list, [map(list, line) for line in shape_set]))

    # A partir des configurations, on génère les quintuplets possibles par translation
    for shape in all_shapes:
        free_shapes = all_shapes[shape]
        translated = []
        for fs in free_shapes:
            translated += possibles(fs)
        SHAPES[shape] = set(translated)

    ###
    # On génère le domaines des variables de case
    ###
        
    CELL = dict()
    for cell in range(N*M):
        CELL[cell] = set()


    for shape, quintuplets in SHAPES.items():
        for quintuplet in quintuplets:
            for cell in quintuplet:
                CELL[cell].update({shape})
    
    ###
    # Création du CSP
    ###
    
    P = constraint_program({**CELL, **SHAPES})
    P.set_arc_consistency()

    ###
    # Ajout des contraintes
    ###

    for cell in range(N*M):
        for shape, quintuplets in SHAPES.items():
            setquint = set()
            for quintuplet in quintuplets:
            
                # Soit la cellule est dans la forme et la forme contient la cellule
                if cell in quintuplet and shape in CELL[cell]:
                    setquint.add((shape, quintuplet))

            for othershape in CELL[cell]:
                for otherquintuplet in quintuplets:
                    
                    # Soit la cellule n'est pas dans la forme et la forme ne contient pas la cellule
                    if othershape != shape and cell not in otherquintuplet:
                        setquint.add((othershape, otherquintuplet))
            
            # mise a jour
            if setquint:
                    P.add_constraint(cell, shape, setquint)

    # compteur de solution
    count = 0
    
    # pour n'afficher qu'une seule solution
    print_one = True
    
    print('Solving {}x{}...'.format(M,N))
    
    # On enregistre le temps d'exécution
    t = time.time()
    for sol in P.solve_all():
        count += 1
        if print_one:
            print('Time for sol. n˚{} : {:.2f}'.format(count, time.time()-t))
            print_sol(sol)
            print_one = False
    print('Solved in a total time of: {:.2f}s'.format(time.time() - t))
    print('Final count: {} solutions'.format(count//4))


if __name__ == '__main__':
    main()

