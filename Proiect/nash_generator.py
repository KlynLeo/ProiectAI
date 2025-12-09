import random
from nash_solver import find_pure_nash_equilibria


def generate_random_payoff():
    """Payoff random pentru fiecare jucător (0..9)."""
    return (random.randint(0, 9), random.randint(0, 9))


def generate_random_game(min_size=2, max_size=4):
    """
    Generează un joc m×n cu payoff-uri random.
    Dimensiunea este între min_size și max_size.
    """
    m = random.randint(min_size, max_size)  
    n = random.randint(min_size, max_size)  

    strategies_A = [f"A{i+1}" for i in range(m)]
    strategies_B = [f"B{j+1}" for j in range(n)]

    matrix = {}
    for a in strategies_A:
        for b in strategies_B:
            matrix[(a, b)] = generate_random_payoff()

    return strategies_A, strategies_B, matrix


def generate_no_pure_nash_game():
    """
    Construim un joc 2x2 de tip Matching Pennies:
    Player A câștigă dacă strategiile sunt diferite,
    Player B câștigă dacă sunt egale.
    Nu există echilibru Nash în strategii pure.
    """
    strategies_A = ["A1", "A2"]
    strategies_B = ["B1", "B2"]

    matrix = {
        ("A1", "B1"): (1, -1),
        ("A1", "B2"): (-1, 1),
        ("A2", "B1"): (-1, 1),
        ("A2", "B2"): (1, -1),
    }

    return strategies_A, strategies_B, matrix


def format_matrix(strats_A, strats_B, matrix):
    header = " " * 12 + "Player B\n"
    header += " " * 12 + "  ".join(f"{b:>6}" for b in strats_B) + "\n"

    body = ""
    for a in strats_A:
        row = f"Player A {a:<3} "
        for b in strats_B:
            u1, u2 = matrix[(a, b)]
            row += f"{str((u1, u2)):>6}  "
        body += row + "\n"

    return header + body



def generate_nash():
    if random.random() < 0.3:
        strats_A, strats_B, matrix = generate_no_pure_nash_game()
    else:
        strats_A, strats_B, matrix = generate_random_game()

    equilibria = find_pure_nash_equilibria(matrix)

    if equilibria:
        answer = "Pure Nash equilibria: " + ", ".join(str(eq) for eq in equilibria)
    else:
        answer = "no nash"

    matrix_text = format_matrix(strats_A, strats_B, matrix)

    text_question = (
        "Given the following parametrized game in normal form, determine whether it has "
        "a pure Nash equilibrium. State all pure Nash equilibria if they exist."
    )

    return {
        "type": "nash",
        "instance": matrix_text,
        "question": text_question,
        "answer": answer
    }
