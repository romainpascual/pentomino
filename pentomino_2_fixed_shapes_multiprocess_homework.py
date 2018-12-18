#!usr/bin/env pypy

import sys
from constraint_programming import constraint_program

import time
import copy

from multiprocessing import Pool, Value

import os
normal_stdout = sys.stdout

sys.setrecursionlimit(10000)

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
    
    F:   ##     12
        ##      2
         #      11

    I:  #####   5
    
    L:  ####    4
        #       1

    N:  ###     3
          ##    22

    P:  ###     3
         ##     12

    T:  #       1
        ###     3
        #       1

    U:  # #     111
        ###     3

    V:  ###     3
        #       1
        #       1

    W:  ##      2
         ##     12
          #     21

    X:   #      11
        ###     3
         #      11
         
    Y:  #       1
        ##      2
        #       1
        #       1
         
    Z:  #       1
        ###     3
          #     21
"""

try:
    [M,N] = [int(x) for x in sys.argv[1].split("x")]
except IndexError:
    print("Invalid args")
    exit()

corners = set([0,N-1, (M-1)*N, N*M-1])


def cell(i,j):
    """
    Renvoie la variable correspondant à la case i, j dans le tableau
    """
    return i * N + j

def possibles(forme):
    """
    Génère les 5 uplets possibles à partir d'une forme libre donnée comme une matrice

    Par exemple,
    F = [[0,1,1], [1,1,0], [0,1,0]]
    """

    uplets = set()
    rows,cols = len(forme), len(forme[0])

    cases = []

    for i in range(rows):
        for j in range(cols):
            if forme[i][j]:
                cases.append([i,j])

    for i in range(M - rows +1):
        for j in range(N-cols +1):
            uplets.add(frozenset(map(lambda x:cell(x[0]+i,x[1]+j), cases)))
    return set(map(tuple, map(sorted, map(tuple, uplets))))


shapes = {
    'F': [[1, 2], [2], [1, 1]],
    'I': [[5]],
    'L': [[4], [1]],
    'N': [[3], [2, 2]],
    'P': [[3], [1, 2]],
    'T': [[1], [3], [1]],
    'U': [[1, 1, 1], [3]],
    'V': [[3], [1], [1]],
    'W': [[2], [1, 2], [2, 1]],
    'X': [[1, 1], [3], [1, 1]],
    'Y': [[1], [2], [1], [1]],
    'Z': [[1], [3], [2, 1]]
}

# formes possibles
FREE_PENTOMINOS = ["U","V","X","Z","N","P","T","W","F","Y","L","I"]

SHAPES = dict()

has_printed = False

def init_has_printed(value):
    global has_printed
    has_printed = value

def print_sol(sol):
    global has_printed
    if not has_printed.value:
        table_sol = [[None for _ in range(N)] for __ in range(M)]
        for cell in sol:
            if type(cell) is int:
                table_sol[cell//N][cell%N] = sol[cell]
        for line in table_sol:
            print(''.join(line))
        has_printed.value = 1


def compactmat_to_mat(shape):
    shape_matrix = []
    max_length = 0
    for line_count, line in enumerate(shape):
        line = line[:]
        shape_matrix.append([])
        while line:
            if len(line)%2 == 1:
                number = line.pop(0)
                shape_matrix[line_count].extend([1 for _ in range(number)])
            else:
                number = line.pop(0)
                shape_matrix[line_count].extend([0 for _ in range(number)])
        max_length = max(max_length, len(shape_matrix[line_count]))
    for line in shape_matrix:
        while len(line) < max_length:
            line.append(0)
    return shape_matrix


def get_all_shapes(shape_matrix):
    # yielding rotated matrix
    symmetric_matrix = shape_matrix[::-1]  # Y axis symmetry
    for _ in range(4):
        shape_matrix = list(zip(*shape_matrix[::-1]))  # rotate matrix
        symmetric_matrix = list(zip(*symmetric_matrix[::-1]))
        yield shape_matrix
        yield symmetric_matrix


def solve_top_right(quintuplet_top_right):
    count_local = 0
    if N - 1 in quintuplet_top_right:
        VAR_SHAPES = copy.deepcopy(SHAPES)

        del VAR_SHAPES[shape_top_left]
        del VAR_SHAPES[shape_top_right]

        for shape_current, quintuplets_current in VAR_SHAPES.items():
            _remove = set()
            for quintuplet_current in quintuplets_current:
                if set(quintuplet_current).intersection(set(quintuplet_top_left)) \
                        or set(quintuplet_current).intersection(quintuplet_top_right):
                    _remove.add(quintuplet_current)
            VAR_SHAPES[shape_current].difference_update(_remove)

        VAR_CELLS = dict()
        for cell in range(N * M):
            VAR_CELLS[cell] = set(FREE_PENTOMINOS)
            VAR_CELLS[cell].remove(shape_top_left)
            VAR_CELLS[cell].remove(shape_top_right)

        for cell in quintuplet_top_left:
            del VAR_CELLS[cell]
        for cell in quintuplet_top_right:
            del VAR_CELLS[cell]

        P = constraint_program({**copy.deepcopy(VAR_CELLS), **copy.deepcopy(VAR_SHAPES)})
        P.set_arc_consistency()

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

        t2 = time.time()
        for sol in P.solve_all():
            count_local += 1
            for i in quintuplet_top_left:
                sol[i] = shape_top_left
            for i in quintuplet_top_right:
                sol[i] = shape_top_right
            sol[shape_top_left] = quintuplet_top_left
            sol[shape_top_right] = quintuplet_top_right
            print_sol(sol)
            t2 = time.time()
        del P
        return count_local



if __name__ == '__main__':
    all_shapes = dict()
    count = 0

    try:
        if N * M != 60:
            print("invalid size")

    except Exception as e:
        print("exception ", e)

    for shape_name, shape in shapes.items():
        shape_matrix = compactmat_to_mat(shape[:])
        shape_set = set()
        for modified_shape in get_all_shapes(shape_matrix[:]):
            shape_set.add(tuple(modified_shape))
        all_shapes[shape_name] = list(map(list, [map(list, line) for line in shape_set]))

    for shape in all_shapes:
        free_shapes = all_shapes[shape]
        l = []
        for fs in free_shapes:
            l += possibles(fs)
        SHAPES[shape] = set(l)

    count = 0
    t = time.time()

    for index_top_left, shape_top_left in enumerate(FREE_PENTOMINOS):
        quintuplets_top_left = SHAPES[shape_top_left]
        for index_top_right in range(index_top_left + 1, len(FREE_PENTOMINOS)):
            shape_top_right = FREE_PENTOMINOS[index_top_right]
            quintuplets_top_right = SHAPES[shape_top_right]
            for quintuplet_top_left in quintuplets_top_left:
                if 0 in quintuplet_top_left:
                    if not has_printed:
                        has_printed = Value('i', 0)
                    else:
                        has_printed = Value('i', 1)
                    pool = Pool(initializer= init_has_printed, initargs=(has_printed,))
                    count_list = pool.map(solve_top_right, quintuplets_top_right)
                    pool.close()
                    pool.join()
                    count += sum(filter(None, count_list))
                    has_printed = True

        # remove shape_top_left from corners
        to_remove = set()
        for quintuplet_top_left in quintuplets_top_left:
            if set(quintuplet_top_left).intersection(corners):
                to_remove.add(quintuplet_top_left)
        SHAPES[shape_top_left].difference_update(to_remove)

    sys.stdout = normal_stdout
    print(count)

