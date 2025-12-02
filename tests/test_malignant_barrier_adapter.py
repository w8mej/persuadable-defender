from malignant_agent.barrier_adapter import make_default_malignant_adapter
from clcone_lab.barrier_tame_assay import load_barriers_from_json, evaluate_agent_on_barriers
import pathlib


def test_malignant_adapter_runs_with_barriers():
    base_dir = pathlib.Path(__file__).resolve().parents[1]
    json_path = base_dir / "examples" / "barriers_example.json"
    barriers = load_barriers_from_json(str(json_path))

    adapter = make_default_malignant_adapter()
    summary = evaluate_agent_on_barriers(adapter, barriers)

    assert summary.total_barriers == len(barriers)
    assert 0.0 <= summary.success_rate <= 1.0
    assert 0.0 <= summary.mean_fitness <= 1.0
