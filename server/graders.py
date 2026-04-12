# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
"""
Pure-Python grader logic and scenario definitions.

ZERO external dependencies — instantly importable for local testing and pytest.
All grading is deterministic: keyword matching + positional scoring.

Task layout:
  Easy   — 2 scenarios: easy_mi, easy_dka
  Medium — 3 scenarios: medium_pe, medium_meningitis, medium_aortic
  Hard   — 2 scenarios: hard_mass_casualty, hard_sepsis_cascade
"""
from typing import List


# ── Easy Scenarios (2) ───────────────────────────────────────────────────────

EASY_SCENARIOS: List[dict] = [
    {
        "id": "easy_mi",
        "case_report": """
🚨 EMERGENCY CASE — 09:45 AM
Severity: P2 | Patient ID: PT-001 | Duration: 45 minutes

Vitals:
  BP: 185/115 mmHg (hypertensive)
  HR: 112 bpm (tachycardia)
  O2 Sat: 93% (hypoxic)
  Temp: 37.2°C (normal)

Presentation:
  Chief Complaint: Crushing substernal chest pain radiating to left arm and jaw
  Associated: Diaphoresis, nausea, shortness of breath
  Duration: 45 minutes, not relieved by rest

Diagnostics:
  ECG: ST elevation in leads II, III, aVF — inferior STEMI pattern
  Troponin I: 3.1 ng/mL (CRITICALLY HIGH — normal <0.04 ng/mL)
  CK-MB: 48 U/L (elevated)
  CBC: Normal
  CXR: No pulmonary edema

Question: What is the primary diagnosis and immediate treatment plan?
""",
        "keywords": ["myocardial infarction", "heart attack", "mi", "stemi", "aspirin",
                     "pci", "percutaneous coronary intervention", "thrombolysis", "cath lab",
                     "heparin", "nitrates", "reperfusion"],
        "required_count": 2,
    },
    {
        "id": "easy_dka",
        "case_report": """
🚨 EMERGENCY CASE — 14:20 PM
Severity: P2 | Patient ID: PT-002 | Duration: 12 hours

Vitals:
  BP: 92/58 mmHg (hypotensive)
  HR: 124 bpm (tachycardia)
  RR: 30/min (Kussmaul breathing)
  Temp: 37.8°C

Presentation:
  Chief Complaint: Confusion, profound weakness, vomiting for 12 hours
  History: Type 1 Diabetes, missed insulin for 3 days
  Breath: Fruity/acetone odor noted on exam

Diagnostics:
  Blood Glucose: 512 mg/dL (CRITICALLY HIGH)
  pH: 7.14 (severe metabolic acidosis)
  Bicarbonate: 8 mEq/L (critically low)
  Anion Gap: 30 mEq/L (high — >12 is abnormal)
  Serum Ketones: 4+ (large)
  Potassium: 5.8 mEq/L (high — will drop with treatment)

Question: What is the primary diagnosis and immediate treatment plan?
""",
        "keywords": ["diabetic ketoacidosis", "dka", "insulin", "iv fluids", "normal saline",
                     "potassium", "electrolyte", "bicarbonate", "glucose", "hydration"],
        "required_count": 2,
    },
]


# ── Medium Scenarios (3) ─────────────────────────────────────────────────────

