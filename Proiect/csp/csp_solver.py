from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional, Set, Tuple


Var = str
Val = int
Domain = Dict[Var, Set[Val]]
Constraint = Tuple[Var, str, Var]  # (A, op, B)


def satisfies(a: int, op: str, b: int) -> bool:
    if op == "!=":
        return a != b
    if op == "<":
        return a < b
    if op == ">":
        return a > b
    if op == "<=":
        return a <= b
    if op == ">=":
        return a >= b
    raise ValueError(f"Unknown operator: {op}")


def _inverse_op(op: str) -> str:
    # For reading constraints in reverse direction: A op B  <=>  B inv_op A
    if op == "!=":
        return "!="
    if op == "<":
        return ">"
    if op == ">":
        return "<"
    if op == "<=":
        return ">="
    if op == ">=":
        return "<="
    raise ValueError(f"Unknown operator: {op}")


def constraints_between(x: Var, y: Var, constraints: List[Constraint]) -> List[Tuple[str, bool]]:
    """
    Returns a list of (op, forward) describing constraints linking x and y.
    forward=True means constraint is x op y.
    forward=False means constraint is y op x (so we must invert when checking x->y).
    """
    rel = []
    for a, op, b in constraints:
        if a == x and b == y:
            rel.append((op, True))
        elif a == y and b == x:
            rel.append((op, False))
    return rel


def consistent_pair(x: Var, xv: int, y: Var, yv: int, constraints: List[Constraint]) -> bool:
    """
    Checks all constraints connecting x and y (in either direction).
    Returns True iff all are satisfied.
    """
    rel = constraints_between(x, y, constraints)
    for op, forward in rel:
        if forward:
            if not satisfies(xv, op, yv):
                return False
        else:
            # constraint is y op x, so for x->y check: y op x  <=>  x inv_op y
            inv = _inverse_op(op)
            if not satisfies(xv, inv, yv):
                return False
    return True


def neighbors(var: Var, constraints: List[Constraint]) -> Set[Var]:
    n = set()
    for a, _, b in constraints:
        if a == var:
            n.add(b)
        elif b == var:
            n.add(a)
    return n


def ac3(domains: Domain, constraints: List[Constraint]) -> Optional[Domain]:
    """
    AC-3 algorithm. Returns pruned domains if arc-consistent, or None if inconsistency found.
    """
    new_domains: Domain = {v: set(vals) for v, vals in domains.items()}

    q = deque()
    for a, _, b in constraints:
        q.append((a, b))
        q.append((b, a))

    def revise(xi: Var, xj: Var) -> bool:
        """
        Removes values from D(xi) that have no supporting value in D(xj).
        Returns True if D(xi) changed.
        """
        removed = False
        to_remove = set()
        for xv in new_domains[xi]:
            # Does there exist yv in Dj that satisfies all constraints between xi and xj?
            supported = any(consistent_pair(xi, xv, xj, yv, constraints) for yv in new_domains[xj])
            if not supported:
                to_remove.add(xv)

        if to_remove:
            new_domains[xi] -= to_remove
            removed = True
        return removed

    while q:
        xi, xj = q.popleft()
        if revise(xi, xj):
            if len(new_domains[xi]) == 0:
                return None
            for xk in neighbors(xi, constraints):
                if xk != xj:
                    q.append((xk, xi))

    return new_domains


def is_consistent(var: Var, value: int, assignment: Dict[Var, int], constraints: List[Constraint]) -> bool:
    """
    Checks consistency of assigning var=value with already assigned variables.
    """
    for other, other_val in assignment.items():
        if other == var:
            continue
        # Check constraints that connect var and other
        if not consistent_pair(var, value, other, other_val, constraints):
            return False
    return True


def select_mrv(domains: Domain, assignment: Dict[Var, int]) -> Var:
    """
    Minimum Remaining Values heuristic: choose unassigned variable with smallest domain.
    """
    unassigned = [v for v in domains.keys() if v not in assignment]
    return min(unassigned, key=lambda v: len(domains[v]))


