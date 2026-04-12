---
title: Medical Triage Env
emoji: 🏥
colorFrom: red
colorTo: gray
sdk: docker
app_port: 7860
license: mit
base_path: /web
tags:
  - openenv
  - medical-triage
  - emergency-medicine
  - triage
  - healthcare
short_description: Deterministic evaluation of AI emergency medicine triage capabilities
---

# 🏥 Medical Triage Environment

A zero-LLM deterministic [OpenEnv](https://github.com/meta-pytorch/OpenEnv) reinforcement learning environment evaluating the emergency medicine triage capabilities of AI agents.

---

## Why This Problem?

Emergency medicine demands skills that are extremely difficult to automate:

- **Signal Extraction** — identifying the critical finding buried among dozens of normal values
- **Deductive Reasoning** — separating true root cause from coincidental red-herring findings  
- **Strict Prioritization** — knowing that treating Patient C before Patient A can cause a preventable death

No existing automated benchmark evaluates LLM agents on clinical triage decision-making. Medical Triage Env fills this gap using fully deterministic heuristic grading — zero LLM-as-a-judge.

---

## Quick Start

```python
import asyncio
from client import MedicalTriageEnv
from models import MedicalTriageAction

async def main():
    async with MedicalTriageEnv(base_url="https://YOUR_USERNAME-medical-triage-env.hf.space") as env:
        result = await env.reset(task_id="medium_pe")
        obs = result.observation
        
        print(obs.case_report)
        
        action = MedicalTriageAction(
            response="Pulmonary embolism confirmed by CT-PA in Signal B. "
                     "The anxiety history in Signal C is a red herring."
        )
        result = await env.step(action)
        print(f"Score: {result.reward:.2f}")

asyncio.run(main())
```

---

## Tasks & Scenarios

The environment evaluates agents across **7 tasks** spanning 3 difficulty tiers. Scenarios rotate randomly per episode reset to prevent memorization.

| Task ID | Difficulty | Challenge | Core Competency |
|---------|-----------|-----------|-----------------|
| `easy_mi` | 🟢 Easy | STEMI Diagnosis & Treatment | Identify inferior STEMI and provide immediate reperfusion plan |
| `easy_dka` | 🟢 Easy | Diabetic Ketoacidosis Management | Identify DKA and manage severe metabolic acidosis |
| `medium_pe` | 🟡 Medium | Pulmonary Embolism vs Panic Attack | Identify PE as root cause; dismiss anxiety as red herring |
| `medium_meningitis` | 🟡 Medium | Bacterial Meningitis vs Stress Headache | Diagnose meningitis from CSF; dismiss exam stress as red herring |
| `medium_aortic` | 🟡 Medium | Aortic Dissection vs Acute MI | Identify Type A dissection; dismiss ACS workup as red herring |
| `hard_mass_casualty` | 🔴 Hard | Mass Casualty Triage — Trauma Bay | Order-dependent triage: tension pneumothorax → femur fracture → PEA arrest |
| `hard_sepsis_cascade` | 🔴 Hard | ICU Crisis — Sepsis / Asthma / Hypoglycemia | Prioritize 3 ICU patients in correct order of reversibility |

**Score ranges by tier:** Easy (max 0.95) · Medium (max 0.80) · Hard (max 0.75)

---

## Action & Observation Spaces

**Action: `MedicalTriageAction`**

| Field | Type | Description |
|-------|------|-------------|
| `response` | `str` | Agent's free-text clinical analysis |

**Observation: `MedicalTriageObservation`**

| Field | Type | Description |
|-------|------|-------------|
| `case_report` | `str` | Full patient case with vitals, labs, imaging |
| `task_id` | `str` | Current difficulty tier |
| `feedback` | `str` | Evaluator feedback |
| `done` | `bool` | Episode completion flag |
| `reward` | `float` | Normalized score (0.01–0.99) |

---

## Reward System (Deterministic)

All grading uses hardened keyword matching — no LLM judges, guaranteed reproducibility.

- **Easy** (max 0.95): Keyword matching with negation filtering + causal language bonus
- **Medium** (max 0.80): Root cause (35%) + red herring dismissal (30%) + symptoms (15%) + signal naming (10%)
- **Hard** (max 0.75): Positional scoring with wrong-order penalty and anti-dump protection

---

## Setup & Running

### Local Development

```bash
# Install dependencies
uv sync

# Run server with hot-reload
uv run uvicorn server.app:app --reload --host 0.0.0.0 --port 7860

# Health check
curl http://localhost:7860/health

# List tasks
curl http://localhost:7860/tasks

# Run inference
HF_TOKEN=your_token uv run python inference.py

# Run specific task
TASK_NAME=hard_mass_casualty HF_TOKEN=your_token uv run python inference.py
```

### Docker

```bash
docker build -t medical_triage_env:latest .
docker run -p 7860:7860 medical_triage_env:latest
```

### Deploy to HuggingFace Spaces

```bash
openenv push --repo-id YOUR_USERNAME/medical-triage-env
```

### Run Tests

```bash
uv run pytest tests/ -v
uv run pytest tests/ -v --cov=server
```

---

## API Reference

```bash
# Reset environment
curl -X POST http://localhost:7860/reset \
     -H "Content-Type: application/json" \
     -d '{"task_id": "medium_pe"}'

# Submit agent action
curl -X POST http://localhost:7860/step \
     -H "Content-Type: application/json" \
     -d '{"action": {"response": "Pulmonary embolism — anticoagulate with heparin."}}'
```