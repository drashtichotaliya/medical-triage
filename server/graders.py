# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Pure-Python grader logic and scenario definitions.

This module has ZERO external dependencies (no openenv, no FastAPI, no httpx).
This makes it instantly importable for local testing and pytest suites
without triggering the openenv framework's network bootstrapping.

The MedicalTriageEnvironment in medical_triage_env_environment.py
delegates all grading logic to this module.
"""

from typing import List


# ── Easy Scenarios ───────────────────────────────────────────────────────────

EASY_SCENARIOS: List[dict] = [
    {
        "id": "easy_chest_pain",
        "case_report": """
🚨 CASE REPORT — 02:47 UTC
Triage Level: P2 | Duration: 12 minutes and ongoing

Vitals & Observations:
  [CRITICAL] Cardiology: Chest pain radiating to left arm, onset 30 minutes ago
  [CRITICAL] Cardiology: ECG shows ST-segment elevation in leads II, III, aVF
  [WARN]     Nursing: Patient diaphoretic and nauseated
  [ERROR]    Pharmacy: Aspirin and nitroglycerin not yet administered
  [INFO]     Neurology: No focal neurological deficits
  [INFO]     Orthopedics: No musculoskeletal complaints

Patient reports: "Crushing chest pressure", "Pain going down my left arm", "Feeling dizzy"

Question: What is the PRIMARY diagnosis and immediate treatment priority?
""",
        "keywords": ["myocardial infarction", "mi", "stemi", "heart attack", "ecg", "st elevation", "aspirin", "cardiac"],
        "required_count": 2,
    },
    {
        "id": "easy_anaphylaxis",
        "case_report": """
🚨 CASE REPORT — 09:15 UTC
Triage Level: P1 | Duration: 7 minutes and ongoing

Vitals & Observations:
  [CRITICAL] Emergency: Urticaria and angioedema following peanut ingestion
  [CRITICAL] Emergency: BP 80/50 mmHg, HR 130 bpm, SpO2 91%
  [WARN]     Respiratory: Stridor and wheezing present
  [ERROR]    Nursing: Epinephrine not yet administered
  [INFO]     Gastroenterology: No abdominal tenderness
  [INFO]     Dermatology: Widespread hives noted

Patient reports: "Can't breathe properly", "Throat feels tight", "Ate peanuts 10 minutes ago"

Question: What is the PRIMARY diagnosis and immediate treatment priority?
""",
        "keywords": ["anaphylaxis", "anaphylactic", "epinephrine", "adrenaline", "allergic", "epipen", "airway"],
        "required_count": 2,
    },
    {
        "id": "easy_hypoglycemia",
        "case_report": """
🚨 CASE REPORT — 16:32 UTC
Triage Level: P2 | Duration: 5 minutes and ongoing

Vitals & Observations:
  [CRITICAL] Endocrinology: Blood glucose 38 mg/dL (normal: 70-99 mg/dL)
  [CRITICAL] Endocrinology: Patient confused, trembling, diaphoretic
  [WARN]     Neurology: Altered mental status, not oriented to time
  [ERROR]    Nursing: Dextrose IV not yet administered
  [INFO]     Cardiology: Heart rate 105 bpm, BP stable at 118/76
  [INFO]     Nephrology: No renal abnormalities noted

Patient history: Type 1 diabetic, skipped meal after insulin dose

Question: What is the PRIMARY diagnosis and immediate treatment priority?
""",
        "keywords": ["hypoglycemia", "hypoglycaemia", "low blood sugar", "glucose", "dextrose", "insulin", "diabetic"],
        "required_count": 2,
    },
]


# ── Medium Scenarios ─────────────────────────────────────────────────────────

MEDIUM_SCENARIOS: List[dict] = [
    {
        "id": "medium_sepsis",
        "case_report": """
🚨 CASE REPORT — 14:23 UTC
Triage Level: P1 | Duration: 8 minutes and ongoing

Signal A — Clinical presentation:
  [CRITICAL] Emergency: Fever 39.8°C, HR 118 bpm, RR 24/min, BP 88/54 mmHg
  [CRITICAL] Emergency: Altered mental status, patient confused
  [WARN]     Emergency: Suspected source — urinary tract infection

Signal B — Lab results (ROOT CAUSE):
  [CRITICAL] Pathology: WBC 18,400/μL with 85% neutrophils
  [CRITICAL] Pathology: Lactate 4.2 mmol/L (severe tissue hypoperfusion)
  [CRITICAL] Pathology: Blood cultures drawn, procalcitonin elevated
  [INFO]     Pathology: Urine culture pending

Signal C — Imaging (RED HERRING):
  [WARN]     Radiology: Chest X-ray shows mild cardiomegaly
  [INFO]     Radiology: No acute pulmonary infiltrates
  [INFO]     Radiology: Echocardiogram within normal limits

