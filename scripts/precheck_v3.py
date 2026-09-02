import subprocess
import json

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
    data.pop("PSComputerName", None)
    data.pop("RunspaceId", None)
    data.pop("PSShowComputerName", None)

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

    data["ReadyForBuild"] = (
        data["MemoryGB"] >= 8
        and
        data["CDriveFreeGB"] >= 20
        and
        not data["SQLInstalled"]
        and
        not data["PendingReboot"]
    )

    print("\n=== PRECHECK V3 REPORT ===\n")

    print(
        json.dumps(
            data,
            indent=4
        )
    )