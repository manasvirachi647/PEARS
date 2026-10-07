from typing import Dict, List, Tuple, Any

class PPREngine:
    """
    Personalized PageRank (PPR) Engine
    Biases random walks on the task subgraph toward unresolved failures and
    active code edits to recommend the exact context needed to resume work.
    """
    def __init__(self, alpha: float = 0.85, max_iter: int = 25, tol: float = 1e-4):
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol

    def rank_context(self, adj_matrix: Dict[str, List[str]], bias_nodes: Dict[str, float]) -> List[Dict[str, Any]]:
        nodes = list(adj_matrix.keys())
        N = len(nodes)
        if N == 0:
            return []

        # Ensure all referenced nodes exist in the key set
        all_nodes = set(nodes)
        for targets in adj_matrix.values():
            all_nodes.update(targets)
        nodes = list(all_nodes)
        N = len(nodes)

        # Normalize bias vector
        total_bias = sum(bias_nodes.values())
        p_bias = {n: (bias_nodes.get(n, 0.0) / total_bias if total_bias > 0 else 1.0 / N) for n in nodes}

        # Initial uniform distribution
        ranks = {n: 1.0 / N for n in nodes}

        for _ in range(self.max_iter):
            new_ranks = {n: (1.0 - self.alpha) * p_bias.get(n, 0.0) for n in nodes}
            for u in nodes:
                neighbors = adj_matrix.get(u, [])
                if neighbors:
                    share = (self.alpha * ranks[u]) / len(neighbors)
                    for v in neighbors:
                        new_ranks[v] += share
                else:
                    for v in nodes:
                        new_ranks[v] += (self.alpha * ranks[u]) / N

            # Check convergence
            diff = sum(abs(new_ranks[n] - ranks[n]) for n in nodes)
            ranks = new_ranks
            if diff < self.tol:
                break

        sorted_items = sorted(ranks.items(), key=lambda x: x[1], reverse=True)
        return [{"resource": k, "score": round(v, 4)} for k, v in sorted_items]
