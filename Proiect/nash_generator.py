import random

# -------------------------------
# PRISONER'S DILEMMA (guaranteed Nash: D,D)
# -------------------------------
def prisoners_dilemma():
    a = random.randint(2, 4)
    b = random.randint(a + 1, a + 4)
    c = random.randint(0, a - 1)

    matrix = f"""
           Player B
                  C       D
A  C   ({a},{a})  (0,{b})
   D   ({b},0)  ({c},{c})
"""

    return matrix.strip(), "Pure Nash equilibrium: (D, D)"


# -------------------------------
# COORDINATION GAME (2 Nash)
# -------------------------------
def coordination_game():
    x = random.randint(3, 6)
    y = random.randint(1, x - 1)

    matrix = f"""
           Player B
            B1       B2
A  A1  ({x},{x})  (0,0)
   A2  (0,0)   ({y},{y})
"""

    return matrix.strip(), "Pure Nash equilibria: (A1, B1) and (A2, B2)"


# -------------------------------
# ZERO-SUM GAME (no pure Nash)
# -------------------------------
def zero_sum_game():
    a = random.randint(1, 4)

    matrix = f"""
           Player B
            L       R
A  U   ({a},-{a})  (-{a},{a})
   D   (-{a},{a})  ({a},-{a})
"""

    return matrix.strip(), "No pure Nash equilibrium exists"


# -------------------------------
# MAIN NASH GENERATOR
# -------------------------------
def generate_nash():
    games = [
        prisoners_dilemma,
        coordination_game,
        zero_sum_game
    ]

    matrix, answer = random.choice(games)()

    question = (
        "Given the following game in normal form, determine whether it has a pure Nash equilibrium. "
        "State all pure Nash equilibria if they exist.\n\n" + matrix
    )

    return {
        "type": "nash",
        "instance": matrix,
        "question": question,
        "answer": answer
    }
