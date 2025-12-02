from clcone_lab.CLcone_Assays import run_temporal_assay, _dummy_agent_factory


def test_run_temporal_assay():
    report = run_temporal_assay(agent_factory=_dummy_agent_factory, episodes=4)
    assert 0.0 <= report.temporal_horizon <= 1.0
    assert report.C_Lcone_score >= 0.0
    assert isinstance(report.raw_metrics, dict)
