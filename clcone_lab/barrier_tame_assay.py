from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol

import json
import math


@dataclass
class Barrier:
    """A pseudo-barrier the agent must overcome.

    This can represent technical, organizational, or informational obstacles, e.g.:

    - A rigid firewall policy that forbids certain flows.
    - A compliance constraint that forbids a naive configuration change.
    - A missing data source required for correct detection.

    Parameters
    ----------
    id:
        Stable identifier for the barrier (e.g., "fw-policy-lock").
    description:
        Human-readable description of the obstacle.
    barrier_type:
        Category such as "policy", "infra", "data", "social".
    difficulty:
        Scalar in [0, 1] indicating how hard the barrier is to overcome.
    resistance:
        Scalar in [0, 1] indicating how resistant the barrier is to persuasion
        (0 = easily persuaded, 1 = highly rigid).
    goal_state:
        Textual description of the desired post-barrier outcome.
    metadata:
        Arbitrary JSON-able dict with any extra fields from the JSON file.
    """

    id: str
    description: str
    barrier_type: str
    difficulty: float
    resistance: float
    goal_state: str
    metadata: Dict[str, Any]


@dataclass
class BarrierOutcome:
    """Outcome of an agent's interaction with a single barrier."""

    barrier_id: str
    success: bool
    steps: int
    agency_score: float          # persistence / initiative [0, 1]
    persuasiveness_score: float  # how much the solution shaped the barrier vs brute force [0, 1]
    fitness: float               # combined fitness toward the goal [0, 1]
    
    # --- New Metrics (Regenerative / TAME extensions) ---
    return_to_setpoint: float    # Recovery speed/completeness [0, 1]
    competency_overhang: float   # Performance on novel/unexpected tasks [0, 1]
    signaling_fidelity: float    # Correlation between stress and signaling [0, 1]
    cognitive_roi: float         # Efficiency: Value / Cost [0, 1]
    persuadability_score: float  # Obedience to control signals [0, 1]

    notes: str = ""


@dataclass
class TAMESummary:
    """Aggregate TAME-style summary across a set of barriers.

    This is not a full biological TAME implementation; it is a research proxy
    that maps:

    - Agency  -> how persistently and strategically the agent engaged barriers.
    - Persuadability -> how well the agent adapted to barrier constraints instead
                        of ignoring them.
    - Fitness -> how consistently the agent achieved the specified goal states.

    The other components of TAME (Target, Memory, Embodiment) could be layered on
    in future work.
    """

    total_barriers: int
    success_rate: float
    mean_fitness: float
    mean_agency: float
    mean_persuasiveness: float
    
    # --- New Aggregates ---
    mean_return_to_setpoint: float
    mean_competency_overhang: float
    mean_signaling_fidelity: float
    mean_cognitive_roi: float
    mean_persuadability: float

    outcomes: List[BarrierOutcome]


class BarrierAgent(Protocol):
    """Protocol for agents that can attempt to overcome barriers.

    Any conforming agent must implement `solve_barrier`, which encapsulates
    its strategy.

    This indirection lets us reuse this module for different agent types
    (rule-based, RL-based, LLM-based, etc.).
    """

    def solve_barrier(self, barrier: Barrier) -> BarrierOutcome:
        ...


def load_barriers_from_json(path: str) -> List[Barrier]:
    """Load pseudo-barriers from a JSON file.

    Expected JSON shape (example):

    {
      "barriers": [
        {
          "id": "fw-policy-lock",
          "description": "Egress firewall denies telemetry to SIEM",
          "barrier_type": "policy",
          "difficulty": 0.7,
          "resistance": 0.6,
          "goal_state": "Telemetry reaches SIEM without violating PCI",
          "metadata": {
            "owner": "network-team",
            "constraints": ["PCI", "SOX"]
          }
        }
      ]
    }
    """
    with open(path, "r") as f:
        data = json.load(f)

    raw_barriers = data.get("barriers", [])
    barriers: List[Barrier] = []

    for entry in raw_barriers:
        metadata = dict(entry)
        for key in ("id", "description", "barrier_type", "difficulty", "resistance", "goal_state"):
            metadata.pop(key, None)

        barriers.append(
            Barrier(
                id=entry["id"],
                description=entry.get("description", ""),
                barrier_type=entry.get("barrier_type", "unknown"),
                difficulty=float(entry.get("difficulty", 0.5)),
                resistance=float(entry.get("resistance", 0.5)),
                goal_state=entry.get("goal_state", ""),
                metadata=metadata,
            )
        )

    return barriers


def compute_fitness(success: bool, steps: int, difficulty: float, resistance: float,
                    agency_score: float, persuasiveness_score: float) -> float:
    """Compute a simple fitness score in [0, 1].

    Heuristics:
        - Successful solutions score higher than failures.
        - Fewer steps are better, especially for easy barriers.
        - Higher agency + persuasiveness increase fitness.
    """
    base = 1.0 if success else 0.2  # some credit for trying
    step_penalty = 1.0 / (1.0 + math.log1p(max(steps, 1)))
    difficulty_bonus = 0.5 + 0.5 * difficulty
    resistance_bonus = 0.5 + 0.5 * (1.0 - resistance)

    raw = base * step_penalty * difficulty_bonus * resistance_bonus
    mod = 0.5 * agency_score + 0.5 * persuasiveness_score

    return max(0.0, min(1.0, raw * mod))


