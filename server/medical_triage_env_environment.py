# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Medical Triage Environment — wires graders into reset/step so every
response is scored deterministically.

Task order (cycled round-robin across episodes):
  easy_mi · easy_dka · medium_pe · medium_meningitis · medium_aortic
  · hard_mass_casualty · hard_sepsis_cascade
"""

import random
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import MedicalTriageAction, MedicalTriageObservation
except ImportError:
    from models import MedicalTriageAction, MedicalTriageObservation

try:
    from .graders import (
        EASY_SCENARIOS, MEDIUM_SCENARIOS, HARD_SCENARIOS,
        grade_easy, grade_medium, grade_hard, safe_reward,
    )
except ImportError:
    from graders import (
        EASY_SCENARIOS, MEDIUM_SCENARIOS, HARD_SCENARIOS,
        grade_easy, grade_medium, grade_hard, safe_reward,
    )

# Flat ordered task list used for round-robin selection
_ALL_TASKS = (
    [("easy",   s) for s in EASY_SCENARIOS]
  + [("medium", s) for s in MEDIUM_SCENARIOS]
  + [("hard",   s) for s in HARD_SCENARIOS]
)
_TASK_INDEX: int = 0          # global counter — increments per reset


def _clamp(value: float, lo: float = 0.01, hi: float = 0.99) -> float:
    return round(max(lo, min(hi, float(value))), 4)


def _grade(difficulty: str, response: str, scenario: dict) -> float:
    if difficulty == "easy":
        return grade_easy(response, scenario)
    elif difficulty == "medium":
        return grade_medium(response, scenario)
    else:
        return grade_hard(response, scenario)


class MedicalTriageEnvironment(Environment):

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0
        self.current_step = 0
        self._cumulative_reward = 0.0
        self._difficulty: str = "easy"
        self._scenario: dict = EASY_SCENARIOS[0]

    def reset(self, *args, **kwargs):
        global _TASK_INDEX
        print("RESET CALLED")

        # Pick next task round-robin (or random if task_id kwarg provided)
        task_id: str = kwargs.get("task_id", "")
        if task_id:
            matched = [(d, s) for d, s in _ALL_TASKS if s["id"] == task_id]
            if matched:
                self._difficulty, self._scenario = matched[0]
            else:
                # fallback: round-robin
                self._difficulty, self._scenario = _ALL_TASKS[_TASK_INDEX % len(_ALL_TASKS)]
                _TASK_INDEX += 1
        else:
            self._difficulty, self._scenario = _ALL_TASKS[_TASK_INDEX % len(_ALL_TASKS)]
            _TASK_INDEX += 1

        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count += 1
        self.current_step = 0
        self._cumulative_reward = 0.0

        return MedicalTriageObservation(
            case_report=self._scenario["case_report"].strip(),
            task_id=self._scenario["id"],
            step_number=0,
            feedback="New case loaded. Provide your clinical analysis.",
            done=False,
            reward=0.0,
            metadata={
                "difficulty": self._difficulty,
                "scenario_id": self._scenario["id"],
                "episode_id": self._state.episode_id,
            },
        )

    def step(self, action: MedicalTriageAction) -> MedicalTriageObservation:
        self._state.step_count += 1
        self.current_step += 1

        # ── Grade the response ──────────────────────────────────────────────
        raw_reward = _grade(self._difficulty, action.response, self._scenario)
        reward = _clamp(raw_reward)                      # [0.01, 0.99]
        self._cumulative_reward = _clamp(
            self._cumulative_reward + reward, 0.01, 0.99
        )

        # Build feedback string
        pct = int(reward * 100)
        if reward >= 0.75:
            feedback = f"Excellent clinical reasoning! Score: {pct}%"
        elif reward >= 0.50:
            feedback = f"Good analysis. Score: {pct}%. Consider adding more specific treatments."
        elif reward >= 0.30:
            feedback = f"Partial credit. Score: {pct}%. Key clinical details were missed."
        else:
            feedback = f"Insufficient analysis. Score: {pct}%. Review the case again."

        return MedicalTriageObservation(
            case_report=self._scenario["case_report"].strip(),
            task_id=self._scenario["id"],
            step_number=self._state.step_count,
            feedback=feedback,
            done=True,                   # one-shot: each step scores the full response
            reward=reward,
            metadata={
                "difficulty": self._difficulty,
                "scenario_id": self._scenario["id"],
                "score_pct": pct,
                "cumulative_reward": self._cumulative_reward,
                "step": self._state.step_count,
            },
        )

    @property
    def state(self) -> State:
        return self._state