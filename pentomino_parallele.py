# coding: utf-8 

import sys
import copy
import time

from constraint_programming import constraint_program

from multiprocessing import Pool, Value

sys.setrecursionlimit(10000)

try:
    [M, N] = [int(x) for x in sys.argv[1].split("x")]
except IndexError:
    print("Invalid args.")
    sys.exit(1)


def init_has_printed(value):
    """
    Cette fonction ne sert qu'a initialiser le partage de la variable 
    commandant l'affichage dans notre multi-threading.
    """
    global has_printed
    has_printed = value


def print_sol(sol):
    """
    Cette fonction permet d'afficher une solution dans la forme demandée.
    """
    global has_printed
    if not has_printed.value:
        table_sol = [[None for _ in range(N)] for __ in range(M)]
        for cell in sol:
            if type(cell) is int:
                table_sol[cell//N][cell%N] = sol[cell]
        for line in table_sol:
            print(''.join(line))
        has_printed.value = 1


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
    # yielding rotated matrix
    symmetric_matrix = shape_matrix[::-1]  # Symétrie de l'axe Y
    for _ in range(4):
        shape_matrix = list(zip(*shape_matrix[::-1]))  # Rotation de la matrice
        symmetric_matrix = list(zip(*symmetric_matrix[::-1]))
        yield shape_matrix
        yield symmetric_matrix


def solve_top_right(quintuplet_top_right):
    """
    Cette fonction est lancée dans le main.
    Elle vise à retourner le nombre de solutions possibles d'une configuration
    telle que la forme en haut à gauche et la forme en haut à droite est fixée.
    """
    count_local = 0  # Compteur des solutions dans cette configuration particulière
    if N - 1 in quintuplet_top_right:

        VAR_SHAPES = copy.deepcopy(SHAPES)  # Variables correspondant aux formes qui va être utilisée dans le solveur

        # On sait déjà quelles seront les formes en haut à droite et en haut à gauche,
        # on ne les considérera donc pas dans le solveur.
        del VAR_SHAPES[shape_top_left]
        del VAR_SHAPES[shape_top_right]

        # On enlève du domaine des autres variables formes tous les dispositions
        # qui intersectent les formes que nous avons fixées
        for shape_current, quintuplets_current in VAR_SHAPES.items():
            _remove = set()
            for quintuplet_current in quintuplets_current:
                if set(quintuplet_current).intersection(set(quintuplet_top_left)) \
                        or set(quintuplet_current).intersection(quintuplet_top_right):
                    _remove.add(quintuplet_current)
            VAR_SHAPES[shape_current].difference_update(_remove)

        # On crée le domaine des variables cases.
        # La case ne peut pas être de la même forme que le pentomino en haut à gauche et en haut à droite.
        VAR_CELLS = dict()
        for cell in range(N * M):
            VAR_CELLS[cell] = set(FREE_PENTOMINOS)
            VAR_CELLS[cell].remove(shape_top_left)
            VAR_CELLS[cell].remove(shape_top_right)

        # On sait déjà quelle est la forme dans les cases en haut à droite et à gauche,
        # on ne les considérera donc pas dans le solveur.
        for cell in quintuplet_top_left:
            del VAR_CELLS[cell]
        for cell in quintuplet_top_right:
            del VAR_CELLS[cell]

        # On crée le solveur de contraintes
        P = constraint_program({**copy.deepcopy(VAR_CELLS), **copy.deepcopy(VAR_SHAPES)})
        P.set_arc_consistency()

        # Le bloc suivant ajoute les contraintes au solveur
        for cell in range(N * M):
            if cell not in quintuplet_top_left and cell not in quintuplet_top_right:
                for shape_current, quintuplets_current in VAR_SHAPES.items():
                    setquint = set()
                    for quintuplet_current in quintuplets_current:
                        if cell in quintuplet_current and shape_current in VAR_CELLS[cell]:
                            # Si la cellule C étudiée est recouverte par la forme F,
                            # alors F est un quintuplet qui doit contenir C
                            setquint.add((shape_current, quintuplet_current))

                    for othershape in VAR_CELLS[cell]:
                        for otherquintuplet in quintuplets_current:
                            if othershape != shape_current and cell not in otherquintuplet:
                                # Si la cellule C étudiée n'est pas recouverte par la forme F,
                                # alors F est un quintuplet qui ne doit pas contenir C.
                                setquint.add((othershape, otherquintuplet))
                    if setquint:
                        P.add_constraint(cell, shape_current, setquint)

        for sol in P.solve_all():  # Pour chaque solution
            count_local += 1  # On compte une solution en plus

            # On rajoute les formes fixées à la solution
            for i in quintuplet_top_left:
                sol[i] = shape_top_left
            for i in quintuplet_top_right:
                sol[i] = shape_top_right
            sol[shape_top_left] = quintuplet_top_left
            sol[shape_top_right] = quintuplet_top_right

            print_sol(sol)
        del P

        # Si toute la colonne de gauche ET toute la colonne de droite sont recouvertes par une forme unique, on sait que
        # l'on va retrouver ces solutions symétrisées.
        # NB: en pratique cela ne se produit QUE pour le cas 3x20, qui est un cas avec tellement peu de solutions que
        # cette méthode est solution : il ne sert à rien de modifier le solveur pour 2 solutions.
        left = set(range(0, N*M, N))
        right = set(range(N-1, N*M, N))
        if left.issubset(set(quintuplet_top_left)) and right.issubset(set(quintuplet_top_right)):
            count_local /= 2

        return count_local


if __name__ == '__main__':
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
    SHAPES = dict()  # Dictionnaire clé = formes, valeurs = quintuplets de cases possibles

    corners = {0, N - 1, (M - 1) * N, N * M - 1}  # Ensemble des coins

    FREE_PENTOMINOS = ["U", "V", "X", "Z", "N", "P", "T", "W", "F", "Y", "L", "I"]  # formes possibles

    has_printed = False  # Cette variable permet d'afficher une seule solution
    count = 0  # Compteur des solutions

    assert N * M == 60  # On vérifie que le rectangle est de taille valide

    t = time.time()

    for shape_name, shape_matrix in shapes.items():  # Génère tous les pentominos possibles (rotations, symétries)
        shape_set = set()
        for modified_shape in get_all_shapes(shape_matrix[:]):
            shape_set.add(tuple(modified_shape))
        all_shapes[shape_name] = list(map(list, [map(list, line) for line in shape_set]))

    for shape in all_shapes:  # Cette boucle génère tous les quintuplets de placement valides pour les pentominos
        free_shapes = all_shapes[shape]
        l = []
        for fs in free_shapes:
            l += possibles(fs)
        SHAPES[shape] = set(l)

    for index_top_left, shape_top_left in enumerate(FREE_PENTOMINOS):

        # On itère sur tous les pentominos (pour fixer le coin supérieur gauche)
        quintuplets_top_left = SHAPES[shape_top_left]
        for index_top_right in range(index_top_left + 1, len(FREE_PENTOMINOS)):

            # On itère sur tous les pentominos restants (pour fixer le coin supérieur droit)
            shape_top_right = FREE_PENTOMINOS[index_top_right]
            quintuplets_top_right = SHAPES[shape_top_right]
            for quintuplet_top_left in quintuplets_top_left:

                # On sélectionne dans cette boucle une configuration du pentomino supérieur gauche
                if 0 in quintuplet_top_left:

                    # On vérifie bien sur que cette configuration peut aller dans le coin supérieur gauche

                    # Le test suivant sert à initialiser le multiprocessing
                    # afin de savoir s'il faudra afficher une solution
                    if not has_printed:
                        has_printed = Value('i', 0)
                    else:
                        has_printed = Value('i', 1)

                    # Les instructions suivantes multiprocessent la suite de notre résolution
                    # et récupèrent le nombre de solutions trouvées
                    pool = Pool(initializer= init_has_printed, initargs=(has_printed,))
                    count_list = pool.map(solve_top_right, quintuplets_top_right)
                    pool.close()
                    pool.join()
                    count += sum(filter(None, count_list))
                    if count != 0:
                        has_printed = True
                    else:
                        has_printed = False

        # Maintenant que l'on a testé toutes les solutions possibles avec une forme en haut à gauche,
        # il ne sera possible de l'obtenir dans un coin seulement s'il l'on obtient une solution symétrique,
        # ce que l'on ne veut pas.
        # On enlève donc cette forme des coins.
        to_remove = set()
        for quintuplet_top_left in quintuplets_top_left:
            if set(quintuplet_top_left).intersection(corners):
                to_remove.add(quintuplet_top_left)
        SHAPES[shape_top_left].difference_update(to_remove)

    print(int(count))
    print('Solved in a total time of: {:.2f}s'.format(time.time() - t))