MEDIUM_SCENARIOS: List[dict] = [
    {
        "id": "medium_pe",
        "case_report": """
🚨 EMERGENCY CASE — 11:30 AM
Severity: P1 | Patient ID: PT-004 | Duration: 2 hours

Signal A — Patient Presentation:
  Chief Complaint: Sudden-onset dyspnea and pleuritic chest pain
  History: 3-week post right total knee replacement, prolonged bed rest
  Associated: Hemoptysis, right leg swelling and tenderness

Signal B — Vitals & Objective Findings (ROOT CAUSE):
  HR: 122 bpm (tachycardia)
  O2 Sat: 87% on room air (cannot be explained by anxiety alone)
  D-dimer: 3,200 ng/mL (CRITICALLY ELEVATED — >500 abnormal)
  CT Pulmonary Angiography: Large filling defect in right main pulmonary artery
  Echo: Right ventricular dilation, septal bowing — right heart strain

Signal C — Psychiatric Context (RED HERRING):
  History: Generalized anxiety disorder, multiple prior panic attacks
  Nursing note: "Patient appears anxious and hyperventilating"
  Psychiatry consult 2 hours ago: Suggested possible somatic panic response

Question: What is the ROOT CAUSE? Which signal is definitive and which is a red herring?
""",
        "root_cause_keywords": ["pulmonary embolism", "pe", "embolism", "thromboembolism",
                                 "blood clot", "dvt", "signal b", "anticoagulation",
                                 "heparin", "anticoagulant", "thrombus"],
        "red_herring_keywords": ["anxiety", "panic", "psychiatric", "signal c",
                                  "red herring", "not the cause", "misleading",
                                  "coincidental", "irrelevant"],
        "symptom_keywords": ["shortness of breath", "dyspnea", "hemoptysis", "signal a",
                              "leg swelling", "pleuritic"],
    },
    {
        "id": "medium_meningitis",
        "case_report": """
🚨 EMERGENCY CASE — 03:15 AM
Severity: P1 | Patient ID: PT-005 | Duration: 8 hours

Signal A — Clinical Presentation:
  Chief Complaint: Severe thunderclap headache, neck stiffness, high fever — 8 hours
  Signs: Kernig sign positive, Brudzinski sign positive, photophobia, phonophobia
  Rash: Non-blanching petechial rash on trunk and extremities
  History: College dormitory resident, no recent vaccinations

Signal B — Stress and Social Context (RED HERRING):
  High academic stress reported (final exam week)
  Sleep-deprived (averaging 3-4 hours/night)
  Counselor note: Known anxiety, history of tension headaches from stress
  Roommate: "This happens every exam season"

Signal C — Lab and Diagnostic Findings (ROOT CAUSE):
  Temp: 40.1°C, WBC: 19,400/μL (markedly elevated)
  CSF: Cloudy/turbid, opening pressure 280 mmH2O (elevated)
  CSF WBC: 1,800 cells/μL (95% neutrophils)
  CSF Glucose: 22 mg/dL (LOW — normal 50-80), CSF Protein: 320 mg/dL (HIGH)
  Gram Stain: Gram-negative diplococci

Question: What is the ROOT CAUSE? Which signal is definitive and which is a red herring?
""",
        "root_cause_keywords": ["meningitis", "bacterial meningitis", "meningococcal",
                                 "neisseria meningitidis", "signal c", "ceftriaxone",
                                 "penicillin", "antibiotics", "dexamethasone"],
        "red_herring_keywords": ["stress", "anxiety", "tension headache", "sleep", "signal b",
                                  "red herring", "not the cause", "misleading",
                                  "coincidental", "irrelevant"],
        "symptom_keywords": ["headache", "neck stiffness", "fever", "signal a",
                              "kernig", "petechial", "photophobia"],
    },
    {
        "id": "medium_aortic",
        "case_report": """
🚨 EMERGENCY CASE — 16:45 PM
Severity: P1 | Patient ID: PT-006 | Duration: 90 minutes

Signal A — Patient Presentation:
  Chief Complaint: Sudden tearing/ripping chest pain radiating to the back between shoulder blades
  History: Hypertension (poorly controlled), Marfan syndrome
  Key Finding: BP asymmetry — Right arm 188/112, Left arm 128/78 (60 mmHg difference)

Signal B — Initial Cardiac Workup (RED HERRING):
  Troponin I: 0.09 ng/mL (mildly elevated — non-specific)
  ECG: Non-specific ST changes, no clear STEMI pattern
  ER Resident Assessment: "Likely atypical presentation of acute MI"
  Cardiology note: "Consider ACS, start heparin"

Signal C — Imaging (ROOT CAUSE):
  CXR: Widened mediastinum (8.5cm)
  CT Aortogram: Type A aortic dissection — intimal flap in ascending aorta
  Echo: Moderate aortic regurgitation, small pericardial effusion

Question: What is the ROOT CAUSE? Which signal is definitive and which is a red herring?
""",
        "root_cause_keywords": ["aortic dissection", "dissection", "type a", "aorta",
                                 "signal c", "cardiothoracic surgery", "emergency surgery",
                                 "surgical", "mediastinum"],
        "red_herring_keywords": ["myocardial infarction", "heart attack", "acs",
                                  "heparin", "signal b", "red herring", "not the cause",
                                  "misleading", "coincidental", "irrelevant", "troponin"],
        "symptom_keywords": ["chest pain", "tearing", "ripping", "signal a",
                              "hypertension", "asymmetric", "blood pressure"],
    },
]


