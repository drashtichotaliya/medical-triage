# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.graders import (
    grade_easy, grade_medium, grade_hard,
    EASY_SCENARIOS, MEDIUM_SCENARIOS, HARD_SCENARIOS,
)


# ── Easy Tests ────────────────────────────────────────────────────────────────

def test_grade_easy_full_hit():
    scenario = EASY_SCENARIOS[0]  # MI / STEMI
    response = "Diagnosis: STEMI — myocardial infarction. Administer aspirin 325mg, activate cath lab for PCI."
    score = grade_easy(response, scenario)
    assert score > 0.6, f"Expected >0.6, got {score}"


def test_grade_easy_negation_filtered():
    scenario = EASY_SCENARIOS[0]
    response = "This is not a myocardial infarction and not a heart attack."
    score = grade_easy(response, scenario)
    assert score == 0.01, f"Expected 0.01 (floor), got {score}"


def test_grade_easy_partial_hit():
    scenario = EASY_SCENARIOS[1]  # DKA
    response = "The patient likely has DKA. Requires insulin therapy."
    score = grade_easy(response, scenario)
    assert score > 0.3, f"Expected >0.3 for partial hit, got {score}"


# ── Medium Tests ──────────────────────────────────────────────────────────────

def test_grade_medium_correct_with_red_herring():
    scenario = MEDIUM_SCENARIOS[0]  # PE
    response = (
        "The root cause is pulmonary embolism confirmed by Signal B — CT-PA shows filling defect. "
        "The anxiety history in Signal C is a red herring and not the cause of the hypoxia."
    )
    score = grade_medium(response, scenario)
    assert score > 0.7, f"Expected >0.7, got {score}"


def test_grade_medium_capped_without_red_herring():
    scenario = MEDIUM_SCENARIOS[0]
    response = "The patient has pulmonary embolism due to recent surgery. Anticoagulation required."
    score = grade_medium(response, scenario)
    assert score <= 0.45, f"Expected <=0.45 without red herring identification, got {score}"


def test_grade_medium_meningitis():
    scenario = MEDIUM_SCENARIOS[1]  # Bacterial meningitis
    response = (
        "Signal C confirms bacterial meningitis — gram-negative diplococci, cloudy CSF. "
        "The stress and sleep deprivation in Signal B are red herrings and irrelevant. "
        "Start ceftriaxone and dexamethasone immediately."
    )
    score = grade_medium(response, scenario)
    assert score > 0.7, f"Expected >0.7, got {score}"


# ── Hard Tests ────────────────────────────────────────────────────────────────

def test_grade_hard_correct_priority_order():
    scenario = HARD_SCENARIOS[0]  # Mass casualty
    response = (
        "First, treat Patient A immediately — tension pneumothorax requires needle decompression "
        "to the right 2nd intercostal space. This is immediately life-threatening.\n"
        "Second, manage Patient B — open femur fracture with hemorrhage needs transfusion "
        "and orthopedic intervention. Tourniquet is controlling bleeding.\n"
        "Third, continue resuscitation of Patient C — cardiac arrest with 14-minute downtime "
        "and non-shockable rhythm carries poor prognosis."
    )
    score = grade_hard(response, scenario)
    assert score > 0.7, f"Expected >0.7, got {score}"


def test_grade_hard_wrong_first_patient_penalized():
    scenario = HARD_SCENARIOS[0]
    response = (
        "First, treat Patient C — cardiac arrest needs CPR.\n"
        "Second, treat Patient B — femur fracture bleeding.\n"
        "Third, treat Patient A — tension pneumothorax."
    )
    score = grade_hard(response, scenario)
    assert score < 0.5, f"Expected <0.5 for wrong priority order, got {score}"


def test_grade_hard_hypoglycemia_first():
    scenario = HARD_SCENARIOS[1]  # Sepsis cascade
    response = (
        "First, treat Patient Z immediately — severe hypoglycemia (glucose 32) is immediately "
        "reversible with D50 IV push. This takes 30 seconds and prevents brain death.\n"
        "Second, intubate Patient Y — silent chest asthma with O2 Sat 81% is rapidly fatal "
        "without airway control and ventilator support.\n"
        "Third, optimize Patient X — septic shock is serious but already on vasopressors; "
        "add broad-spectrum antibiotics and send blood cultures."
    )
    score = grade_hard(response, scenario)
    assert score > 0.7, f"Expected >0.7, got {score}"