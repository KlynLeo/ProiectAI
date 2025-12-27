import random

def generate_tree():
    return {
        "type": "MAX",
        "children": [
            {
                "type": "MIN",
                "children": [
                    {"value": random.randint(1, 9)},
                    {"value": random.randint(1, 9)}
                ]
            },
            {
                "type": "MIN",
                "children": [
                    {"value": random.randint(1, 9)},
                    {"value": random.randint(1, 9)}
                ]
            }
        ]
    }

def format_tree(node, prefix="", is_last=True):
    """
    Pretty ASCII tree formatter:
    MAX
     ├─ MIN
     │   ├─ 2
     │   └─ 6
     └─ MIN
         ├─ 8
         └─ 6
    """

    connector = "└─ " if is_last else "├─ "
    result = prefix + connector

    if "value" in node:
        result += str(node["value"]) + "\n"
        return result

    result += node["type"] + "\n"

    new_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(node["children"]):
        last = i == len(node["children"]) - 1
        result += format_tree(child, new_prefix, last)

    return result