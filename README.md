# SQL AI Agent

An AI-powered SQL Server Build Assistant for performing controlled SQL Server readiness checks, build planning, installation, validation, and audit reporting.

## Project Status

**Current phase:** Phase 1 MVP  
**Current milestone:** PreCheck Engine v5 and FastAPI v1 completed

> This project is under active development. Features marked as planned are not yet implemented.

---

## Project Objective

SQL AI Agent is a Python-based automation platform designed to simplify and standardize SQL Server build activities.

The solution is being developed to support the following workflow:

1. Receive a SQL Server build request.
2. Validate the target Windows server.
3. Evaluate SQL Server installation readiness.
4. Generate a build plan.
5. Obtain administrator approval.
6. Perform a controlled SQL Server installation.
7. Validate the completed installation.
8. Generate audit and evidence reports.

The long-term solution will incorporate:

- FastAPI
- Swagger UI
- Streamlit
- PowerShell Remoting
- SQL Server unattended installation
- Retrieval-Augmented Generation, or RAG
- Large Language Models, or LLMs
- Model Context Protocol, or MCP
- Human-in-the-loop approval
- Agentic AI orchestration

---

## Current Features

### Completed

- Remote Windows server connectivity through PowerShell Remoting
- Domain-authenticated execution using the logged-in Windows account
- Hostname, domain, and operating-system discovery
- Logical CPU discovery
- Physical-memory discovery
- C drive capacity and free-space discovery
- Default SQL Server service detection
- Pending-reboot detection
- Rule-based build-readiness evaluation
- Structured PASS and FAIL checks
- PreCheck summary generation
- JSON report generation
- FastAPI backend
- Swagger UI
- API health endpoint
- Dynamic PreCheck API execution
- GitHub source-control integration

### Planned

- Dynamic target-server selection
- Pydantic request and response models
- Streamlit frontend
- SQL Server build-request form
- Build-plan generation
- Human approval workflow
- SQL Server `ConfigurationFile.ini` generation
- Automated SQL Server installation
- Post-installation validation
- Centralized audit logging
- RAG-based standards retrieval
- LLM-assisted build-plan explanations
- MCP tools
- Multi-agent orchestration

---

## Lab Infrastructure

| Server | IP Address | Purpose |
|---|---:|---|
| DC | 10.18.1.4 | Active Directory Domain Controller and DNS |
| SQL01 | 10.18.1.5 | SQL Server 2019 installation target |
| AIDEV | 10.18.1.6 | Python, FastAPI, Swagger UI, and development server |

### Domain

```text
SQLAI.com
```

### Operating System

```text
Windows Server 2019 Datacenter
```

### SQL Server Installation Media

```text
\\AIDEV\SQL_Server_Media
```

> Installation media, passwords, tokens, private keys, and other secrets must not be committed to GitHub.

---

## Current Architecture

```text
User
  |
  v
Swagger UI
  |
  v
FastAPI Backend
  |
  v
PreCheck API
  |
  v
Python PreCheck Engine
  |
  v
PowerShell Remoting
  |
  v
SQL01
  |
  v
Readiness Assessment
  |
  v
JSON Report
```

### Current Execution Flow

```text
GET /precheck
  |
  v
FastAPI executes precheck_v5.py
  |
  v
PowerShell connects to SQL01
  |
  v
Server facts are collected
  |
  v
Readiness rules are evaluated
  |
  v
SQL01_PreCheck.json is generated
  |
  v
FastAPI returns the latest JSON report
```

---

## PreCheck Engine Development

### PreCheck v1

Initial remote connectivity and discovery:

- Hostname
- Domain
- Operating system
- Python-to-PowerShell integration
- PowerShell Remoting to SQL01
- JSON output

### PreCheck v2

Infrastructure discovery enhancements:

- Logical CPU count
- Physical memory
- C drive total capacity
- C drive available space
- Conversion of byte values into GB values

### PreCheck v3

SQL Server readiness evaluation:

- Default SQL Server service detection
- Pending-reboot detection
- Rule-based `ReadyForBuild` result

### PreCheck v4

Report persistence:

- Execution timestamp
- JSON report generation
- Report saved under the `reports` directory

Generated runtime artifact:

```text
reports\SQL01_PreCheck.json
```

### PreCheck v5

Professional assessment structure:

- Memory check
- Disk-space check
- SQL installation check
- Pending-reboot check
- Expected value
- Actual value
- PASS or FAIL status
- Summary counts
- Manager-friendly JSON format

---

## Current Readiness Rules

The current MVP evaluates the following conditions:

| Check | Expected Result |
|---|---|
| Memory | At least 8 GB |
| C drive free space | At least 20 GB |
| SQL Server default instance | Not already installed |
| Pending reboot | No reboot pending |

The current readiness logic is:

