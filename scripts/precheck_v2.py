import subprocess
import json


ps_command = r'''
Invoke-Command -ComputerName SQL01 -HideComputerName -ScriptBlock {

    $os = Get-CimInstance Win32_OperatingSystem
    $cs = Get-CimInstance Win32_ComputerSystem

    $disk = Get-CimInstance Win32_LogicalDisk `
        -Filter "DeviceID='C:'"

    [PSCustomObject]@{

        Hostname = $env:COMPUTERNAME

        Domain = $cs.Domain

        OperatingSystem = $os.Caption

        TotalMemoryBytes = $cs.TotalPhysicalMemory

        LogicalCPUCount = $cs.NumberOfLogicalProcessors

        CDriveFreeBytes = $disk.FreeSpace

        CDriveSizeBytes = $disk.Size
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
    print("\n=== PRECHECK REPORT ===\n")
    print(json.dumps(data, indent=4))
