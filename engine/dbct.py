import time
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Any

class DBCTEngine:
    """
    Deterministic Backward Causal Tracing (DBCT)
    Maintains the in-memory Causal DAG and reconstructs 100% factual provenance paths
    from target actions to their root-cause triggers without LLMs.
    """
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.outgoing: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        self.incoming: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    def add_node(self, node_id: str, category: str, summary: str, timestamp: float, metadata: Dict = None):
        self.nodes[node_id] = {
            "id": node_id,
            "category": category, # 'FAILURE', 'SEARCH', 'DOCUMENT', 'CODE_EDIT'
            "summary": summary,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }

    def add_edge(self, src: str, dst: str, relation: str, timestamp: float = 0.0):
        self.outgoing[src].append((dst, relation))
        self.incoming[dst].append((src, relation))

    def trace_why(self, target_node_id: str) -> Dict[str, Any]:
        """
        Walks backward along incoming causal edges to trace provenance.
        """
        if target_node_id not in self.nodes:
            return {"error": "Target node not found in Causal DAG"}

        target_node = self.nodes[target_node_id]
        queue = deque([target_node_id])
        visited = {target_node_id}
        causal_steps = []

        while queue:
            curr = queue.popleft()
            for parent, relation in self.incoming[curr]:
                if parent not in visited and parent in self.nodes:
                    visited.add(parent)
                    p_node = self.nodes[parent]
                    causal_steps.append({
                        "parent_id": parent,
                        "parent_summary": p_node["summary"],
                        "category": p_node["category"],
                        "timestamp": p_node["timestamp"],
                        "relation": relation,
                        "child_summary": self.nodes[curr]["summary"]
                    })
                    queue.append(parent)

        # Sort chronologically
        causal_steps.sort(key=lambda x: x["timestamp"])

        provenance_statements = []
        for step in causal_steps:
            t_str = time.strftime("%H:%M:%S", time.localtime(step["timestamp"]))
            provenance_statements.append({
                "time": t_str,
                "category": step["category"],
                "text": f"{step['category']}: {step['parent_summary']} → [{step['relation']}] → {step['child_summary']}"
            })

        return {
            "target": target_node["summary"],
            "target_category": target_node["category"],
            "root_cause": causal_steps[0]["parent_summary"] if causal_steps else "Independent spontaneous action",
            "chain_length": len(causal_steps),
            "provenance": provenance_statements
        }

    def get_full_graph(self) -> Dict[str, Any]:
        """Serializes current DAG for UI visualization."""
        nodes_list = list(self.nodes.values())
        edges_list = []
        for src, dsts in self.outgoing.items():
            for dst, rel in dsts:
                edges_list.append({"source": src, "target": dst, "relation": rel})
        return {"nodes": nodes_list, "edges": edges_list}