```python
ReadyForBuild = (
    MemoryGB >= 8
    and CDriveFreeGB >= 20
    and not SQLInstalled
    and not PendingReboot
)
```

> These thresholds are temporary MVP rules. Future versions will load approved requirements from configuration files or organizational standards.

---

## Example PreCheck Assessment

```json
{
  "Hostname": "SQL01",
  "Domain": "sqlai.com",
  "OperatingSystem": "Microsoft Windows Server 2019 Datacenter",
  "LogicalCPUCount": 2,
  "SQLInstalled": false,
  "PendingReboot": false,
  "MemoryGB": 7.95,
  "CDriveFreeGB": 113.5,
  "CDriveSizeGB": 126.45,
  "ReadyForBuild": false,
  "Checks": [
    {
      "CheckName": "Memory Check",
      "Expected": ">= 8 GB",
      "Actual": "7.95 GB",
      "Status": "FAIL"
    },
    {
      "CheckName": "Disk Check",
      "Expected": ">= 20 GB",
      "Actual": "113.5 GB",
      "Status": "PASS"
    },
    {
      "CheckName": "SQL Installation Check",
      "Expected": "Not Installed",
      "Actual": "Not Installed",
      "Status": "PASS"
    },
    {
      "CheckName": "Pending Reboot Check",
      "Expected": "No Reboot Pending",
      "Actual": "No Reboot Pending",
      "Status": "PASS"
    }
  ],
  "Summary": {
    "TotalChecks": 4,
    "PassedChecks": 3,
    "FailedChecks": 1
  },
  "ExecutionTime": "2026-09-02 16:10:28"
}
```

---

## FastAPI Backend

FastAPI exposes the PreCheck Engine through REST APIs.

### Root Endpoint

```http
GET /
```

Example response:

```json
{
  "Application": "SQL AI Agent",
  "Version": "1.0"
}
```

### Health Endpoint

```http
GET /health
```

Example response:

```json
{
  "Status": "Healthy"
}
```

### PreCheck Endpoint

```http
GET /precheck
```

The endpoint performs the following operations:

1. Executes `scripts/precheck_v5.py`.
2. Connects remotely to SQL01.
3. Collects the current target-server information.
4. Evaluates readiness checks.
5. Updates the JSON report.
6. Returns the latest assessment as the API response.

---

## Swagger UI

After starting the FastAPI application, Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

Current endpoints:

```text
GET /
GET /health
GET /precheck
```

Swagger UI can be used to execute and validate each API endpoint.

---

## Repository Structure

```text
SQLAI-Agent
|
|-- api
|   |-- main.py
|
|-- frontend
|   |-- .gitkeep
|
|-- scripts
|   |-- precheck_v1.py
|   |-- precheck_v3.py
|   |-- precheck_v4.py
|   |-- precheck_v5.py
|
|-- configs
|   |-- .gitkeep
|
|-- database
|   |-- .gitkeep
|
|-- docs
|   |-- .gitkeep
|
|-- logs
|
|-- reports
|   |-- SQL01_PreCheck.json
|
|-- tests
|   |-- .gitkeep
|
|-- .gitignore
|-- README.md
|-- requirements.txt
```

> The exact files displayed on GitHub depend on which files have been committed. Git does not track empty directories unless a placeholder such as `.gitkeep` is present.

---

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python 3.12 |
| REST API | FastAPI |
| API server | Uvicorn |
| API documentation | Swagger UI |
| Remote execution | PowerShell Remoting |
| Authentication | Windows domain authentication |
| Target operating system | Windows Server 2019 Datacenter |
| SQL Server version | SQL Server 2019 |
| Source control | Git and GitHub |
| Report format | JSON |
| Planned frontend | Streamlit |

---

## Prerequisites

The current MVP requires:

- Python 3.12
- Git
- PowerShell 5.1 or later
- Domain connectivity from AIDEV to SQL01
- DNS resolution for SQL01
- WinRM enabled on SQL01
- PowerShell Remoting permission for the execution account
- A Python virtual environment
- FastAPI
- Uvicorn

---

## Local Setup

### 1. Clone the repository

```powershell
git clone https://github.com/appanigrahi/SQL-AI-Agent.git
```

### 2. Open the project directory

```powershell
cd SQL-AI-Agent
```

### 3. Create the virtual environment

```powershell
python -m venv venv
```

