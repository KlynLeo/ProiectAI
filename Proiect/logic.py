import json
import random
import re
from collections import Counter
import math

ignored_words = {"search", "algorithm", "method", "strategy", "problem", "solution", "with"}
abbreviations = {
    "dfs": "depth first search",
    "bfs": "breadth first search",
    "ucs": "uniform cost search",
    "a*": "a star",
    "astar": "a star",
    "idfs": "iterative deepening depth first search"
}

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    words = text.split()
    expanded_words = []
    for w in words:
        if w in abbreviations:
            expanded_words.extend(abbreviations[w].split())
        else:
            expanded_words.append(w)
    return [w for w in expanded_words if w not in ignored_words]

def load_bank(path="questions_bank.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_dynamic_question():
    data = load_bank()
    problem_key = random.choice(list(data.keys()))
    info = data[problem_key]
    instance_info = random.choice(info["instances"])
    instance = instance_info["instance"]
    correct_answer = instance_info["strategy"]

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

    return {
        "type": "open",
        "problem": problem_key,
        "instance": instance,
        "question": question_text,
        "answer": correct_answer
    }

def build_synonyms_from_bank(bank):
    synonyms = {}
    for problem in bank.values():
        for inst in problem["instances"]:
            strategy = inst["strategy"].lower()
            words = normalize_text(strategy)
            alt_forms = set()
            if words:
                alt_forms.add(" ".join(words))
                alt_forms.add("".join(words))
                alt_forms.add(" ".join(words[::-1]))
                for w in words:
                    alt_forms.add(w)
            synonyms[strategy] = list(alt_forms)
    return synonyms

class Exam:
    def __init__(self):
        self.selected_questions = []
        self.user_answers = []
        self.current_index = 0
        self.bank = load_bank()
        self.synonyms = build_synonyms_from_bank(self.bank)

    def select_questions(self, num_questions):
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
        if not self.selected_questions:
            return 0
        scores = [self._compare_answers(ans, q["answer"])
                  for q, ans in zip(self.selected_questions, self.user_answers)]
        return int(sum(scores) / len(scores))

    def _compare_answers(self, user_answer, correct_answer):
        user_words = normalize_text(user_answer)
        correct_words = normalize_text(correct_answer)

        alt_forms = self.synonyms.get(correct_answer.lower(), [])
        if any(" ".join(user_words) == s for s in alt_forms):
            return 100
  
        all_words = set(user_words) | set(correct_words)
        if not all_words:
            return 0
        user_counts = Counter(user_words)
        correct_counts = Counter(correct_words)
        dot = sum(user_counts[w] * correct_counts[w] for w in all_words)
        norm_user = math.sqrt(sum(user_counts[w] ** 2 for w in all_words))
        norm_correct = math.sqrt(sum(correct_counts[w] ** 2 for w in all_words))
        if norm_user == 0 or norm_correct == 0:
            return 0
        cosine = dot / (norm_user * norm_correct)
        return int(cosine * 100)