Question: What is the ROOT CAUSE? Which signal confirms the diagnosis and which is a red herring?
""",
        "root_cause_keywords": ["sepsis", "septic shock", "lactate", "infection", "wbc", "neutrophil", "signal b", "lab"],
        "red_herring_keywords": ["cardiomegaly", "cardiac", "signal c", "radiology", "chest x-ray", "red herring", "misleading"],
        "symptom_keywords": ["fever", "hypotension", "tachycardia", "signal a", "altered mental"],
    },
    {
        "id": "medium_pulmonary_embolism",
        "case_report": """
🚨 CASE REPORT — 11:05 UTC
Triage Level: P1 | Duration: 15 minutes and ongoing

Signal A — Imaging (RED HERRING):
  [WARN]     Radiology: Chest X-ray shows Hampton's hump opacity
  [INFO]     Radiology: Non-specific finding, present in many conditions
  [INFO]     Radiology: No pleural effusion detected

Signal B — Clinical & Lab findings:
  [CRITICAL] Emergency: Sudden dyspnea, pleuritic chest pain, HR 122 bpm
  [CRITICAL] Emergency: SpO2 87% on room air, RR 28/min
  [WARN]     Hematology: D-dimer markedly elevated at 3,400 ng/mL

Signal C — Confirmatory imaging (ROOT CAUSE):
  [CRITICAL] Radiology: CT pulmonary angiography — bilateral segmental filling defects
  [CRITICAL] Radiology: Right heart strain pattern on ECG (S1Q3T3)
  [CRITICAL] Radiology: Wells score 7 — high probability PE

Question: What is the ROOT CAUSE? Which signal confirms the diagnosis and which is a red herring?
""",
        "root_cause_keywords": ["pulmonary embolism", "pe", "ct pulmonary", "filling defect", "signal c", "wells score", "anticoagul"],
        "red_herring_keywords": ["hampton", "chest x-ray", "signal a", "non-specific", "red herring", "misleading", "irrelevant"],
        "symptom_keywords": ["dyspnea", "d-dimer", "signal b", "tachycardia", "hypoxia"],
    },
    {
        "id": "medium_meningitis",
        "case_report": """
🚨 CASE REPORT — 00:01 UTC
Triage Level: P1 | Duration: 3 minutes and ongoing

Signal A — Clinical presentation:
  [CRITICAL] Emergency: Severe headache, neck stiffness, photophobia, fever 40.1°C
  [CRITICAL] Emergency: Positive Kernig's and Brudzinski's signs
  [CRITICAL] Emergency: Petechial rash spreading rapidly

Signal B — Non-specific labs (RED HERRING):
  [WARN]     Pathology: Mild transaminase elevation (AST 52, ALT 61)
  [INFO]     Pathology: Liver function otherwise unremarkable
  [INFO]     Pathology: No significant renal dysfunction

Signal C — CSF analysis (ROOT CAUSE):
  [CRITICAL] Pathology: CSF — turbid fluid, opening pressure 340 mmH2O
  [CRITICAL] Pathology: WBC 3,200 cells/μL (95% neutrophils), glucose critically low
  [CRITICAL] Pathology: Gram-positive diplococci on CSF Gram stain

Question: What is the ROOT CAUSE? Which signal confirms the diagnosis and which is a red herring?
""",
        "root_cause_keywords": ["meningitis", "csf", "gram stain", "signal c", "lumbar puncture", "diplococci", "bacterial"],
        "red_herring_keywords": ["transaminase", "liver", "signal b", "alt", "ast", "red herring", "misleading", "irrelevant"],
        "symptom_keywords": ["kernig", "brudzinski", "signal a", "neck stiffness", "petechial"],
    },
]


# ── Hard Scenarios ───────────────────────────────────────────────────────────

HARD_SCENARIOS: List[dict] = [
    {
        "id": "hard_polytrauma",
        "case_report": """
🚨 CASE REPORT — 03:15 UTC
Triage Level: P0 — Critical | Duration: 23 minutes and escalating

Patient map: Airway → Breathing → Circulation → Disability → Exposure (ABCDE)
             Trauma → TBI → Hemorrhage → Fractures → Internal injuries

Findings:
  [CRITICAL] Airway: GCS 8, unprotected airway, gurgling respirations
  [CRITICAL] Breathing: Left-sided absent breath sounds, tracheal deviation RIGHT
  [CRITICAL] Circulation: BP 74/40, HR 138, 2L blood loss estimated
  [WARN]     Disability: Left pupil dilated and non-reactive
  [ERROR]    Orthopedics: Open femur fracture, active arterial bleeding
  [ERROR]    Neurosurgery: CT head — epidural hematoma, midline shift 6mm
  [WARN]     Radiology: Splenic laceration grade III on FAST exam