# ── Hard Scenarios (2) ───────────────────────────────────────────────────────

HARD_SCENARIOS: List[dict] = [
    {
        "id": "hard_mass_casualty",
        "case_report": """
🚨 MASS CASUALTY INCIDENT — 20:30 PM
Severity: P0 — Multi-patient | Duration: Ongoing

Patient Routing: EMS Dispatch → Trauma Bay → ICU/OR
Resources: 1 trauma surgeon, 2 trauma bays, 1 ventilator

Patient Reports:
  [PATIENT A] 45M — GSW to chest, BP: 78/48 (shock), HR: 138, GCS: 10
                      Absent breath sounds right side, tracheal deviation LEFT
                      Clinical: Tension pneumothorax suspected
  [PATIENT B] 32F — Open femur fracture, BP: 102/72, HR: 108, GCS: 15
                      Active hemorrhage — tourniquet applied, conscious and talking
                      Distal pulses intact
  [PATIENT C] 67M — Witnessed cardiac arrest, CPR in progress x14 minutes
                      No shockable rhythm on monitor (PEA), 3 rounds epinephrine given
                      Downtime: 14 minutes, no bystander CPR initially

Question: Write a PRIORITIZED action plan — FIRST, SECOND, THIRD patient and WHY.
""",
        "first_keywords": ["patient a", "tension pneumothorax", "needle decompression",
                            "chest decompression", "a first", "treat a", "needle thoracostomy",
                            "immediate", "airway", "pneumothorax"],
        "second_keywords": ["patient b", "femur", "fracture", "hemorrhage", "transfusion",
                             "b second", "blood", "ortho", "vascular", "bleeding"],
        "third_keywords": ["patient c", "cardiac arrest", "cpr", "poor prognosis",
                            "c third", "expectant", "resuscitation", "pea", "downtime"],
    },
    {
        "id": "hard_sepsis_cascade",
        "case_report": """
🚨 SIMULTANEOUS MULTI-PATIENT EMERGENCY — 08:15 AM
Severity: P0 — ICU Critical | Duration: 45 minutes

Resources: 1 intensivist, 2 nurses, 1 IV team, 1 ventilator available

Patient Reports:
  [PATIENT X] 72M — Septic shock, BP: 68/42, HR: 142, Temp: 40.4°C
                      Lactate: 7.1 mmol/L, vasopressors escalating (norepinephrine max dose)
                      Suspected gram-negative bacteremia — blood cultures pending x2 hours
                      Multi-organ dysfunction: Cr 3.2, bili 4.8, platelets falling
  [PATIENT Y] 28F — Severe acute asthma exacerbation, O2 Sat: 81% on 15L NRB
                      Peak flow <20% predicted, silent chest developing
                      Not responding to back-to-back nebulizers x3, IV magnesium given
                      Accessory muscle use, tripod positioning, unable to speak in sentences
  [PATIENT Z] 55M — Found unconscious at home, blood glucose: 32 mg/dL (CRITICALLY LOW)
                      Family reports insulin overdose (took 5x normal dose 1 hour ago)
                      No IV access yet, GCS: 6 (E1V2M3)

Question: Write a PRIORITIZED action plan — FIRST, SECOND, THIRD patient and WHY.
""",
        "first_keywords": ["patient z", "hypoglycemia", "glucose", "dextrose", "d50",
                            "d10", "glucagon", "z first", "treat z", "sugar", "immediate reversal",
                            "blood sugar", "iv glucose"],
        "second_keywords": ["patient y", "asthma", "intubation", "ventilator", "intubate",
                             "ketamine", "rsi", "y second", "airway", "silent chest",
                             "respiratory failure", "breathing"],
        "third_keywords": ["patient x", "sepsis", "antibiotics", "broad spectrum",
                            "vasopressors", "cultures", "x third", "septic shock",
                            "blood cultures", "source control"],
    },
]


# ── Graders ──────────────────────────────────────────────────────────────────

