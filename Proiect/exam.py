import random

from search_problem_identification.search_logic import (
    load_bank,
    generate_dynamic_search_question,
    compare_search_answers,
)

from nash_equilibrum.nash_logic import (
    generate_nash,
    evaluate_nash_answer,
    extract_equilibria
)

from minimax.minimax_logic import (
    generate_minimax_question,
    evaluate_minimax_answer
)


class Exam:
    def __init__(self):
        self.bank = load_bank()
        self.questions = []
        self.user_answers = []
        self.current_index = 0

    def select_questions(self, n, include_search=True, include_nash=True, include_minimax=True):
        self.questions = []
        enabled = []

        if include_search:
            enabled.append("search")
        if include_nash:
            enabled.append("nash")
        if include_minimax:
            enabled.append("minimax")

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

        self.user_answers = [""] * n
        self.current_index = 0

    def get_current_question(self):
        if self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index]

    def submit_answer(self, ans):
        self.user_answers[self.current_index] = ans.strip()
        self.current_index += 1

    def is_finished(self):
        return self.current_index >= len(self.questions)

    def grade(self):
        total = 0

        for ans, q in zip(self.user_answers, self.questions):
            if q["type"] == "search":
                total += compare_search_answers(ans, q["answer"])
            elif q["type"] == "nash":
                total += evaluate_nash_answer(ans, extract_equilibria(q["answer"]))
            elif q["type"] == "minimax":
                total += evaluate_minimax_answer(ans, q["answer"])

        return total // len(self.questions)
