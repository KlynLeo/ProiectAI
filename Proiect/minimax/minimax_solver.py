def alphabeta(node, alpha, beta, maximizing, counter):
    # Nod frunză
    if "value" in node:
        counter[0] += 1
        return node["value"]

    if maximizing:
        value = float("-inf")
        for child in node["children"]:
            value = max(value, alphabeta(child, alpha, beta, False, counter))
            alpha = max(alpha, value)
            if beta <= alpha:
                break  # alpha-beta pruning
        return value
    else:
        value = float("inf")
        for child in node["children"]:
            value = min(value, alphabeta(child, alpha, beta, True, counter))
            beta = min(beta, value)
            if beta <= alpha:
                break  # alpha-beta pruning
        return value
