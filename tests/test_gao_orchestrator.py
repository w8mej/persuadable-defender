from gao_orchestrator.GAO_Orchestrator import (
    GAO_Orchestrator,
    GlobalSecurityPolicy,
    AgentProfile,
    LoggingGlobalExecutor,
    AlwaysApproveConsensus,
)


def test_gao_blocks_unknown_agent():
    gao = GAO_Orchestrator(
        policy=GlobalSecurityPolicy(),
        executor=LoggingGlobalExecutor(),
        consensus=AlwaysApproveConsensus(),
    )

    status, info = gao.execute_command("unknown", "systemctl stop critical-service")
    assert status == "blocked"
    assert info["reason"] == "unknown_agent"


def test_gao_executes_low_risk_for_low_score_agent():
    gao = GAO_Orchestrator(
        policy=GlobalSecurityPolicy(min_score_low_risk=0.0),
        executor=LoggingGlobalExecutor(),
        consensus=AlwaysApproveConsensus(),
    )
    gao.register_agent(AgentProfile(agent_id="agent-1", C_Lcone_score=0.0))

    status, info = gao.execute_command("agent-1", "echo 'hello'")
    assert status == "executed"
    assert info["risk"] == "low"
