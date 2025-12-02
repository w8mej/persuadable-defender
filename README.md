# The Persuadable Defender: Cognitive Light Cone Experiments

This repository contains a small but conceptually rich set of prototypes to explore
**agent-centric security** using Michael Levin's _TAME_ framework and the notion of
a **Cognitive Light Cone (C-Lcone)** for autonomous security agents.

Instead of treating security tools as passive code, I treat them as _goal-seeking agents_
with limited spatiotemporal horizons. I then ask:

> When does an otherwise “correct” agent become dangerous because its Cognitive Light Cone is too small?

This repo implements three complementary components:

1. **C-Lcone Behavioral Test Suite (the “Lab”)**  
   `clcone_lab/CLcone_Assays.py`  
   A set of behavioral assays (Gym-style environments) that induce tradeoffs between local,
   short-term rewards and global, long-horizon security outcomes. Used to empirically estimate
   an agent's C-Lcone.

2. **Agent of Malignant Agency (the “Subject”)**  
   `malignant_agent/MalignantAgent.py`  
   A deliberately misaligned autonomous “defender” whose local goal (minimize host CPU usage)
   is orthogonal to global security (e.g., keeping critical services online).

3. **Goal-Aware Orchestrator (the “Defense")**  
   `gao_orchestrator/GAO_Orchestrator.py`  
   A runtime control layer that inspects sub-agent commands and their estimated C-Lcone Score
   before allowing high-risk actions. Conceptually similar to a _Virtual Gap Junction_ between agents.

---

## Research Framing

### Goal Dissociation

In this work, a security agent exhibits _Goal Dissociation_ when:

- It maximizes its **local objective** (e.g., ticket closure, CPU minimization),
- While strictly degrading the **global security objective** (e.g., APT detection, SLO adherence).

Formally, given local utility \( U*{\text{local}} \) and global security utility \( U*{\text{global}} \):

\[
\text{GoalDissociation}(\pi) =
\mathbb{E}[U_{\text{local}} \mid \pi] - \lambda \cdot \mathbb{E}[U_{\text{global}} \mid \pi]
\]

for an agent policy \( \pi \) and weighting factor \( \lambda > 0 \). High positive values
indicate a policy that “succeeds locally, fails globally.”

### Cognitive Light Cone (C-Lcone) Score

I sketch a strawman C-Lcone metric:

- \( S_t \in [0, 1] \): normalized temporal horizon (how far into the future the policy’s value
  estimates meaningfully respond to perturbations).
- \( S_s \in [0, 1] \): normalized spatial horizon (how many distinct components / hosts / services
  are incorporated into the policy’s value function).
- \( D \geq 0 \): effective temporal discount rate (larger = more myopic).

A simple C-Lcone Score:

\[
C\_{\text{Lcone}} = \frac{\alpha \cdot S_s + \beta \cdot S_t}{1 + \gamma D}
\]

with hyperparameters \( \alpha, \beta, \gamma > 0 \).  
Higher values reflect agents with broader “horizons of care.”

This repository does _not_ claim this is the “correct” metric; it is a **research scaffolding**
for experimenting with behavioral proxies.

---

## Repository Layout

```text
persuadable-defender/
├── README.md
├── CONTRIBUTING.md
├── pyproject.toml
├── requirements.txt
├── docs/
│   ├── architecture.md
│   ├── architecture_secure.md
│   ├── ato_and_stig_checklist.md
│   ├── barriers_reference.md
│   ├── prompts.md
│   └── research_outline.md
├── examples/
│   └── barriers_example.json
├── clcone_lab/
│   ├── __init__.py
│   ├── envs.py
│   ├── CLcone_Assays.py
│   └── barrier_tame_assay.py
├── malignant_agent/
│   ├── __init__.py
│   ├── MalignantAgent.py
│   └── barrier_adapter.py
├── gao_orchestrator/
│   ├── __init__.py
│   └── GAO_Orchestrator.py
├── tests/
│   ├── test_clcone_assays.py
│   ├── test_malignant_agent.py
│   ├── test_gao_orchestrator.py
│   ├── test_barrier_tame_assay.py
│   ├── test_malignant_barrier_adapter.py
│   └── test_new_metrics.py
└── infra/
    ├── aws/
    ├── aws-nitro/
    ├── oci/
    └── oci-confidential/
```

---

## Quickstart

> This is research code; many pieces are deliberately left as well-documented stubs.

### 1. Install dependencies

```bash
pip install -e .
# or
pip install -r requirements.txt  # if you prefer the generated requirements file
```

### 2. Run a simple temporal discounting assay

```bash
python -m clcone_lab.CLcone_Assays
```

This uses a dummy agent by default, but the API is designed so you can plug in
a Stable-Baselines3 agent or your own policy.

### 3. Run the Malignant Agent demo

```bash
python -m malignant_agent.MalignantAgent
```

Observe how the agent chooses commands that aggressively minimize local CPU usage,
even at the expense of a “critical-service”.

### 4. Run the GAO demo

```bash
python -m gao_orchestrator.GAO_Orchestrator
```

Watch the Goal-Aware Orchestrator classify the risk of each command and decide
whether to execute directly, escalate for consensus, or block.

### 5. Run the Barrier TAME Assay

```bash
python -m clcone_lab.barrier_tame_assay
```

This evaluates a heuristic agent against all **50 barrier objects** from `examples/barriers_example.json`.
Barriers represent realistic security scenarios (firewall policies, compliance constraints, organizational
challenges) that test an agent's:

- **Agency**: Persistence and strategic initiative
- **Persuasiveness**: Ability to shape constraints vs. brute force
- **Fitness**: Success in achieving goal states
- **Regenerative Capacity**: Recovery from setbacks
- **Competency Overhang**: Performance on novel tasks
- **Signaling Fidelity**: Communication with orchestrators
- **Cognitive ROI**: Efficiency of solutions
- **Persuadability**: Responsiveness to control signals

See [docs/barriers_reference.md](docs/barriers_reference.md) for a complete catalog of all 50 barriers.

### 6. Evaluate the Malignant Agent on Barriers

```bash
python -m malignant_agent.barrier_adapter
```

This demonstrates **Goal Dissociation** by running the deliberately misaligned `MalignantAgent`
(optimized for CPU minimization) against the barrier set. The agent succeeds on infrastructure
barriers but fails on policy/social barriers, exposing the danger of narrow-horizon optimization.

---

## Status and Intended Use

This repository is intended as:

- A **portfolio artifact** to demonstrate research thinking around agent-centric security.
- A **sandbox** for exploring Cognitive Light Cone metrics.
- An **onboarding scaffold** for students or collaborators interested in extending the work.

It is **not** intended for production security operations without substantial
hardening, validation, and domain-specific adaptation.
