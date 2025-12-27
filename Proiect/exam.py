import random

# -----------------------------
# SEARCH imports
# -----------------------------
from search_problem_identification.search_logic import (
    load_bank,
    generate_dynamic_search_question,
    compare_search_answers,
)

# -----------------------------
# NASH imports
# -----------------------------
from nash_equilibrum.nash_logic import (
    generate_nash,
    evaluate_nash_answer,
    extract_equilibria
)

# -----------------------------
# MINIMAX imports
# -----------------------------
from minimax.minimax_logic import (
    generate_minimax_question,
    evaluate_minimax_answer
)

# -----------------------------
# CSP imports
# -----------------------------
from csp.csp_logic import (
    generate_csp_question,
    evaluate_csp_answer,
)

# -----------------------------
# HISTORY
# -----------------------------
from exam_history import append_exam


def _json_safe_question(q: dict) -> dict:
    safe = {}
    for k, v in q.items():
        if isinstance(v, (dict, list, str, int, float)) or v is None:
            safe[k] = v
        else:
            safe[k] = str(v)
    return safe


class Exam:
    """
    Exam manager for multiple question types:
    - Search
    - Nash Equilibrium
    - Minimax (Alpha-Beta)
    - CSP
    """

    def __init__(self):
        self.bank = load_bank()
        self.questions = []
        self.user_answers = []
        self.current_index = 0

    # -------------------------------------------------------------
    # Question selection
    # -------------------------------------------------------------
    def select_questions(
        self,
        n,
        include_search=True,
        include_nash=True,
        include_minimax=True,
        include_csp=True,
    ):
        self.questions = []
        enabled = []

        if include_search:
            enabled.append("search")
        if include_nash:
            enabled.append("nash")
        if include_minimax:
            enabled.append("minimax")
        if include_csp:
            enabled.append("csp")

        if not enabled:
            raise ValueError("No question types enabled.")

        for _ in range(n):
            qtype = random.choice(enabled)

            if qtype == "search":
                self.questions.append(generate_dynamic_search_question(self.bank))
            elif qtype == "nash":
                self.questions.append(generate_nash())
            elif qtype == "minimax":
                self.questions.append(generate_minimax_question())
            elif qtype == "csp":
                self.questions.append(generate_csp_question())

        self.user_answers = [""] * n
        self.current_index = 0

        # save exam history
        json_questions = [_json_safe_question(q) for q in self.questions]
        append_exam(json_questions)

    # -------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------
    def get_current_question(self):
        if self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index]

    def submit_answer(self, ans):
        if self.current_index < len(self.questions):
            self.user_answers[self.current_index] = ans.strip()
            self.current_index += 1

    def is_finished(self):
        return self.current_index >= len(self.questions)

    # -------------------------------------------------------------
    # Grading helpers
    # -------------------------------------------------------------
    def _grade_search(self, user_ans, q):
        return compare_search_answers(user_ans, q["answer"])

    def _grade_nash(self, user_ans, q):
        correct_eq = extract_equilibria(q["answer"])
        return evaluate_nash_answer(user_ans, correct_eq)

    def _grade_minimax(self, user_ans, q):
        return evaluate_minimax_answer(user_ans, q["answer"])

    def _grade_csp(self, user_ans, q):
        return evaluate_csp_answer(user_ans, q["answer"])

    # -------------------------------------------------------------
    # Final grading
    # -------------------------------------------------------------
    def grade(self):
        if not self.questions:
            return 0

        total = 0

        for user_ans, q in zip(self.user_answers, self.questions):
            if q["type"] == "search":
                total += self._grade_search(user_ans, q)
            elif q["type"] == "nash":
                total += self._grade_nash(user_ans, q)
            elif q["type"] == "minimax":
                total += self._grade_minimax(user_ans, q)
            elif q["type"] == "csp":
                total += self._grade_csp(user_ans, q)
            else:
                raise ValueError(f"Unknown question type: {q['type']}")

        return total // len(self.questions)
