import random
from typing import Dict, List, Set, Tuple


Var = str
Val = int
Domain = Dict[Var, Set[Val]]
Constraint = Tuple[Var, str, Var]  # (A, op, B)


OPS = ["!=", "<", ">", "<=", ">="]


def _rand_domain(min_val: int, max_val: int, min_size: int, max_size: int) -> Set[int]:
    size = random.randint(min_size, max_size)
    pool = list(range(min_val, max_val + 1))
    random.shuffle(pool)
    return set(pool[:size])


def _satisfies(a: int, op: str, b: int) -> bool:
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


def generate_csp_instance(
    n_vars: int = 4,
    min_val: int = 1,
    max_val: int = 6,
    min_domain_size: int = 2,
    max_domain_size: int = 4,
    min_constraints: int = 3,
    max_constraints: int = 6,
    unsat_probability: float = 0.20,
    partial_assignment_size: int = 1,
) -> Tuple[List[Var], Domain, List[Constraint], Dict[Var, Val]]:
    """
    Generates a *mostly solvable* random binary CSP by first sampling a hidden solution
    and then adding constraints consistent with it. Sometimes makes it UNSAT with a small probability.
    """
    n_vars = max(3, n_vars)
    variables = [chr(ord("A") + i) for i in range(n_vars)]

    # Domains
    domains: Domain = {}
    for v in variables:
        domains[v] = _rand_domain(min_val, max_val, min_domain_size, max_domain_size)

    # Ensure each domain has at least 2 values
    for v in variables:
        if len(domains[v]) < 2:
            domains[v].add(random.randint(min_val, max_val))

    # Sample a hidden solution (pick one value from each domain)
    hidden_solution = {v: random.choice(list(domains[v])) for v in variables}

    # Build constraints consistent with hidden solution
    constraints: List[Constraint] = []
    n_constraints = random.randint(min_constraints, max_constraints)

    all_pairs = [(variables[i], variables[j]) for i in range(n_vars) for j in range(i + 1, n_vars)]
    random.shuffle(all_pairs)

    for (x, y) in all_pairs:
        if len(constraints) >= n_constraints:
            break
        op = random.choice(OPS)

        # Make sure hidden solution satisfies it.
        xv, yv = hidden_solution[x], hidden_solution[y]
        if _satisfies(xv, op, yv):
            constraints.append((x, op, y))
        else:
            # Try another operator that works
            working_ops = [o for o in OPS if _satisfies(xv, o, yv)]
            if working_ops:
                constraints.append((x, random.choice(working_ops), y))

    # If not enough constraints, add more random ones that still satisfy hidden solution
    while len(constraints) < n_constraints:
        x, y = random.sample(variables, 2)
        if x == y:
            continue
        op = random.choice(OPS)
        if _satisfies(hidden_solution[x], op, hidden_solution[y]):
            constraints.append((x, op, y))

    # Occasionally make it UNSAT by injecting a contradiction
    if random.random() < unsat_probability:
        # Pick a variable and force it away from all its domain values via contradiction with a fixed var
        x, y = random.sample(variables, 2)
        # Create a constraint that is impossible given their domains (simple way):
        # If domains are within [min_val, max_val], add x < y and y < x both as constraints by using same pair reversed.
        constraints.append((x, "<", y))
        constraints.append((y, "<", x))

    # Create partial assignment (subset of variables)
    partial_assignment_size = max(0, min(partial_assignment_size, n_vars - 1))
    partial_vars = random.sample(variables, partial_assignment_size)
    partial_assignment = {v: hidden_solution[v] for v in partial_vars}

    return variables, domains, constraints, partial_assignment


def format_csp_problem(
    variables: List[Var],
    domains: Domain,
    constraints: List[Constraint],
    partial: Dict[Var, Val],
) -> str:
    lines = []
    lines.append("Variables: " + ", ".join(variables))
    lines.append("Domains:")
    for v in variables:
        lines.append(f"  {v} ∈ {sorted(domains[v])}")
    lines.append("Constraints:")
    for a, op, b in constraints:
        lines.append(f"  {a} {op} {b}")
    lines.append("Partial assignment:")
    if partial:
        for v in sorted(partial.keys()):
            lines.append(f"  {v} = {partial[v]}")
    else:
        lines.append("  (none)")
    return "\n".join(lines)
