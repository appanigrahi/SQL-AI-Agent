import sys
import subprocess
import json
import os
import re
from datetime import datetime


# --------------------------------------------------
# 1. Read and validate the target server name
# --------------------------------------------------

DEFAULT_SERVER = "SQL01"

if len(sys.argv) > 1:
    server_name = sys.argv[1].strip()
else:
    server_name = DEFAULT_SERVER

# Allow only valid Windows hostname characters.
# This prevents arbitrary PowerShell content from being supplied.
if not re.fullmatch(r"[A-Za-z0-9.-]{1,255}", server_name):
    print("ERROR:")
    print(
        "Invalid server name. Use only letters, numbers, "
        "periods, and hyphens."
    )
    sys.exit(1)


# --------------------------------------------------
# 2. PowerShell remote discovery script
# --------------------------------------------------

ps_command = r'''
$ErrorActionPreference = "Stop"

Invoke-Command `
    -ComputerName "__SERVER_NAME__" `
    -HideComputerName `
    -ScriptBlock {

        $os = Get-CimInstance Win32_OperatingSystem

        $cs = Get-CimInstance Win32_ComputerSystem

        $disk = Get-CimInstance Win32_LogicalDisk `
            -Filter "DeviceID='C:'"

        $sqlInstalled = (
            Get-Service `
                -Name MSSQLSERVER `
                -ErrorAction SilentlyContinue
        ) -ne $null

        $pendingReboot = Test-Path `
            "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired"

        [PSCustomObject]@{
            Hostname             = $env:COMPUTERNAME
            Domain               = $cs.Domain
            OperatingSystem      = $os.Caption
            TotalMemoryBytes     = [Int64]$cs.TotalPhysicalMemory
            LogicalCPUCount      = [Int32]$cs.NumberOfLogicalProcessors
            CDriveFreeBytes      = [Int64]$disk.FreeSpace
            CDriveSizeBytes      = [Int64]$disk.Size
            SQLInstalled         = [Boolean]$sqlInstalled
            PendingReboot        = [Boolean]$pendingReboot
        }
    } |
    ConvertTo-Json -Depth 5
'''

# Replace the explicit placeholder with the validated server name.
ps_command = ps_command.replace(
    "__SERVER_NAME__",
    server_name
)


# --------------------------------------------------
# 3. Execute PowerShell
# --------------------------------------------------

print(f"\nChecking Server: {server_name}\n")

result = subprocess.run(
    [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        ps_command
    ],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)


# --------------------------------------------------
# 4. Handle PowerShell execution errors
# --------------------------------------------------

if result.returncode != 0:
    print("ERROR:")
    print(f"PreCheck failed for server: {server_name}")

    if result.stderr.strip():
        print(result.stderr.strip())
    elif result.stdout.strip():
        print(result.stdout.strip())
    else:
        print("PowerShell returned no error details.")

    sys.exit(result.returncode)


if not result.stdout.strip():
    print("ERROR:")
    print(
        f"PowerShell returned no JSON output for "
        f"server: {server_name}"
    )
    sys.exit(1)


# --------------------------------------------------
# 5. Convert PowerShell JSON into a Python dictionary
# --------------------------------------------------

try:
    data = json.loads(result.stdout)

except json.JSONDecodeError as error:
    print("ERROR:")
    print("PowerShell output could not be parsed as JSON.")
    print(f"JSON parsing details: {error}")

    print("\nRaw PowerShell output:")
    print(result.stdout)

    if result.stderr.strip():
        print("\nPowerShell error output:")
        print(result.stderr)

    sys.exit(1)


# --------------------------------------------------
# 6. Remove PowerShell remoting metadata
# --------------------------------------------------

data.pop("PSComputerName", None)
data.pop("RunspaceId", None)
data.pop("PSShowComputerName", None)


# --------------------------------------------------
# 7. Convert byte values into readable GB values
# --------------------------------------------------

data["MemoryGB"] = round(
    data["TotalMemoryBytes"] / (1024 ** 3),
    2
)

data["CDriveFreeGB"] = round(
    data["CDriveFreeBytes"] / (1024 ** 3),
    2
)

data["CDriveSizeGB"] = round(
    data["CDriveSizeBytes"] / (1024 ** 3),
    2
)


# --------------------------------------------------
# 8. Evaluate individual readiness checks
# --------------------------------------------------

checks = [
    {
        "CheckName": "Memory Check",
        "Expected": ">= 8 GB",
        "Actual": f"{data['MemoryGB']} GB",
        "Status": (
            "PASS"
            if data["MemoryGB"] >= 8
            else "FAIL"
        )
    },
    {
        "CheckName": "Disk Check",
        "Expected": ">= 20 GB",
        "Actual": f"{data['CDriveFreeGB']} GB",
        "Status": (
            "PASS"
            if data["CDriveFreeGB"] >= 20
            else "FAIL"
        )
    },
    {
        "CheckName": "SQL Installation Check",
        "Expected": "Not Installed",
        "Actual": (
            "Installed"
            if data["SQLInstalled"]
            else "Not Installed"
        ),
        "Status": (
            "PASS"
            if not data["SQLInstalled"]
            else "FAIL"
        )
    },
    {
        "CheckName": "Pending Reboot Check",
        "Expected": "No Reboot Pending",
        "Actual": (
            "Reboot Pending"
            if data["PendingReboot"]
            else "No Reboot Pending"
        ),
        "Status": (
            "PASS"
            if not data["PendingReboot"]
            else "FAIL"
        )
    }
]

data["Checks"] = checks


# --------------------------------------------------
# 9. Generate summary and final readiness result
# --------------------------------------------------

passed_checks = len(
    [
        check
        for check in checks
        if check["Status"] == "PASS"
    ]
)

failed_checks = len(
    [
        check
        for check in checks
        if check["Status"] == "FAIL"
    ]
)

data["Summary"] = {
    "TotalChecks": len(checks),
    "PassedChecks": passed_checks,
    "FailedChecks": failed_checks
}

# The server is ready only when every check passes.
data["ReadyForBuild"] = failed_checks == 0


# --------------------------------------------------
# 10. Remove low-level byte values
# --------------------------------------------------

data.pop("TotalMemoryBytes", None)
data.pop("CDriveFreeBytes", None)
data.pop("CDriveSizeBytes", None)


# --------------------------------------------------
# 11. Add execution metadata
# --------------------------------------------------

data["RequestedServer"] = server_name

data["ExecutionTime"] = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)


# --------------------------------------------------
# 12. Display the report
# --------------------------------------------------

print("=== PRECHECK V5 REPORT ===\n")

print(
    json.dumps(
        data,
        indent=4
    )
)


# --------------------------------------------------
# 13. Save the JSON report
# --------------------------------------------------

os.makedirs(
    "reports",
    exist_ok=True
)

# Use the actual remote hostname returned by SQL01.
report_file = os.path.join(
    "reports",
    f"{data['Hostname']}_PreCheck.json"
)

with open(
    report_file,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        data,
        file,
        indent=4
    )

print("\nReport Saved:")
print(report_file)