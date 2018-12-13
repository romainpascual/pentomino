#!/usr/bin/env python3

# 2018 - Ecole Centrale Supélec
# Les élèves du cours d'optimisation et leur enseignant Christoph Dürr


import sys


class constraint_program:
    """Implements a basic constraint programming solver with binary constraints.

    Variables names can be integers, strings, any hashable object.

    Variable i has value assign[i] in a solution. While a solution is begin
    searched, some variables are not yet assigned, which is indicated by
    assign[i] == None.

    Constraints over two variables (aka binary constraints) are stored in the
    attribute constr. For every variable x, constr[x] contains a list of
    couples (y, rel), where y another variable and rel is the set of value
    pairs (u,v) that are valid in the contraint relating x with y, i.e. x=u
    and y=v is valid for this constraint.
    """

    def __init__(self, var):
        """creates an instance to the constraint programming problem.

        :param var: a dictionary that associates to each variable x,
                    its domain var[x].
                    The domain can be a list or a set.
        """
        self.var = var
        self.constr = {x: [] for x in var}
        self.assign = {x: None for x in var}
        self.log = []  # history of domain changes
        self.maintain_arc_consistency = False
        self.stat_nodes = 0
        # sanity check
        for x in var:
            for y in var:
                if x != y and var[x] is var[y]:
                    raise "variables have same domain object"

    def add_constraint(self, x, y, rel):
        """Adds a binary constraint over the variables x and y.

        :param x,y: indices of variables
        :param rel: set of couples of values defining the relation
        :comment: it is ok to add several constraints with the same
            relation object.
        """
        self.constr[x].append((y, rel))
        self.constr[y].append((x, {(v, u) for (u, v) in rel}))

    def solve_all(self):
        """Iterates over all solutions
        """
        self.stat_nodes += 1
        x = self.choice_var()  # branching variable
        if x is None:
            yield self.assign  # solution found
        else:
            for u in self.var[x]:
                # if not self.backward_check(x, u):
                #     continue
                history = self.save_context()  # fc
                self.assign[x] = u  # try all possible assignements to variable x
                Q = self.forward_check(x)  # fc
                if self.maintain_arc_consistency:  # fc
                    self.arc_consistency(Q)  # fc
                for sol in self.solve_all():
                    yield sol
                self.assign[x] = None
                self.restore_context(history)  # fc

    def solve(self):
        """Finds one solution
        """
        for sol in self.solve_all():
            return sol
        return None

    def choice_var(self):
        """Choose a branching variable

        :returns: a variable index x such that assign[x] == None and its domain is minimal
        """
        best = None
        for x in self.var:
            if type(x) is str and self.assign[x] is not None:
                for cell in self.assign[x]:
                    if self.assign[cell] is None:
                        return cell
        for x in self.var:
            if self.assign[x] is None and \
                    (best is None or type(x) is str):
                if type(x) is str:
                    if len(self.var[x]) < len(self.var[best]) or type(best) is int:
                        best = x
                elif type(best) is not str:
                    best = x
        # print('best', best)
        # print(self.assign)
        return best

    # def choice_var(self):
    #     """Choose a branching variable
    #
    #     :returns: a variable index x such that assign[x] == None and its domain is minimal
    #     """
    #     best = None
    #     for x in self.var:
    #         if self.assign[x] is None and \
    #                 (best is None or len(self.var[x]) < len(self.var[best])):
    #             best = x
    #     print('best', best)
    #     print(self.assign)
    #     return best

    def backward_check(self, x, u):
        for (y, rel) in self.constr[x]:
            v = self.assign[y]
            if v is not None and (u, v) not in rel:
                # print("bc {}={}, {}={} not in {}".format(x, u, y, v, str(rel)))
                return False
        return True

    def forward_check(self, x):
        """After x has been assigned to some value u,
            remove recursively from all related variables y values v
            such that (u,v) is not in the relation
            relating x with y.

        :param x: a variable index
        :param v: a value in the domain of x
        :returns: the set of variables for which the domain changed.
        """
        changed = set()
        for (y, rel) in self.constr[x]:
            if self.assign[y] is None:
                to_remove = set()
                for v in self.var[y]:
                    if (self.assign[x], v) not in rel:
                        to_remove.add(v)
                if to_remove:
                    self.remove_vals(y, to_remove)
                    changed.add(y)
        return changed

    def set_arc_consistency(self):
        """Sets the solver in a mode where it maintains
           arc_consistency at every moment.
        """
        self.maintain_arc_consistency = True
        all_vars = list(self.var.keys())
        self.arc_consistency(all_vars)

    def arc_consistency(self, Q):
        """Maintains the arc consistency after the domain of
        the variables in set Q got decreased.

        Implements the algorithm AC3.

        :param Q: a set of variable indices
        """
        while Q:
            x = Q.pop()
            for (y, relation) in self.constr[x]:
                if self.assign[y] is None:
                    if self.revise(x, y, relation):
                        Q.add(y)

    def revise(self, x, y, relation):
        """The domain of the variable x just got
           decreased. This method checks if the domain of y
           contains values v which do not have support
           in the domain of x for the given relation,
           in which case it removes them.

        :returns: True if the domain of y has been changed.
        """
        to_remove = set()
        for v in self.var[y]:
            if not self.hasSupport(y, v, x, relation):
                to_remove.add(v)
        self.remove_vals(y, to_remove)
        return to_remove

    def hasSupport(self, y, v, x, relation):
        """Checks whether the assignment y=v has a supporting
           value u in the domain of x, i.e.
           such that (u,v) belongs to the given relation.
        """
        for u in self.var[x]:
            if (u, v) in relation:
                return True
        return False

    def remove_vals(self, y, to_remove):
        """ Removes values from the domain of y
        """
        self.var[y] -= to_remove  # set difference
        self.log.append((y, to_remove))

    def save_context(self):
        """ Returns an index which can be used to restore the
            variable domains up to this point.
        """
        return len(self.log)

    def restore_context(self, history):
        """ Restores the domains of the variables
            up to the given point in time.
        """
        while len(self.log) > history:
            (y, to_remove) = self.log.pop()
            self.var[y] |= to_remove  # set union


