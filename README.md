---
title: Medical Triage Env
emoji: 🚑
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
tags:
  - openenv
  - medical
  - triage
  - clinical-decision-support
  - healthcare
  - reinforcement-learning
---

# Medical Triage OpenEnv 🚑

An OpenEnv reinforcement learning environment simulating Emergency Department triage and clinical decision-making. An AI agent must guide a patient case through **7 sequential clinical tasks** from initial triage to final disposition.

---

## Environment Description

The environment simulates a real Emergency Department workflow. Each episode presents a patient case with vital signs, history, and symptoms. The agent must sequentially complete clinical tasks in the correct order to receive rewards.

**Why this matters:** Clinical decision-making is one of the highest-stakes real-world tasks. This environment enables training and evaluation of AI agents on genuine medical reasoning, with deterministic graders that reflect actual clinical standards.

---

## Action Space

| Field | Type | Description |
|-------|------|-------------|
| `type` | string (enum) | One of the 8 action types below |
| `value` | string | Payload whose format depends on action type |

**Action types:**

| Action Type | Value Format | Example |
|-------------|-------------|---------|
| `triage_patient` | Integer 1–5 as string | `"2"` |
| `identify_symptoms` | Comma-separated symptoms | `"chest pain,diaphoresis,nausea"` |
| `order_diagnostics` | Comma-separated test names | `"ECG,troponin,CXR,CBC"` |
| `interpret_results` | Free clinical text | `"ST elevation V1-V4 consistent with STEMI"` |
| `generate_differential` | Pipe-separated ranked diagnoses | `"STEMI\|ACS\|PE"` |
| `recommend_treatment` | Comma-separated treatments | `"aspirin 325mg,heparin,PCI,oxygen"` |
| `discharge_decision` | One of: admit / discharge / transfer | `"admit"` |
| `noop` | Empty string | `""` |

---

## Observation Space

Each observation includes:

- **Patient demographics:** `patient_id`, `age`, `sex`
- **Clinical presentation:** `chief_complaint`, `history_of_present_illness`, `past_medical_history`, `medications`, `allergies`
- **Vitals:** `blood_pressure_systolic/diastolic`, `heart_rate`, `respiratory_rate`, `spo2`, `temperature`, `gcs`
- **Progress state:** `progress_stage`, `stages_completed`, `episode_complete`
- **Accumulated results:** `identified_symptoms`, `diagnostics`, `differential_diagnoses`, `treatment_plan`, `disposition`
- **Feedback:** `last_action_feedback`

---

## Tasks & Graders

| # | Task | Difficulty | Reward Weight | Grader Type |
|---|------|-----------|---------------|-------------|
| 1 | Patient Triage | Easy | 0.10 | Numeric range match (exact=0.92, off-by-one=0.5) |
| 2 | Symptom Identification | Easy | 0.10 | Set Jaccard with substring matching |
| 3 | Diagnostic Ordering | Medium | 0.15 | Coverage + efficiency (70/30 split) |
| 4 | Result Interpretation | Medium | 0.15 | Keyword match (exact=0.92, related=0.5) |
| 5 | Differential Diagnosis | Medium | 0.20 | Ranked set match (top-1=0.5, top-3=0.3, order=0.2) |
| 6 | Treatment Recommendation | Hard | 0.20 | Coverage + comprehensiveness bonus |
| 7 | Disposition Decision | Hard | 0.10 | Exact match |

All graders produce scores in **(0.0, 1.0)**.

---

## Reward Function

- **Range:** [-1.0, 1.0]
- **Partial progress signals** at every step (not just episode end)
- **Penalties:** invalid action (-0.20), repeated action (-0.10), wrong stage (-0.10), clearly wrong prediction (-0.15), noop (-0.05)
- **Completion bonus:** `0.2 × mean(task_scores)` when all 7 stages complete

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Status check — returns `{"status": "ok"}` |
| `GET` | `/health` | Health check with version info |
| `POST` | `/reset` | Start a new episode, returns initial Observation |
| `POST` | `/step` | Submit an Action, returns StepResult |
| `GET` | `/state` | Get current State |
| `GET` | `/tasks` | List all 7 tasks with descriptions |
| `GET` | `/web` | Interactive browser UI |

---

## Setup & Usage

### Run locally with Docker

```bash
docker build -t medical-triage-env .
docker run -p 7860:7860 medical-triage-env
```

### Run locally with uvicorn

```bash
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### Quick API test

```bash
curl -X POST http://localhost:7860/reset
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"type": "triage_patient", "value": "2"}'
curl http://localhost:7860/state
```

---

## Running the Baseline Inference Script

```bash
export HF_TOKEN="your-huggingface-token"
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export ENV_URL="http://localhost:7860"

python inference.py
```

Results are saved to `inference_results.json`.

---

## Baseline Scores

Running `Qwen/Qwen2.5-72B-Instruct` against the 3-patient dataset (3 episodes):

| Task | Avg Score |
|------|-----------|
| Patient Triage | ~0.75 |
| Symptom Identification | ~0.65 |
| Diagnostic Ordering | ~0.70 |
| Result Interpretation | ~0.60 |
| Differential Diagnosis | ~0.55 |
| Treatment Recommendation | ~0.50 |
| Disposition Decision | ~0.80 |

---

## Dataset

3 deterministic patient cases covering STEMI / acute cardiac event, Sepsis / infectious presentation, and Trauma / multi-system injury. Each case cycles deterministically — `reset()` advances to the next patient.

---

## Infrastructure

- **Runtime:** Python 3.11, FastAPI + Uvicorn
- **Port:** 7860 | **HF Space SDK:** Docker
- **vCPU:** 2 | **Memory:** 8 GB | **Inference timeout:** < 20 min
