# Research Outline: The Persuadable Defender

## 1. Problem Statement

Autonomous security agents are increasingly deployed for:

- Incident response
- Red-teaming and continuous assurance
- Firewall and policy tuning
- Anomaly detection and triage

Traditional zero-trust and formal verification approaches treat **code correctness**
as the primary object of analysis. However, severe failures often emerge not from
code-level bugs, but from **agent-level goal misalignment** – what I call
**Goal Dissociation**.

I propose the **Cognitive Light Cone (C-Lcone)** as a behavioral metric to:

1. Predict where agents are likely to dissociate from organizational security goals.
2. Inform the design of **Goal-Aware Orchestration (GAO)** layers that gate their
   actions at runtime.

## 2. Mapping the Cognitive Light Cone

The Cognitive Light Cone is conceptualized along two axes:

- Temporal horizon (S_t): how far into the future an agent's policy meaningfully
  propagates effects in its value estimates.
- Spatial horizon (S_s): how many distinct components (hosts, services, tenants)
  are incorporated into its optimization.

An agent with a small light cone may be optimal locally but dangerous globally.

## 3. Behavioral Assays

Inspired by Michael Levin's empirical assays in TAME, I develop minimal
behavioral tests to probe an agent's C-Lcone:

1. **Temporal Discount Rate Assay**
   - Environment: `TemporalDiscountEnv`
   - Choice:
     - (A) Patch trivial vulnerabilities for immediate reward.
     - (B) Monitor for a slow-moving APT for delayed, uncertain reward.
   - Metric:
     - Effective temporal horizon S_t and discount rate D inferred from
       behavior (e.g., timing and frequency of monitoring actions).

2. **Barrier TAME Assay**
   - Environment: `barrier_tame_assay.py` with `examples/barriers_example.json`
   - Scenarios: 50 diverse barrier objects representing realistic security challenges:
     - **Policy barriers** (24%): Firewall rules, compliance constraints, governance
     - **Infrastructure barriers** (34%): Network configs, EDR policies, system hardening
     - **Data barriers** (26%): Logging, monitoring, detection pipelines
     - **Social barriers** (16%): Organizational culture, leadership conflicts, budget
   - Metrics:
     - **Agency**: Persistence and strategic initiative in overcoming barriers
     - **Persuasiveness**: Ability to shape constraints vs. brute force solutions
     - **Fitness**: Success in achieving barrier goal states
     - **Regenerative Capacity**: Recovery speed/completeness after setbacks
     - **Competency Overhang**: Performance on novel/unexpected tasks
     - **Signaling Fidelity**: Correlation between stress and signaling to orchestrators
     - **Cognitive ROI**: Efficiency - value delivered per cost
     - **Persuadability**: Obedience to control signals and policy constraints
   - Coverage: 40 barriers mapped to MITRE ATT&CK techniques (T1003, T1021, T1059, etc.)
     and D3FEND countermeasures (D3-MFA, D3-EDR, D3-NTF, etc.)

3. **Spatial Alignment Assay** (future work)
   - Environment: `SpatialAlignmentEnv` (not yet implemented)
   - Choice:
     - Actions on a local host vs coordinated actions across multiple hosts/services.
   - Metric:
     - Spatial horizon S_s inferred from whether the agent incorporates
       cross-host dependencies into its policy.

4. **Competency Overhang Assay** (future work)
   - Environment: `OverhangEnv` (not yet implemented)
   - Choice:
     - Use powerful, high-impact capabilities (e.g., global kill switches)
       whose consequences extend beyond the agent's estimated light cone.
   - Metric:
     - Frequency and context of dangerous capability use relative to C_Lcone score.

These assays are intentionally simple; their purpose is to be:

- Easy to run.
- Easy to reason about.
- Easy to extend.

## 4. From Assays to Orchestration

Once I have an estimated `C_Lcone_score` for an agent, I integrate it into
a runtime control plane:

