## Imports

import sys, copy, time
from constraint_programming import constraint_program
sys.setrecursionlimit(10000)

## Lecture de l'entrée

# Cette lecture est nécessaire en dehors du main parce que les variables sont utilisées
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
if __name__ == '__main__':

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

    all_shapes = dict()
    SHAPES = dict()

    corners = {0, N - 1, (M - 1) * N, N * M - 1}  # Ensemble des coins

    FREE_PENTOMINOS = ["U", "V", "X", "Z", "N", "P", "T", "W", "F", "Y", "L", "I"]

    for shape_name, shape_matrix in shapes.items():
        shape_set = set()
        for modified_shape in get_all_shapes(shape_matrix[:]):
            shape_set.add(tuple(modified_shape))
        all_shapes[shape_name] = list(map(list, [map(list, line) for line in shape_set]))

    for shape in all_shapes:
        free_shapes = all_shapes[shape]
        translated = []
        for fs in free_shapes:
            translated += possibles(fs)
        SHAPES[shape] = set(translated)

    count = 0
    t = time.time()
    print_one = True

    # on sélectionne une forme à placer dans le coin en haut à gauche
    for index_top_left, shape_top_left in enumerate(FREE_PENTOMINOS):
        quintuplets_top_left = SHAPES[shape_top_left]

        # on sélectionne une forme à placer dans le coin en haut à droite
        for index_top_right in range(index_top_left + 1, len(FREE_PENTOMINOS)):
            shape_top_right = FREE_PENTOMINOS[index_top_right]
            quintuplets_top_right = SHAPES[shape_top_right]

            # on récupère uniquement les possibilités où la forme est effectivement en haut à gauche
            for quintuplet_top_left in quintuplets_top_left:
                if 0 in quintuplet_top_left:

                    # on récupère uniquement les possibilités où la forme est effectivement en haut à droite
                    for quintuplet_top_right in quintuplets_top_right:
                        if N - 1 in quintuplet_top_right:

                            ###
                            # On met à jour le domaines des variables de forme
                            ###

                            # on récupère les autres formes
                            VAR_SHAPES = copy.deepcopy(SHAPES)

                            del VAR_SHAPES[shape_top_left]
                            del VAR_SHAPES[shape_top_right]

                            # on supprime des autres formes les possibilités qui intersectent une des
                            # deux forme placée dans un coin
                            for shape_current, quintuplets_current in VAR_SHAPES.items():
                                _remove = set()
                                for quintuplet_current in quintuplets_current:
                                    if set(quintuplet_current).intersection(set(quintuplet_top_left)) \
                                            or set(quintuplet_current).intersection(quintuplet_top_right):
                                        _remove.add(quintuplet_current)
                                VAR_SHAPES[shape_current].difference_update(_remove)

                            ###
                            # On génère le domaines des variables de case
                            ###

                            # Les domaines sont restreints aux formes différentes de celles placées dans un coin

                            VAR_CELLS = dict()
                            for cell in range(N * M):
                                if cell not in quintuplet_top_left and cell not in quintuplet_top_right:
                                    VAR_CELLS[cell] = set(FREE_PENTOMINOS)
                                    VAR_CELLS[cell].remove(shape_top_left)
                                    VAR_CELLS[cell].remove(shape_top_right)

                            P = constraint_program({**copy.deepcopy(VAR_CELLS), **copy.deepcopy(VAR_SHAPES)})
                            P.set_arc_consistency()

                            ###
                            # Ajout des contraintes
                            ###

                            # Ces contraintes sont identiques à celles de l'approche naïve
                            # sauf qu'elles ne portent pas sur les formes que l'on a fixé.

                            for cell in range(N * M):
                                if cell not in quintuplet_top_left and cell not in quintuplet_top_right:
                                    for shape_current, quintuplets_current in VAR_SHAPES.items():
                                        setquint = set()
                                        for quintuplet_current in quintuplets_current:
                                            if cell in quintuplet_current and shape_current in VAR_CELLS[cell]:
                                                setquint.add((shape_current, quintuplet_current))

                                        for othershape in VAR_CELLS[cell]:
                                            for otherquintuplet in quintuplets_current:
                                                if othershape != shape_current and cell not in otherquintuplet:
                                                    setquint.add((othershape, otherquintuplet))
                                        if setquint:
                                            P.add_constraint(cell, shape_current, setquint)

                            for sol in P.solve_all():
                                # Si toute la colonne de gauche ET toute la colonne de droite sont recouvertes par
                                # une forme unique, on sait que l'on va retrouver ces solutions symétrisées.
                                # NB: en pratique cela ne se produit QUE pour le cas 3x20, qui est un cas avec
                                # tellement peu de solutions que cette méthode est solution : il ne sert à rien de
                                # modifier le solveur pour 2 solutions.
                                left = set(range(0, N * M, N))
                                right = set(range(N - 1, N * M, N))
                                if left.issubset(set(quintuplet_top_left)) and right.issubset(
                                        set(quintuplet_top_right)):
                                    count += 0.5
                                else:
                                    count += 1

                                # On rajoute à la solution les deux formes que l'on a fixé
                                for i in quintuplet_top_left:
                                    sol[i] = shape_top_left
                                for i in quintuplet_top_right:
                                    sol[i] = shape_top_right
                                sol[shape_top_left] = quintuplet_top_left
                                sol[shape_top_right] = quintuplet_top_right

                                if print_one:
                                    print_sol(sol)
                                    print_one = False

                            del P

        ###
        # Suppression des symétries
        ###

        # On enlève toutes les positions de la forme considérée qui couvrent un angle
        to_remove = set()
        for quintuplet_top_left in quintuplets_top_left:
            if set(quintuplet_top_left).intersection(corners):
                to_remove.add(quintuplet_top_left)
        SHAPES[shape_top_left].difference_update(to_remove)

    print('{}'.format(int(count)))

