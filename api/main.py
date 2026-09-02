import subprocess
import json
from pathlib import Path
from fastapi import FastAPI

app = FastAPI(
    title="SQL AI Agent",
    version="1.0"
)

@app.get("/")
def home():

    return {
        "Application": "SQL AI Agent",
        "Version": "1.0"
    }

@app.get("/health")
def health():

    return {
        "Status": "Healthy"
    }
@app.get("/precheck")
def get_precheck():

    result = subprocess.run(
        ["python", "scripts/precheck_v5.py"],
        capture_output=True,
        text=True
    )

    report_file = Path(
        "reports/SQL01_PreCheck.json"
    )

    if not report_file.exists():

        return {
            "Error": "PreCheck report not found"
        }

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data
