# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Medical Triage Environment Client."""
from typing import Dict
from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

try:
    from .models import MedicalTriageAction, MedicalTriageObservation
except ImportError:
    from models import MedicalTriageAction, MedicalTriageObservation


class MedicalTriageEnv(
    EnvClient[MedicalTriageAction, MedicalTriageObservation, State]
):
    """
    Client for the Medical Triage Environment.
    Connects via WebSocket to the environment server.

    The agent receives patient case reports and must provide clinical
    analysis, diagnoses, and prioritized treatment plans.

    Example:
        >>> with MedicalTriageEnv(base_url="http://localhost:8000") as client:
        ...     result = client.reset(task_id="medium")
        ...     print(result.observation.case_report)
        ...     result = client.step(MedicalTriageAction(response="Pulmonary embolism confirmed by CT-PA."))
        ...     print(result.reward)
    """

    def _step_payload(self, action: MedicalTriageAction) -> Dict:
        return {"response": action.response}

    def _parse_result(self, payload: Dict) -> StepResult[MedicalTriageObservation]:
        obs_data = payload.get("observation", {})
        observation = MedicalTriageObservation(
            case_report=obs_data.get("case_report", ""),
            task_id=obs_data.get("task_id", ""),
            step_number=obs_data.get("step_number", 0),
            feedback=obs_data.get("feedback", ""),
            done=payload.get("done", False),
            reward=payload.get("reward", 0.0),
            metadata=obs_data.get("metadata", {}),
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )