import requests
import os
import re
import subprocess
from tqdm import tqdm  


#  pyinstaller --clean -y -n "updater" --onefile updater_script2.py 


# Google Apps Script to get the latest file info (returns JSON with file_id & file_name)
# APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbznGngwK7ha-3ZXqBVKKpZDUq62VPMBUJApfXtmwwYh4-n6FWSXaUeY6GxAl8iBsy1S/exec"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxpXi7-HOks26evXkONnOjC0p4ugrD8NarL1dWlrgdVxpgfODdkvcAeKpERE9AwXgyC/exec"
API_KEY = "AIzaSyD99xTpQI2nO5R9_J07rqVsflgkjb05D2s"

# Config paths
def config_deb_file_path():
    """Define the path for storing the update file."""
    home_dir = os.path.expanduser("~")
    database_dir = os.path.join(home_dir, "Documents", "PlantScada", "database")
    return os.path.join(database_dir, "update.deb")

UPDATE_DEB_FILE = config_deb_file_path()

def get_installed_version():
    """Retrieve the currently installed version using dpkg."""
    try:
        result = subprocess.run(["dpkg-query", "-W", "-f=${Version}", "scada"], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Error getting installed version: {e}")
        return "0.0.0"

def extract_version_from_filename(file_name):
    """Extract the version number from the .deb file name (e.g., scada-v1.2.3.deb)."""
    match = re.search(r"scada-v(\d+\.\d+\.\d+)\.deb", file_name)
    return match.group(1) if match else None

def get_latest_file_info():
    """Fetch the latest .deb file information from Google Apps Script."""
    try:
        response = requests.get(APPS_SCRIPT_URL)

        if response.status_code == 200:
            data = response.json()  # Expecting JSON response like {"file_id": "...", "file_name": "scada-v1.2.3.deb"}
            file_id = data.get("file_id")
            file_name = data.get("file_name")
            
            if not file_id or not file_name:
                print("❌ Invalid response format.")
                return None, None
            
            print(f"📂 Latest File: {file_name} (ID: {file_id})")
            return file_id, file_name
        else:
            print(f"❌ Failed to get file info: {response.text}")
            return None, None
    except requests.RequestException as e:
        print(f"❌ Error fetching file info: {e}")
        return None, None

def download_update(file_id, latest_version):
    """Download the latest .deb file only if the version is newer."""
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={API_KEY}"

    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))  # Get total file size
        block_size = 1024 * 1024  # 🔹 1MB chunks

        if response.status_code == 200:
            with open(UPDATE_DEB_FILE, "wb") as f, tqdm(
                desc=f"Downloading v{latest_version}",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024
            ) as progress_bar:
                
                for chunk in response.iter_content(block_size):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))  # Update progress

            print(f"✅ Downloaded {UPDATE_DEB_FILE} successfully.")
            return True
        else:
            print(f"❌ Error downloading file: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def install_update():
    """Install the new application version."""
    try:
        print("🛠️ Stopping application service...")
        subprocess.run(["sudo", "systemctl", "stop", "scada"], check=True)

        print("🔧 Removing old version...")
        subprocess.run(["sudo", "dpkg", "-r", "scada"], check=True)

        print("📦 Installing new version...")
        subprocess.run(["sudo", "dpkg", "-i", UPDATE_DEB_FILE], check=True)

        print("🚀 Restarting application...")
        subprocess.run(["sudo", "systemctl", "start", "scada"], check=True)

        print("✅ Update installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing update: {e}")
        return False

def main():
    print("🔍 Checking for updates...")

    installed_version = get_installed_version()
    file_id, file_name = get_latest_file_info()
    
    if not file_id or not file_name:
        print("❌ No new update available.")
        return

    # Extract latest version from the .deb filename
    latest_version = extract_version_from_filename(file_name)
    
    if not latest_version:
        print("❌ Failed to extract version from file name.")
        return

    print(f"🔄 Installed: v{installed_version}, Available: v{latest_version}")

    if installed_version == latest_version:
        print("✅ Already updated to the latest version.")
    else:
        print(f"⬇️ New version available: v{latest_version}. Updating...")
        if download_update(file_id, latest_version):
            if install_update():
                print("🎉 Update completed successfully!")
            else:
                print("❌ Installation failed.")
        else:
            print("❌ Download failed.")

if __name__ == "__main__":
    main()


