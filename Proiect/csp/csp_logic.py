import ast
import random
import re
from typing import Dict, Optional

from csp.csp_generator import generate_csp_instance, format_csp_problem
from csp.csp_solver import solve_csp


ALGORITHMS = ["FC", "MRV", "AC-3"]


def _canonical_answer(sol: Optional[Dict[str, int]]) -> str:
    if sol is None:
        return "None"
    # stable representation
    items = ", ".join(f"'{k}': {sol[k]}" for k in sorted(sol.keys()))
    return "{" + items + "}"


def generate_csp_question():
    variables, domains, constraints, partial = generate_csp_instance()
    algorithm = random.choice(ALGORITHMS)

    solution = solve_csp(variables, domains, constraints, partial, algorithm)

    return {
        "type": "csp",
        "algorithm": algorithm,
        "question": (
            "Given the following CSP (variables, domains, constraints, and a partial assignment), "
            f"what will be the final assignment of the remaining variables if we use "
            f"Backtracking with the optimization {algorithm}?"
        ),
        "instance": format_csp_problem(variables, domains, constraints, partial),
        "answer": _canonical_answer(solution),
    }


def _parse_user_assignment(text: str) -> Optional[Dict[str, int]]:
    s = text.strip()
    if not s:
        return None

    try:
        obj = ast.literal_eval(s)
        if isinstance(obj, dict):
            return {
                str(k).strip().upper(): int(v)
                for k, v in obj.items()
            }
    except Exception:
        pass

    pairs = re.findall(r"\b([A-Za-z])\s*=\s*(-?\d+)\b", s)
    if pairs:
        return {k.upper(): int(v) for k, v in pairs}

    return None


def evaluate_csp_answer(user_answer: str, correct_answer: str) -> int:
    raw = user_answer.strip().lower()
    user_says_none = bool(
        re.fullmatch(r"(none|no solution|unsat|infeasible)", raw)
    )

    user_parsed = _parse_user_assignment(user_answer)
    correct_sol = None if correct_answer.strip() == "None" else ast.literal_eval(correct_answer)

    if correct_sol is None:
        return 100 if user_says_none else 0

    if user_parsed is None:
        return 0

    correct_norm = {
        str(k).strip().upper(): int(v)
        for k, v in correct_sol.items()
    }

    return 100 if user_parsed == correct_norm else 0
