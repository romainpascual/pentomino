#!usr/bin/env pypy

import sys
from constraint_programming import constraint_program

import time
import copy

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init(autoreset=True)

    COLOR = {'X': Style.RESET_ALL + Back.CYAN + Fore.BLACK + 'X',
             'L': Style.RESET_ALL + Back.LIGHTYELLOW_EX + Fore.BLACK + 'L',
             'V': Style.RESET_ALL + Back.LIGHTMAGENTA_EX + Fore.BLACK + 'V',
             'I': Style.RESET_ALL + Back.MAGENTA + 'I',
             'N': Style.RESET_ALL + Back.LIGHTBLUE_EX + 'N',
             'P': Style.RESET_ALL + Back.LIGHTGREEN_EX + Fore.RED + 'P',
             'T': Style.RESET_ALL + Back.RED + Fore.BLACK + 'T',
             'U': Style.RESET_ALL + Back.WHITE + Fore.BLACK + 'U',
             'F': Style.RESET_ALL + Back.BLUE + 'F',
             'W': Style.RESET_ALL + Back.YELLOW + Fore.BLACK + 'W',
             'Y': Style.RESET_ALL + Back.LIGHTCYAN_EX + Fore.BLACK + 'Y',
             'Z': Style.RESET_ALL + 'Z',
             ' ': Style.RESET_ALL + ' '
             }

except ModuleNotFoundError:
    COLOR = {'X': 'X',
             'L': 'L',
             'V': 'V',
             'I': 'I',
             'N': 'N',
             'P': 'P',
             'T': 'T',
             'U': 'U',
             'F': 'F',
             'W': 'W',
             'Y': 'Y',
             'Z': 'Z'
             }


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
FREE_PENTOMINOS = ["U","V","X","I","N","P","T","L","F","W","Y","Z"]

FORM = dict()

VAR = {}

for k in range(M*N):
    VAR[k]=set(FREE_PENTOMINOS)

P = constraint_program(VAR)


def print_shape(shape):
    printstring = ''
    for line in shape:
        while line:
            if len(line)%2 == 1:
                number = line.pop(0)
                printstring += '#'*number
            else:
                number = line.pop(0)
                printstring += ' '*number
        printstring += '\n'
    print(printstring[:-1])

