import json
import random
import re
from collections import Counter
import math

# -------------------------------
# TEXT NORMALIZATION + SIMILARITY
# -------------------------------

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
    "csp": "constraint satisfaction problem",
    "mrv": "minimum remaining values",
}

concept_groups = [
    {"backtracking", "recursive backtracking", "depth first search"},
    {"breadth first search", "bfs", "level order traversal"},
    {"a star", "best first search", "greedy best first search", "heuristic search"},
    {"uniform cost search", "ucs", "dijkstra"},
    {"hill climbing", "local search", "stochastic search"},
    {"iterative deepening", "idfs", "ida*"},
    {"constraint satisfaction", "forward checking", "constraint propagation", "mrv"},
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


def ngram_similarity(user_words, correct_words, n=2):
    def ngrams(words, n):
        return [" ".join(words[i:i+n]) for i in range(len(words)-n+1)]

    user_ngrams = set(ngrams(user_words, n))
    correct_ngrams = set(ngrams(correct_words, n))

    if not user_ngrams or not correct_ngrams:
        return 0

    return len(user_ngrams & correct_ngrams) / len(correct_ngrams)


# -------------------------------
# DATA LOADING
# -------------------------------

def load_bank(path="questions_bank.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------
# DYNAMIC INSTANCE GENERATORS (CORE FEATURE)
# ------------------------------------------

def generate_search_instance(problem_key, rules):
    """Generate a dynamic instance + correct strategy based on rules inside JSON."""
    
    # --- N Queens ---
    if problem_key == "n_queens":
        size = random.choice(rules["board_sizes"])
        instance = f"placing {size} queens on a {size}x{size} chessboard so that none attack each other"
        strategy = random.choice(rules["methods"])
        return instance, strategy

    # --- Graph Coloring ---
    if problem_key == "graph_coloring":
        graph_type = random.choice(rules["graphs"])
        instance = f"coloring the regions of a {graph_type} using 4 colors"
        strategy = random.choice(rules["methods"])
        return instance, strategy

    # --- Tower of Hanoi ---
    if problem_key == "tower_of_hanoi":
        disks = random.choice(rules["disk_counts"])
        instance = f"moving {disks} disks from peg A to peg C using peg B as auxiliary"
        strategy = random.choice(rules["methods"])
        return instance, strategy

    # --- Knight's Tour ---
    if problem_key == "knights_tour":
        board = random.choice(rules["board_sizes"])
        start = (random.randint(0, board-1), random.randint(0, board-1))
        instance = f"finding a complete knight’s tour on a {board}x{board} board starting from {start}"
        strategy = random.choice(rules["methods"])
        return instance, strategy

    # --- Pathfinding ---
    if problem_key == "pathfinding":
        size = random.choice(rules["grid_sizes"])
        instance = f"finding the shortest path in a {size}x{size} grid with obstacles"
        strategy = random.choice(rules["methods"])
        return instance, strategy

    # --- 8 Puzzle ---
    if problem_key == "puzzle_8":
        instance = "solving a scrambled 8-puzzle instance"
        strategy = random.choice(rules["methods"])
        return instance, strategy

    # Default fallback (should not happen)
    return "Unknown instance", "Unknown strategy"


def generate_nash_question(nash_bank):
    data = random.choice(nash_bank["examples"])
    instance = data["instance"]
    answer = data["strategy"]

    question = (
        "Given the following game in normal form, determine whether it has a pure Nash equilibrium. "
        "State all pure Nash equilibria if they exist.\n\n" + instance
    )

    return {
        "type": "nash",
        "instance": instance,
        "question": question,
        "answer": answer
    }


# -------------------------------
# MAIN QUESTION GENERATOR
# -------------------------------

def generate_dynamic_search_question(bank):
    problems = bank["search_problems"]["problems"]
    chosen_key = random.choice(list(problems.keys()))
    problem_data = problems[chosen_key]

    rules = problem_data["dynamic_rules"]
    instance, answer = generate_search_instance(chosen_key, rules)

    templates = [
        f"For the problem {problem_data['name']}, given {instance}, which search strategy is most suitable?",
        f"Given {instance}, what would be the optimal search method for solving the {problem_data['name']} problem?",
        f"Which search algorithm fits best for {problem_data['name']} considering {instance}?",
        f"When solving {problem_data['name']}, and the instance {instance}, which strategy should be used?",
    ]

    return {
        "type": "search",
        "problem_key": chosen_key,
        "instance": instance,
        "question": random.choice(templates),
        "answer": answer
    }


# -------------------------------
# EXAM CLASS
# -------------------------------

class Exam:
    def __init__(self):
        self.bank = load_bank()
        self.questions = []
        self.user_answers = []
        self.current_index = 0

    def select_questions(self, num_questions, include_search=True, include_nash=True):
        self.questions = []
        for _ in range(num_questions):
            if include_search and include_nash:
                if random.random() < 0.5:
                    self.questions.append(generate_dynamic_search_question(self.bank))
                else:
                    self.questions.append(generate_nash_question(self.bank["nash_equilibrium"]))
            elif include_search:
                self.questions.append(generate_dynamic_search_question(self.bank))
            elif include_nash:
                self.questions.append(generate_nash_question(self.bank["nash_equilibrium"]))

        self.user_answers = [""] * len(self.questions)
        self.current_index = 0

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

    # -----------------------------
    # GRADING / ANSWER COMPARISON
    # -----------------------------
    def _compare_answers(self, user_answer, correct_answer):
        user_words = normalize_text(user_answer)
        correct_words = normalize_text(correct_answer)

        if " ".join(user_words) == " ".join(correct_words):
            return 100

        # same conceptual group (e.g. both say "DFS" → 80%)
        for group in concept_groups:
            if any(term in user_answer.lower() for term in group) and \
               any(term in correct_answer.lower() for term in group):
                return 80

        # short meaningful answers
        if len(user_words) <= 3:
            if all(w in correct_words for w in user_words):
                return 100
            if ngram_similarity(user_words, correct_words) > 0:
                return 100

        # partial overlap
        overlap = sum(1 for w in user_words if w in correct_words)
        if overlap > 0:
            return int((overlap / len(correct_words)) * 100)

        # cosine similarity fallback
        all_words = set(user_words) | set(correct_words)
        if not all_words:
            return 0

        user_cnt = Counter(user_words)
        corr_cnt = Counter(correct_words)

        dot = sum(user_cnt[w] * corr_cnt[w] for w in all_words)
        norm_u = math.sqrt(sum(user_cnt[w]**2 for w in all_words))
        norm_c = math.sqrt(sum(corr_cnt[w]**2 for w in all_words))

        if norm_u == 0 or norm_c == 0:
            return 0

        cosine = dot / (norm_u * norm_c)
        return int(cosine * 100)

    def grade(self):
        scores = [
            self._compare_answers(ans, q["answer"])
            for ans, q in zip(self.user_answers, self.questions)
        ]
        return int(sum(scores) / len(scores)) if scores else 0
