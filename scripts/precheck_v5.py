import subprocess
import json
import os
from datetime import datetime

ps_command = r'''
Invoke-Command -ComputerName SQL01 -HideComputerName -ScriptBlock {

    $os = Get-CimInstance Win32_OperatingSystem

    $cs = Get-CimInstance Win32_ComputerSystem

    $disk = Get-CimInstance Win32_LogicalDisk `
        -Filter "DeviceID='C:'"

    $sqlInstalled = (
        Get-Service MSSQLSERVER `
        -ErrorAction SilentlyContinue
    ) -ne $null

    $pendingReboot = Test-Path `
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired"

    [PSCustomObject]@{

        Hostname = $env:COMPUTERNAME

        Domain = $cs.Domain

        OperatingSystem = $os.Caption

        TotalMemoryBytes = $cs.TotalPhysicalMemory

        LogicalCPUCount = $cs.NumberOfLogicalProcessors

        CDriveFreeBytes = $disk.FreeSpace

        CDriveSizeBytes = $disk.Size

        SQLInstalled = $sqlInstalled

        PendingReboot = $pendingReboot
    }

} | ConvertTo-Json
'''

result = subprocess.run(
    ["powershell", "-Command", ps_command],
    capture_output=True,
    text=True
)

if result.stderr:

    print("ERROR:")
    print(result.stderr)

else:

    data = json.loads(result.stdout)

    # Remove PowerShell metadata
    data.pop("PSComputerName", None)
    data.pop("RunspaceId", None)
    data.pop("PSShowComputerName", None)

    # Convert values
    data["MemoryGB"] = round(
        data["TotalMemoryBytes"] / (1024 * 1024 * 1024),
        2
    )

    data["CDriveFreeGB"] = round(
        data["CDriveFreeBytes"] / (1024 * 1024 * 1024),
        2
    )

    data["CDriveSizeGB"] = round(
        data["CDriveSizeBytes"] / (1024 * 1024 * 1024),
        2
    )

    # Build Readiness Logic
    data["ReadyForBuild"] = (
        data["MemoryGB"] >= 8
        and
        data["CDriveFreeGB"] >= 20
        and
        not data["SQLInstalled"]
        and
        not data["PendingReboot"]
    )
    checks = [

    {
        "CheckName": "Memory Check",
        "Expected": ">= 8 GB",
        "Actual": f"{data['MemoryGB']} GB",
        "Status": "PASS" if data["MemoryGB"] >= 8 else "FAIL"
    },

    {
        "CheckName": "Disk Check",
        "Expected": ">= 20 GB",
        "Actual": f"{data['CDriveFreeGB']} GB",
        "Status": "PASS" if data["CDriveFreeGB"] >= 20 else "FAIL"
    },

    {
        "CheckName": "SQL Installation Check",
        "Expected": "Not Installed",
        "Actual": "Installed" if data["SQLInstalled"] else "Not Installed",
        "Status": "PASS" if not data["SQLInstalled"] else "FAIL"
    },

    {
        "CheckName": "Pending Reboot Check",
        "Expected": "No Reboot Pending",
        "Actual": "Reboot Pending" if data["PendingReboot"] else "No Reboot Pending",
        "Status": "PASS" if not data["PendingReboot"] else "FAIL"
    }
    ]
    data["Checks"] = checks
    passed_checks = len(
        [c for c in checks if c["Status"] == "PASS"]
        )
    failed_checks = len(
        [c for c in checks if c["Status"] == "FAIL"]
        )
    data["Summary"] = {
        "TotalChecks": len(checks),
        "PassedChecks": passed_checks,
        "FailedChecks": failed_checks
        }
    # Remove low-level byte values from the final report
    data.pop("TotalMemoryBytes", None)
    data.pop("CDriveFreeBytes", None)
    data.pop("CDriveSizeBytes", None)
    # Timestamp
    data["ExecutionTime"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print("\n=== PRECHECK V5 REPORT ===\n")

    print(json.dumps(data, indent=4))

    # Create reports folder
    os.makedirs("reports", exist_ok=True)

    # Save report
    report_file = f"reports\\{data['Hostname']}_PreCheck.json"

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