Recent events:
  03:01 UTC — High-speed MVA, unrestrained driver
  02:45 UTC — Patient was ambulatory at scene, now unconscious

Question: Write a PRIORITIZED action plan — FIRST, SECOND, THIRD steps to stabilize this patient and WHY.
""",
        "first_keywords": ["airway", "intubation", "intubate", "rsi", "rapid sequence", "gcs", "tension pneumothorax", "needle decompression", "breathing"],
        "second_keywords": ["circulation", "hemorrhage", "bleeding", "transfusion", "blood", "bp", "pressure", "femur", "tourniquet"],
        "third_keywords": ["neurosurgery", "hematoma", "epidural", "spleen", "splenic", "ct", "fracture", "disability"],
    },
    {
        "id": "hard_multiorgan",
        "case_report": """
🚨 CASE REPORT — 18:44 UTC
Triage Level: P0 — Critical | Duration: 31 minutes and escalating

Patient map: ICU → Ventilator → Vasopressors → Dialysis → Antibiotics

Findings:
  [CRITICAL] Pulmonology: PaO2/FiO2 ratio 88 — severe ARDS, refractory hypoxemia
  [CRITICAL] Nephrology: Creatinine 6.8 mg/dL, urine output <10 mL/hr — anuric AKI
  [CRITICAL] Cardiology: MAP 52 mmHg despite norepinephrine 0.4 mcg/kg/min
  [ERROR]    Hematology: Platelets 28,000/μL, PT/INR 3.2 — DIC pattern
  [ERROR]    Microbiology: Blood cultures — Gram-negative bacteremia (48hr result)
  [WARN]     Gastroenterology: Ileus, unable to absorb enteral nutrition

Recent events:
  18:30 UTC — Antibiotics not yet broadened despite positive blood cultures
  18:15 UTC — Vasopressor dose not escalated despite falling MAP

Question: Write a PRIORITIZED action plan — FIRST, SECOND, THIRD steps to stabilize this patient and WHY.
""",
        "first_keywords": ["antibiotic", "antimicrobial", "bacteremia", "sepsis", "culture", "broad spectrum", "meropenem", "vancomycin", "source control"],
        "second_keywords": ["vasopressor", "norepinephrine", "map", "hemodynamic", "shock", "vasopressin", "blood pressure", "circulation"],
        "third_keywords": ["dialysis", "renal replacement", "ards", "ventilator", "prone", "dic", "coagulopathy", "platelet", "nutrition"],
    },
    {
        "id": "hard_pediatric_emergency",
        "case_report": """
🚨 CASE REPORT — 22:05 UTC
Triage Level: P0 — Partial critical | Duration: 18 minutes and escalating

Patient map: Pediatric ED → Airway → Seizure Control → Metabolic → Imaging

Findings:
  [CRITICAL] Neurology: Active generalized tonic-clonic seizure, duration >15 min — status epilepticus
  [CRITICAL] Neurology: Lorazepam 0.1 mg/kg given x2 — seizure not aborted
  [CRITICAL] Metabolic: Blood glucose 28 mg/dL, sodium 118 mEq/L (severe hyponatremia)
  [WARN]     Respiratory: SpO2 88%, airway compromised by ongoing convulsions
  [ERROR]    Pharmacy: Second-line anticonvulsant (levetiracetam/fosphenytoin) not yet ordered
  [INFO]     Radiology: CT head pending — no results yet

Recent events:
  22:00 UTC — 4-year-old, 16 kg child, brought in by parents after prolonged home seizure
  21:50 UTC — No prior seizure history, recent gastroenteritis for 3 days

