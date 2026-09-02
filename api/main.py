import json
import re
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="SQL AI Agent",
    version="3.0"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRECHECK_SCRIPT = (
    PROJECT_ROOT /
    "scripts" /
    "precheck_v5.py"
)

BUILD_PLAN_SCRIPT = (
    PROJECT_ROOT /
    "scripts" /
    "build_plan_v1.py"
)

REPORTS_FOLDER = (
    PROJECT_ROOT /
    "reports"
)


def validate_server(server):

    if not re.fullmatch(
        r"[A-Za-z0-9.-]{1,255}",
        server
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid server name."
        )

    return server


@app.get("/")
def home():

    return {
        "Application": "SQL AI Agent",
        "Version": "3.0"
    }


@app.get("/health")
def health():

    return {
        "Status": "Healthy"
    }


@app.get("/precheck")
def precheck(
    server: str = Query(
        default="SQL01"
    )
):

    server = validate_server(server)

    result = subprocess.run(
        [
            sys.executable,
            str(PRECHECK_SCRIPT),
            server
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        raise HTTPException(
            status_code=502,
            detail=result.stderr
        )

    report_file = (
        REPORTS_FOLDER /
        f"{server}_PreCheck.json"
    )

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as file:

        report = json.load(file)

    return report


@app.get("/buildplan")
def buildplan(

    server: str,

    sql_version: str,

    edition: str,

    instance_name: str

):

    result = subprocess.run(
        [
            sys.executable,
            str(BUILD_PLAN_SCRIPT),
            server,
            sql_version,
            edition,
            instance_name
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        raise HTTPException(
            status_code=500,
            detail=result.stderr
        )

    build_plan_file = (
        REPORTS_FOLDER /
        f"{server}_BuildPlan.json"
    )

    with open(
        build_plan_file,
        "r",
        encoding="utf-8"
    ) as file:

        build_plan = json.load(file)

    return build_plan