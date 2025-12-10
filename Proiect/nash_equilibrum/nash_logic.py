import ast
import random
import re
from nash_equilibrum.nash_solver import find_pure_nash_equilibria
from nash_equilibrum.nash_generator import (
    generate_random_game,
    generate_no_nash_game,
    format_matrix,
)


def generate_nash():

    if random.random() < 0.3:
        A, B, matrix = generate_no_nash_game()
    else:
        A, B, matrix = generate_random_game()

    equilibria = find_pure_nash_equilibria(matrix)

    if equilibria:
        answer = "Pure Nash equilibria: " + ", ".join(str(eq) for eq in equilibria)
    else:
        answer = "No pure Nash equilibrium exists"

    return {
        "type": "nash",
        "instance": format_matrix(A, B, matrix),
        "question": (
            "Given the following normal-form game, determine whether it has a "
            "pure Nash equilibrium. State all equilibria if they exist."
        ),
        "answer": answer
    }


def extract_equilibria(text):
    try:
        eq_list = ast.literal_eval(text)
        return [(str(a).upper(), str(b).upper()) for a, b in eq_list]
    except:
        pass
    pattern = r"\((?:')?([A-Z]\d+)(?:')?[,\s]+(?:')?([A-Z]\d+)(?:')?\)"
    matches = re.findall(pattern, text.upper())
    
    if matches:
        return [(a.strip(), b.strip()) for a, b in matches]
    
    return []


def evaluate_nash_answer(user_answer, correct_equilibria):
    user_answer = user_answer.strip()
    user_says_no = bool(re.search(r'\b(no|none|not|does not exist)\b', user_answer.lower()))
    user_says_yes = bool(re.search(r'\byes\b', user_answer.lower()))
    correct_has_none = len(correct_equilibria) == 0

    # Case 1: No equilibrium exists
    if correct_has_none:
        return 100 if user_says_no else 0

    # Case 2: User says "no" but equilibria exist
    if user_says_no:
        return 0

    # Case 3: Extract user's equilibria
    user_eq = extract_equilibria(user_answer)
    
    # If user just says "yes" without providing equilibria
    if user_says_yes and not user_eq:
        return 30
    
    # If no equilibria extracted
    if not user_eq:
        return 0
    
    # Case 4: Perfect match (all correct, no extras)
    if set(user_eq) == set(correct_equilibria):
        return 100
    
    # Case 5: Partial credit with penalty for wrong answers
    user_set = set(user_eq)
    correct_set = set(correct_equilibria)
    
    correct_found = user_set & correct_set  # intersection
    wrong_provided = user_set - correct_set  # user gave but aren't correct
    missed = correct_set - user_set  # correct ones user didn't find
    
    # No correct answers found
    if not correct_found:
        return 0
    
    # Calculate score with penalty
    # Base score: proportion of correct equilibria found
    base_score = (len(correct_found) / len(correct_equilibria)) * 100
    
    # Penalty: -10 points for each wrong equilibrium provided
    penalty = len(wrong_provided) * 10
    
    final_score = max(0, int(base_score - penalty))
    
    return final_score