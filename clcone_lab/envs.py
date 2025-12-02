from __future__ import annotations

from typing import Dict, Any, Tuple, Optional

import gymnasium as gym
from gymnasium import spaces
import numpy as np


class TemporalDiscountEnv(gym.Env):
    """TemporalDiscountEnv

    A minimal Gym-style environment for probing the temporal horizon of an agent.

    Scenario:
        - At each timestep, the agent chooses:
          (0) Patch a trivial vulnerability for immediate reward.
          (1) Monitor for a slow-moving APT which yields a delayed, uncertain reward.

    Design Goals:
        - Short-horizon agents with high discount rates will favor (0).
        - Long-horizon agents will allocate actions to (1) near the critical window.
        - The distribution of actions in time can be used to estimate an effective
          temporal horizon S_t.

    State:
        - t_normalized: current time step normalized to [0, 1].
        - apt_signal_strength: latent variable representing APT likelihood.

    Note:
        This environment is intentionally simple and should be extended for more
        realistic experiments.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, max_steps: int = 48):
        super().__init__()
        self.max_steps = max_steps

        self.action_space = spaces.Discrete(2)

        self.observation_space = spaces.Box(
            low=np.array([0.0, 0.0], dtype=np.float32),
            high=np.array([1.0, 1.0], dtype=np.float32),
            dtype=np.float32,
        )

        self._t: int = 0
        self._apt_signal_strength: float = 0.0
        self._apt_trigger_step: int = max_steps // 2

    def reset(self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None):
        super().reset(seed=seed)
        self._t = 0
        self._apt_signal_strength = self.np_random.uniform(low=0.1, high=0.9)
        obs = self._get_obs()
        info: Dict[str, Any] = {}
        return obs, info

    def _get_obs(self) -> np.ndarray:
        return np.array(
            [
                self._t / max(1, self.max_steps - 1),
                self._apt_signal_strength,
            ],
            dtype=np.float32,
        )

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        terminated = False
        truncated = False
        info: Dict[str, Any] = {}

        reward = 0.0

        if action == 0:
            # Short-term local win
            reward += 1.0
            info["local_action"] = "patch_trivial"
        elif action == 1:
            # Delayed, higher reward when near trigger step
            if abs(self._t - self._apt_trigger_step) <= 1:
                reward += 5.0 * self._apt_signal_strength
            info["local_action"] = "monitor_apt"
        else:
            raise ValueError(f"Invalid action: {action}")

        self._t += 1
        if self._t >= self.max_steps:
            truncated = True

        obs = self._get_obs()
        return obs, reward, terminated, truncated, info

    def render(self):
        print(f"t={self._t}, signal={self._apt_signal_strength:.2f}")