def forward_check(domains: Domain, assignment: Dict[Var, int], constraints: List[Constraint], recently_assigned: Var) -> Optional[Domain]:
    """
    Forward checking after assigning recently_assigned.
    Prunes neighbors' domains based on constraints with recently_assigned.
    Returns new domains, or None if a domain becomes empty.
    """
    new_domains: Domain = {v: set(vals) for v, vals in domains.items()}
    x = recently_assigned
    xv = assignment[x]

    for y in neighbors(x, constraints):
        if y in assignment:
            continue
        filtered = set()
        for yv in new_domains[y]:
            if consistent_pair(x, xv, y, yv, constraints):
                filtered.add(yv)
        new_domains[y] = filtered
        if len(new_domains[y]) == 0:
            return None

    return new_domains


def backtracking_basic(assignment: Dict[Var, int], domains: Domain, constraints: List[Constraint], var_order: List[Var]) -> Optional[Dict[Var, int]]:
    if len(assignment) == len(domains):
        return assignment

    # pick next in fixed order
    for v in var_order:
        if v not in assignment:
            var = v
            break

    for value in sorted(domains[var]):
        if is_consistent(var, value, assignment, constraints):
            new_assignment = dict(assignment)
            new_assignment[var] = value
            result = backtracking_basic(new_assignment, domains, constraints, var_order)
            if result is not None:
                return result

    return None


def backtracking_mrv(assignment: Dict[Var, int], domains: Domain, constraints: List[Constraint]) -> Optional[Dict[Var, int]]:
    if len(assignment) == len(domains):
        return assignment

    var = select_mrv(domains, assignment)

    for value in sorted(domains[var]):
        if is_consistent(var, value, assignment, constraints):
            new_assignment = dict(assignment)
            new_assignment[var] = value
            result = backtracking_mrv(new_assignment, domains, constraints)
            if result is not None:
                return result

    return None


def backtracking_fc(assignment: Dict[Var, int], domains: Domain, constraints: List[Constraint], var_order: List[Var]) -> Optional[Dict[Var, int]]:
    if len(assignment) == len(domains):
        return assignment

    # fixed order (FC is the "optimization" here)
    for v in var_order:
        if v not in assignment:
            var = v
            break

    for value in sorted(domains[var]):
        if not is_consistent(var, value, assignment, constraints):
            continue

        new_assignment = dict(assignment)
        new_assignment[var] = value

        pruned = forward_check(domains, new_assignment, constraints, recently_assigned=var)
        if pruned is None:
            continue

        result = backtracking_fc(new_assignment, pruned, constraints, var_order)
        if result is not None:
            return result

    return None


def solve_csp(
    variables: List[Var],
    domains: Domain,
    constraints: List[Constraint],
    partial_assignment: Dict[Var, int],
    algorithm: str,
) -> Optional[Dict[Var, int]]:
    """
    algorithm in {"FC", "MRV", "AC-3"}
    - FC  : Backtracking + Forward Checking (fixed variable order)
    - MRV : Backtracking + MRV (no forward checking)
    - AC-3: AC-3 preprocessing + plain backtracking (fixed order)
    """
    algorithm = algorithm.upper().strip()
    base_domains: Domain = {v: set(vals) for v, vals in domains.items()}

    # apply partial assignment consistency + domain restriction
    assignment = dict(partial_assignment)
    for v, val in assignment.items():
        if v not in base_domains or val not in base_domains[v]:
            return None
        if not is_consistent(v, val, {k: assignment[k] for k in assignment if k != v}, constraints):
            return None
        base_domains[v] = {val}

    var_order = list(variables)

    if algorithm == "AC-3":
        pruned = ac3(base_domains, constraints)
        if pruned is None:
            return None
        # plain backtracking (fixed order) after AC-3
        return backtracking_basic(assignment, pruned, constraints, var_order)

    if algorithm == "FC":
        # forward checking backtracking
        return backtracking_fc(assignment, base_domains, constraints, var_order)

    if algorithm == "MRV":
        # MRV heuristic backtracking
        return backtracking_mrv(assignment, base_domains, constraints)

    raise ValueError(f"Unknown algorithm: {algorithm}")
