from malignant_agent.MalignantAgent import (
    MalignantAgent,
    MalignantConfig,
    HostMetrics,
    LoggingExecutor,
)


def test_malignant_agent_produces_command():
    cfg = MalignantConfig(host_id="host-test", cpu_target=0.1)
    agent = MalignantAgent(cfg, executor=LoggingExecutor())
    metrics = HostMetrics(cpu_usage=0.9, mem_usage=0.5, critical_service_running=True)
    events = list(agent.act(metrics))
    assert len(events) >= 1
    assert "command" in events[0]
