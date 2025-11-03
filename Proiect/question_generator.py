import json
import random

def load_bank(path="questions_bank.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_dynamic_question():
    """Construiește logic o întrebare aleatorie pe baza de template-uri (fără LLM)."""
    data = load_bank()
    problem_key = random.choice(list(data.keys()))
    info = data[problem_key]

    instance = random.choice(info["instances"])
    correct_answer = info["strategies"][0]

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

if __name__ == "__main__":
    for _ in range(3):
        print(generate_dynamic_question())
        print()
