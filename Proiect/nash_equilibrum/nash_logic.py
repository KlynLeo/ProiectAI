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

    if correct_has_none:
        return 100 if user_says_no else 0

    if user_says_no:
        return 0

    user_eq = extract_equilibria(user_answer)
    
    if user_says_yes and not user_eq:
        return 30
    
    if not user_eq:
        return 0
    
    if set(user_eq) == set(correct_equilibria):
        return 100
    
    user_set = set(user_eq)
    correct_set = set(correct_equilibria)
    
    correct_found = user_set & correct_set 
    wrong_provided = user_set - correct_set  
    
    if not correct_found:
        return 0

    base_score = (len(correct_found) / len(correct_equilibria)) * 100
    
    penalty = len(wrong_provided) * 10
    
    final_score = max(0, int(base_score - penalty))
    
    return final_score