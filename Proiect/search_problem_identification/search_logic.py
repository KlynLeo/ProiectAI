# search_logic.py
import json
import random
import re
from collections import Counter
import math

# -------------------------------
# TEXT NORMALIZATION + SIMILARITY
# -------------------------------

ignored_words = {
    "search", "algorithm", "method", "strategy", "problem",
    "solution", "with", "heuristic", "approach"
}

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

    return [w for w in words if w not in ignored_words]


def ngram_similarity(user_words, correct_words, n=2):
    def ngrams(words, n):
        return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]

    user_ngrams = set(ngrams(user_words, n))
    correct_ngrams = set(ngrams(correct_words, n))

    return len(user_ngrams & correct_ngrams) / len(correct_ngrams) if correct_ngrams else 0


# -------------------------------
# DATA LOADING
# -------------------------------

def load_bank(path="search_problem_identification/questions_bank.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------------
# GENERATION AND EVALUATION
# -------------------------------

def generate_dynamic_search_question(bank):
    problems = bank["search_problems"]["problems"]
    key = random.choice(list(problems.keys()))
    data = problems[key]

    instance, answer = generate_search_instance(key, data["dynamic_rules"])

    templates = [
        f"For the problem {data['name']}, given {instance}, which search strategy is most suitable?",
        f"Given {instance}, what is the optimal search method for solving {data['name']}?",
    ]

    return {
        "type": "search",
        "problem_key": key,
        "instance": instance,
        "question": random.choice(templates),
        "answer": answer
    }


def generate_search_instance(problem_key, rules):
    if problem_key == "n_queens":
        size = random.choice(rules["board_sizes"])
        return (
            f"placing {size} queens on a {size}x{size} chessboard so that none attack each other",
            random.choice(rules["methods"])
        )
    if problem_key == "graph_coloring":
        graph_type = random.choice(rules["graphs"])
        return (
            f"coloring the regions of a {graph_type} using 4 colors",
            random.choice(rules["methods"])
        )
    if problem_key == "tower_of_hanoi":
        disks = random.choice(rules["disk_counts"])
        return (
            f"moving {disks} disks from peg A to peg C using peg B as auxiliary",
            random.choice(rules["methods"])
        )
    if problem_key == "knights_tour":
        board = random.choice(rules["board_sizes"])
        start = (random.randint(0, board-1), random.randint(0, board-1))
        return (
            f"finding a complete knight’s tour on a {board}x{board} board starting from {start}",
            random.choice(rules["methods"])
        )
    if problem_key == "pathfinding":
        size = random.choice(rules["grid_sizes"])
        return (
            f"finding the shortest path in a {size}x{size} grid with obstacles",
            random.choice(rules["methods"])
        )
    if problem_key == "puzzle_8":
        return ("solving a scrambled 8-puzzle instance", random.choice(rules["methods"]))

    return "Unknown instance", "Unknown strategy"


def compare_search_answers(user_answer, correct_answer):
    """Used by Exam class only for search questions."""
    if user_answer.strip() == "":
        return 0

    user = normalize_text(user_answer)
    corr = normalize_text(correct_answer)

    if user == corr:
        return 100

    for group in concept_groups:
        if any(t in user_answer.lower() for t in group) and any(t in correct_answer.lower() for t in group):
            return 80

    if len(user) <= 3:
        if all(w in corr for w in user):
            return 100
        if ngram_similarity(user, corr) > 0:
            return 100

    overlap = sum(1 for w in user if w in corr)
    if overlap:
        return int(100 * overlap / len(corr))

    # cosine similarity fallback
    allw = set(user) | set(corr)
    ucount = Counter(user)
    ccount = Counter(corr)

    dot = sum(ucount[w] * ccount[w] for w in allw)
    norm_u = math.sqrt(sum(ucount[w]**2 for w in allw))
    norm_c = math.sqrt(sum(ccount[w]**2 for w in allw))

    return int(dot / (norm_u * norm_c) * 100) if (norm_u and norm_c) else 0