Question: Write a PRIORITIZED action plan — FIRST, SECOND, THIRD steps to manage this patient and WHY.
""",
        "first_keywords": ["airway", "oxygen", "spo2", "seizure", "benzodiazepine", "lorazepam", "second-line", "levetiracetam", "fosphenytoin", "anticonvulsant"],
        "second_keywords": ["glucose", "dextrose", "hypoglycemia", "sodium", "hyponatremia", "metabolic", "electrolyte", "saline"],
        "third_keywords": ["ct", "imaging", "neurosurgery", "intubation", "icu", "admit", "eeg", "cause", "meningitis"],
    },
]


# ── Graders ──────────────────────────────────────────────────────────────────

def safe_reward(raw: float) -> float:
    """Clamp the reward strictly between 0.01 and 0.99 to pass OpenEnv validation constraints."""
    return round(min(max(float(raw), 0.01), 0.99), 2)


def grade_easy(response: str, scenario: dict) -> float:
    r = response.lower()
    score = 0.0
    keywords = scenario["keywords"]
    required = scenario["required_count"]

    hits = sum(1 for kw in keywords if kw in r and f"not {kw}" not in r and f"not a {kw}" not in r)

    if hits >= required:
        score = 0.5 + min(0.5, (hits - required) * 0.1 + 0.3)
    elif hits == 1:
        score = 0.3

    # Bonus for mentioning diagnosis or treatment clearly
    root_cause_terms = ["diagnosis", "treat", "administer", "immediate", "priority", "caused by", "due to", "indicating"]
    if any(term in r for term in root_cause_terms):
        score = min(1.0, score + 0.1)

    # Cap easy score to 0.95 max
    return safe_reward(min(score, 0.95))


def grade_medium(response: str, scenario: dict) -> float:
    r = response.lower()
    score = 0.0

    target_signal = ""
    if scenario["id"] == "medium_sepsis": target_signal = "signal b"
    if scenario["id"] == "medium_pulmonary_embolism": target_signal = "signal c"
    if scenario["id"] == "medium_meningitis": target_signal = "signal c"

    # Root cause identification (35%)
    root_hits = sum(1 for kw in scenario["root_cause_keywords"] if kw in r)
    causal_terms = ["because", "due to", "since", "causes", "resulting", "as a result", "leads to", "confirms", "indicates", "consistent with"]
    has_explanation = any(term in r for term in causal_terms)

    if root_hits >= 2 and has_explanation:
        score += 0.35
    elif root_hits >= 1 and has_explanation:
        score += 0.15
    elif root_hits >= 1:
        score += 0.05

    # Red herring explicit identification (30%)
    strict_dismissal_terms = [
        "red herring", "false alarm", "misleading", "non-specific",
        "coincidental", "irrelevant", "not related", "incidental"
    ]
    dismissal_hits = sum(1 for kw in strict_dismissal_terms if kw in r)
    signal_ident_hits = sum(1 for kw in scenario["red_herring_keywords"] if kw in r)

    red_herring_identified = dismissal_hits >= 1 and signal_ident_hits >= 1
    if red_herring_identified:
        score += 0.30

    # Symptom identification (15%)
    symptom_hits = sum(1 for kw in scenario["symptom_keywords"] if kw in r)
    if symptom_hits >= 1:
        score += 0.15

    # Correct signal letter explicitly named as root cause (10% bonus)
    if target_signal and (target_signal in r):
        score += 0.10

    # Hard cap if red herring not explicitly identified
    if not red_herring_identified:
        score = min(score, 0.45)

    # Medium ceiling: 0.80
    return safe_reward(min(score, 0.80))


def grade_hard(response: str, scenario: dict) -> float:
    r = response.lower()
    score = 0.0
    lines = [line for line in r.split("\n") if line.strip()]

    if not lines:
        return 0.01

    # Split into thirds
    third = max(1, len(lines) // 3)
    first_part = " ".join(lines[:third])
    mid_part = " ".join(lines[third:2 * third])
    last_part = " ".join(lines[2 * third:])

    wrong_service_penalty = 0.0
    # Penalize if a lower-priority issue is treated as the primary action
    if scenario["id"] == "hard_polytrauma":
        if "hematoma" in first_part or "splenic" in first_part or "femur" in first_part:
            wrong_service_penalty = 0.2
    elif scenario["id"] == "hard_multiorgan":
        if "dialysis" in first_part or "ards" in first_part or "dic" in first_part:
            wrong_service_penalty = 0.2
    elif scenario["id"] == "hard_pediatric_emergency":
        if "ct" in first_part or "imaging" in first_part or "icu" in first_part:
            wrong_service_penalty = 0.2

    # First action (40%)
    first_in_position = any(kw in first_part for kw in scenario["first_keywords"])
    if first_in_position:
        score += 0.40

    # Second action (30%)
    second_in_position = any(kw in mid_part for kw in scenario["second_keywords"])
    if second_in_position:
        score += 0.30

    # Third action (20%)
    third_in_position = any(kw in last_part for kw in scenario["third_keywords"])
    if third_in_position:
        score += 0.20

    # Exclusivity penalty: penalize if lower-priority items appear in the first section
    exclusivity_penalty = 0.0
    if any(kw in first_part for kw in scenario["second_keywords"]):
        exclusivity_penalty += 0.15
    if any(kw in first_part for kw in scenario["third_keywords"]):
        exclusivity_penalty += 0.15

    # Bonus for explicit prioritization language (10%)
    priority_terms = ["first", "second", "third", "priority", "immediately", "then", "finally",
                      "step 1", "step 2", "step 3", "next", "subsequently"]
    priority_hits = sum(1 for term in priority_terms if term in r)
    if priority_hits >= 3:
        score += 0.10

    # Apply penalties
    score -= wrong_service_penalty
    score -= exclusivity_penalty

    # Cap if most critical action not addressed first
    if not first_in_position:
        score = min(score, 0.4)

    # Require at least 5 lines for any score above 0.5
    if len(lines) < 5:
        score = min(score, 0.3)

    # Hard ceiling: 0.75
    return safe_reward(min(score, 0.75))