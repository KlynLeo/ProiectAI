# nash_solver.py
# -----------------------------------------------------
# Pure Nash Equilibrium Finder for Normal-Form Games
# Matrix is a dict mapping (s1, s2) -> (u1, u2)
# -----------------------------------------------------

def find_pure_nash_equilibria(matrix):

    strategies_p1 = list(dict.fromkeys(k[0] for k in matrix))
    strategies_p2 = list(dict.fromkeys(k[1] for k in matrix))

    equilibria = []

    for s1 in strategies_p1:
        for s2 in strategies_p2:

            u1, u2 = matrix[(s1, s2)]

            if any(matrix[(s1_alt, s2)][0] > u1 for s1_alt in strategies_p1):
                continue

            if any(matrix[(s1, s2_alt)][1] > u2 for s2_alt in strategies_p2):
                continue

            equilibria.append((s1, s2))

    return equilibria
