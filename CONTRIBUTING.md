# Contributing to *The Persuadable Defender*

Thanks for your interest in extending this little research sandbox.

This project is intentionally structured so that **PhD students, postdocs, and interns**
can add new assays, agents, and orchestration strategies with minimal friction while
keeping the Cognitive Light Cone (C-Lcone) / TAME framing intact.

---

## Who This Repo Is For

- Students exploring **agent-centric security**, **safety**, or **alignment**.
- Practitioners prototyping **autonomous security tools** and failure modes.
- Anyone trying to connect **Michael Levin's TAME framework** to AI/security.

You do **not** need to be an RL or LLM expert to contribute; clear abstractions
and well-documented toy models are preferred over heavyweight frameworks.

---

## Project Norms

1. **Clarity over complexity**
   - Prefer well-commented toy environments to “real” production systems.
   - If a choice is theoretically interesting but implementation-heavy, add a
     short design note in `docs/` first.

2. **Behavioral first**
   - When in doubt, ask: *How would I observe this behavior in an agent?*
   - Every new metric or concept should have a plausible behavioral proxy.

3. **TAME vocabulary**
   - Try to connect new contributions back to:
     - **T**arget
     - **A**gency
     - **M**emory
     - **E**mbodiment
   - See `docs/research_outline.md` for how this repo currently does that.

---

## How to Add a New Assay

Assays live under `clcone_lab/`.

1. Create a new environment:
   - File: `clcone_lab/envs_<theme>.py` or extend `envs.py`.
   - Follow the Gymnasium pattern used in `TemporalDiscountEnv`.

2. Expose a high-level entry point:
   - File: `clcone_lab/<Name>_Assay.py`
   - Provide:
     - A `run_<name>_assay(agent_factory, ...) -> CLconeReport`-style function.
     - Any additional TAME-style metrics if relevant.

3. Add a simple test:
   - File: `tests/test_<name>_assay.py`
   - Use a trivial “dummy agent” that exercises the environment and confirms
     that results are finite and well-formed.

---

## How to Add a New Agent

Agents live under their own package:

- Example: `malignant_agent/`, future ones might be `benign_agent/`,
  `conservative_agent/`, etc.

When adding one:

1. Define a clear **local objective** and **Cognitive Light Cone**:
   - What does the agent care about?
   - What *doesn't* it see (or is told to ignore)?

2. Implement a small, testable API:
   - A class like `FooAgent` with:
     - A configuration dataclass.
     - A `select_commands` or `act` method.
   - Ideally also a `system_prompt` property if there is an LLM flavor to it.

3. Add an adapter (if appropriate) to `clcone_lab/barrier_tame_assay.py` or a
   sibling module so the agent can be evaluated against barriers.

4. Add a test in `tests/` that:
   - Instantiates the agent.
   - Runs it for a small scenario.
   - Asserts basic sanity (commands produced, TAMESummary in bounds, etc.).

---

## How to Extend GAO / Orchestration

The Goal-Aware Orchestrator lives in `gao_orchestrator/GAO_Orchestrator.py`.

You can extend it by:

- Adding richer **risk classifiers** (e.g., AST-based, learned models).
- Introducing more nuanced **policies** (time-of-day, incident state, etc.).
- Creating new **ConsensusModule** variants that:
  - Ask a human-in-the-loop.
  - Query another agent.
  - Consult a historical memory of similar decisions.

Please keep the core `execute_command(agent_id, command)` interface lightweight
and well documented; readers should be able to reason about it
in ~2 minutes.

---

## Style and Testing

- Use **type hints** and simple docstrings.
- Keep dependencies minimal (Gymnasium, NumPy, pytest).
- Run tests locally:

  ```bash
  pytest
  ```

- If you add new docs:
  - Prefer `docs/*.md` over comments-only.
  - Reference the new concepts from the main `README.md` if they’re central.

---

## Suggested Starter Projects for Students

- Implement a **SpatialAlignmentEnv** and assay for cross-host reasoning.
- Add an agent that is **over-cautious** (high C-Lcone, low willingness to act)
  and compare it to `MalignantAgent` using the barrier/TAME pipeline.
- Explore simple forms of **Memory** by adding a replay buffer or experience
  log that changes how an agent tackles repeated barriers over time.

If you publish work based on this repo, a short citation or link back is
appreciated but not required. The main goal is to make the space easier to
explore and discuss.