def print_sol(sol):
    table_sol = [[None for _ in range(N)] for __ in range(M)]
    for cell in sol:
        if type(cell) is int:
            table_sol[cell//N][cell%N] = COLOR[sol[cell]]
    for line in table_sol:
        print(''.join(line))



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

    # print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in shape_matrix]))
    # print('-'*12)




def get_all_shapes(shape_matrix):
    # yielding rotated matrix
    symmetric_matrix = shape_matrix[::-1]  # Y axis symmetry
    for _ in range(4):
        shape_matrix = list(zip(*shape_matrix[::-1]))  # rotate matrix
        symmetric_matrix = list(zip(*symmetric_matrix[::-1]))
        yield shape_matrix
        yield symmetric_matrix
    # translated = shape_matrix[::-1]  # Y axis symmetry
    # translatedXY [line[::-1] for line in shape_matrix][::1]  # X and Y symmetry

# for forme in shapes:
#     repr_to_mat(forme[:])

def mat_to_compactmat(shape_matrix):

    compactmat = []
    for line_count, line in enumerate(shape_matrix[:]):
        line = line[:]
        compactmat.append([])
        while line[-1] == 0:
            line.pop()
        last_char = line[0]
        count = 0
        while line:
            current_char = line.pop(0)
            if current_char != last_char:
                compactmat[line_count].append(current_char * count)
                last_char = current_char
                count = 0
            count+=1
        if current_char == 1:
            compactmat[line_count].append(current_char * count)
    return compactmat

def main(argv=[]):
    all_shapes = dict()

    try:
        if N*M != 60:
            print("invalid size")

    except Exception as e:
        print("exception ",e)

    for shape_name, shape in shapes.items():
        shape_matrix = compactmat_to_mat(shape[:])
        shape_set = set()
        for modified_shape in get_all_shapes(shape_matrix[:]):
            # print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in modified_shape]))
            shape_set.add(tuple(modified_shape))
        all_shapes[shape_name] = list(map(list, [map(list, line) for line in shape_set]))

    # for shape_name, shape_set in all_shapes.items():
    #     print('-'*18)
    #     print("{} a {} alternatives.".format(shape_name, len(shape_set)))
    #     print(shape_name, ':')
    #     for shape_matrix in shape_set:
    #         # print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in shape_matrix]))
    #         print_shape(mat_to_compactmat(shape_matrix[:]))
    #         print('-'*12)

    print('-'*8)

    for forme in all_shapes:
        free_shapes = all_shapes[forme]
        l = []
        for fs in free_shapes:
            l += possibles(fs)
        FORM[forme] = set(l)
 
    count = 0
    t = time.time()

    for index, f in enumerate(FREE_PENTOMINOS):
        for index2 in range(index+1, len(FREE_PENTOMINOS)):
            fprime = FREE_PENTOMINOS[index2]
            if fprime != f:
                quintuplets = FORM[f]
                quintupletsprime = FORM[fprime]
                for quintuplet in quintuplets:
                    if 0 in quintuplet:
                        for quintupletprime in quintupletsprime:
                            if N-1 in quintupletprime:
                                FORM_bis = copy.deepcopy(FORM)
                                FORM_bis[f] = {quintuplet}
                                FORM_bis[fprime] = {quintupletprime}
                                for f2, qs2 in FORM_bis.items():
                                    if f2 != f and f2 != fprime:
                                        _remove = set()
                                        for q2 in qs2:
                                            if set(q2).intersection(set(quintuplet)) or set(q2).intersection(quintupletprime):
                                                _remove.add(q2)
                                        FORM_bis[f2].difference_update(_remove)

                                VAR_FORM = dict()
                                for cell in range(N*M):
                                    if cell in quintuplet:
                                        VAR_FORM[cell] = {f}
                                    elif cell in quintupletprime:
                                        VAR_FORM[cell] = {fprime}
                                    else :
                                        VAR_FORM[cell] = set(FREE_PENTOMINOS)
                                        VAR_FORM[cell].remove(f)
                                        VAR_FORM[cell].remove(fprime)

                                # for f2, qs2 in FORM_bis.items():
                                #     for q2 in qs2:
                                #         if not any(c in quintuplet for c in q2):
                                #             for cell in q2:
                                #                 VAR_FORM[cell].update({f2})

                                for i in quintuplet:
                                    del VAR_FORM[i]
                                for i in quintupletprime:
                                    del VAR_FORM[i]
                                del FORM_bis[f]
                                del FORM_bis[fprime]

                                P = constraint_program({**copy.deepcopy(VAR_FORM), **copy.deepcopy(FORM_bis)})
                                P.set_arc_consistency()

                                # print('#'*12)
                                # print(f)
                                # for i, j in FORM_bis.items():
                                #     print(i, j)
                                # print('-'*12)
                                # for i, j in VAR_FORM.items():
                                #     print(i,j)
                                # print("sleep", file=sys.stderr)
                                # # time.sleep(10)

                                for cell in range(N*M):
                                    if cell not in quintuplet and cell not in quintupletprime:
                                        for f2, qs2 in FORM_bis.items():
                                            if f2 != f and f2 != fprime:
                                                setquint = set()
                                                for q2 in qs2:
                                                    if cell in q2 and f2 in VAR_FORM[cell]:
                                                        setquint.add((f2, q2))

                                                for othershape in VAR_FORM[cell]:
                                                      for otherquintuplet in qs2:
                                                        if othershape != f2 and othershape != f and othershape != fprime and cell not in otherquintuplet:
                                                            setquint.add((othershape, otherquintuplet))
                                                if setquint:
                                                    P.add_constraint(cell, f2, setquint)

                                # for cell in quintuplet:
                                #     P.add_constraint(cell, f, {(f, quintuplet)})

                                print('Solving {} {} + {} {}...'.format(f, quintuplet, fprime, quintupletprime))
                                t2 = time.time()

                                for sol in P.solve_all():
                                    count += 1
                                    print('Time for sol. n˚{} : {} -- Total: {}'.format(count, time.time() - t2, time.time()-t))
                                    for i in quintuplet:
                                        sol[i] = f
                                    for i in quintupletprime:
                                        sol[i] = fprime
                                    sol[f] = quintuplet
                                    sol[fprime] = quintupletprime
                                    print_sol(sol)
                                    t2 = time.time()
                                # print('Solved {0} in {1}.'.format(f, time.time() - t))
                                del P

        # remove f from angles
        to_remove = set()
        for q in quintuplets:
            if set(q).intersection(corners):
                to_remove.add(q)
        # print('on supprime {} de {}'.format(to_remove, f))
        FORM[f].difference_update(to_remove)

    print('Final count: ', count)

if __name__ == '__main__':
    main()

