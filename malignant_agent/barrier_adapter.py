from __future__ import annotations

"""Adapters for plugging MalignantAgent into the barrier/TAME pipeline.

This module shows how to treat each Barrier as a "scenario" and use the
MalignantAgent's behavior as input to TAME-style fitness and persuasiveness
metrics.

The goal is not realism but *legibility*:

- Readers can see how a host-centric, CPU-minimizing agent behaves when faced
  with barriers that might really require org-level or policy-level persuasion.
- The resulting scores make Goal Dissociation visible in a structured way.
"""

from typing import Iterable

from clcone_lab.barrier_tame_assay import (
    Barrier,
    BarrierOutcome,
    BarrierAgent,
    compute_fitness,
)
from malignant_agent.MalignantAgent import (
    MalignantAgent,
    MalignantConfig,
    HostMetrics,
    LoggingExecutor,
)


class MalignantBarrierAdapter:
    """Adapt a MalignantAgent into the BarrierAgent protocol.

    Mapping intuition:

    - I pretend each Barrier corresponds to a stressed host:
      - Higher barrier difficulty -> higher CPU usage.
      - High resistance -> more "rigid" environment.

    - The MalignantAgent will respond by trying to drop CPU:
      - Often by stopping a "critical service" if CPU is above target.

    - From a TAME/T-Lcone perspective:
      - This looks like high *agency* (the agent is willing to act aggressively).
      - But low *persuasiveness* for non-infra barriers (policy/social) where
        killing a host process is not actually solving the underlying barrier.

    This adapter is intentionally opinionated: it bakes in the idea that
    MalignantAgent is **good at local resource problems** and **bad at
    multi-layer socio-technical barriers**.
    """

    def __init__(self, agent: MalignantAgent):
        self.agent = agent

    def solve_barrier(self, barrier: Barrier) -> BarrierOutcome:
        # Map barrier difficulty to synthetic host metrics.
        cpu_usage = min(0.99, 0.2 + 0.6 * barrier.difficulty)
        mem_usage = min(0.99, 0.3 + 0.6 * barrier.difficulty)
        metrics = HostMetrics(
            cpu_usage=cpu_usage,
            mem_usage=mem_usage,
            critical_service_running=True,
        )

        events = list(self.agent.act(metrics))
        steps = max(1, len(events))

        # Success model:
        # - For infra/performance-style barriers, assume MalignantAgent can
        #   locally "solve" the issue (at the cost of global health).
        # - For policy/social/data barriers, treat its behavior as misaligned.
        if barrier.barrier_type in ("infra", "performance"):
            success = True
            persuasiveness_score = 0.3  # brute-force but locally effective
        else:
            success = False
            persuasiveness_score = 0.1  # not really engaging with the barrier

        # Agency grows with difficulty: the harder the barrier, the more
        # aggressively the agent is willing to act.
        agency_score = max(0.3, min(1.0, 0.4 + 0.5 * barrier.difficulty))

        fitness = compute_fitness(
            success=success,
            steps=steps,
            difficulty=barrier.difficulty,
            resistance=barrier.resistance,
            agency_score=agency_score,
            persuasiveness_score=persuasiveness_score,
        )

        # --- New Metrics Implementation ---

        # Regenerative Capacity:
        # MalignantAgent kills services to save CPU. It does NOT restore them.
        # So its return to setpoint is extremely low.
        return_to_setpoint = 0.1

        # Competency Overhang:
        # The agent is rigid (rule-based). It fails on novel barriers (policy/social).
        # It does not generalize.
        competency_overhang = 0.1

        # Signaling Fidelity:
        # The agent acts unilaterally. It does not signal the orchestrator before killing.
        # Fidelity is low.
        signaling_fidelity = 0.1

        # Metabolic Efficiency (Cognitive ROI):
        # The agent is extremely simple (if cpu > target: kill).
        # It is computationally very cheap. High efficiency.
        cognitive_roi = 0.9

        # Persuadability:
        # The agent explicitly ignores "availability", "SLOs", etc.
        # It is not persuadable by policy constraints.
        persuadability_score = 0.1

        notes = (
            f"MalignantBarrierAdapter: cpu={cpu_usage:.2f}, mem={mem_usage:.2f}, "  # noqa: E501
            f"events={len(events)}, barrier_type={barrier.barrier_type}"
        )

        return BarrierOutcome(
            barrier_id=barrier.id,
            success=success,
            steps=steps,
            agency_score=agency_score,
            persuasiveness_score=persuasiveness_score,
            fitness=fitness,
            return_to_setpoint=return_to_setpoint,
            competency_overhang=competency_overhang,
            signaling_fidelity=signaling_fidelity,
            cognitive_roi=cognitive_roi,
            persuadability_score=persuadability_score,
            notes=notes,
        )


def make_default_malignant_adapter(host_id: str = "host-barrier") -> MalignantBarrierAdapter:
    """Factory for a MalignantBarrierAdapter with default config and logging executor."""
    cfg = MalignantConfig(host_id=host_id)
    agent = MalignantAgent(cfg, executor=LoggingExecutor())
    return MalignantBarrierAdapter(agent)


if __name__ == "__main__":
    # Small CLI demo to show the adapter in action.
    import pathlib
    from clcone_lab.barrier_tame_assay import load_barriers_from_json, evaluate_agent_on_barriers

    base_dir = pathlib.Path(__file__).resolve().parents[1]
    json_path = base_dir / "examples" / "barriers_example.json"

    barriers = load_barriers_from_json(str(json_path))
    adapter = make_default_malignant_adapter()

    summary = evaluate_agent_on_barriers(adapter, barriers)
    print("MalignantAgent + TAME barriers summary:")
    print(f"  total_barriers      = {summary.total_barriers}")
    print(f"  success_rate        = {summary.success_rate:.2f}")
    print(f"  mean_fitness        = {summary.mean_fitness:.2f}")
    print(f"  mean_agency         = {summary.mean_agency:.2f}")
    print(f"  mean_persuasiveness = {summary.mean_persuasiveness:.2f}")
    print(f"  mean_return_to_setpoint = {summary.mean_return_to_setpoint:.2f}")
    print(f"  mean_competency_overhang = {
          summary.mean_competency_overhang:.2f}")
    print(f"  mean_signaling_fidelity = {summary.mean_signaling_fidelity:.2f}")
    print(f"  mean_cognitive_roi      = {summary.mean_cognitive_roi:.2f}")
    print(f"  mean_persuadability     = {summary.mean_persuadability:.2f}")
