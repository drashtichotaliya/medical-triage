# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
"""
Medical Triage Environment - Inference Script

MANDATORY environment variables:
    HF_TOKEN       Your Hugging Face API key
    API_BASE_URL   LLM API endpoint (default: HF router)
    MODEL_NAME     Model identifier (default: Qwen2.5-72B-Instruct)
    ENV_URL        Live environment URL (default: HF Space)

STDOUT FORMAT (required by hackathon):
    [START] task=<name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<0.00> rewards=<r1,r2,...>
"""
import os
import sys
import textwrap
from typing import List, Optional

from openai import OpenAI

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import MedicalTriageEnv
from models import MedicalTriageAction

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
ENV_URL = os.getenv("ENV_URL", "https://drashtichotaliya-medical-triage.hf.space")

BENCHMARK = "medical_triage_env"
SUCCESS_SCORE_THRESHOLD = 0.5
TEMPERATURE = 0.0
MAX_TOKENS = 512

SYSTEM_PROMPT = textwrap.dedent("""
    You are an expert emergency physician and clinical triage specialist with 15 years
    of experience in high-acuity emergency medicine and mass casualty management.

    You will receive patient case reports containing vitals, symptoms, lab results,
    and imaging findings. Your job is to:
    1. Identify the primary diagnosis from objective clinical evidence
    2. Distinguish true emergencies from misleading or coincidental findings (red herrings)
    3. Provide a prioritized, evidence-based treatment or triage plan

    Be specific. Reference exact vital signs, lab values, and clinical findings.
    For multi-patient scenarios, clearly state FIRST, SECOND, THIRD priorities with reasoning.
    Keep responses concise and clinically structured.
""").strip()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    clean_action = action.replace("\n", " ").replace("\r", " ")
    print(f"[STEP] step={step} action={clean_action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(task: str, success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] task={task} success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)


def get_model_response(client: OpenAI, case_report: str, task_id: str, feedback: str) -> str:
    user_prompt = textwrap.dedent(f"""
        Task difficulty: {task_id}
        Previous feedback: {feedback}

        PATIENT CASE REPORT:
        {case_report}

        Analyze this case and provide your clinical assessment.
    """).strip()

    if not HF_TOKEN:
        return "Dummy response due to missing HF_TOKEN."

    for attempt in range(3):
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                stream=False,
            )
            text = (completion.choices[0].message.content or "").strip()
            if text:
                return text
        except Exception:
            if attempt < 2:
                import time
                time.sleep((attempt + 1) * 2)

    return "Unable to analyze case after retries."


def run_task(env_client, llm_client, task_id: str):
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    rewards = []
    success = False
    score = 0.0

    try:
        result = env_client.reset(task_id=task_id)
        obs = result.observation

        response = get_model_response(
            llm_client,
            case_report=obs.case_report,
            task_id=obs.task_id,
            feedback=obs.feedback,
        )

        result = env_client.step(MedicalTriageAction(response=response))
        reward = result.reward

        rewards.append(reward)
        log_step(step=1, action=response, reward=reward, done=True, error=None)

        score = round(min(max(reward, 0.01), 0.99), 2)
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        score = 0.0
    finally:
        log_end(task=task_id, success=success, steps=1, score=score, rewards=rewards)


def main() -> None:
    import time

    target_task = os.getenv("TASK_NAME")
    tasks_to_run = [target_task] if target_task else ["easy", "medium", "hard"]

    llm_client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "dummy")

    for attempt in range(10):
        try:
            with MedicalTriageEnv(base_url=ENV_URL).sync() as env:
                for t in tasks_to_run:
                    run_task(env, llm_client, t)
            break
        except Exception as e:
            print(f"Safe Retry (Attempt {attempt+1}/10) — Waiting for container: {e}", flush=True)
            if attempt < 9:
                time.sleep(10)
            else:
                print("Fatal: Could not connect to environment after retries.", flush=True)
                sys.exit(0)


if __name__ == "__main__":
    main()