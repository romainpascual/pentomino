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

[M,N] = [int(x) for x in sys.argv[1].split("x")]

F = [[0,1,1], [1,1,0], [0,1,0]]


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

    return uplets


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
FREE_PENTOMINOS = ["F","I","L","N","P","T","U","V","W","X","Y","Z"]

FORM = dict()
FORM["F"] = possibles(F)

VAR = {}

for k in range(M*N):
    VAR[k]=set(FREE_PENTOMINOS)

P = constraint_program(VAR)

"""
for f in FORMES:
    for k in range(m*n):
        P.add_constraint(f,k {f,v) for}
"""

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
        print(FORM)

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
    # print(all_shapes)

    for forme in all_shapes:
        free_shapes = all_shapes[forme]
        l = []
        for fs in free_shapes:
            l += possibles(fs)
        FORM[forme] = set(l)

    # r = 1
    # for f in FORM:
    #     print(f, '\n')
    #     r *= len(FORM[f])
    #     print(len(FORM[f]))
    #     print('-'*8)
    #     print()
    # print(len(str(r)))

    pos_2_shape = dict()
    for shape, quintuplets in FORM.items():
        for quintuplet in quintuplets:
            pos_2_shape[tuple(quintuplet)] = {shape, 'NoForm'}

    for k in range(M * N):
        VAR[k] = set(FREE_PENTOMINOS)

    VAR.update(pos_2_shape)
    print(VAR)

    P = constraint_program(VAR)

    for quintuplet, shape in pos_2_shape.items():
        shape = shape.copy()
        shape.remove('NoForm')
        shape = shape.pop()
        # print('#'*12, shape)
        for i in quintuplet:
            CELL_IN_SHAPE_CONSTRAINT = {(shape, shape)}
            P.add_constraint(i, quintuplet, CELL_IN_SHAPE_CONSTRAINT)

    print('Solving...')
    sol = P.solve()
    print(sol)

if __name__ == '__main__':
    main()

