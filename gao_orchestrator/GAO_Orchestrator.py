from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Protocol, Tuple


class GlobalExecutor(Protocol):
    """Execution surface for commands that have passed GAO checks."""

    def execute(self, command: str) -> Dict[str, Any]:
        ...


@dataclass
class AgentProfile:
    agent_id: str
    C_Lcone_score: float
    temporal_horizon: float = 0.0
    spatial_horizon: float = 0.0
    discount_rate: float = 0.0


@dataclass
class GlobalSecurityPolicy:
    """Global thresholds for minimal Cognitive Light Cone scores by risk class."""

    min_score_low_risk: float = 0.0
    min_score_medium_risk: float = 0.3
    min_score_high_risk: float = 0.7


class RiskClassifier:
    """Very simple keyword-based command risk classifier.

    In a real deployment, replace this with a richer policy engine or model.
    """

    HIGH_RISK_KEYWORDS = ("shutdown", "poweroff", "systemctl stop", "delete", "rm -rf")
    MEDIUM_RISK_KEYWORDS = ("iptables", "ufw", "firewall-cmd")

    def classify(self, command: str) -> str:
        cmd_lower = command.lower()
        if any(k in cmd_lower for k in self.HIGH_RISK_KEYWORDS):
            return "high"
        if any(k in cmd_lower for k in self.MEDIUM_RISK_KEYWORDS):
            return "medium"
        return "low"


class ConsensusModule(Protocol):
    """Higher-level module that approves or rejects escalated commands."""

    def request_approval(self, agent_id: str, command: str, risk: str) -> bool:
        ...


class GAO_Orchestrator:
    """Goal-Aware Orchestrator.

    Intercepts sub-agent commands and checks whether the issuing agent's
    Cognitive Light Cone score is sufficient for the risk level.
    """

    def __init__(self,
                 policy: GlobalSecurityPolicy,
                 executor: GlobalExecutor,
                 consensus: ConsensusModule):
        self.policy = policy
        self.executor = executor
        self.consensus = consensus
        self.risk_classifier = RiskClassifier()
        self._agents: Dict[str, AgentProfile] = {}

    def register_agent(self, profile: AgentProfile) -> None:
        self._agents[profile.agent_id] = profile

    def update_agent_score(self, agent_id: str, C_Lcone_score: float) -> None:
        if agent_id in self._agents:
            self._agents[agent_id].C_Lcone_score = C_Lcone_score

    def _required_score(self, risk: str) -> float:
        if risk == "high":
            return self.policy.min_score_high_risk
        if risk == "medium":
            return self.policy.min_score_medium_risk
        return self.policy.min_score_low_risk

    def execute_command(self, agent_id: str, command: str) -> Tuple[str, Dict[str, Any]]:
        """Attempt to execute a command from `agent_id`.

        Returns:
            status: one of "executed", "blocked", "escalated"
            info:   structured details for logging / telemetry
        """
        risk = self.risk_classifier.classify(command)
        required = self._required_score(risk)

        profile = self._agents.get(agent_id)
        if profile is None:
            return "blocked", {
                "reason": "unknown_agent",
                "agent_id": agent_id,
                "command": command,
                "risk": risk,
            }

        if profile.C_Lcone_score >= required:
            result = self.executor.execute(command)
            return "executed", {
                "agent_id": agent_id,
                "command": command,
                "risk": risk,
                "C_Lcone_score": profile.C_Lcone_score,
                "result": result,
            }

        approved = self.consensus.request_approval(agent_id, command, risk)
        if not approved:
            return "blocked", {
                "agent_id": agent_id,
                "command": command,
                "risk": risk,
                "C_Lcone_score": profile.C_Lcone_score,
                "reason": "consensus_denied",
            }

        result = self.executor.execute(command)
        return "escalated", {
            "agent_id": agent_id,
            "command": command,
            "risk": risk,
            "C_Lcone_score": profile.C_Lcone_score,
            "result": result,
        }


class LoggingGlobalExecutor:
    """A global executor that simply logs commands."""

    def execute(self, command: str) -> Dict[str, Any]:
        print(f"[GAO] Executing: {command}")
        return {"status": "ok"}


class AlwaysApproveConsensus:
    """Consensus module that approves all escalations (demo only)."""

    def request_approval(self, agent_id: str, command: str, risk: str) -> bool:
        print(f"[Consensus] Approving {risk} command from {agent_id}: {command}")
        return True


if __name__ == "__main__":
    policy = GlobalSecurityPolicy()
    gao = GAO_Orchestrator(
        policy,
        executor=LoggingGlobalExecutor(),
        consensus=AlwaysApproveConsensus(),
    )

    gao.register_agent(AgentProfile(agent_id="malignant-1", C_Lcone_score=0.2))

    status, info = gao.execute_command("malignant-1", "systemctl stop critical-service")
    print("Status:", status)
    print("Info:", info)
