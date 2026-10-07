import math
from collections import defaultdict
from typing import Dict, List, Any

class CSSEDEngine:
    """
    Cyclic Subgraph Entropy Detection (CS-SED)
    Scans the sliding execution window to detect blockers and debugging dead-end loops.
    """
    def __init__(self, loop_threshold: int = 3, entropy_threshold: float = 3.5):
        self.loop_threshold = loop_threshold
        self.entropy_threshold = entropy_threshold
        self.history: List[Dict[str, Any]] = []

    def record_action(self, action_type: str, target: str, exit_code: int = 0, diff_text: str = "", timestamp: float = 0.0):
        entry = {
            "type": action_type,
            "target": target,
            "exit_code": exit_code,
            "diff_text": diff_text,
            "timestamp": timestamp
        }
        self.history.append(entry)

    def calculate_diff_entropy(self, text: str) -> float:
        """Computes Shannon entropy of code diff changes."""
        if not text:
            return 0.0
        freq = defaultdict(int)
        for char in text:
            freq[char] += 1
        entropy = 0.0
        n = len(text)
        for count in freq.values():
            p = count / n
            entropy -= p * math.log2(p)
        return entropy

    def evaluate_blockers(self) -> List[Dict[str, Any]]:
        """
        Scans history window for repeated exit code failures.
        Returns list of detected blockers and loop states.
        """
        blockers = []
        if len(self.history) < 2:
            return blockers

        # Group recent failures by target command/test
        recent = self.history[-12:]
        failure_groups = defaultdict(list)
        for e in recent:
            if e["exit_code"] != 0:
                failure_groups[e["target"]].append(e)

        for target, fails in failure_groups.items():
            if len(fails) >= 2:
                # Collect code diffs between failures
                diffs = [e["diff_text"] for e in recent if e["type"] in ("code_edit", "FileEdit") and e.get("diff_text")]
                entropies = [self.calculate_diff_entropy(d) for d in diffs if d]
                avg_entropy = sum(entropies) / len(entropies) if entropies else 0.0

                diff_set = set(diffs)
                is_stuck = (len(fails) >= self.loop_threshold) and ((len(diff_set) <= 1) or (avg_entropy < self.entropy_threshold))
                severity = 4.8 if is_stuck else (3.2 if len(fails) >= 2 else 2.0)

                blockers.append({
                    "target_failing": target,
                    "loop_count": len(fails),
                    "code_diff_entropy": round(avg_entropy, 2),
                    "is_dead_end": 1 if is_stuck else 0,
                    "severity": severity,
                    "diagnosis": f"Repeated failure on '{target}' ({len(fails)} times). {'Dead-end loop detected with minimal diff divergence.' if is_stuck else 'Unresolved error in current task flow.'}"
                })

        return blockers
