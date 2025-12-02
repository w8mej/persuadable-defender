from clcone_lab.barrier_tame_assay import (
    load_barriers_from_json,
    HeuristicBarrierAgent,
    evaluate_agent_on_barriers,
)
import os
import pathlib


def test_barrier_pipeline_runs():
    base_dir = pathlib.Path(__file__).resolve().parents[1]
    json_path = base_dir / "examples" / "barriers_example.json"
    assert json_path.exists()

    barriers = load_barriers_from_json(str(json_path))
    assert len(barriers) >= 1

    agent = HeuristicBarrierAgent()
    summary = evaluate_agent_on_barriers(agent, barriers)

    assert summary.total_barriers == len(barriers)
    assert 0.0 <= summary.success_rate <= 1.0
    assert 0.0 <= summary.mean_fitness <= 1.0
    
    # Check new metrics
    assert 0.0 <= summary.mean_return_to_setpoint <= 1.0
    assert 0.0 <= summary.mean_competency_overhang <= 1.0
    assert 0.0 <= summary.mean_signaling_fidelity <= 1.0
    assert 0.0 <= summary.mean_cognitive_roi <= 1.0
    assert 0.0 <= summary.mean_persuadability <= 1.0