### 4. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```powershell
pip install -r requirements.txt
```

### 6. Validate PowerShell Remoting

```powershell
Test-WSMan SQL01
```

Then test an authenticated remote session:

```powershell
Enter-PSSession -ComputerName SQL01
```

Exit the remote session:

```powershell
Exit-PSSession
```

---

## Running the PreCheck Engine Directly

Run:

```powershell
python .\scripts\precheck_v5.py
```

Expected behavior:

- The current SQL01 configuration is collected.
- Individual readiness checks are evaluated.
- A summary is generated.
- A JSON report is displayed.
- The report file is created or updated.

Report location:

```text
reports\SQL01_PreCheck.json
```

---

## Running FastAPI

From the repository root, run:

```powershell
uvicorn api.main:app --reload
```

Expected startup message:

```text
Uvicorn running on http://127.0.0.1:8000
```

Open the application endpoints:

- [Application root](http://127.0.0.1:8000)
- [Health endpoint](http://127.0.0.1:8000/health)
- [PreCheck endpoint](http://127.0.0.1:8000/precheck)
- [Swagger UI](http://127.0.0.1:8000/docs)

> The current Uvicorn binding is suitable for local testing on AIDEV. Remote browser access will require an appropriate host binding and an approved Windows Firewall rule.

---

## Security Principles

The project follows these initial safety principles:

- Passwords must not be hardcoded.
- Passwords and tokens must not be committed to GitHub.
- The current solution uses the authenticated Windows session.
- SQL installation actions will require explicit approval.
- The future agent must not expose unrestricted PowerShell execution.
- The future agent must not expose unrestricted SQL execution.
- All installation actions must be allow-listed.
- Build actions must generate audit evidence.
- Sensitive report data must be protected.
- Secrets must eventually be retrieved from an approved secrets store.

---

## Current Limitations

The current MVP has the following limitations:

- SQL01 is hardcoded as the target server.
- Only the C drive is evaluated.
- SQL detection currently checks the default `MSSQLSERVER` service.
- Named SQL Server instances are not yet detected.
- The readiness thresholds are hardcoded.
- The API executes a Python script through `subprocess`.
- The API does not yet use a formal response model.
- The generated report uses a fixed filename.
- Execution history is not yet stored in an audit database.
- Authentication and authorization are not yet implemented for FastAPI.
- Streamlit is not yet implemented.
- SQL Server installation is not yet implemented.
- RAG, LLM, MCP, and agent orchestration are not yet implemented.

---

## Development Roadmap

### Phase 1: Foundation

- [x] GitHub repository
- [x] Python virtual environment
- [x] DNS and network validation
- [x] WinRM validation
- [x] PowerShell Remoting
- [x] PreCheck Engine
- [x] Structured readiness checks
- [x] JSON reporting
- [x] FastAPI backend
- [x] Swagger UI
- [x] Dynamic PreCheck execution

### Phase 2: Reusable API

- [ ] Dynamic target-server input
- [ ] Pydantic request model
- [ ] Pydantic response model
- [ ] Consistent API error handling
- [ ] Unique request ID
- [ ] Execution status tracking
- [ ] API audit records

### Phase 3: Streamlit Frontend

- [ ] Target-server input
- [ ] Run PreCheck button
- [ ] Readiness summary
- [ ] PASS and FAIL display
- [ ] Detailed check results
- [ ] Build history
- [ ] Report download

### Phase 4: SQL Build Planning

- [ ] SQL Server version selection
- [ ] Edition selection
- [ ] Instance-name selection
- [ ] Feature selection
- [ ] Service-account input
- [ ] Drive-layout input
- [ ] Collation selection
- [ ] Port selection
- [ ] TempDB configuration
- [ ] Build-plan generation
- [ ] Human approval

### Phase 5: SQL Server Installation

- [ ] Installation-media validation
- [ ] Configuration-file generation
- [ ] Unattended SQL Server installation
- [ ] Cumulative-update installation
- [ ] Service validation
- [ ] Connectivity validation
- [ ] Post-install configuration
- [ ] Installation evidence collection
- [ ] Controlled retry handling

### Phase 6: Agentic AI

- [ ] Approved runbook collection
- [ ] RAG ingestion pipeline
- [ ] Vector database
- [ ] LLM integration
- [ ] MCP server
- [ ] Policy-gated MCP tools
- [ ] Planner agent
- [ ] Validation agent
- [ ] Execution agent
- [ ] Reporting agent
- [ ] Human-in-the-loop controls
- [ ] Complete audit trail

---

## Definition of Success

The MVP will be considered complete when the platform can:

1. Accept a SQL Server build request.
2. Validate the target Windows server.
3. Display all readiness checks.
4. Generate a deterministic build plan.
5. Obtain explicit approval.
6. Generate an approved SQL Server setup configuration.
7. Perform a controlled unattended installation.
8. Validate SQL Server services and connectivity.
9. Produce a timestamped audit report.
10. Display the result through Streamlit and Swagger UI.

---

## Disclaimer

This project is currently intended for a controlled lab environment.

Do not use the current code to install SQL Server on production systems without:

- Organizational approval
- Security review
- Formal testing
- Service-account design
- Secrets-management integration
- Backup and recovery planning
- Change-management approval
- Rollback procedures
- Audit and access controls
