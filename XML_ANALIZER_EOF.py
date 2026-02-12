import requests
import urllib.parse
import time
import os
import logging
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from datetime import datetime

# -------------------------
# CONFIGURATION
# -------------------------
NVD_API_KEY = os.getenv("NVD_API_KEY")  # Set using setx
RATE_DELAY = 1.2
AUTO_SAVE_INTERVAL = 10

if not NVD_API_KEY:
    raise ValueError("❌ NVD_API_KEY not set. Use: setx NVD_API_KEY your_key")

# -------------------------
# LOGGING
# -------------------------
logging.basicConfig(
    filename="vuln_engine.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------
# RISK LOGIC
# -------------------------
def calculate_risk(score):
    if score >= 9:
        return "Critical"
    elif score >= 7:
        return "High"
    elif score >= 4:
        return "Medium"
    elif score > 0:
        return "Low"
    return "None"

def risk_color(risk):
    colors = {
        "Critical": "FF0000",
        "High": "FF6600",
        "Medium": "FFD700",
        "Low": "90EE90"
    }
    return PatternFill(start_color=colors.get(risk, "FFFFFF"),
                       end_color=colors.get(risk, "FFFFFF"),
                       fill_type="solid")

# -------------------------
# EOL CHECK
# -------------------------
def check_eol(product_name):
    try:
        slug = product_name.lower().replace(" ", "-")
        url = f"https://endoflife.date/api/{slug}.json"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return "Unknown"

        data = response.json()

        for entry in data:
            if entry.get("eol") is True:
                return "EOL"
            if entry.get("eol") is False:
                return "Supported"

        return "Unknown"

    except:
        return "Unknown"

# -------------------------
# NVD CLIENT
# -------------------------
def fetch_cves(product, version):

    query = urllib.parse.quote(f"{product} {version}")
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={query}&resultsPerPage=2000"

    headers = {"apiKey": NVD_API_KEY}

    for attempt in range(3):
        try:
            start = time.time()
            response = requests.get(url, headers=headers, timeout=20)

            if response.status_code == 429:
                logging.warning("Rate limit hit. Sleeping 10 sec.")
                time.sleep(10)
                continue

            if response.status_code != 200:
                logging.error(f"API error {response.status_code}")
                return 0, 0, []

            data = response.json()
            cve_list = []
            highest_score = 0

            for item in data.get("vulnerabilities", []):
                cve_id = item["cve"]["id"]
                cve_list.append(cve_id)

                metrics = item["cve"].get("metrics", {})
                if "cvssMetricV31" in metrics:
                    score = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
                    highest_score = max(highest_score, score)

            elapsed = time.time() - start
            time.sleep(max(0, RATE_DELAY - elapsed))

            return len(cve_list), highest_score, cve_list[:20]

        except Exception as e:
            logging.error(f"Exception: {e}")
            time.sleep(5)

    return 0, 0, []

# -------------------------
# MAIN ENGINE
# -------------------------
def scan_excel(input_file):

    start_time = time.time()

    wb = load_workbook(input_file)
    ws = wb.active

    # Headers
    ws.cell(row=1, column=3).value = "CVE Count"
    ws.cell(row=1, column=4).value = "Highest CVSS"
    ws.cell(row=1, column=5).value = "Risk Level"
    ws.cell(row=1, column=6).value = "CVE IDs (Top 20)"
    ws.cell(row=1, column=7).value = "EOL Status"

    # Full CVE Sheet
    if "Full_CVE_List" not in wb.sheetnames:
        cve_sheet = wb.create_sheet("Full_CVE_List")
        cve_sheet.append(["Software", "Version", "CVE ID"])
    else:
        cve_sheet = wb["Full_CVE_List"]

    max_row = ws.max_row
    total_cves = 0

    for row in range(2, max_row + 1):

        name = ws.cell(row=row, column=1).value
        version = ws.cell(row=row, column=2).value

        if not name or not version:
            continue

        logging.info(f"Scanning {name} {version}")
        print(f"🔎 {name} {version}")

        cve_count, score, cve_list = fetch_cves(name, version)
        risk = calculate_risk(score)
        eol_status = check_eol(name)

        ws.cell(row=row, column=3).value = cve_count
        ws.cell(row=row, column=4).value = score
        ws.cell(row=row, column=5).value = risk
        ws.cell(row=row, column=5).fill = risk_color(risk)
        ws.cell(row=row, column=6).value = ", ".join(cve_list)
        ws.cell(row=row, column=7).value = eol_status

        total_cves += cve_count

        for cve in cve_list:
            cve_sheet.append([name, version, cve])

        if row % AUTO_SAVE_INTERVAL == 0:
            wb.save("autosave_temp.xlsx")
            print("💾 Auto-saved progress...")

    # Summary Sheet
    summary = wb.create_sheet("Summary")
    summary.append(["Scan Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    summary.append(["Total Applications", max_row - 1])
    summary.append(["Total CVEs Found", total_cves])
    summary.append(["Scan Duration (seconds)", round(time.time() - start_time, 2)])

    output_name = f"Enterprise_Vulnerability_Report_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    wb.save(output_name)

    print(f"\n✅ Enterprise report saved: {output_name}")

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    scan_excel("input.xlsx")
