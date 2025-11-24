import subprocess
import uuid
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS so frontend can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create reports folder if not exists
REPORT_DIR = "backend/reports"
os.makedirs(REPORT_DIR, exist_ok=True)


@app.get("/run-tests")
def run_tests(tag: str):
    report_name = f"report_{tag}_{uuid.uuid4().hex}.html"
    report_path = os.path.join(REPORT_DIR, report_name)

    command = [
        "pytest",
        "-m", tag,
        f"--html={report_path}",
        "--self-contained-html"
    ]

    subprocess.run(command)

    return {
        "message": "Test execution completed",
        "report": report_name
    }


@app.get("/get-report/{filename}")
def get_report(filename: str):
    file_path = os.path.join(REPORT_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "Report not found"}

    with open(file_path, "r", encoding="utf-8") as file:
        return {"html": file.read()}