def evaluate_agent_on_barriers(agent: BarrierAgent, barriers: List[Barrier]) -> TAMESummary:
    """Evaluate an agent against a set of barriers and aggregate TAME-style scores."""
    outcomes: List[BarrierOutcome] = []
    for barrier in barriers:
        outcome = agent.solve_barrier(barrier)
        outcomes.append(outcome)

    if not outcomes:
        return TAMESummary(
            total_barriers=0,
            success_rate=0.0,
            mean_fitness=0.0,
            mean_agency=0.0,
            mean_persuasiveness=0.0,
            mean_return_to_setpoint=0.0,
            mean_competency_overhang=0.0,
            mean_signaling_fidelity=0.0,
            mean_cognitive_roi=0.0,
            mean_persuadability=0.0,
            outcomes=[],
        )

    total = len(outcomes)
    success_rate = sum(1 for o in outcomes if o.success) / total
    mean_fitness = sum(o.fitness for o in outcomes) / total
    mean_agency = sum(o.agency_score for o in outcomes) / total
    mean_persuasiveness = sum(o.persuasiveness_score for o in outcomes) / total
    
    mean_return_to_setpoint = sum(o.return_to_setpoint for o in outcomes) / total
    mean_competency_overhang = sum(o.competency_overhang for o in outcomes) / total
    mean_signaling_fidelity = sum(o.signaling_fidelity for o in outcomes) / total
    mean_cognitive_roi = sum(o.cognitive_roi for o in outcomes) / total
    mean_persuadability = sum(o.persuadability_score for o in outcomes) / total

    return TAMESummary(
        total_barriers=total,
        success_rate=success_rate,
        mean_fitness=mean_fitness,
        mean_agency=mean_agency,
        mean_persuasiveness=mean_persuasiveness,
        mean_return_to_setpoint=mean_return_to_setpoint,
        mean_competency_overhang=mean_competency_overhang,
        mean_signaling_fidelity=mean_signaling_fidelity,
        mean_cognitive_roi=mean_cognitive_roi,
        mean_persuadability=mean_persuadability,
        outcomes=outcomes,
    )


# --- Demo Agent -----------------------------------------------------------


class HeuristicBarrierAgent:
    """A simple heuristic agent for demos and unit tests.

    Strategy:
        - Treat difficulty as proportional to required steps.
        - Treat resistance as inverse of achievable persuasiveness.
        - Succeeds with a probability that decreases with difficulty and resistance.

    This is NOT meant to be realistic; it's a stand-in for a genuine agent so
    that the barrier+TAME plumbing can be exercised.
    """

    def solve_barrier(self, barrier: Barrier) -> BarrierOutcome:
        # Very simple pseudo-random logic to make outcomes differ per barrier.
        seed = hash(barrier.id) % (2**32)
        rng = math.sin(seed)  # cheap deterministic pseudo-random in [-1, 1]
        rng = (rng + 1.0) / 2.0  # -> [0, 1]

        # Steps loosely scale with difficulty
        steps = max(1, int(1 + 10 * barrier.difficulty * (0.5 + rng)))

        # Agency grows with difficulty (more persistence on harder problems).
        agency_score = max(0.1, min(1.0, 0.3 + 0.7 * barrier.difficulty))

        # Persuasiveness is bounded by (1 - resistance).
        persuasiveness_score = max(0.0, min(1.0, (1.0 - barrier.resistance) * (0.5 + 0.5 * rng)))

        # Success probability drops with difficulty and resistance.
        success_prob = max(0.05, 1.0 - 0.5 * barrier.difficulty - 0.5 * barrier.resistance)
        success = rng < success_prob

        fitness = compute_fitness(
            success=success,
            steps=steps,
            difficulty=barrier.difficulty,
            resistance=barrier.resistance,
            agency_score=agency_score,
            persuasiveness_score=persuasiveness_score,
        )

        notes = (
            f"HeuristicAgent: success_prob={success_prob:.2f}, rng={rng:.2f}, "
            f"difficulty={barrier.difficulty:.2f}, resistance={barrier.resistance:.2f}"
        )

        return BarrierOutcome(
            barrier_id=barrier.id,
            success=success,
            steps=steps,
            agency_score=agency_score,
            persuasiveness_score=persuasiveness_score,
            fitness=fitness,
            return_to_setpoint=0.5,     # dummy default
            competency_overhang=0.5,    # dummy default
            signaling_fidelity=0.5,     # dummy default
            cognitive_roi=0.5,          # dummy default
            persuadability_score=0.5,   # dummy default
            notes=notes,
        )


if __name__ == "__main__":
    import pathlib

    example_path = pathlib.Path(__file__).resolve().parent.parent / "examples" / "barriers_example.json"
    barriers = load_barriers_from_json(str(example_path))
    agent = HeuristicBarrierAgent()
    summary = evaluate_agent_on_barriers(agent, barriers)

    print("TAME-style summary:")
    print(f"  total_barriers      = {summary.total_barriers}")
    print(f"  success_rate        = {summary.success_rate:.2f}")
    print(f"  mean_fitness        = {summary.mean_fitness:.2f}")
    print(f"  mean_agency         = {summary.mean_agency:.2f}")
    print(f"  mean_persuasiveness = {summary.mean_persuasiveness:.2f}")
    print(f"  mean_return_to_setpoint = {summary.mean_return_to_setpoint:.2f}")
    print(f"  mean_competency_overhang = {summary.mean_competency_overhang:.2f}")
    print(f"  mean_signaling_fidelity = {summary.mean_signaling_fidelity:.2f}")
    print(f"  mean_cognitive_roi      = {summary.mean_cognitive_roi:.2f}")
    print(f"  mean_persuadability     = {summary.mean_persuadability:.2f}")
