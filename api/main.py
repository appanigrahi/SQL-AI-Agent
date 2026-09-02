import json
import re
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query


# --------------------------------------------------
# 1. Application configuration
# --------------------------------------------------

app = FastAPI(
    title="SQL AI Agent",
    description=(
        "Controlled SQL Server build, readiness validation, "
        "installation, and reporting API."
    ),
    version="2.0"
)


# --------------------------------------------------
# 2. Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRECHECK_SCRIPT = (
    PROJECT_ROOT
    / "scripts"
    / "precheck_v5.py"
)

REPORTS_DIRECTORY = (
    PROJECT_ROOT
    / "reports"
)


# --------------------------------------------------
# 3. Server-name validation
# --------------------------------------------------

def validate_server_name(server: str) -> str:
    """
    Validate and normalize a Windows server name.

    Allowed characters:
    - Letters
    - Numbers
    - Periods
    - Hyphens
    """

    normalized_server = server.strip()

    if not normalized_server:
        raise HTTPException(
            status_code=400,
            detail="Server name cannot be empty."
        )

    if not re.fullmatch(
        r"[A-Za-z0-9.-]{1,255}",
        normalized_server
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid server name. Use only letters, "
                "numbers, periods, and hyphens."
            )
        )

    return normalized_server


# --------------------------------------------------
# 4. Root endpoint
# --------------------------------------------------

@app.get(
    "/",
    summary="Application information"
)
def home():
    """
    Return basic SQL AI Agent application information.
    """

    return {
        "Application": "SQL AI Agent",
        "Version": "2.0",
        "CurrentPhase": "Phase 1 MVP",
        "CurrentCapability": "Dynamic SQL Server PreCheck"
    }


# --------------------------------------------------
# 5. Health endpoint
# --------------------------------------------------

@app.get(
    "/health",
    summary="API health status"
)
def health():
    """
    Verify that the FastAPI application is running.
    """

    return {
        "Status": "Healthy",
        "Application": "SQL AI Agent"
    }


# --------------------------------------------------
# 6. Dynamic PreCheck endpoint
# --------------------------------------------------

@app.get(
    "/precheck",
    summary="Run SQL Server build-readiness checks"
)
def get_precheck(
    server: str = Query(
        default="SQL01",
        description=(
            "Target Windows server name or fully qualified "
            "domain name."
        ),
        examples=["SQL01"]
    )
):
    """
    Run PreCheck Engine v5 against the selected server.

    Processing sequence:

    1. Validate the requested server name.
    2. Execute precheck_v5.py using the active Python runtime.
    3. Wait for the PreCheck Engine to complete.
    4. Read the newly generated JSON report.
    5. Return the report through the API.
    """

    target_server = validate_server_name(server)

    if not PRECHECK_SCRIPT.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "PreCheck script was not found at: "
                f"{PRECHECK_SCRIPT}"
            )
        )

    REPORTS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    result = subprocess.run(
        [
            sys.executable,
            str(PRECHECK_SCRIPT),
            target_server
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        error_details = (
            result.stderr.strip()
            or result.stdout.strip()
            or "No error details were returned."
        )

        raise HTTPException(
            status_code=502,
            detail={
                "Message": "PreCheck execution failed.",
                "RequestedServer": target_server,
                "ExecutionOutput": error_details
            }
        )

    expected_report = (
        REPORTS_DIRECTORY
        / f"{target_server}_PreCheck.json"
    )

    if not expected_report.exists():
        matching_reports = list(
            REPORTS_DIRECTORY.glob(
                "*_PreCheck.json"
            )
        )

        if not matching_reports:
            raise HTTPException(
                status_code=500,
                detail={
                    "Message": (
                        "PreCheck completed, but no report "
                        "file was generated."
                    ),
                    "RequestedServer": target_server
                }
            )

        expected_report = max(
            matching_reports,
            key=lambda report: report.stat().st_mtime
        )

    try:
        with expected_report.open(
            "r",
            encoding="utf-8"
        ) as report_handle:
            report_data = json.load(
                report_handle
            )

    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=500,
            detail={
                "Message": (
                    "The generated PreCheck report "
                    "contains invalid JSON."
                ),
                "ReportFile": str(expected_report),
                "Error": str(error)
            }
        ) from error

    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail={
                "Message": (
                    "The generated PreCheck report "
                    "could not be opened."
                ),
                "ReportFile": str(expected_report),
                "Error": str(error)
            }
        ) from error

    return {
        "APIStatus": "Success",
        "RequestedServer": target_server,
        "ReportFile": expected_report.name,
        "PreCheckReport": report_data
    }