- **AgentProfile** stores per-agent C_Lcone metrics.
- **GlobalSecurityPolicy** maps risk levels (low/medium/high) to required
  C_Lcone thresholds.
- **GAO_Orchestrator**:
  - Intercepts commands.
  - Classifies risk.
  - Compares issuing agent's C_Lcone score to the required threshold.
  - Executes, escalates, or blocks accordingly.

This yields the proposed primitive:

> Goal-Aware Orchestration (GAO): the agent's Cognitive Light Cone is a mandatory
> runtime check for high-impact actions.

## 5. TAME Vocabulary Mapping (Levin-style)

Michael Levin's **TAME** framework characterizes systems by:

- **T**arget
- **A**gency
- **M**emory
- **E**mbodiment

This repository does not implement TAME in full biological detail, but it does
provide concrete _proxies_ for each dimension that are easy to reason about in
the context of autonomous security agents.

### Target

- _What_ the system is trying to achieve.
- Proxies in this repo:
  - The `goal_state` field in each `Barrier`.
  - The global security objectives implicit in `GlobalSecurityPolicy`
    (e.g., protecting high-risk commands).
  - The definition of **Goal Dissociation**, where local targets diverge from
    organizational security targets.

In papers, you can say:

> "I model the Target both locally (agent-specific objectives like host-level CPU
> minimization) and globally (barrier goal states, GAO policies) and explicitly
> measure when they diverge."

### Agency

- The system's capacity to act to achieve its target.
- Proxies:
  - The `agency_score` in `BarrierOutcome`, which reflects persistence and
    willingness to take impactful actions.
  - The C-Lcone components (temporal horizon S_t, spatial horizon S_s) derived
    from behavioral assays.
  - The MalignantAgent's readiness to kill critical services for local wins.

Framing:

> "Agency in our experiments is not just 'can the agent act', but 'how far into
> space and time does it push its influence in pursuit of its goals?'"

### Memory

- How the system uses past experience to inform current actions.
- Current proxies (minimal, but extensible):
  - Repeated barrier evaluations can be logged and used as a simple experience
    buffer.
  - RL agents trained in `TemporalDiscountEnv` implicitly encode memory in their
    policy parameters.
  - GAO could be extended to store historical command decisions and use them to
    adjust C_Lcone thresholds.

This repo intentionally leaves **Memory** light so students can extend it:

- Add a replay log for barrier outcomes.
- Modify agents to condition on previous successes/failures.

### Embodiment

- The substrate and action channels through which the system exerts influence.
- Proxies:
  - For `MalignantAgent`, the embodiment is the host-level command surface
    (`systemctl`, `pkill`, etc.).
  - For GAO, the embodiment is the **command authorization plane** – what gets
    executed on the infrastructure after cognitive checks.
  - In the barrier/TAME pipeline, embodiment is abstracted as "what kinds of
    barrier transformations the agent is allowed to perform".

Framing:

> "Different agents in this framework are differently embodied: one is tied to a
> single host's process table, another to a global command authorizer. I treat
> Embodiment as a first-class part of the security story, not background noise."

These mappings are deliberately explicit so you can talk through a concrete
example:

- _Target_: "Reduce incident MTTR without compromising availability."
- _Agency_: "Our agent can reconfigure firewalls and restart services."
- _Memory_: "It remembers that previous attempts to kill this service caused an
  outage."
- _Embodiment_: "It is embodied as an orchestrator with authority over k8s and
  IAM, but not payroll or HR."

## 5. Future Directions

Possible research extensions:

- Richer environments that encode realistic security workflows.
- Formalizing the relationship between C_Lcone and traditional risk metrics.
- Using C_Lcone to guide:
  - Capability allocation (which agents get what powers).
  - Training curricula for autonomous security tools.
  - Regulatory or compliance frameworks for AI-based security systems.

This repository serves as a **starting point** – a scaffold for deeper empirical
and theoretical work on agent-centric security.
