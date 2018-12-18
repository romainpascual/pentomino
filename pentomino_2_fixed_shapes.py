#!usr/bin/env pypy

## Imports

import sys, copy, time
from constraint_programming import constraint_program
sys.setrecursionlimit(10000)

## Utilisation de colorama pour le rendu
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
	
	FREE_PENTOMINOS = ["F","I","L","N","P","T","U","V","W","X","Y","Z"]

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

                            print('Solving {} {} + {} {}...'.format(shape_top_left,
                                                                    quintuplet_top_left,
                                                                    shape_top_right,
                                                                    quintuplet_top_right))

                            for sol in P.solve_all():
                                count += 1
																					
								# On rajoute à la solution les deux formes que l'on a fixé
                                for i in quintuplet_top_left:
                                    sol[i] = shape_top_left
                                for i in quintuplet_top_right:
                                    sol[i] = shape_top_right
                                sol[shape_top_left] = quintuplet_top_left
                                sol[shape_top_right] = quintuplet_top_right
								
								if print_one:
									print('Time for sol. n˚{} : {.2f}'.format(count, time.time()-t))
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

	print('Solved in a total time of: {.2f}s'.format(time.time() - t))
    print('Final count: {} solutions'.format(count))

