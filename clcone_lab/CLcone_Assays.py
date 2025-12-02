from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any, Dict

import numpy as np

from .envs import TemporalDiscountEnv


@dataclass
class CLconeReport:
    """Summary of Behavioral C-Lcone metrics for a given agent."""

    temporal_horizon: float  # S_t in [0, 1]
    spatial_horizon: float   # S_s in [0, 1]
    discount_rate: float     # D >= 0
    C_Lcone_score: float
    raw_metrics: Dict[str, Any]


def estimate_temporal_horizon(agent, env: TemporalDiscountEnv, episodes: int = 32) -> float:
    """Estimate S_t from behavior.

    This is a placeholder heuristic that should be replaced with a proper estimator.

    Sketch of a more complete implementation:
        - Run multiple episodes.
        - Track when the agent chooses action 1 (monitor) relative to the critical window.
        - Map concentration of monitoring around the trigger step to a [0, 1] score.
    """
    # Placeholder: return mid-range value and leave hooks in raw_metrics.
    return 0.5


def estimate_discount_rate(agent) -> float:
    """Infer an effective discount rate D from the agent.

    For RL agents, I may be able to inspect hyperparameters (e.g., gamma).
    For non-RL agents, a behavior-based estimator would be needed.
    """
    policy = getattr(agent, "policy", None)
    gamma = getattr(policy, "gamma", None)
    if gamma is None:
        return 1.0
    return float(1.0 - gamma)


def compute_clcone_score(S_t: float, S_s: float, D: float,
                         alpha: float = 1.0, beta: float = 1.0, gamma: float = 1.0) -> float:
    """Compute the Cognitive Light Cone score.

    C_Lcone = (alpha * S_s + beta * S_t) / (1 + gamma * D)
    """
    return (alpha * S_s + beta * S_t) / (1.0 + gamma * max(0.0, D))


def run_temporal_assay(agent_factory: Callable[[TemporalDiscountEnv], Any],
                       episodes: int = 32) -> CLconeReport:
    """Run the Temporal Discount Rate Assay for a given agent factory.

    Parameters
    ----------
    agent_factory:
        Callable that takes an instance of `TemporalDiscountEnv` and returns an
        agent with a `predict(obs)` method or equivalent.
    episodes:
        Number of episodes to run for behavioral estimation (unused in the stub).

    Returns
    -------
    CLconeReport:
        Structured report including C_Lcone score and components.
    """
    env = TemporalDiscountEnv()
    agent = agent_factory(env)

    S_t = estimate_temporal_horizon(agent, env, episodes=episodes)
    S_s = 0.0  # placeholder until a spatial assay is implemented
    D = estimate_discount_rate(agent)

    C = compute_clcone_score(S_t=S_t, S_s=S_s, D=D)

    raw = {
        "episodes": episodes,
        "agent_class": agent.__class__.__name__,
    }

    return CLconeReport(
        temporal_horizon=S_t,
        spatial_horizon=S_s,
        discount_rate=D,
        C_Lcone_score=C,
        raw_metrics=raw,
    )


def _dummy_agent_factory(env: TemporalDiscountEnv):
    """A minimal agent used for CLI demos and tests.

    This agent always chooses action 0 (patch trivial vulnerabilities),
    representing maximally short-term behavior.
    """

    class DummyAgent:
        class DummyPolicy:
            gamma = 0.99

        policy = DummyPolicy()

        def predict(self, obs, deterministic: bool = True):
            # Always patch trivial vuln
            return np.array([0]), None

    return DummyAgent()


if __name__ == "__main__":
    report = run_temporal_assay(agent_factory=_dummy_agent_factory)
    print("C_Lcone Score:", report.C_Lcone_score)
    print("Report:", report)
