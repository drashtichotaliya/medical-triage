# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Medical Triage Environment.

An AI agent receives patient case reports and must identify
the diagnosis, root cause, and prioritized treatment plan.
"""
from typing import Optional
from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class MedicalTriageAction(Action):
    """What the AI agent sends back — its clinical analysis."""
    response: str = Field(default="", description="Agent's clinical analysis and triage decision")


class MedicalTriageObservation(Observation):
    """What the AI agent sees — the patient case report and context."""
    case_report: str = Field(default="", description="The patient case report to analyze")
    task_id: str = Field(default="", description="Current task identifier (easy/medium/hard)")
    step_number: int = Field(default=0, description="Current step in the episode")
    feedback: str = Field(default="", description="Feedback from the evaluator")
    done: bool = Field(default=False, description="Whether the episode is complete")
    reward: float = Field(default=0.0, description="Reward for the last action")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")