def safe_reward(raw: float) -> float:
    """Clamp reward strictly between 0.01 and 0.99 for OpenEnv validation compliance."""
    return round(min(max(float(raw), 0.01), 0.99), 2)


def grade_easy(response: str, scenario: dict) -> float:
    r = response.lower()
    keywords = scenario["keywords"]
    required = scenario["required_count"]

    hits = sum(
        1 for kw in keywords
        if kw in r and f"not {kw}" not in r and f"not a {kw}" not in r
    )

    score = 0.0
    if hits >= required:
        score = 0.5 + min(0.45, (hits - required) * 0.1 + 0.3)
    elif hits == 1:
        score = 0.3

    causal_terms = ["diagnosis is", "consistent with", "indicates", "confirms",
                    "due to", "because", "caused by", "suggests", "treatment"]
    if any(term in r for term in causal_terms):
        score = min(1.0, score + 0.1)

    return safe_reward(min(score, 0.95))


def grade_medium(response: str, scenario: dict) -> float:
    r = response.lower()
    score = 0.0

    root_hits = sum(1 for kw in scenario["root_cause_keywords"] if kw in r)
    causal_terms = ["because", "due to", "confirms", "demonstrates", "indicates",
                    "primary", "caused by", "root cause", "definitive"]
    has_explanation = any(term in r for term in causal_terms)

    if root_hits >= 2 and has_explanation:
        score += 0.35
    elif root_hits >= 1 and has_explanation:
        score += 0.15
    elif root_hits >= 1:
        score += 0.05

    strict_dismissal = ["red herring", "misleading", "not the cause", "false alarm",
                        "coincidental", "irrelevant", "distractor"]
    dismissal_hits = sum(1 for term in strict_dismissal if term in r)
    signal_hits = sum(1 for kw in scenario["red_herring_keywords"] if kw in r)

    red_herring_identified = dismissal_hits >= 1 and signal_hits >= 1
    if red_herring_identified:
        score += 0.30

    symptom_hits = sum(1 for kw in scenario["symptom_keywords"] if kw in r)
    if symptom_hits >= 1:
        score += 0.15

    target = ""
    if scenario["id"] == "medium_pe":
        target = "signal b"
    elif scenario["id"] == "medium_meningitis":
        target = "signal c"
    elif scenario["id"] == "medium_aortic":
        target = "signal c"
    if target and target in r:
        score += 0.10

    if not red_herring_identified:
        score = min(score, 0.45)

    return safe_reward(min(score, 0.80))


def grade_hard(response: str, scenario: dict) -> float:
    r = response.lower()
    lines = [line for line in r.split("\n") if line.strip()]

    if not lines:
        return 0.01

    third = max(1, len(lines) // 3)
    first_part = " ".join(lines[:third])
    mid_part = " ".join(lines[third:2 * third])
    last_part = " ".join(lines[2 * third:])

    wrong_first_penalty = 0.0
    if scenario["id"] == "hard_mass_casualty":
        if any(kw in first_part for kw in ["patient b", "patient c"]):
            wrong_first_penalty = 0.2
    elif scenario["id"] == "hard_sepsis_cascade":
        if any(kw in first_part for kw in ["patient x", "patient y", "sepsis", "asthma"]):
            wrong_first_penalty = 0.2

    first_score = 0.40 if any(kw in first_part for kw in scenario["first_keywords"]) else 0.0
    second_score = 0.30 if any(kw in mid_part for kw in scenario["second_keywords"]) else 0.0
    third_score = 0.20 if any(kw in last_part for kw in scenario["third_keywords"]) else 0.0

    exclusivity_penalty = 0.0
    if any(kw in first_part for kw in scenario["second_keywords"]):
        exclusivity_penalty += 0.15
    if any(kw in first_part for kw in scenario["third_keywords"]):
        exclusivity_penalty += 0.15

    priority_terms = ["first", "second", "third", "step 1", "step 2", "step 3",
                      "immediately", "then", "finally", "priority"]
    bonus = 0.10 if sum(1 for t in priority_terms if t in r) >= 3 else 0.0

    score = first_score + second_score + third_score + bonus
    score -= wrong_first_penalty + exclusivity_penalty

    if first_score == 0:
        score = min(score, 0.40)

    if len(lines) < 5:
        score = min(score, 0.30)

    return safe_reward(min(score, 0.75))