import requests
import os
from tqdm import tqdm  
import requests
import subprocess


UPDATE_DEB_FILE = "/home/vipl/update.deb"

def config_deb_file_path():
    home_dir = os.path.expanduser("~")
    database_dir = os.path.join(home_dir, "Documents", "PlantScada", "database")
    return os.path.join(database_dir, "update.deb")

def get_latest_file_id():
    """Fetch the latest .deb file ID from Google Apps Script."""
    
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbznGngwK7ha-3ZXqBVKKpZDUq62VPMBUJApfXtmwwYh4-n6FWSXaUeY6GxAl8iBsy1S/exec"

    try:
        response = requests.get(APPS_SCRIPT_URL)
        if response.status_code == 200 and "Error" not in response.text:
            file_id = response.text.strip()
            print(f"Latest File ID: {file_id}")
            return file_id
        else:
            print("Failed to get file ID:", response.text)
            return None
    except requests.RequestException as e:
        print("Error fetching file ID:", e)
        return None


def download_update(file_id):
    """Download the latest .deb file from Google Drive API with a progress bar."""
    API_KEY = "AIzaSyD99xTpQI2nO5R9_J07rqVsflgkjb05D2s"
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={API_KEY}"
    
    UPDATE_DEB_FILE = config_deb_file_path()
    
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))  # Get total file size
        block_size = 1024 * 1024  # 🔹 1MB chunks

        if response.status_code == 200:
            with open(UPDATE_DEB_FILE, "wb") as f, tqdm(
                desc="Downloading",
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
    
    UPDATE_DEB_FILE = config_deb_file_path()
    
    try:
        subprocess.run(["sudo", "systemctl", "stop", "scada"], check=True)
        subprocess.run(["sudo", "dpkg", "-r", "scada"], check=True)
        subprocess.run(["sudo", "dpkg", "-i", UPDATE_DEB_FILE], check=True)
        subprocess.run(["sudo", "systemctl", "start", "scada"], check=True)
        print("Update installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing update: {e}")
        return False


def main():
    print("Checking for updates...")

    file_id = get_latest_file_id()
    if file_id:
        if download_update(file_id):
            if install_update():
                print("Update completed successfully!")
            else:
                print("Installation failed.")
        else:
            print("Download failed.")
    else:
        print("No new update available.")


if __name__ == "__main__":
    main()
