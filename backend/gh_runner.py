# backend/gh_runner.py
import json
import os
import time
import uuid
import zipfile
import io
import requests
import re
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta

# -------------------------------------------------------------------------
# GitHub Config
# -------------------------------------------------------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

if not GITHUB_TOKEN or not GITHUB_REPO:
    raise RuntimeError("❌ Please set GITHUB_TOKEN and GITHUB_REPO env vars")

API_BASE = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_TOKEN}"
}

POLL_INTERVAL = 5
POLL_TIMEOUT = 600  # 10 minutes

# -------------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]   # captive/
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------------------
app = FastAPI(title="GitHub Actions Test Runner")
jobs: Dict[str, Dict] = {}

# -------------------------------------------------------------------------
# Request model for running test
# -------------------------------------------------------------------------
class RunTestPayload(BaseModel):
    test_case: str   # Function name (e.g. "test_valid_login")
    requester: Optional[str] = "ui"


# -------------------------------------------------------------------------
# Auto-discover test cases
# -------------------------------------------------------------------------
def discover_tests():

    TEST_DIR = BASE_DIR / "tests"
    mapping = {}

    for root, dirs, files in os.walk(TEST_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                file_path = Path(root) / file
                content = file_path.read_text(encoding="utf-8")

                functions = re.findall(r"def (test_[a-zA-Z0-9_]+)\(", content)

                for fn in functions:
                    pytest_path = f"{file_path.relative_to(BASE_DIR)}::{fn}"
                    mapping[fn] = pytest_path.replace("\\", "/")

    return mapping


# -------------------------------------------------------------------------
# Trigger GitHub workflow
# -------------------------------------------------------------------------
def trigger_github_workflow(client_payload: dict):
    url = f"{API_BASE}/repos/{GITHUB_REPO}/dispatches"

    payload = {
        "event_type": "run-job",
        "client_payload": client_payload
    }

    print("\n========== DISPATCH TO GITHUB ==========")
    print("URL:", url)
    print("Payload:", payload)
    print("Headers:", HEADERS)
    print("========================================\n")

    resp = requests.post(url, headers=HEADERS, json=payload)

    print(">>> GitHub Response Code:", resp.status_code)
    print(">>> GitHub Response Body:", resp.text)

    return resp.status_code == 204, resp


# -------------------------------------------------------------------------
# Download HTML artifact report
# -------------------------------------------------------------------------
def download_and_extract_report(artifact_url: str):
    resp = requests.get(artifact_url, headers=HEADERS)
    if resp.status_code != 200:
        return None

    z = zipfile.ZipFile(io.BytesIO(resp.content))

    for name in z.namelist():
        if name.endswith(".html"):
            return z.read(name).decode("utf-8")

    return None


# -------------------------------------------------------------------------
# Background monitor worker
# -------------------------------------------------------------------------
def background_monitor_job(job_id: str):
    job = jobs[job_id]
    job["status"] = "dispatching"

    pytest_target = job["pytest_target"]

    # Send workflow trigger
    client_payload = {
        "job_id": job_id,
        "pytest_target": pytest_target,
        "requester": job["requester"]
    }

    ok, resp = trigger_github_workflow(client_payload)
    if not ok:
        job["status"] = "dispatch_failed"
        job["error"] = resp.text
        return

    job["status"] = "dispatched"

    # -------------------------------
    # Find workflow run
    # -------------------------------
    run_id = None
    deadline = time.time() + POLL_TIMEOUT

    while time.time() < deadline:
        r = requests.get(
            f"{API_BASE}/repos/{GITHUB_REPO}/actions/runs",
            headers=HEADERS
        )

        runs = r.json().get("workflow_runs", [])

        for run in runs:
            if run.get("event") == "repository_dispatch":
                run_id = run["id"]
                break

        if run_id:
            break

        time.sleep(POLL_INTERVAL)

    if not run_id:
        job["status"] = "workflow_not_found"
        return

    job["workflow_run_id"] = run_id
    job["status"] = "running"

    # -------------------------------
    # Poll until completed
    # -------------------------------
    while time.time() < deadline:
        r = requests.get(
            f"{API_BASE}/repos/{GITHUB_REPO}/actions/runs/{run_id}",
            headers=HEADERS
        )
        data = r.json()

        if data.get("status") == "completed":
            job["conclusion"] = data.get("conclusion")
            break

        time.sleep(POLL_INTERVAL)

    job["status"] = "completed"

    # -------------------------------
    # Fetch artifact
    # -------------------------------
    a = requests.get(
        f"{API_BASE}/repos/{GITHUB_REPO}/actions/runs/{run_id}/artifacts",
        headers=HEADERS
    ).json()

    artifacts = a.get("artifacts", [])
    if not artifacts:
        job["status"] = "no_artifact"
        return

    artifact_id = artifacts[0]["id"]
    artifact_url = f"{API_BASE}/repos/{GITHUB_REPO}/actions/artifacts/{artifact_id}/zip"

    html = download_and_extract_report(artifact_url)
    if not html:
        job["status"] = "artifact_missing"
        return

    # Save report
    out_path = REPORTS_DIR / f"{job_id}.html"
    out_path.write_text(html, encoding="utf-8")

    job["report_path"] = str(out_path)
    job["status"] = "report_ready"
    job["completed_at"] = datetime.now(timezone.utc).isoformat()


# -------------------------------------------------------------------------
# API — Run Test
# -------------------------------------------------------------------------
@app.post("/api/run-test")
def run_test(payload: RunTestPayload, background: BackgroundTasks):

    test_map = discover_tests()

    if payload.test_case not in test_map:
        raise HTTPException(400, f"Test '{payload.test_case}' not found")

    pytest_target = test_map[payload.test_case]
    job_id = uuid.uuid4().hex

    # Save job info
    jobs[job_id] = {
        "job_id": job_id,
        "pytest_target": pytest_target,
        "requester": payload.requester,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Run background monitor
    background.add_task(background_monitor_job, job_id)

    return {
        "message": "Test started",
        "job_id": job_id,
        "pytest_target": pytest_target
    }


# -------------------------------------------------------------------------
# API — Job Status
# -------------------------------------------------------------------------
@app.get("/api/job-status/{job_id}")
def job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[job_id]


# -------------------------------------------------------------------------
# API — Fetch HTML Report
# -------------------------------------------------------------------------
@app.get("/reports/{job_id}.html")
def get_report(job_id: str):
    path = REPORTS_DIR / f"{job_id}.html"
    if not path.exists():
        raise HTTPException(404, "Report not ready")
    return FileResponse(path, media_type="text/html")


# -------------------------------------------------------------------------
# API — For Dropdown Test List
# -------------------------------------------------------------------------
@app.get("/api/test-list")
def test_list():
    return discover_tests()
