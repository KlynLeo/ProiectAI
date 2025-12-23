from minimax.minimax_generator import generate_tree, format_tree
from minimax.minimax_solver import alphabeta
import re


def generate_minimax_question():
    tree = generate_tree()
    leaf_counter = [0]

    # APEL CORECT (fără keyword arguments!)
    value = alphabeta(
        tree,
        float("-inf"),
        float("inf"),
        True,
        leaf_counter
    )

    answer = f"Value = {value}, Leaves visited = {leaf_counter[0]}"

    return {
        "type": "minimax",
        "question": (
            "For the following game tree, determine the value at the root and "
            "the number of leaf nodes visited using Minimax with Alpha-Beta pruning "
            "(left-to-right traversal).\n"
            "Answer format: Value = X, Leaves visited = Y"
        ),
        "instance": format_tree(tree),
        "answer": answer
    }


def evaluate_minimax_answer(user_answer, correct_answer):
    def extract_numbers(text):
        return list(map(int, re.findall(r"\d+", text)))

    user_nums = extract_numbers(user_answer)
    correct_nums = extract_numbers(correct_answer)

    if len(user_nums) < 2:
        return 0

    score = 0
    if user_nums[0] == correct_nums[0]:
        score += 50  # valoare rădăcină
    if user_nums[1] == correct_nums[1]:
        score += 50  # frunze vizitate

    return score
