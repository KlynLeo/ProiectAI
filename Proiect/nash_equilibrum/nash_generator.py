

import random


def generate_random_payoff():
    return (random.randint(0, 9), random.randint(0, 9))


def generate_random_game(min_size=2, max_size=4):
    """
    Create a random m×n normal-form game.
    """
    m = random.randint(min_size, max_size)
    n = random.randint(min_size, max_size)

    A = [f"A{i+1}" for i in range(m)]
    B = [f"B{j+1}" for j in range(n)]

    matrix = {}
    for a in A:
        for b in B:
            matrix[(a, b)] = generate_random_payoff()

    return A, B, matrix


def generate_no_nash_game():
    """
    Matching pennies game → no pure Nash equilibrium.
    """
    A = ["A1", "A2"]
    B = ["B1", "B2"]

    matrix = {
        ("A1", "B1"): (1, -1),
        ("A1", "B2"): (-1, 1),
        ("A2", "B1"): (-1, 1),
        ("A2", "B2"): (1, -1),
    }

    return A, B, matrix


def format_matrix(A, B, matrix):
    """
    Return a formatted normal-form game matrix as text.
    """
    header = " " * 12 + "Player B\n"
    header += " " * 12 + "  ".join(f"{b:>6}" for b in B) + "\n"

    body = ""
    for a in A:
        row = f"Player A {a:<3} "
        for b in B:
            u1, u2 = matrix[(a, b)]
            row += f"{str((u1, u2)):>6}  "
        body += row + "\n"

    return header + body
