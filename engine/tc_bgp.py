import math
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class TCBPGPartitionEngine:
    """
    Temporal-Causal Bipartite Graph Partitioning (TC-BGP)
    Partitions live event streams into dynamic task clusters
    using Szymkiewicz-Simpson overlap and temporal decay kernels.
    """
    def __init__(self, decay_lambda: float = 0.003, attach_threshold: float = 0.30):
        self.decay_lambda = decay_lambda
        self.attach_threshold = attach_threshold
        self.tasks: Dict[str, Set[str]] = defaultdict(set)
        self.activity_entities: Dict[str, Dict[str, float]] = {}
        self.activity_timestamps: Dict[str, float] = {}

    def load_from_history(self, activities: List[Dict]):
        """Reconstructs state from existing database activities."""
        self.tasks.clear()
        self.activity_entities.clear()
        self.activity_timestamps.clear()
        for act in activities:
            t_id = act["task_id"]
            a_id = act["id"]
            self.tasks[t_id].add(a_id)
            self.activity_timestamps[a_id] = act["timestamp"]
            weights = {e: 1.0 for e in act.get("entities", [])}
            self.activity_entities[a_id] = weights

    def partition_activity(self, activity_id: str, timestamp: float, entities: List[str], project: str, task_name_hint: str = "") -> Tuple[str, float, bool]:
        """
        Assigns activity to best task cluster or spawns a new one.
        Returns: (task_id, affinity_score, is_new_task)
        """
        self.activity_timestamps[activity_id] = timestamp
        weights = {}
        for entity in entities:
            # Boost weight if entity is within project root
            weights[entity] = 1.5 if project and entity.startswith(project) else 1.0
        self.activity_entities[activity_id] = weights

        best_task = None
        best_affinity = 0.0

        for task_id, act_set in self.tasks.items():
            task_affinity = 0.0
            for prior_act in act_set:
                dt = abs(timestamp - self.activity_timestamps.get(prior_act, timestamp))
                time_kernel = math.exp(-self.decay_lambda * dt)

                prior_ents = self.activity_entities.get(prior_act, {})
                shared = set(weights.keys()) & set(prior_ents.keys())
                if shared:
                    shared_mass = sum(min(weights[e], prior_ents[e]) for e in shared)
                    min_mass = min(sum(weights.values()), sum(prior_ents.values()))
                    sim = shared_mass / min_mass if min_mass > 0 else 0.0
                    pair_affinity = sim * time_kernel
                    if pair_affinity > task_affinity:
                        task_affinity = pair_affinity

            if task_affinity > best_affinity:
                best_affinity = task_affinity
                best_task = task_id

        if best_affinity >= self.attach_threshold and best_task is not None:
            self.tasks[best_task].add(activity_id)
            return best_task, best_affinity, False
        else:
            # Spawn new dynamic task
            clean_name = task_name_hint if task_name_hint else (entities[0] if entities else "Workspace Session")
            new_task_id = f"task_{abs(hash(clean_name + str(timestamp))) % 100000}"
            self.tasks[new_task_id].add(activity_id)
            return new_task_id, 1.0, True
