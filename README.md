 Windows Vulnerability Intelligence Engine

A Python-based Windows software inventory and vulnerability intelligence tool that:

* Reads software name and version from an Excel file
* Fetches CVE data from the National Vulnerability Database (NVD)
* Extracts CVSS scores
* Calculates risk levels
* Detects End-of-Life (EOL) status
* Generates structured Excel vulnerability reports

This project demonstrates how enterprise vulnerability management systems operate internally.

---

## Features

### Asset Processing

* Reads software inventory from Excel
* Handles large software lists
* Auto-save checkpoints during scanning

### Vulnerability Intelligence

* NVD API integration
* Version-aware CVE lookup
* CVSS score extraction
* Risk classification (Critical, High, Medium, Low)
* Full CVE listing sheet
* Summary dashboard sheet

### Reliability and Engineering Controls

* Secure API key handling via environment variables
* Rate-limit aware request handling
* Retry logic for API failures
* Timeout protection
* Logging system

---

## Requirements

* Python 3.8 or higher
* Windows OS
* Internet connection

Python packages:

```
openpyxl
requests
```

Install using:

```
pip install openpyxl requests
```

---

## NVD API Setup

This tool requires an API key from the National Vulnerability Database.

### Step 1: Request an API Key

Request a free API key from:

[https://nvd.nist.gov/developers/request-an-api-key](https://nvd.nist.gov/developers/request-an-api-key)

---

### Step 2: Set Environment Variable

Do not hardcode your API key inside the script.

#### PowerShell

```
setx NVD_API_KEY "your_real_api_key_here"
```

Close and reopen your terminal after setting it.

To verify:

```
echo $env:NVD_API_KEY
```

---

## Input File Format

Create an Excel file named:

```
input.xlsx
```

Structure:

| Software       | Version |
| -------------- | ------- |
| 7-Zip          | 24.09   |
| Docker Desktop | 4.41.2  |
| Google Chrome  | 121.0   |

The first row must contain headers.

---

## How to Run

```
python main.py
```

---

## Output

The tool generates:

```
Enterprise_Vulnerability_Report_YYYY-MM-DD.xlsx
```

### Main Sheet

* Software Name
* Version
* CVE Count
* Highest CVSS
* Risk Level
* CVE IDs (Top 20)
* EOL Status

### Full_CVE_List Sheet

* Software
* Version
* Individual CVE IDs

### Summary Sheet

* Scan Date
* Total Applications
* Total CVEs Found
* Scan Duration (seconds)

---

## Risk Classification Logic

| CVSS Score | Risk Level |
| ---------- | ---------- |
| 9.0 – 10   | Critical   |
| 7.0 – 8.9  | High       |
| 4.0 – 6.9  | Medium     |
| 0.1 – 3.9  | Low        |
| 0          | None       |

---

## Rate Limiting and Stability

* Implements delay control between API calls
* Handles HTTP 429 (rate limit)
* Retries on temporary API failures
* Auto-saves progress every configured interval
* Logs activity to `vuln_engine.log`

---

## Security Considerations

* The tool is read-only
* It does not modify registry or system files
* No exploit functionality is included
* API keys are handled securely via environment variables

---

## Limitations

* Keyword-based CVE matching (not full CPE-based validation)
* EOL detection depends on public lifecycle data availability
* Accuracy depends on NVD indexing structure

---

## Future Improvements

* CPE-based precise version validation
* Multi-threaded rate limiting
* CLI argument support
* Web dashboard interface
* Dockerized deployment
* Threat intelligence enrichment

---

## License

MIT License

---

