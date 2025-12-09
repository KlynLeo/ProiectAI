
def find_pure_nash_equilibria(matrix):
    print("Matrix received for Nash computation:", matrix)
    strategies_p1 = sorted(set(k[0] for k in matrix.keys()))
    strategies_p2 = sorted(set(k[1] for k in matrix.keys()))

    nash_equilibria = []

    for s1 in strategies_p1:
        for s2 in strategies_p2:

            u1, u2 = matrix[(s1, s2)]

            best_response_p1 = True
            for s1_alt in strategies_p1:
                if matrix[(s1_alt, s2)][0] > u1:
                    best_response_p1 = False
                    break

            best_response_p2 = True
            for s2_alt in strategies_p2:
                if matrix[(s1, s2_alt)][1] > u2:
                    best_response_p2 = False
                    break

            if best_response_p1 and best_response_p2:
                nash_equilibria.append((s1, s2))

    return nash_equilibria
