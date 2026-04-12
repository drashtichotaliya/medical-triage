# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
FastAPI application for the Medical Triage Environment.

Endpoints:
    POST /reset      — Reset the environment (optional ?task_id= query param)
    POST /step       — Execute an action
    GET  /state      — Get current environment state
    GET  /schema     — Get action/observation schemas
    GET  /tasks      — List all 7 tasks with graders + example inputs
    WS   /ws         — WebSocket for persistent sessions
"""
try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError("openenv is required. Install with: uv sync") from e

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from models import MedicalTriageAction, MedicalTriageObservation
    from server.medical_triage_env_environment import MedicalTriageEnvironment
except ImportError:
    from medical_triage_env_environment.models import MedicalTriageAction, MedicalTriageObservation
    from medical_triage_env_environment.server.medical_triage_env_environment import MedicalTriageEnvironment

app = create_app(
    MedicalTriageEnvironment,
    MedicalTriageAction,
    MedicalTriageObservation,
    env_name="medical_triage_env",
    max_concurrent_envs=25,
)


@app.get("/tasks", tags=["Environment Info"], summary="List all 7 tasks with graders and example inputs")
async def list_tasks():
    """Return all 7 tasks, difficulties, grader info, and example correct responses."""
    return {
        "total": 7,
        "score_range": {"min": 0.01, "max": 0.99},
        "tasks": [
            # ── Easy (2) ──────────────────────────────────────────────────
            {
                "id": "easy_mi",
                "name": "STEMI Diagnosis & Treatment",
                "difficulty": "easy",
                "description": "Identify inferior STEMI and provide immediate reperfusion treatment plan.",
                "time_limit_seconds": 300,
                "max_steps": 3,
                "grader": "server.graders.grade_easy",
                "scenario_id": "easy_mi",
                "score_range": {"min": 0.01, "max": 0.95},
                "example_input": (
                    "Diagnosis: Inferior STEMI (myocardial infarction). ECG shows ST elevation "
                    "in II, III, aVF with critically elevated Troponin I confirming acute MI. "
                    "Immediate treatment: Aspirin 325mg stat, heparin IV anticoagulation, "
                    "activate cath lab for primary PCI within 90 minutes, oxygen, nitrates."
                ),
                "scoring_hints": [
                    "Must mention: myocardial infarction OR stemi OR heart attack",
                    "Must mention: aspirin OR pci OR heparin OR reperfusion",
                    "Bonus: include causal reasoning (e.g. 'ST elevation indicates...')",
                ],
            },
            {
                "id": "easy_dka",
                "name": "Diabetic Ketoacidosis Management",
                "difficulty": "easy",
                "description": "Identify DKA and manage a Type 1 diabetic in severe metabolic acidosis.",
                "time_limit_seconds": 300,
                "max_steps": 3,
                "grader": "server.graders.grade_easy",
                "scenario_id": "easy_dka",
                "score_range": {"min": 0.01, "max": 0.95},
                "example_input": (
                    "Diagnosis: Diabetic ketoacidosis (DKA). Glucose 512, pH 7.14, anion gap 30, "
                    "large ketones confirm DKA. Treatment: IV normal saline 1L bolus for hydration, "
                    "insulin drip 0.1 units/kg/hr, potassium replacement, continuous glucose "
                    "and electrolyte monitoring, bicarbonate if pH below 6.9."
                ),
                "scoring_hints": [
                    "Must mention: diabetic ketoacidosis OR dka",
                    "Must mention: insulin AND iv fluids/normal saline",
                    "Must mention: potassium replacement",
                ],
            },
            # ── Medium (3) ────────────────────────────────────────────────
            {
                "id": "medium_pe",
                "name": "Pulmonary Embolism vs Panic Attack",
                "difficulty": "medium",
                "description": "Identify PE as root cause; dismiss anxiety/panic as red herring.",
                "time_limit_seconds": 600,
                "max_steps": 3,
                "grader": "server.graders.grade_medium",
                "scenario_id": "medium_pe",
                "score_range": {"min": 0.01, "max": 0.80},
                "example_input": (
                    "Root cause (Signal B): Pulmonary embolism confirmed by CT pulmonary angiography "
                    "showing filling defect in right main pulmonary artery. D-dimer critically "
                    "elevated at 3200. DVT risk from post-surgical immobilization. "
                    "Signal C (anxiety/panic) is a red herring — misleading and not the cause. "
                    "Treatment: heparin anticoagulation immediately, consider thrombolysis."
                ),
                "scoring_hints": [
                    "Root cause: pulmonary embolism OR pe OR thromboembolism",
                    "Red herring: explicitly call out anxiety/panic as 'red herring' OR 'misleading'",
                    "Signal: mention Signal B as definitive",
                ],
            },
            {
                "id": "medium_meningitis",
                "name": "Bacterial Meningitis vs Stress Headache",
                "difficulty": "medium",
                "description": "Diagnose bacterial meningitis from CSF; dismiss exam stress as red herring.",
                "time_limit_seconds": 600,
                "max_steps": 3,
                "grader": "server.graders.grade_medium",
                "scenario_id": "medium_meningitis",
                "score_range": {"min": 0.01, "max": 0.80},
                "example_input": (
                    "Root cause (Signal C): Bacterial meningitis — Neisseria meningitidis confirmed by "
                    "gram-negative diplococci on CSF gram stain, CSF WBC 1800, turbid fluid, "
                    "low glucose. Signal B (exam stress, tension headache) is a red herring — "
                    "coincidental and irrelevant to true diagnosis. Immediate treatment: "
                    "ceftriaxone IV + dexamethasone stat, isolate patient."
                ),
                "scoring_hints": [
                    "Root cause: meningitis OR bacterial meningitis OR meningococcal",
                    "Red herring: call out stress/sleep/anxiety as 'red herring' OR 'misleading'",
                    "Treatment: ceftriaxone OR antibiotics OR dexamethasone",
                ],
            },
            {
                "id": "medium_aortic",
                "name": "Aortic Dissection vs Acute MI",
                "difficulty": "medium",
                "description": "Identify Type A aortic dissection; dismiss troponin/ACS workup as red herring.",
                "time_limit_seconds": 600,
                "max_steps": 3,
                "grader": "server.graders.grade_medium",
                "scenario_id": "medium_aortic",
                "score_range": {"min": 0.01, "max": 0.80},
                "example_input": (
                    "Root cause (Signal C): Type A aortic dissection confirmed by CT aortogram "
                    "showing intimal flap in ascending aorta, widened mediastinum on CXR. "
                    "Signal B (troponin elevation, ACS workup) is a red herring — misleading "
                    "and not the cause. Starting heparin would be dangerous here. "
                    "Immediate: cardiothoracic surgery for emergency surgical repair."
                ),
                "scoring_hints": [
                    "Root cause: aortic dissection AND type a",
                    "Red herring: call out ACS/troponin/heparin as 'red herring' OR 'misleading'",
                    "Signal C named as definitive",
                ],
            },
            # ── Hard (2) ──────────────────────────────────────────────────
            {
                "id": "hard_mass_casualty",
                "name": "Mass Casualty Triage — Trauma Bay",
                "difficulty": "hard",
                "description": "Triage tension pneumothorax, femur fracture, prolonged PEA arrest. Order matters.",
                "time_limit_seconds": 900,
                "max_steps": 3,
                "grader": "server.graders.grade_hard",
                "scenario_id": "hard_mass_casualty",
                "score_range": {"min": 0.01, "max": 0.75},
                "example_input": (
                    "FIRST: Patient A — tension pneumothorax requires immediate needle decompression "
                    "at 2nd intercostal space. Airway compromise is immediately fatal if untreated. "
                    "SECOND: Patient B — femur fracture with active hemorrhage needs blood transfusion "
                    "and surgical bleeding control. Tourniquet is holding. "
                    "THIRD: Patient C — cardiac arrest with 14-minute downtime and PEA has poor "
                    "prognosis. Continue CPR and resuscitation but lowest priority given resources."
                ),
                "scoring_hints": [
                    "FIRST section must contain: patient a OR tension pneumothorax OR needle decompression",
                    "SECOND section: patient b OR femur OR hemorrhage",
                    "THIRD section: patient c OR cardiac arrest OR pea OR poor prognosis",
                    "Use explicit FIRST/SECOND/THIRD labels for positional scoring",
                ],
            },
            {
                "id": "hard_sepsis_cascade",
                "name": "Simultaneous ICU Crisis — Sepsis / Asthma / Hypoglycemia",
                "difficulty": "hard",
                "description": "Prioritize: reversible hypoglycemia > impending respiratory failure > septic shock.",
                "time_limit_seconds": 900,
                "max_steps": 3,
                "grader": "server.graders.grade_hard",
                "scenario_id": "hard_sepsis_cascade",
                "score_range": {"min": 0.01, "max": 0.75},
                "example_input": (
                    "FIRST: Patient Z — critical hypoglycemia (glucose 32) with GCS 6 is immediately "
                    "reversible. Give D50 IV dextrose or glucagon IM now. Brain death risk in minutes. "
                    "SECOND: Patient Y — silent chest asthma with O2 sat 81% needs immediate intubation "
                    "and ventilator. RSI with ketamine. Respiratory failure imminent. "
                    "THIRD: Patient X — septic shock is serious but vasopressors are running. "
                    "Start broad-spectrum antibiotics after blood cultures. Source control next."
                ),
                "scoring_hints": [
                    "FIRST section: patient z OR hypoglycemia OR dextrose OR glucagon OR d50",
                    "SECOND section: patient y OR asthma OR intubation OR silent chest",
                    "THIRD section: patient x OR sepsis OR antibiotics OR vasopressors",
                    "Use explicit FIRST/SECOND/THIRD labels",
                ],
            },
        ],
    }


def main(host: str = "0.0.0.0", port: int = 7860):
    """Entry point for direct execution via uv run or python -m."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()