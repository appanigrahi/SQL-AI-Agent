import json
import os
import sys
from datetime import datetime

# --------------------------------------------------
# Input Parameters
# --------------------------------------------------

server_name = sys.argv[1]
sql_version = sys.argv[2]
edition = sys.argv[3]
instance_name = sys.argv[4]

# --------------------------------------------------
# Request ID
# --------------------------------------------------

request_id = datetime.now().strftime(
    "REQ-%Y%m%d-%H%M%S"
)

# --------------------------------------------------
# Build Plan
# --------------------------------------------------

build_plan = {

    "RequestId": request_id,

    "ServerName": server_name,

    "SQLVersion": sql_version,

    "Edition": edition,

    "InstanceName": instance_name,

    "Status": "PLANNED",

    "GeneratedTime": datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    ),

    "Steps": [

        "Run PreCheck",

        "Validate Prerequisites",

        "Generate ConfigurationFile.ini",

        "Install SQL Server",

        "Validate SQL Services",

        "Generate Audit Report"
    ]
}

# --------------------------------------------------
# Save Report
# --------------------------------------------------

os.makedirs(
    "reports",
    exist_ok=True
)

report_file = (
    f"reports\\{server_name}_BuildPlan.json"
)

with open(
    report_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        build_plan,
        file,
        indent=4
    )

# --------------------------------------------------
# Display
# --------------------------------------------------

print(
    json.dumps(
        build_plan,
        indent=4
    )
)

print(
    f"\nBuild Plan Saved: {report_file}"
)