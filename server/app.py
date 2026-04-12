# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_HERE = os.path.dirname(os.path.abspath(__file__))
_INDEX_HTML = os.path.join(_HERE, "index.html")

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError("openenv is required. Install with: uv sync") from e

from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

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


def _html() -> str:
    if os.path.exists(_INDEX_HTML):
        with open(_INDEX_HTML, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>UI not found. Expected: " + _INDEX_HTML + "</h1>"


# Paths that should return the UI
_UI_PATHS = {"/", "", "/web", "/web/", "/index.html", "/web/index.html"}


class UIMiddleware(BaseHTTPMiddleware):
    """Serve index.html for all browser-navigation GET requests to known UI paths."""
    async def dispatch(self, request: Request, call_next):
        if request.method == "GET" and request.url.path in _UI_PATHS:
            return HTMLResponse(content=_html(), status_code=200)
        return await call_next(request)


app.add_middleware(UIMiddleware)


# Explicit route declarations as belt-and-suspenders
@app.get("/",           include_in_schema=False)
@app.get("/web",        include_in_schema=False)
@app.get("/web/",       include_in_schema=False)
@app.get("/index.html", include_in_schema=False)
async def serve_ui():
    return HTMLResponse(content=_html(), status_code=200)


# ── Tasks ─────────────────────────────────────────────────────────────────────
@app.get("/tasks", tags=["Environment Info"], summary="List all 7 tasks")
async def list_tasks():
    return {
        "total": 7,
        "score_range": {"min": 0.01, "max": 0.99},
        "tasks": [
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
                    "Bonus: include causal reasoning",
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
                    "Red herring: explicitly call anxiety/panic a red herring OR misleading",
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
                    "coincidental and irrelevant. Treatment: ceftriaxone IV + dexamethasone stat."
                ),
                "scoring_hints": [
                    "Root cause: meningitis OR bacterial meningitis OR meningococcal",
                    "Red herring: call stress/anxiety a red herring OR misleading",
                    "Treatment: ceftriaxone OR antibiotics OR dexamethasone",
                ],
            },
            {
                "id": "medium_aortic",
                "name": "Aortic Dissection vs Acute MI",
                "difficulty": "medium",
                "description": "Identify Type A aortic dissection; dismiss ACS workup as red herring.",
                "time_limit_seconds": 600,
                "max_steps": 3,
                "grader": "server.graders.grade_medium",
                "scenario_id": "medium_aortic",
                "score_range": {"min": 0.01, "max": 0.80},
                "example_input": (
                    "Root cause (Signal C): Type A aortic dissection confirmed by CT aortogram — "
                    "intimal flap in ascending aorta, widened mediastinum on CXR. "
                    "Signal B (troponin, ACS workup) is a red herring — misleading and not the cause. "
                    "Heparin is contraindicated here. Immediate: cardiothoracic surgery."
                ),
                "scoring_hints": [
                    "Root cause: aortic dissection AND type a",
                    "Red herring: call ACS/troponin a red herring OR misleading",
                    "Signal C named as definitive",
                ],
            },
            {
                "id": "hard_mass_casualty",
                "name": "Mass Casualty Triage — Trauma Bay",
                "difficulty": "hard",
                "description": "Triage 3 patients: tension pneumothorax, femur fracture, prolonged PEA arrest. Order matters.",
                "time_limit_seconds": 900,
                "max_steps": 3,
                "grader": "server.graders.grade_hard",
                "scenario_id": "hard_mass_casualty",
                "score_range": {"min": 0.01, "max": 0.75},
                "example_input": (
                    "FIRST: Patient A — tension pneumothorax requires immediate needle decompression. "
                    "Airway compromise is fatal if untreated. "
                    "SECOND: Patient B — femur fracture with active hemorrhage, blood transfusion "
                    "and surgical bleeding control. "
                    "THIRD: Patient C — cardiac arrest 14-minute PEA downtime, poor prognosis, "
                    "continue CPR lowest priority."
                ),
                "scoring_hints": [
                    "FIRST section: patient a OR tension pneumothorax OR needle decompression",
                    "SECOND section: patient b OR femur OR hemorrhage",
                    "THIRD section: patient c OR cardiac arrest OR pea",
                    "Use explicit FIRST/SECOND/THIRD labels",
                ],
            },
            {
                "id": "hard_sepsis_cascade",
                "name": "ICU Crisis — Sepsis / Asthma / Hypoglycemia",
                "difficulty": "hard",
                "description": "Prioritize 3 ICU patients: reversible hypoglycemia > respiratory failure > septic shock.",
                "time_limit_seconds": 900,
                "max_steps": 3,
                "grader": "server.graders.grade_hard",
                "scenario_id": "hard_sepsis_cascade",
                "score_range": {"min": 0.01, "max": 0.75},
                "example_input": (
                    "FIRST: Patient Z — hypoglycemia glucose 32, GCS 6, give D50 IV dextrose immediately. "
                    "SECOND: Patient Y — silent chest asthma O2 81%, immediate intubation with ketamine RSI. "
                    "THIRD: Patient X — septic shock, start broad-spectrum antibiotics, "
                    "vasopressors running, blood cultures."
                ),
                "scoring_hints": [
                    "FIRST section: patient z OR hypoglycemia OR dextrose OR glucagon",
                    "SECOND section: patient y OR asthma OR intubation",
                    "THIRD section: patient x OR sepsis OR antibiotics",
                    "Use explicit FIRST/SECOND/THIRD labels",
                ],
            },
        ],
    }


def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


    import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"🔥 Running on PORT: {port}")
    uvicorn.run("server.app:app", host="0.0.0.0", port=port)