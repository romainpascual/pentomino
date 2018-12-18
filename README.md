Optimization - Academic project - Last year MSc studies @ CentraleSupélec Adam Hotait and Romain Pascual

### Pentomino problem
see https://en.wikipedia.org/wiki/Pentomino

# Problem

We have 12 shapes called pentominos, made of 5 cells, that we want to arrange on a 60-cell grid with no overlap. The shapes can be rotated or flipped.
We want to draw a solution and give the total number of solutions, excluding trivial variations obtained by rotation and reflection of the whole rectangle.

# Description of files

- constraint_programming.py: CSP solver

- pentomino_naive.py: naive implementation
- ? pentomino_corners.py: we choose two shapes for the two upper corners
- ? pentomino_corners_multiprocessing: we allow multi-processing

- documentation.pdf: some explanations on how we design the constraint satisfaction problem (variables and constraints)

