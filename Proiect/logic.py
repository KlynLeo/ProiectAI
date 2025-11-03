import json
import random
import re

def load_bank(path="questions_bank.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_dynamic_question():
    """Construiește logic o întrebare aleatorie pe baza de template-uri (fără LLM)."""
    data = load_bank()
    problem_key = random.choice(list(data.keys()))
    info = data[problem_key]

    # Alegem o instanță concretă și strategia ei corectă
    instance_info = random.choice(info["instances"])
    instance = instance_info["instance"]
    correct_answer = instance_info["strategy"]

    # Template-uri diferite de formulare
    templates = [
        f"For the problem of {problem_key.replace('_', ' ')}, given {instance}, which search strategy would be most suitable to solve it?",
        f"Given the problem {problem_key.replace('_', ' ')}, and the instance {instance}, which algorithm should be chosen to obtain an optimal solution?",
        f"Which of the known search strategies fits best for solving the {problem_key.replace('_', ' ')} problem, considering {instance}?",
        f"Suppose we are solving {problem_key.replace('_', ' ')}. For the case of {instance}, what is the most appropriate search approach?",
        f"When addressing {problem_key.replace('_', ' ')} with {instance}, which strategy is expected to perform best according to AI principles?",
        f"Identify the search algorithm that would efficiently solve {problem_key.replace('_', ' ')} if the scenario involves {instance}.",
        f"In artificial intelligence, how would you approach {problem_key.replace('_', ' ')} given {instance}? Which method is most effective?"
    ]

    question_text = random.choice(templates)

    # ✅ returnăm obiectul complet
    return {
        "type": "open",
        "problem": problem_key,
        "instance": instance,
        "question": question_text,
        "answer": correct_answer
    }

# ---------------------------------------------------------------------
# CLASA PRINCIPALĂ DE EXAMEN
# ---------------------------------------------------------------------

class Exam:
    def __init__(self):
        self.selected_questions = []
        self.user_answers = []
        self.current_index = 0

    def select_questions(self, num_questions):
        """Generează un set nou de întrebări dinamice."""
        self.selected_questions = [generate_dynamic_question() for _ in range(num_questions)]
        self.user_answers = [""] * len(self.selected_questions)
        self.current_index = 0

    def get_current_question(self):
        if self.current_index >= len(self.selected_questions):
            return None
        return self.selected_questions[self.current_index]

    def submit_answer(self, answer):
        if self.current_index < len(self.selected_questions):
            self.user_answers[self.current_index] = answer.strip()
            self.current_index += 1

    def is_finished(self):
        return self.current_index >= len(self.selected_questions)

    def grade(self):
        """Calculează scorul mediu al utilizatorului (procentual)."""
        if not self.selected_questions:
            return 0
        scores = [self._compare_answers(ans, q["answer"])
                  for q, ans in zip(self.selected_questions, self.user_answers)]
        return int(sum(scores) / len(scores))

    def _compare_answers(self, user_answer, correct_answer):
        """Compară două răspunsuri simplu, fără LLM: bazat pe cuvinte cheie."""
        user_answer = re.sub(r'[^a-zA-Z ]', '', user_answer.lower())
        correct_answer = re.sub(r'[^a-zA-Z ]', '', correct_answer.lower())
        user_words = set(user_answer.split())
        correct_words = set(correct_answer.split())
        if not correct_words:
            return 0
        overlap = len(user_words & correct_words)
        return int((overlap / len(correct_words)) * 100)
