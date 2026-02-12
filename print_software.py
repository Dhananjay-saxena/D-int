import winreg
import subprocess
import platform
from openpyxl import Workbook


# -----------------------------------
# REGISTRY SCAN (HKLM + HKCU + 32bit)
# -----------------------------------
def get_registry_apps():
    programs = []

    registry_locations = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for hive, path in registry_locations:
        try:
            reg_key = winreg.OpenKey(hive, path)
        except:
            continue

        for i in range(winreg.QueryInfoKey(reg_key)[0]):
            try:
                subkey_name = winreg.EnumKey(reg_key, i)
                subkey = winreg.OpenKey(reg_key, subkey_name)

                name = winreg.QueryValueEx(subkey, "DisplayName")[0]

                try:
                    version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                except:
                    version = "Unknown"

                programs.append((name.strip(), version.strip()))

            except:
                continue

    return programs


# -----------------------------------
# WMI SCAN (MSI based software)
# -----------------------------------
def get_wmi_apps():
    programs = []

    try:
        output = subprocess.check_output(
            ['wmic', 'product', 'get', 'name,version'],
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        ).decode(errors="ignore")

        lines = output.split("\n")[1:]

        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                version = parts[-1]
                name = " ".join(parts[:-1])
                programs.append((name.strip(), version.strip()))

    except:
        pass

    return programs


# -----------------------------------
# MICROSOFT STORE APPS
# -----------------------------------
def get_store_apps():
    programs = []

    try:
        ps_command = 'powershell "Get-AppxPackage | Select Name, Version"'
        output = subprocess.check_output(ps_command, shell=True).decode(errors="ignore")

        lines = output.split("\n")[3:]

        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                name = parts[0]
                version = parts[1]
                programs.append((name.strip(), version.strip()))

    except:
        pass

    return programs


# -----------------------------------
# REMOVE DUPLICATES
# -----------------------------------
def remove_duplicates(programs):
    seen = set()
    unique = []

    for name, version in programs:
        key = (name.lower(), version)
        if key not in seen and name != "":
            seen.add(key)
            unique.append((name, version))

    return unique


# -----------------------------------
# EXPORT TO EXCEL
# -----------------------------------
def generate_excel(programs):
    wb = Workbook()
    ws = wb.active
    ws.title = "Windows Software Inventory"

    ws.append(["Software Name", "Version"])

    for name, version in programs:
        ws.append([name, version])

    wb.save("Windows_Software_Inventory.xlsx")
    print("✅ Excel file created: Windows_Software_Inventory.xlsx")


# -----------------------------------
# MAIN
# -----------------------------------
def main():

    if platform.system() != "Windows":
        print("❌ Windows only")
        return

    print("🔍 Scanning Registry...")
    registry_apps = get_registry_apps()

    print("🔍 Scanning WMI...")
    wmi_apps = get_wmi_apps()

    print("🔍 Scanning Microsoft Store apps...")
    store_apps = get_store_apps()

    all_apps = registry_apps + wmi_apps + store_apps
    unique_apps = remove_duplicates(all_apps)

    print(f"✔ Total applications found: {len(unique_apps)}")

    generate_excel(unique_apps)


if __name__ == "__main__":
    main()
