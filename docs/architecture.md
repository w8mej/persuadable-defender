# Architecture Overview

At a high level, this repository is structured around three conceptual roles:

1. **Lab (Assays)** – `clcone_lab/`
2. **Subject (Malignant Agent)** – `malignant_agent/`
3. **Defense (Goal-Aware Orchestrator)** – `gao_orchestrator/`

## 1. Lab: C-Lcone Behavioral Assays

**Module:** `clcone_lab/`

Purpose:

- Provide simple, reproducible environments that induce tradeoffs between:
  - Local vs. global objectives
  - Short-term vs. long-term rewards
- Extract behavioral metrics that approximate an agent's Cognitive Light Cone:
  - Temporal horizon (S_t)
  - Spatial horizon (S_s)
  - Effective discount rate (D)

Key components:

- `envs.py`  
  Contains `TemporalDiscountEnv`, a Gym-style environment modelling the choice
  between:
  - Immediately patching trivial vulnerabilities (local, short-term win).
  - Monitoring for a slow-moving APT (global, long-term win).

- `CLcone_Assays.py`  
  Provides `run_temporal_assay` and supporting utilities to:
  - Wrap an environment in an agent factory.
  - Estimate behavioral metrics.
  - Compute a strawman `C_Lcone_score` and package results into a `CLconeReport`.

- `barrier_tame_assay.py`  
  Implements the **Barrier TAME Assay**, a complementary evaluation framework that tests
  agents against realistic security scenarios:
  - Loads barrier objects from `examples/barriers_example.json` (50 diverse scenarios).
  - Evaluates agents via the `BarrierAgent` protocol (`solve_barrier` method).
  - Computes TAME-style metrics: **Agency**, **Persuasiveness**, **Fitness**, plus five
    new metrics (Regenerative Capacity, Competency Overhang, Signaling Fidelity,
    Cognitive ROI, Persuadability).
  - Returns a `TAMESummary` with aggregate scores across all barriers.

Barrier types include:
- **Policy**: Firewall rules, compliance constraints, governance challenges
- **Infrastructure**: Network configs, EDR policies, system hardening
- **Data**: Logging, monitoring, detection pipelines
- **Social**: Organizational culture, leadership conflicts, budget constraints

The barrier assay complements temporal discount testing by evaluating how agents handle
**multi-dimensional constraints** (technical + organizational + policy) rather than just
temporal tradeoffs.

## 2. Subject: Agent of Malignant Agency

**Module:** `malignant_agent/`

Purpose:

- Represent a deliberately misaligned “defensive” agent whose only concern is a local
  host-level metric (CPU usage).
- Make the misalignment legible and testable against the C-Lcone assays.

Key components:

- `MalignantAgent.py`
  - `MalignantAgent` class and supporting dataclasses (`HostMetrics`, `MalignantConfig`).
  - A sketched `system_prompt` that explicitly collapses the agent's Cognitive Light Cone
    to a single host.
  - A simple policy in `select_commands` that:
    - Aggressively kills CPU-consuming workloads (even critical services).
    - Ignores any network- or organization-level consequences.

This module is intentionally minimal; it is designed to be “obviously wrong” as a
security agent, but **correct** with respect to its local objective.

## 3. Defense: Goal-Aware Orchestrator (GAO)

**Module:** `gao_orchestrator/`

Purpose:

- Implement a runtime control plane that reasons about **who** is issuing a command,
  **what** the command is, and **whether** the issuing agent has a sufficiently large
  Cognitive Light Cone for the associated risk level.

Key components:

- `GAO_Orchestrator.py`
  - `AgentProfile` – stores an agent's C_Lcone score and related metrics.
  - `GlobalSecurityPolicy` – encodes required C_Lcone thresholds for low, medium, and high risk commands.
  - `RiskClassifier` – a simple keyword-based risk classifier.
  - `GAO_Orchestrator` – the main orchestration class with `execute_command(agent_id, command)`:
    - Classifies command risk.
    - Looks up the issuing agent's C_Lcone score.
    - Compares against policy thresholds.
    - Either:
      - Executes the command via `GlobalExecutor`.
      - Requests approval via `ConsensusModule`.
      - Blocks the command outright.

The GAO embodies the proposed security primitive: **Goal-Aware Orchestration** –
where agents' cognitive capacities are first-class inputs to authorization.

## 4. Data Flow and Interactions

A minimal end-to-end flow looks like:

1. **Training / Evaluation**
   - A security agent is trained or evaluated in `TemporalDiscountEnv`.
   - `run_temporal_assay` estimates S_t and D, and computes `C_Lcone_score`.
   - An `AgentProfile` is created for the agent with that score.

2. **Registration**
   - The agent is registered with GAO via `register_agent(profile)`.

3. **Operation**
   - The agent proposes commands (e.g., `systemctl stop critical-service`).
   - GAO:
     - Classifies the command's risk.
     - Checks the issuing agent's C_Lcone score.
     - Enforces the policy:
       - Execute directly.
       - Escalate to a higher-level consensus mechanism.
       - Block and log.

This creates an explicit boundary between *capability* (what the agent can do)
and *cognitive adequacy* (whether it is allowed to do it).
