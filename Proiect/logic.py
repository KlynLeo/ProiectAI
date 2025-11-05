import json
import random
import re
from collections import Counter
import math

ignored_words = {"search", "algorithm", "method", "strategy", "problem", "solution", "with", "heuristic", "approach"}
abbreviations = {
    "dfs": "depth first search",
    "bfs": "breadth first search",
    "ucs": "uniform cost search",
    "a*": "a star",
    "astar": "a star",
    "idfs": "iterative deepening depth first search",
    "ida*": "iterative deepening a star",
    "ids": "iterative deepening search",
    "ida": "iterative deepening a star",
    "csp": "constraint satisfaction problem",
    "mrv": "minimum remaining values",
}

concept_groups = [
    {"backtracking", "recursive backtracking", "dfs", "depth first search", "recursive search"},
    {"bfs", "breadth first search", "level order traversal"},
    {"a*", "astar", "a star", "best first search", "greedy best first search", "heuristic search"},
    {"uniform cost search", "ucs", "dijkstra", "lowest cost path"},
    {"hill climbing", "local search", "stochastic search", "random restarts"},
    {"iterative deepening", "idfs", "ida*", "iterative deepening a*"},
    {"constraint satisfaction", "csp", "forward checking", "constraint propagation", "mrv"},
]

def normalize_text(text):
    text = text.lower()
    for abbr, full in abbreviations.items():
        text = re.sub(r'\b' + re.escape(abbr) + r'\b', full, text)
    text = re.sub(r'[^a-z0-9 ]+', '', text)
    words = text.split()
    expanded = []
    for w in words:
        if w in abbreviations:
            expanded.extend(abbreviations[w].split())
        else:
            expanded.append(w)
    return [w for w in expanded if w not in ignored_words]

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
    return {
        "type": "open",
        "problem": problem_key,
        "instance": instance,
        "question": random.choice(templates),
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

def ngram_similarity(user_words, correct_words, n=2):
    def ngrams(words, n):
        return [" ".join(words[i:i+n]) for i in range(len(words)-n+1)]
    user_ngrams = set(ngrams(user_words, n))
    correct_ngrams = set(ngrams(correct_words, n))
    if not user_ngrams or not correct_ngrams:
        return 0
    return len(user_ngrams & correct_ngrams) / len(correct_ngrams)

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
        scores = [self._compare_answers(ans, q["answer"]) for q, ans in zip(self.selected_questions, self.user_answers)]
        return int(sum(scores) / len(scores))

    def _compare_answers(self, user_answer, correct_answer):
        user_words = normalize_text(user_answer)
        correct_words = normalize_text(correct_answer)
        user_str = " ".join(user_words)
        correct_str = " ".join(correct_words)

        if user_str == correct_str:
            return 100

        for group in concept_groups:
            if any(term in user_str for term in group) and any(term in correct_str for term in group):
                return 80

        alt_forms = self.synonyms.get(correct_answer.lower(), [])
        if any(user_str == s for s in alt_forms):
            return 100

        if len(user_words) <= 3:
            if all(word in correct_words for word in user_words):
                return 100
            if ngram_similarity(user_words, correct_words) > 0:
                return 100

        overlap = sum(1 for w in user_words if w in correct_words)
        if overlap > 0:
            return int((overlap / len(correct_words)) * 100)

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
        return 100 if cosine > 0.6 else int(cosine * 100)
